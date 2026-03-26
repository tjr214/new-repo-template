from __future__ import annotations

import hashlib
import json
import re
from collections import OrderedDict
from dataclasses import dataclass


BTCA_SCHEMA_URL = "https://btca.dev/btca.schema.json"
BTCA_DATA_DIRECTORY = ".btca"
BTCA_MODEL = "gpt-5.4"
BTCA_PROVIDER = "openai"
BTCA_SIDECAR_RELATIVE_PATH = ".nurt/btca-managed-resources.json"
BTCA_DOCS_RELATIVE_PATH = "docs/BTCA_RESOURCES.md"
BTCA_CONFIG_RELATIVE_PATH = "btca.config.jsonc"
BTCA_SIDECAR_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ProjectContext:
    kind: str
    auth: str | None = None


@dataclass(frozen=True)
class ResourceDefinition:
    name: str
    url: str
    branch: str
    type: str = "git"
    search_path: str | None = None
    special_notes: str | None = None

    def as_config_resource(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "type": self.type,
            "name": self.name,
            "url": self.url,
            "branch": self.branch,
        }
        if self.search_path is not None:
            payload["searchPath"] = self.search_path
        if self.special_notes is not None:
            payload["specialNotes"] = self.special_notes
        return payload


@dataclass(frozen=True)
class ManagedResourceRecord:
    name: str
    reasons: tuple[str, ...]
    fingerprint: str


@dataclass(frozen=True)
class GeneratedBtcaFiles:
    config_text: str
    docs_text: str
    sidecar_text: str
    resource_names: tuple[str, ...]


@dataclass(frozen=True)
class MergeBtcaFilesResult:
    config_text: str
    docs_text: str
    sidecar_text: str
    warnings: tuple[str, ...]


RESOURCE_DEFINITIONS: tuple[ResourceDefinition, ...] = (
    ResourceDefinition(
        name="turborepo",
        url="https://github.com/vercel/turborepo",
        branch="main",
    ),
    ResourceDefinition(
        name="bun",
        url="https://github.com/oven-sh/bun",
        branch="main",
    ),
    ResourceDefinition(
        name="tanstack-router-start",
        url="https://github.com/TanStack/router",
        branch="main",
    ),
    ResourceDefinition(
        name="convex-better-auth",
        url="https://github.com/get-convex/better-auth",
        branch="main",
    ),
    ResourceDefinition(
        name="clerk-docs",
        url="https://github.com/clerk/clerk-docs",
        branch="main",
    ),
    ResourceDefinition(
        name="expo-docs",
        url="https://github.com/expo/expo",
        branch="main",
        search_path="docs",
    ),
    ResourceDefinition(
        name="react-native-tvos",
        url="https://github.com/react-native-tvos/react-native-tvos",
        branch="main",
    ),
    ResourceDefinition(
        name="expo-tv-config",
        url="https://github.com/react-native-tvos/config-tv",
        branch="main",
    ),
    ResourceDefinition(
        name="better-auth-core",
        url="https://github.com/better-auth/better-auth",
        branch="main",
    ),
    ResourceDefinition(
        name="convex-docs",
        url="https://github.com/get-convex/convex-docs",
        branch="main",
    ),
    ResourceDefinition(
        name="textual",
        url="https://github.com/Textualize/textual",
        branch="main",
        search_path="docs",
        special_notes=(
            "Official Textual framework docs and examples for widget, layout, and "
            "testing guidance."
        ),
    ),
    ResourceDefinition(
        name="rich-docs",
        url="https://github.com/Textualize/rich",
        branch="master",
        search_path="docs",
        special_notes=(
            "Official Rich docs for terminal rendering, console output, and "
            "fallback presentation patterns."
        ),
    ),
    ResourceDefinition(
        name="pytest-textual-snapshot",
        url="https://github.com/Textualize/pytest-textual-snapshot",
        branch="main",
        special_notes=(
            "Snapshot-testing plugin for Textual visual regression coverage and "
            "review workflows."
        ),
    ),
    ResourceDefinition(
        name="uv",
        url="https://github.com/astral-sh/uv",
        branch="main",
        search_path="docs",
        special_notes=(
            "Official uv docs and repo for project management and command behavior "
            "guidance."
        ),
    ),
    ResourceDefinition(
        name="react-docs",
        url="https://github.com/reactjs/react.dev",
        branch="main",
    ),
    ResourceDefinition(
        name="react-native-docs",
        url="https://github.com/facebook/react-native-website",
        branch="main",
    ),
    ResourceDefinition(
        name="vite",
        url="https://github.com/vitejs/vite",
        branch="main",
    ),
    ResourceDefinition(
        name="electron-forge",
        url="https://github.com/electron/forge",
        branch="main",
    ),
    ResourceDefinition(
        name="electron",
        url="https://github.com/electron/electron",
        branch="main",
    ),
    ResourceDefinition(
        name="typescript-docs",
        url="https://github.com/microsoft/TypeScript-Website",
        branch="v2",
    ),
    ResourceDefinition(
        name="pytest",
        url="https://github.com/pytest-dev/pytest",
        branch="main",
    ),
    ResourceDefinition(
        name="ruff",
        url="https://github.com/astral-sh/ruff",
        branch="main",
    ),
    ResourceDefinition(
        name="mypy",
        url="https://github.com/python/mypy",
        branch="master",
    ),
)

RESOURCE_BY_NAME = {resource.name: resource for resource in RESOURCE_DEFINITIONS}

FOUNDATION_RESOURCE_NAMES: tuple[str, ...] = ("turborepo", "bun")

TARGET_RESOURCE_NAMES: dict[str, tuple[str, ...]] = {
    "python": ("uv", "textual", "rich-docs", "pytest", "ruff", "mypy"),
    "python-lib": ("uv", "pytest", "ruff", "mypy"),
    "typescript-cli": ("typescript-docs",),
    "typescript-lib": ("typescript-docs",),
    "web": ("tanstack-router-start", "react-docs", "vite", "typescript-docs"),
    "backend": ("convex-docs", "typescript-docs"),
    "desktop": ("electron-forge", "electron", "typescript-docs"),
    "mobile": ("expo-docs", "react-docs", "react-native-docs", "typescript-docs"),
    "tv": (
        "expo-docs",
        "react-docs",
        "react-native-docs",
        "react-native-tvos",
        "expo-tv-config",
        "typescript-docs",
    ),
}

BACKEND_AUTH_RESOURCE_NAMES: dict[str, tuple[str, ...]] = {
    "clerk": ("clerk-docs",),
    "better-auth": ("better-auth-core", "convex-better-auth"),
    "none": (),
}

CAMEL_CASE_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def project_contexts_from_projects(
    projects: tuple[object, ...],
) -> tuple[ProjectContext, ...]:
    contexts: list[ProjectContext] = []
    for project in projects:
        kind = getattr(project, "kind")
        auth = getattr(project, "auth", None)
        if not isinstance(kind, str):
            raise ValueError("project kind must be a string")
        if auth is not None and not isinstance(auth, str):
            raise ValueError("project auth must be a string or None")
        contexts.append(ProjectContext(kind=kind, auth=auth))
    return tuple(contexts)


def _append_reason(
    reasons_by_name: OrderedDict[str, list[str]],
    *,
    resource_name: str,
    reason: str,
) -> None:
    reasons = reasons_by_name.setdefault(resource_name, [])
    if reason not in reasons:
        reasons.append(reason)


def resolve_managed_resource_names(
    projects: tuple[ProjectContext, ...],
) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    reasons_by_name: OrderedDict[str, list[str]] = OrderedDict()

    for resource_name in FOUNDATION_RESOURCE_NAMES:
        _append_reason(
            reasons_by_name, resource_name=resource_name, reason="foundation"
        )

    for project in projects:
        if project.kind == "foundation":
            continue
        for resource_name in TARGET_RESOURCE_NAMES.get(project.kind, ()):
            _append_reason(
                reasons_by_name,
                resource_name=resource_name,
                reason=project.kind,
            )
        if project.kind == "backend":
            auth_key = project.auth if project.auth is not None else "none"
            for resource_name in BACKEND_AUTH_RESOURCE_NAMES.get(auth_key, ()):
                _append_reason(
                    reasons_by_name,
                    resource_name=resource_name,
                    reason=f"backend:{auth_key}",
                )

    ordered_names = tuple(
        resource.name
        for resource in RESOURCE_DEFINITIONS
        if resource.name in reasons_by_name
    )
    reasons = {name: tuple(reasons_by_name[name]) for name in ordered_names}
    return ordered_names, reasons


def _resource_payloads_for_names(
    resource_names: tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    payloads: list[dict[str, object]] = []
    for name in resource_names:
        definition = RESOURCE_BY_NAME.get(name)
        if definition is None:
            raise ValueError(f"unknown BTCA resource definition: {name}")
        payloads.append(definition.as_config_resource())
    return tuple(payloads)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def fingerprint_resource(resource: dict[str, object]) -> str:
    digest = hashlib.sha256(_canonical_json(resource).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _render_json(payload: object) -> str:
    return json.dumps(payload, indent=2) + "\n"


def render_btca_config(
    resources: tuple[dict[str, object], ...],
    *,
    top_level_fields: dict[str, object] | None = None,
) -> str:
    if top_level_fields is None:
        payload: dict[str, object] = {
            "$schema": BTCA_SCHEMA_URL,
            "dataDirectory": BTCA_DATA_DIRECTORY,
            "resources": list(resources),
            "model": BTCA_MODEL,
            "provider": BTCA_PROVIDER,
        }
        return _render_json(payload)

    payload = dict(top_level_fields)
    payload["resources"] = list(resources)
    return _render_json(payload)


def _xml_tag_name(raw_key: str) -> str:
    return CAMEL_CASE_BOUNDARY.sub("_", raw_key).lower()


def render_btca_resources_doc(resources: tuple[dict[str, object], ...]) -> str:
    lines = ["<current_btca_resources>", ""]
    for resource in resources:
        name = resource.get("name")
        resource_type = resource.get("type")
        if not isinstance(name, str) or not isinstance(resource_type, str):
            raise ValueError("BTCA resources require string name and type fields")
        lines.append("<configured_resource>")
        lines.append(f"<name>{name}</name>")
        lines.append(f"<type>{resource_type}</type>")
        for key, value in resource.items():
            if key in {"name", "type"}:
                continue
            if isinstance(value, (str, int, float)):
                lines.append(f"<{_xml_tag_name(key)}>{value}</{_xml_tag_name(key)}>")
        lines.append("</configured_resource>")
        lines.append("")
    lines.append("</current_btca_resources>")
    lines.append("")
    return "\n".join(lines)


def render_btca_sidecar(
    records: tuple[ManagedResourceRecord, ...],
) -> str:
    payload = {
        "schema_version": BTCA_SIDECAR_SCHEMA_VERSION,
        "managed_resources": [
            {
                "name": record.name,
                "reasons": list(record.reasons),
                "fingerprint": record.fingerprint,
            }
            for record in records
        ],
    }
    return _render_json(payload)


def _parse_btca_config(config_text: str) -> dict[str, object]:
    payload = json.loads(config_text)
    if not isinstance(payload, dict):
        raise ValueError("btca.config.jsonc must contain a JSON object")
    resources = payload.get("resources")
    if not isinstance(resources, list):
        raise ValueError("btca.config.jsonc must contain a list field 'resources'")
    return payload


def _coerce_resource_list(resources_obj: object) -> tuple[dict[str, object], ...]:
    if not isinstance(resources_obj, list):
        raise ValueError("BTCA resources must be a list")
    resources: list[dict[str, object]] = []
    for resource in resources_obj:
        if not isinstance(resource, dict):
            raise ValueError("BTCA resources must be JSON objects")
        name = resource.get("name")
        resource_type = resource.get("type")
        if not isinstance(name, str) or not isinstance(resource_type, str):
            raise ValueError("BTCA resources must include string name and type fields")
        resources.append(dict(resource))
    return tuple(resources)


def _parse_sidecar(sidecar_text: str) -> tuple[ManagedResourceRecord, ...]:
    payload = json.loads(sidecar_text)
    if not isinstance(payload, dict):
        raise ValueError("BTCA sidecar must contain a JSON object")
    if payload.get("schema_version") != BTCA_SIDECAR_SCHEMA_VERSION:
        raise ValueError("unsupported BTCA sidecar schema_version")
    records_obj = payload.get("managed_resources")
    if not isinstance(records_obj, list):
        raise ValueError("BTCA sidecar must contain list field 'managed_resources'")

    records: list[ManagedResourceRecord] = []
    for record_obj in records_obj:
        if not isinstance(record_obj, dict):
            raise ValueError("BTCA sidecar records must be objects")
        name = record_obj.get("name")
        reasons_obj = record_obj.get("reasons")
        fingerprint = record_obj.get("fingerprint")
        if not isinstance(name, str) or not isinstance(fingerprint, str):
            raise ValueError("BTCA sidecar records require string name and fingerprint")
        if not isinstance(reasons_obj, list) or not all(
            isinstance(reason, str) for reason in reasons_obj
        ):
            raise ValueError("BTCA sidecar reasons must be a list of strings")
        records.append(
            ManagedResourceRecord(
                name=name,
                reasons=tuple(reasons_obj),
                fingerprint=fingerprint,
            )
        )
    return tuple(records)


def generate_scaffold_btca_files(
    projects: tuple[ProjectContext, ...],
) -> GeneratedBtcaFiles:
    resource_names, reasons_by_name = resolve_managed_resource_names(projects)
    resources = _resource_payloads_for_names(resource_names)
    records = tuple(
        ManagedResourceRecord(
            name=name,
            reasons=reasons_by_name[name],
            fingerprint=fingerprint_resource(resource),
        )
        for name, resource in zip(resource_names, resources, strict=True)
    )
    return GeneratedBtcaFiles(
        config_text=render_btca_config(resources),
        docs_text=render_btca_resources_doc(resources),
        sidecar_text=render_btca_sidecar(records),
        resource_names=resource_names,
    )


def merge_add_mode_btca_files(
    *,
    existing_config_text: str,
    existing_sidecar_text: str,
    projects: tuple[ProjectContext, ...],
) -> MergeBtcaFilesResult:
    config_payload = _parse_btca_config(existing_config_text)
    existing_resources = _coerce_resource_list(config_payload.get("resources"))
    sidecar_records = _parse_sidecar(existing_sidecar_text)
    managed_records_by_name = {record.name: record for record in sidecar_records}

    desired_names, desired_reasons_by_name = resolve_managed_resource_names(projects)
    desired_resources = _resource_payloads_for_names(desired_names)
    desired_by_name = {
        name: resource
        for name, resource in zip(desired_names, desired_resources, strict=True)
    }

    final_resources: list[dict[str, object]] = []
    updated_records: OrderedDict[str, ManagedResourceRecord] = OrderedDict()
    warnings: list[str] = []
    existing_names: set[str] = set()

    for resource in existing_resources:
        name_obj = resource.get("name")
        assert isinstance(name_obj, str)
        resource_name = name_obj
        existing_names.add(resource_name)
        desired_resource = desired_by_name.get(resource_name)
        current_record = managed_records_by_name.get(resource_name)

        if desired_resource is None:
            final_resources.append(resource)
            if current_record is not None:
                updated_records[resource_name] = current_record
            continue

        desired_reasons = desired_reasons_by_name[resource_name]
        current_fingerprint = fingerprint_resource(resource)
        desired_fingerprint = fingerprint_resource(desired_resource)

        if current_record is None:
            final_resources.append(resource)
            if current_fingerprint != desired_fingerprint:
                warnings.append(
                    "preserved untracked BTCA resource "
                    f"'{resource_name}' because it conflicts with a nurt-managed name"
                )
            continue

        if current_fingerprint == current_record.fingerprint:
            final_resources.append(desired_resource)
            updated_records[resource_name] = ManagedResourceRecord(
                name=resource_name,
                reasons=desired_reasons,
                fingerprint=desired_fingerprint,
            )
            continue

        if current_fingerprint == desired_fingerprint:
            final_resources.append(resource)
            updated_records[resource_name] = ManagedResourceRecord(
                name=resource_name,
                reasons=desired_reasons,
                fingerprint=current_fingerprint,
            )
            continue

        final_resources.append(resource)
        updated_records[resource_name] = ManagedResourceRecord(
            name=resource_name,
            reasons=desired_reasons,
            fingerprint=current_record.fingerprint,
        )
        warnings.append(
            "preserved customized nurt-managed BTCA resource "
            f"'{resource_name}' because it drifted from the last managed fingerprint"
        )

    for resource_name, desired_resource in zip(
        desired_names, desired_resources, strict=True
    ):
        if resource_name in existing_names:
            continue
        final_resources.append(desired_resource)
        updated_records[resource_name] = ManagedResourceRecord(
            name=resource_name,
            reasons=desired_reasons_by_name[resource_name],
            fingerprint=fingerprint_resource(desired_resource),
        )

    final_records = tuple(
        updated_records[resource_name]
        for resource_name in [
            resource.get("name")
            for resource in final_resources
            if isinstance(resource.get("name"), str)
            and resource.get("name") in updated_records
        ]
    )

    return MergeBtcaFilesResult(
        config_text=render_btca_config(
            tuple(final_resources), top_level_fields=config_payload
        ),
        docs_text=render_btca_resources_doc(tuple(final_resources)),
        sidecar_text=render_btca_sidecar(final_records),
        warnings=tuple(warnings),
    )
