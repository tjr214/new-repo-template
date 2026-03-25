from __future__ import annotations

from pathlib import Path

from new_repo_template.ralph_config import (
    DEFAULT_MAX_LOOPS,
    load_ralph_config,
    resolve_user_ralph_config_path,
)
from new_repo_template.ralph_tasks import (
    load_ralph_task_plan,
    resolve_execution_settings,
    validate_ralph_task_file,
)


def _write_schema(repo_root: Path) -> None:
    docs_tasks = repo_root / "docs" / "tasks"
    docs_tasks.mkdir(parents=True, exist_ok=True)
    source_schema = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "tasks"
        / "task-template-schema.json"
    )
    (docs_tasks / "task-template-schema.json").write_text(
        source_schema.read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def _write_task_file(repo_root: Path, *, framework: str, name: str = "demo") -> Path:
    task_path = repo_root / "docs" / "tasks" / f"{name}.yaml"
    task_path.parent.mkdir(parents=True, exist_ok=True)
    task_path.write_text(
        f"""# Task Implementation Plan
metadata:
  version: "1.1.0"
  created_date: "2026-03-24"
  last_updated: "2026-03-24"
  author: "test"
  license: null
  framework: "{framework}"
task:
  name: "Demo Task"
  description: |
    Demo description.
  status: "pending"
  phases:
    - id: "phase-1"
      name: "Phase One"
      description: |
        Demo phase.
      status: "pending"
      steps:
        - id: "step-1.1"
          name: "Step One"
          description: "Demo step"
          status: "pending"
          instructions:
            - id: "instr-1.1.1"
              content: |
                Demo instruction.
              status: "pending"
""",
        encoding="utf-8",
    )
    return task_path


def test_ralph_config_prefers_project_file_and_validates_defaults(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "ralph.config.yaml").write_text(
        """default_model: custom/model
max_loops: 12
models:
  - id: custom/model
    label: Custom
""",
        encoding="utf-8",
    )

    user_config_root = tmp_path / "user-config"
    user_config_root.mkdir()
    user_config_path = user_config_root / "ralph.config.yaml"
    user_config_path.write_text(
        """default_model: user/model
max_loops: 99
models:
  - id: user/model
    label: User
""",
        encoding="utf-8",
    )

    config = load_ralph_config(
        cwd=repo_root,
        user_config_path=user_config_path,
    )

    assert config.source_path == repo_root / "ralph.config.yaml"
    assert config.default_model == "custom/model"
    assert config.max_loops == 12
    assert tuple(model.id for model in config.models) == ("custom/model",)

    built_in = load_ralph_config(cwd=tmp_path / "missing", user_config_path=None)
    assert built_in.max_loops == DEFAULT_MAX_LOOPS
    assert built_in.default_model in {model.id for model in built_in.models}


def test_resolve_user_ralph_config_path_uses_platform_specific_locations(
    tmp_path: Path,
) -> None:
    env = {
        "HOME": str(tmp_path / "home"),
        "XDG_CONFIG_HOME": str(tmp_path / "xdg-config"),
        "APPDATA": str(tmp_path / "appdata"),
    }

    assert (
        resolve_user_ralph_config_path(platform="linux", env=env)
        == Path(env["XDG_CONFIG_HOME"]) / "nurt" / "ralph.config.yaml"
    )
    assert (
        resolve_user_ralph_config_path(platform="darwin", env=env)
        == Path(env["HOME"])
        / "Library"
        / "Application Support"
        / "nurt"
        / "ralph.config.yaml"
    )
    assert (
        resolve_user_ralph_config_path(platform="win32", env=env)
        == Path(env["APPDATA"]) / "nurt" / "ralph.config.yaml"
    )


def test_ralph_task_framework_controls_agent_and_bmad_closeout(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_schema(repo_root)

    bmad_task = _write_task_file(repo_root, framework="bmad", name="bmad-task")
    standalone_task = _write_task_file(
        repo_root, framework="standalone", name="standalone-task"
    )

    bmad_plan = load_ralph_task_plan(bmad_task)
    standalone_plan = load_ralph_task_plan(standalone_task)

    assert resolve_execution_settings(bmad_plan).agent == "bmad-master"
    assert resolve_execution_settings(bmad_plan).bmad_closeout is True
    assert resolve_execution_settings(standalone_plan).agent == "build"
    assert resolve_execution_settings(standalone_plan).bmad_closeout is False


def test_validate_ralph_task_file_requires_framework_metadata(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _write_schema(repo_root)
    task_path = repo_root / "docs" / "tasks" / "missing-framework.yaml"
    task_path.parent.mkdir(parents=True, exist_ok=True)
    task_path.write_text(
        """metadata:
  version: "1.1.0"
  created_date: "2026-03-24"
  last_updated: "2026-03-24"
  author: "test"
  license: null
task:
  name: "Demo Task"
  description: "Demo"
  status: "pending"
  phases:
    - id: "phase-1"
      name: "Phase"
      description: "Demo"
      status: "pending"
      steps:
        - id: "step-1.1"
          name: "Step"
          description: "Demo"
          status: "pending"
          instructions:
            - id: "instr-1.1.1"
              content: "Demo"
              status: "pending"
""",
        encoding="utf-8",
    )

    result = validate_ralph_task_file(task_path, cwd=repo_root)

    assert result.is_valid is False
    assert "framework" in result.output
