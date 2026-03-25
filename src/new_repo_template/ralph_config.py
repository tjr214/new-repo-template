from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from new_repo_template.snapshot_assets_loader import load_template_text


RALPH_CONFIG_FILE_NAME = "ralph.config.yaml"
DEFAULT_MAX_LOOPS = 20


@dataclass(frozen=True)
class RalphModelConfig:
    id: str
    label: str


@dataclass(frozen=True)
class RalphConfig:
    default_model: str
    max_loops: int
    models: tuple[RalphModelConfig, ...]
    source_path: Path | None


def resolve_user_ralph_config_path(
    *,
    platform: str | None = None,
    env: dict[str, str] | None = None,
) -> Path:
    active_platform = sys.platform if platform is None else platform
    active_env = os.environ if env is None else env
    home = Path(active_env.get("HOME", str(Path.home())))

    if active_platform.startswith("darwin"):
        return (
            home / "Library" / "Application Support" / "nurt" / RALPH_CONFIG_FILE_NAME
        )

    if active_platform.startswith("win"):
        appdata = active_env.get("APPDATA")
        appdata_root = Path(appdata) if appdata else home / "AppData" / "Roaming"
        return appdata_root / "nurt" / RALPH_CONFIG_FILE_NAME

    xdg_config_home = active_env.get("XDG_CONFIG_HOME")
    config_root = Path(xdg_config_home) if xdg_config_home else home / ".config"
    return config_root / "nurt" / RALPH_CONFIG_FILE_NAME


def _built_in_config_text() -> str:
    try:
        return load_template_text(f"foundation/{RALPH_CONFIG_FILE_NAME}")
    except FileNotFoundError:
        return (
            "default_model: openai/gpt-5.4\n"
            f"max_loops: {DEFAULT_MAX_LOOPS}\n"
            "models:\n"
            "  - id: openai/gpt-5.4\n"
            "    label: GPT-5.4\n"
        )


def _load_yaml_mapping(raw_text: str, *, source_label: str) -> dict[str, object]:
    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {source_label}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"RALPH config must be a YAML mapping in {source_label}")
    return data


def _parse_positive_int(value: object, *, field_name: str, source_label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer in {source_label}")
    return value


def _parse_models(
    models_obj: object,
    *,
    source_label: str,
) -> tuple[RalphModelConfig, ...]:
    if not isinstance(models_obj, list) or not models_obj:
        raise ValueError(f"models must be a non-empty list in {source_label}")

    models: list[RalphModelConfig] = []
    for index, model_obj in enumerate(models_obj, start=1):
        if not isinstance(model_obj, dict):
            raise ValueError(f"models[{index}] must be an object in {source_label}")
        model_id = model_obj.get("id")
        label = model_obj.get("label")
        if not isinstance(model_id, str) or model_id.strip() == "":
            raise ValueError(f"models[{index}].id must be a non-empty string")
        if not isinstance(label, str) or label.strip() == "":
            raise ValueError(f"models[{index}].label must be a non-empty string")
        models.append(RalphModelConfig(id=model_id, label=label))
    return tuple(models)


def _parse_ralph_config(
    data: dict[str, object],
    *,
    source_path: Path | None,
    source_label: str,
) -> RalphConfig:
    models = _parse_models(data.get("models"), source_label=source_label)
    default_model = data.get("default_model")
    if not isinstance(default_model, str) or default_model.strip() == "":
        raise ValueError(f"default_model must be a non-empty string in {source_label}")

    available_model_ids = {model.id for model in models}
    if default_model not in available_model_ids:
        raise ValueError(
            f"default_model must match one of the configured model ids in {source_label}"
        )

    max_loops = _parse_positive_int(
        data.get("max_loops", DEFAULT_MAX_LOOPS),
        field_name="max_loops",
        source_label=source_label,
    )
    return RalphConfig(
        default_model=default_model,
        max_loops=max_loops,
        models=models,
        source_path=source_path,
    )


def load_ralph_config(
    *,
    cwd: Path,
    user_config_path: Path | None = None,
) -> RalphConfig:
    local_config_path = cwd / RALPH_CONFIG_FILE_NAME
    if local_config_path.exists():
        raw_text = local_config_path.read_text(encoding="utf-8")
        return _parse_ralph_config(
            _load_yaml_mapping(raw_text, source_label=str(local_config_path)),
            source_path=local_config_path,
            source_label=str(local_config_path),
        )

    resolved_user_config_path = (
        resolve_user_ralph_config_path()
        if user_config_path is None
        else user_config_path
    )
    if resolved_user_config_path.exists():
        raw_text = resolved_user_config_path.read_text(encoding="utf-8")
        return _parse_ralph_config(
            _load_yaml_mapping(raw_text, source_label=str(resolved_user_config_path)),
            source_path=resolved_user_config_path,
            source_label=str(resolved_user_config_path),
        )

    built_in_text = _built_in_config_text()
    return _parse_ralph_config(
        _load_yaml_mapping(built_in_text, source_label="built-in Ralph config"),
        source_path=None,
        source_label="built-in Ralph config",
    )
