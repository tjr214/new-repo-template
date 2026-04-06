from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from new_repo_template.btca_config_manager import (
    BTCA_CONFIG_RELATIVE_PATH,
    BTCA_DOCS_RELATIVE_PATH,
    BTCA_SIDECAR_RELATIVE_PATH,
    merge_add_mode_btca_files,
    project_contexts_from_projects,
)
from new_repo_template import scaffold
from new_repo_template.project_naming import normalize_project_name
from new_repo_template.snapshot_assets_loader import load_template_text
from new_repo_template.version_baseline import generate_project_lockfiles


SIMULATE_ADD_FAILURE_ENV = "NURT_ADD_SIMULATE_FAILURE"

ADDABLE_TARGET_CHOICES: tuple[str, ...] = tuple(
    target for target in scaffold.TARGET_CHOICES if target != "foundation"
)

APP_BASE_DIRS: dict[str, str] = {
    "python": "apps/python",
    "web": "apps/web",
    "backend": "apps/backend",
    "desktop": "apps/desktop",
    "mobile": "apps/mobile",
    "tv": "apps/tv",
    "typescript-cli": "apps/typescript-cli",
}

LIBRARY_BASE_DIRS: dict[str, str] = {
    "python-lib": "packages/python",
    "typescript-lib": "packages/typescript",
}


@dataclass(frozen=True)
class ExistingRepoState:
    repo_root: Path
    projects: tuple[scaffold.ProjectSpec, ...]
    has_shared_package: bool
    has_design_tokens_package: bool
    has_ui_package: bool

    @property
    def backend_projects(self) -> tuple[scaffold.ProjectSpec, ...]:
        return tuple(project for project in self.projects if project.kind == "backend")

    @property
    def backend_names(self) -> tuple[str, ...]:
        return tuple(project.name for project in self.backend_projects)

    @property
    def python_projects(self) -> tuple[scaffold.ProjectSpec, ...]:
        return tuple(project for project in self.projects if project.kind == "python")

    @property
    def python_libraries(self) -> tuple[scaffold.ProjectSpec, ...]:
        return tuple(
            project for project in self.projects if project.kind == "python-lib"
        )

    @property
    def desktop_projects(self) -> tuple[scaffold.ProjectSpec, ...]:
        return tuple(project for project in self.projects if project.kind == "desktop")

    @property
    def has_web(self) -> bool:
        return any(project.kind == "web" for project in self.projects)


@dataclass(frozen=True)
class AddPlan:
    repo_root: Path
    existing_projects: tuple[scaffold.ProjectSpec, ...]
    requested_projects: tuple[scaffold.ProjectSpec, ...]
    combined_projects: tuple[scaffold.ProjectSpec, ...]
    create_shared_package: bool
    create_design_tokens_package: bool
    create_ui_package: bool
    write_root_python_workspace: bool
    root_python_workspace_content: str | None
    retrofit_python_apps: tuple[scaffold.ProjectSpec, ...]
    retrofit_desktops: tuple[scaffold.ProjectSpec, ...]
    btca_config_content: str
    btca_sidecar_content: str
    btca_docs_content: str
    btca_warnings: tuple[str, ...]
    retrofits: tuple[str, ...]
    lockfiles: tuple[str, ...]


@dataclass(frozen=True)
class AddExecutionSummary:
    added_projects: tuple[str, ...]
    retrofits: tuple[str, ...]
    lockfiles: tuple[str, ...]
    btca_warnings: tuple[str, ...]


def _parse_project_token(token: str) -> scaffold.ProjectSpec:
    if ":" not in token:
        raise ValueError(
            "project must use the form <type>:<name>, for example web:dashboard"
        )
    raw_kind, raw_name = token.split(":", 1)
    kind = raw_kind.strip().lower()
    if kind not in ADDABLE_TARGET_CHOICES:
        if kind == "foundation":
            raise ValueError("foundation is not addable; choose a project target")
        raise ValueError(f"unsupported project type: {raw_kind}")
    return scaffold.ProjectSpec(kind=kind, name=normalize_project_name(raw_name))


def _parse_mapping_option(
    *, token: str, option_name: str, allowed_values: tuple[str, ...] | None = None
) -> tuple[str, str]:
    if ":" not in token:
        raise ValueError(
            f"{option_name} must use the form <name>:<value>, got {token!r}"
        )
    raw_name, raw_value = token.split(":", 1)
    name = normalize_project_name(raw_name)
    value = raw_value.strip().lower()
    if value == "":
        raise ValueError(f"{option_name} value cannot be empty")
    if allowed_values is not None and value not in allowed_values:
        raise ValueError(
            f"{option_name} value must be one of {', '.join(allowed_values)}"
        )
    return name, value


def _iter_existing_project_dirs(base_dir: Path) -> tuple[Path, ...]:
    if not base_dir.exists() or not base_dir.is_dir():
        return ()
    return tuple(sorted(path for path in base_dir.iterdir() if path.is_dir()))


def _detect_backend_auth(backend_root: Path) -> str | None:
    auth_config = backend_root / "convex" / "auth.config.ts"
    if not auth_config.exists() or not auth_config.is_file():
        return None
    content = auth_config.read_text(encoding="utf-8")
    if "better-auth" in content:
        return "better-auth"
    if "clerk" in content:
        return "clerk"
    return None


def inventory_existing_repo(*, repo_root: Path) -> ExistingRepoState:
    projects: list[scaffold.ProjectSpec] = []

    for kind, relative_root in APP_BASE_DIRS.items():
        for project_root in _iter_existing_project_dirs(repo_root / relative_root):
            auth = _detect_backend_auth(project_root) if kind == "backend" else None
            projects.append(
                scaffold.ProjectSpec(kind=kind, name=project_root.name, auth=auth)
            )

    for kind, relative_root in LIBRARY_BASE_DIRS.items():
        for project_root in _iter_existing_project_dirs(repo_root / relative_root):
            projects.append(scaffold.ProjectSpec(kind=kind, name=project_root.name))

    ordering = {kind: index for index, kind in enumerate(scaffold.TARGET_CHOICES)}
    ordered_projects = tuple(
        sorted(projects, key=lambda item: (ordering[item.kind], item.name))
    )

    return ExistingRepoState(
        repo_root=repo_root,
        projects=ordered_projects,
        has_shared_package=(
            repo_root / "packages" / "shared" / "package.json"
        ).exists(),
        has_design_tokens_package=(
            repo_root / "packages" / "design-tokens" / "package.json"
        ).exists(),
        has_ui_package=(repo_root / "packages" / "ui" / "package.json").exists(),
    )


def resolve_add_projects(
    *,
    parser,  # argparse.ArgumentParser
    args,
    existing_state: ExistingRepoState,
) -> tuple[scaffold.ProjectSpec, ...]:
    raw_targets = list(getattr(args, "target", None) or [])
    raw_projects = list(getattr(args, "project", None) or [])

    if not raw_targets and not raw_projects:
        parser.error("at least one --target or --project selection is required")

    selected_targets = scaffold.normalize_targets(raw_targets)
    if "foundation" in selected_targets:
        parser.error("foundation is not addable; choose a project target")

    requested_projects: list[scaffold.ProjectSpec] = [
        scaffold.ProjectSpec(kind=target, name=scaffold.default_project_name(target))
        for target in selected_targets
    ]

    for token in raw_projects:
        try:
            requested_projects.append(_parse_project_token(token))
        except ValueError as exc:
            parser.error(str(exc))

    requested_keys: set[tuple[str, str]] = set()
    duplicate_projects: list[str] = []
    for project in requested_projects:
        key = (project.kind, project.name)
        if key in requested_keys:
            duplicate_projects.append(f"{project.kind}:{project.name}")
            continue
        requested_keys.add(key)
    if duplicate_projects:
        parser.error(
            "duplicate project selections are not allowed: "
            + ", ".join(duplicate_projects)
        )

    existing_keys = {
        (project.kind, project.name) for project in existing_state.projects
    }
    collisions = [
        f"{project.kind}:{project.name}"
        for project in requested_projects
        if (project.kind, project.name) in existing_keys
    ]
    if collisions:
        parser.error("project already exists: " + ", ".join(collisions))

    requested_backend_names = {
        project.name for project in requested_projects if project.kind == "backend"
    }
    if args.auth is not None and not requested_backend_names:
        parser.error("auth option is only valid when backend target is selected")

    backend_auth_map: dict[str, str | None] = {}
    for token in list(getattr(args, "backend_auth", None) or []):
        backend_name = ""
        backend_auth = ""
        try:
            backend_name, backend_auth = _parse_mapping_option(
                token=token,
                option_name="--backend-auth",
                allowed_values=("clerk", "better-auth", "none"),
            )
        except ValueError as exc:
            parser.error(str(exc))
        if backend_name not in requested_backend_names:
            parser.error(
                f"--backend-auth references unknown backend project: {backend_name}"
            )
        backend_auth_map[backend_name] = (
            None if backend_auth == "none" else backend_auth
        )

    default_backend_auth = None if args.auth in {None, "none"} else str(args.auth)

    resolved_projects: list[scaffold.ProjectSpec] = []
    for project in requested_projects:
        if project.kind != "backend":
            resolved_projects.append(project)
            continue
        auth = backend_auth_map.get(project.name, default_backend_auth)
        if auth is None and project.name not in backend_auth_map and args.auth is None:
            parser.error(
                "auth option is required when backend target is selected; use clerk, better-auth, or none"
            )
        resolved_projects.append(
            scaffold.ProjectSpec(kind=project.kind, name=project.name, auth=auth)
        )

    requested_web_names = {
        project.name for project in resolved_projects if project.kind == "web"
    }
    combined_backend_names = {
        project.name for project in existing_state.backend_projects
    }
    combined_backend_names.update(
        project.name for project in resolved_projects if project.kind == "backend"
    )

    web_backend_map: dict[str, str] = {}
    for token in list(getattr(args, "web_backend", None) or []):
        web_name = ""
        backend_name = ""
        try:
            web_name, backend_name = _parse_mapping_option(
                token=token,
                option_name="--web-backend",
            )
        except ValueError as exc:
            parser.error(str(exc))
        if web_name not in requested_web_names:
            parser.error(f"--web-backend references unknown web project: {web_name}")
        if backend_name not in combined_backend_names:
            parser.error(
                f"--web-backend references unknown backend project: {backend_name}"
            )
        web_backend_map[web_name] = backend_name

    if requested_web_names and len(combined_backend_names) > 1:
        missing = sorted(
            name for name in requested_web_names if name not in web_backend_map
        )
        if missing:
            parser.error(
                "web-backend binding is required when multiple backend projects exist: "
                + ", ".join(missing)
            )

    if requested_web_names and len(combined_backend_names) == 1:
        backend_name = next(iter(combined_backend_names))
        for web_name in requested_web_names:
            web_backend_map.setdefault(web_name, backend_name)

    final_projects: list[scaffold.ProjectSpec] = []
    for project in resolved_projects:
        if project.kind == "web":
            final_projects.append(
                scaffold.ProjectSpec(
                    kind=project.kind,
                    name=project.name,
                    backend_binding=web_backend_map.get(project.name),
                )
            )
            continue
        final_projects.append(project)

    return tuple(final_projects)


def _supports_python_workspace(projects: tuple[scaffold.ProjectSpec, ...]) -> bool:
    return any(project.kind in {"python", "python-lib"} for project in projects)


def _workspace_project_name(repo_root: Path) -> str:
    return f"{normalize_project_name(repo_root.name)}-workspace"


def _read_text_or_none(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _project_path_exists(repo_root: Path, project: scaffold.ProjectSpec) -> bool:
    return (repo_root / Path(scaffold.project_relative_root(project))).exists()


def _expected_python_lane_text(
    *,
    project: scaffold.ProjectSpec,
    library_project: scaffold.ProjectSpec | None,
) -> str:
    return scaffold.render_python_lane_pyproject(
        project=project,
        library_project=library_project,
    )


def _python_library_to_wire(
    projects: tuple[scaffold.ProjectSpec, ...],
) -> scaffold.ProjectSpec | None:
    libraries = [project for project in projects if project.kind == "python-lib"]
    return libraries[0] if len(libraries) == 1 else None


def _needs_desktop_retrofit(project_root: Path) -> bool:
    package_json = project_root / "package.json"
    renderer_path = project_root / "src" / "renderer.ts"

    if not package_json.exists() or not renderer_path.exists():
        return False

    data = json.loads(package_json.read_text(encoding="utf-8"))
    dependencies = data.get("dependencies")
    if (
        isinstance(dependencies, dict)
        and dependencies.get("@generated/shared") == "workspace:*"
    ):
        renderer_text = renderer_path.read_text(encoding="utf-8")
        return (
            renderer_text.strip()
            != scaffold.DESKTOP_RENDERER_WITH_SHARED_TEMPLATE.strip()
        )
    return True


def build_add_plan(
    *,
    repo_root: Path,
    existing_state: ExistingRepoState,
    requested_projects: tuple[scaffold.ProjectSpec, ...],
) -> AddPlan:
    for project in requested_projects:
        if _project_path_exists(repo_root, project):
            raise ValueError(
                f"project path already exists: {scaffold.project_relative_root(project)}"
            )

    combined_projects = (*existing_state.projects, *requested_projects)
    retrofits: list[str] = []

    root_python_workspace_content: str | None = None
    write_root_python_workspace = False
    root_pyproject_path = repo_root / "pyproject.toml"
    if _supports_python_workspace(combined_projects):
        root_python_workspace_content = scaffold.render_root_python_workspace_pyproject(
            projects=combined_projects,
            workspace_project_name=_workspace_project_name(repo_root),
        )
        current_root_pyproject = _read_text_or_none(root_pyproject_path)
        if current_root_pyproject is None:
            write_root_python_workspace = True
            retrofits.append("create root pyproject.toml for the uv workspace")
        elif current_root_pyproject != root_python_workspace_content:
            if not _supports_python_workspace(existing_state.projects):
                raise ValueError(
                    "existing root pyproject.toml prevents automatic Python workspace upgrade"
                )
            expected_existing = scaffold.render_root_python_workspace_pyproject(
                projects=existing_state.projects,
                workspace_project_name=_workspace_project_name(repo_root),
            )
            if current_root_pyproject not in {
                expected_existing,
                root_python_workspace_content,
            }:
                raise ValueError(
                    "existing root pyproject.toml has unsupported customizations for automatic add-mode updates"
                )
            write_root_python_workspace = True
            retrofits.append("update root pyproject.toml workspace members")

    create_shared_package = False
    if (
        any(
            project.kind in {"web", "backend", "desktop", "mobile", "tv"}
            for project in combined_projects
        )
        and not existing_state.has_shared_package
    ):
        create_shared_package = True
        retrofits.append(
            "create packages/shared for the shared frontend/backend copy layer"
        )

    create_design_tokens_package = False
    if (
        any(project.kind in {"web", "desktop"} for project in combined_projects)
        and not existing_state.has_design_tokens_package
    ):
        create_design_tokens_package = True
        retrofits.append(
            "create packages/design-tokens for the shared frontend theme contract"
        )

    create_ui_package = False
    if (
        any(project.kind == "web" for project in combined_projects)
        and not existing_state.has_ui_package
    ):
        create_ui_package = True
        retrofits.append("create packages/ui for the owned web component foundation")

    retrofit_python_apps: list[scaffold.ProjectSpec] = []
    if any(project.kind == "python-lib" for project in requested_projects):
        shared_library = _python_library_to_wire(combined_projects)
        if shared_library is not None and len(existing_state.python_projects) == 1:
            app_project = existing_state.python_projects[0]
            app_pyproject_path = (
                repo_root
                / scaffold.project_relative_root(app_project)
                / "pyproject.toml"
            )
            current_text = _read_text_or_none(app_pyproject_path)
            expected_current = _expected_python_lane_text(
                project=app_project,
                library_project=None,
            )
            expected_updated = _expected_python_lane_text(
                project=app_project,
                library_project=shared_library,
            )
            if current_text == expected_updated:
                pass
            elif current_text == expected_current:
                retrofit_python_apps.append(app_project)
                retrofits.append(
                    f"patch {scaffold.project_relative_root(app_project)}/pyproject.toml to depend on the new workspace Python library"
                )
            else:
                raise ValueError(
                    f"unsupported customizations in {scaffold.project_relative_root(app_project)}/pyproject.toml prevent automatic python-lib retrofit"
                )

    retrofit_desktops: list[scaffold.ProjectSpec] = []
    if any(project.kind == "web" for project in requested_projects):
        for desktop_project in existing_state.desktop_projects:
            desktop_root = repo_root / scaffold.project_relative_root(desktop_project)
            if not _needs_desktop_retrofit(desktop_root):
                continue
            renderer_path = desktop_root / "src" / "renderer.ts"
            renderer_text = _read_text_or_none(renderer_path)
            if renderer_text not in {
                scaffold.DESKTOP_RENDERER_TEMPLATE,
                scaffold.DESKTOP_RENDERER_WITH_SHARED_TEMPLATE,
            }:
                raise ValueError(
                    f"unsupported customizations in {scaffold.project_relative_root(desktop_project)}/src/renderer.ts prevent automatic desktop retrofit"
                )
            retrofit_desktops.append(desktop_project)
            retrofits.append(
                f"patch {scaffold.project_relative_root(desktop_project)} for shared desktop wiring"
            )

    btca_config_path = repo_root / BTCA_CONFIG_RELATIVE_PATH
    current_btca_config = _read_text_or_none(btca_config_path)
    if current_btca_config is None:
        raise ValueError(
            f"missing {BTCA_CONFIG_RELATIVE_PATH}; automatic BTCA add-mode updates require a nurt-generated repo root"
        )

    btca_sidecar_path = repo_root / BTCA_SIDECAR_RELATIVE_PATH
    current_btca_sidecar = _read_text_or_none(btca_sidecar_path)
    if current_btca_sidecar is None:
        raise ValueError(
            f"missing {BTCA_SIDECAR_RELATIVE_PATH}; automatic BTCA add-mode updates require a feature 9.0 repo"
        )

    btca_merge_result = merge_add_mode_btca_files(
        existing_config_text=current_btca_config,
        existing_sidecar_text=current_btca_sidecar,
        projects=project_contexts_from_projects(tuple(combined_projects)),
    )

    current_btca_docs = _read_text_or_none(repo_root / BTCA_DOCS_RELATIVE_PATH)
    if current_btca_config != btca_merge_result.config_text:
        retrofits.append(
            "update btca.config.jsonc for the merged project BTCA resources"
        )
    if current_btca_sidecar != btca_merge_result.sidecar_text:
        retrofits.append(
            "update .nurt/btca-managed-resources.json for managed BTCA tracking"
        )
    if current_btca_docs != btca_merge_result.docs_text:
        retrofits.append("update docs/BTCA_RESOURCES.md to reflect final BTCA state")

    lockfiles = ["bun.lock"]
    if _supports_python_workspace(combined_projects):
        lockfiles.append("uv.lock")

    return AddPlan(
        repo_root=repo_root,
        existing_projects=existing_state.projects,
        requested_projects=requested_projects,
        combined_projects=tuple(combined_projects),
        create_shared_package=create_shared_package,
        create_design_tokens_package=create_design_tokens_package,
        create_ui_package=create_ui_package,
        write_root_python_workspace=write_root_python_workspace,
        root_python_workspace_content=root_python_workspace_content,
        retrofit_python_apps=tuple(retrofit_python_apps),
        retrofit_desktops=tuple(retrofit_desktops),
        btca_config_content=btca_merge_result.config_text,
        btca_sidecar_content=btca_merge_result.sidecar_text,
        btca_docs_content=btca_merge_result.docs_text,
        btca_warnings=btca_merge_result.warnings,
        retrofits=tuple(retrofits),
        lockfiles=tuple(lockfiles),
    )


def render_add_plan(plan: AddPlan) -> str:
    lines = [
        "Resolved add plan:",
        f"- repo root: {plan.repo_root}",
        "- existing projects:",
    ]
    if not plan.existing_projects:
        lines.append("  - foundation")
    else:
        lines.extend(
            f"  - {project.kind}:{project.name}" for project in plan.existing_projects
        )

    lines.append("- requested additions:")
    lines.extend(
        f"  - {'; '.join(_project_details(project))}"
        for project in plan.requested_projects
    )

    lines.append("- required retrofits:")
    if not plan.retrofits:
        lines.append("  - none")
    else:
        lines.extend(f"  - {item}" for item in plan.retrofits)

    lines.append("- lockfiles:")
    lines.extend(f"  - {lockfile}" for lockfile in plan.lockfiles)
    lines.append("- BTCA warnings:")
    if plan.btca_warnings:
        lines.extend(f"  - {warning}" for warning in plan.btca_warnings)
    else:
        lines.append("  - none")
    return "\n".join(lines)


def _project_details(project: scaffold.ProjectSpec) -> tuple[str, ...]:
    details = [f"{project.kind}:{project.name}"]
    if project.kind == "backend":
        details.append(f"auth={project.auth if project.auth is not None else 'none'}")
    if project.kind == "web" and project.backend_binding is not None:
        details.append(f"backend={project.backend_binding}")
    return tuple(details)


@dataclass
class _BackupEntry:
    existed: bool
    is_symlink: bool
    content: bytes | None
    symlink_target: str | None
    mode: int | None


class _RepoMutationTransaction:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self._backups: dict[Path, _BackupEntry] = {}
        self._created_dirs: list[Path] = []

    def _backup_path(self, path: Path) -> None:
        if path in self._backups:
            return
        if not path.exists() and not path.is_symlink():
            self._backups[path] = _BackupEntry(
                existed=False,
                is_symlink=False,
                content=None,
                symlink_target=None,
                mode=None,
            )
            return
        stat_result = path.lstat()
        if path.is_symlink():
            self._backups[path] = _BackupEntry(
                existed=True,
                is_symlink=True,
                content=None,
                symlink_target=os.readlink(path),
                mode=stat_result.st_mode,
            )
            return
        self._backups[path] = _BackupEntry(
            existed=True,
            is_symlink=False,
            content=path.read_bytes(),
            symlink_target=None,
            mode=stat_result.st_mode,
        )

    def _ensure_parent_dir(self, path: Path) -> None:
        pending: list[Path] = []
        current = path.parent
        while current != self.repo_root and not current.exists():
            pending.append(current)
            current = current.parent
        if not self.repo_root.exists():
            raise ValueError(f"repo root does not exist: {self.repo_root}")
        for directory in reversed(pending):
            directory.mkdir(exist_ok=True)
            self._created_dirs.append(directory)

    def write_text(self, path: Path, content: str) -> None:
        self._backup_path(path)
        self._ensure_parent_dir(path)
        if path.exists() or path.is_symlink():
            if path.is_dir():
                raise ValueError(f"cannot overwrite directory with file: {path}")
            path.unlink()
        path.write_text(content, encoding="utf-8")

    def copy_from_stage(self, src: Path, dest: Path) -> None:
        self._backup_path(dest)
        self._ensure_parent_dir(dest)
        if dest.exists() or dest.is_symlink():
            if dest.is_dir():
                raise ValueError(f"cannot overwrite directory with file: {dest}")
            dest.unlink()
        if src.is_symlink():
            dest.symlink_to(os.readlink(src))
            return
        shutil.copy2(src, dest)

    def rollback(self) -> None:
        for path, backup in reversed(tuple(self._backups.items())):
            if path.exists() or path.is_symlink():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            if not backup.existed:
                continue
            self._ensure_parent_dir(path)
            if backup.is_symlink:
                assert backup.symlink_target is not None
                path.symlink_to(backup.symlink_target)
            else:
                assert backup.content is not None
                path.write_bytes(backup.content)
            if backup.mode is not None and not path.is_symlink():
                path.chmod(backup.mode)

        for directory in reversed(self._created_dirs):
            try:
                directory.rmdir()
            except OSError:
                continue


def _stage_scaffold_content(plan: AddPlan) -> Path:
    stage_root = Path(tempfile.mkdtemp(prefix="nurt-add-stage-"))
    shared_library = _python_library_to_wire(plan.combined_projects)
    has_web = any(project.kind == "web" for project in plan.combined_projects)

    if plan.create_shared_package:
        scaffold.scaffold_shared_workspace_package(
            output_root=stage_root,
            projects=plan.combined_projects,
        )

    if plan.create_design_tokens_package:
        scaffold.scaffold_design_tokens_workspace_package(
            output_root=stage_root,
            projects=plan.combined_projects,
        )

    if plan.create_ui_package:
        scaffold.scaffold_ui_workspace_package(
            output_root=stage_root,
            projects=plan.combined_projects,
        )

    if plan.write_root_python_workspace:
        assert plan.root_python_workspace_content is not None
        (stage_root / "pyproject.toml").write_text(
            plan.root_python_workspace_content,
            encoding="utf-8",
        )

    for project in plan.requested_projects:
        if project.kind == "python":
            scaffold.scaffold_python_lane(
                output_root=stage_root,
                project=project,
                library_project=shared_library,
            )
        elif project.kind == "python-lib":
            scaffold.scaffold_python_library(output_root=stage_root, project=project)
        elif project.kind == "typescript-cli":
            scaffold.scaffold_typescript_cli_project(
                output_root=stage_root, project=project
            )
        elif project.kind == "typescript-lib":
            scaffold.scaffold_typescript_library(
                output_root=stage_root, project=project
            )
        elif project.kind == "web":
            scaffold.scaffold_web_project(output_root=stage_root, project=project)
        elif project.kind == "backend":
            scaffold.scaffold_backend_project(output_root=stage_root, project=project)
        elif project.kind == "desktop":
            scaffold.scaffold_desktop_project(
                output_root=stage_root,
                project=project,
                has_web=has_web,
            )
        elif project.kind == "mobile":
            scaffold.scaffold_mobile_project(output_root=stage_root, project=project)
        elif project.kind == "tv":
            scaffold.scaffold_tv_project(output_root=stage_root, project=project)
        else:
            raise ValueError(f"unsupported add project kind: {project.kind}")

    _write_requested_web_auth_assets(stage_root=stage_root, plan=plan)
    return stage_root


def _backend_lookup(
    projects: tuple[scaffold.ProjectSpec, ...],
) -> dict[str, scaffold.ProjectSpec]:
    return {project.name: project for project in projects if project.kind == "backend"}


def _write_requested_web_auth_assets(*, stage_root: Path, plan: AddPlan) -> None:
    backend_by_name = _backend_lookup(plan.combined_projects)

    for web_project in (
        project for project in plan.requested_projects if project.kind == "web"
    ):
        backend_name = web_project.backend_binding
        if backend_name is None:
            continue
        backend = backend_by_name.get(backend_name)
        if backend is None or backend.auth is None:
            continue
        auth_templates = scaffold.AUTH_ENV_TEMPLATE_FILES[backend.auth]
        web_root = stage_root / scaffold.project_relative_root(web_project)
        web_root.mkdir(parents=True, exist_ok=True)
        (web_root / ".env.example").write_text(
            load_template_text(auth_templates["web"]),
            encoding="utf-8",
        )
        backend_root = stage_root / scaffold.project_relative_root(backend)
        backend_root.mkdir(parents=True, exist_ok=True)
        (backend_root / ".env.example").write_text(
            load_template_text(auth_templates["backend"]),
            encoding="utf-8",
        )
        web_src = web_root / "src"
        web_src.mkdir(parents=True, exist_ok=True)
        if backend.auth == "clerk":
            (web_src / "auth-provider.ts").write_text(
                scaffold.WEB_AUTH_PROVIDER_CLERK_TEMPLATE,
                encoding="utf-8",
            )
        else:
            (web_src / "auth-client.ts").write_text(
                scaffold.WEB_AUTH_CLIENT_BETTER_AUTH_TEMPLATE,
                encoding="utf-8",
            )


def _iter_stage_files(stage_root: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for path in stage_root.rglob("*"):
        if path.is_dir():
            continue
        files.append(path)
    return tuple(
        sorted(files, key=lambda item: item.relative_to(stage_root).as_posix())
    )


def _patch_python_app_for_library(
    *,
    repo_root: Path,
    app_project: scaffold.ProjectSpec,
    library_project: scaffold.ProjectSpec,
    transaction: _RepoMutationTransaction,
) -> None:
    app_pyproject_path = (
        repo_root / scaffold.project_relative_root(app_project) / "pyproject.toml"
    )
    current_text = app_pyproject_path.read_text(encoding="utf-8")
    expected_existing = scaffold.render_python_lane_pyproject(
        project=app_project,
        library_project=None,
    )
    if current_text == expected_existing:
        transaction.write_text(
            app_pyproject_path,
            scaffold.render_python_lane_pyproject(
                project=app_project,
                library_project=library_project,
            ),
        )


def _patch_desktop_for_shared(
    *,
    repo_root: Path,
    desktop_project: scaffold.ProjectSpec,
    transaction: _RepoMutationTransaction,
) -> None:
    desktop_root = repo_root / scaffold.project_relative_root(desktop_project)
    package_json_path = desktop_root / "package.json"
    renderer_path = desktop_root / "src" / "renderer.ts"

    package_data = json.loads(package_json_path.read_text(encoding="utf-8"))
    dependencies = package_data.get("dependencies")
    if not isinstance(dependencies, dict):
        dependencies = {}
        package_data["dependencies"] = dependencies
    dependencies.setdefault("@generated/shared", "workspace:*")
    dependencies.setdefault("@generated/design-tokens", "workspace:*")
    package_text = json.dumps(package_data, indent=2) + "\n"
    transaction.write_text(package_json_path, package_text)

    renderer_text = renderer_path.read_text(encoding="utf-8")
    if renderer_text != scaffold.DESKTOP_RENDERER_WITH_SHARED_TEMPLATE:
        transaction.write_text(
            renderer_path, scaffold.DESKTOP_RENDERER_WITH_SHARED_TEMPLATE
        )


def execute_add(plan: AddPlan) -> AddExecutionSummary:
    stage_root = _stage_scaffold_content(plan)
    transaction = _RepoMutationTransaction(plan.repo_root)
    shared_library = _python_library_to_wire(plan.combined_projects)

    try:
        for staged_file in _iter_stage_files(stage_root):
            relative = staged_file.relative_to(stage_root)
            destination = plan.repo_root / relative
            transaction.copy_from_stage(staged_file, destination)
            if os.environ.get(
                SIMULATE_ADD_FAILURE_ENV
            ) == "after-root-python-upgrade" and relative == Path("pyproject.toml"):
                raise RuntimeError("simulated add failure after root python upgrade")

        if shared_library is not None:
            for app_project in plan.retrofit_python_apps:
                _patch_python_app_for_library(
                    repo_root=plan.repo_root,
                    app_project=app_project,
                    library_project=shared_library,
                    transaction=transaction,
                )

        for desktop_project in plan.retrofit_desktops:
            _patch_desktop_for_shared(
                repo_root=plan.repo_root,
                desktop_project=desktop_project,
                transaction=transaction,
            )

        btca_config_path = plan.repo_root / BTCA_CONFIG_RELATIVE_PATH
        if _read_text_or_none(btca_config_path) != plan.btca_config_content:
            transaction.write_text(btca_config_path, plan.btca_config_content)

        btca_sidecar_path = plan.repo_root / BTCA_SIDECAR_RELATIVE_PATH
        if _read_text_or_none(btca_sidecar_path) != plan.btca_sidecar_content:
            transaction.write_text(btca_sidecar_path, plan.btca_sidecar_content)

        btca_docs_path = plan.repo_root / BTCA_DOCS_RELATIVE_PATH
        if _read_text_or_none(btca_docs_path) != plan.btca_docs_content:
            transaction.write_text(btca_docs_path, plan.btca_docs_content)
    except Exception:
        transaction.rollback()
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)

    lockfile_status = generate_project_lockfiles(project_root=plan.repo_root)
    if lockfile_status != 0:
        raise RuntimeError("lockfile regeneration failed after add")

    return AddExecutionSummary(
        added_projects=tuple(
            f"{project.kind}:{project.name}" for project in plan.requested_projects
        ),
        retrofits=plan.retrofits,
        lockfiles=plan.lockfiles,
        btca_warnings=plan.btca_warnings,
    )


def render_add_completion(*, repo_root: Path, summary: AddExecutionSummary) -> str:
    lines = [
        "nurt add completed successfully.",
        f"- repo root: {repo_root}",
        "- added projects:",
    ]
    lines.extend(f"  - {project}" for project in summary.added_projects)
    lines.append("- retrofits:")
    if summary.retrofits:
        lines.extend(f"  - {retrofit}" for retrofit in summary.retrofits)
    else:
        lines.append("  - none")
    lines.append("- lockfiles:")
    lines.extend(f"  - {lockfile}" for lockfile in summary.lockfiles)
    lines.append("- BTCA warnings:")
    if summary.btca_warnings:
        lines.extend(f"  - {warning}" for warning in summary.btca_warnings)
    else:
        lines.append("  - none")
    return "\n".join(lines)
