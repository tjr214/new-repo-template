from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_scaffold_command(
    *, repo_root: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.scaffold", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def run_nurt_command(*, cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[2]
    env["PYTHONPATH"] = str(repo_root / "src")
    env.setdefault("NURT_UPDATE_CHECK_SIMULATE", "none")
    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.nurt_cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_web_backend_tv_scaffolds_device_link_baseline(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fullstack-tv-device-link"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--target",
            "tv",
            "--auth",
            "clerk",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend+tv scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    web_root = output_dir / "apps" / "web" / "web"
    backend_root = output_dir / "apps" / "backend" / "backend"
    tv_root = output_dir / "apps" / "tv" / "tv"

    device_route = web_root / "src" / "routes" / "device.tsx"
    device_backend = backend_root / "convex" / "deviceLink.ts"
    backend_http = backend_root / "convex" / "http.ts"
    backend_schema = backend_root / "convex" / "schema.ts"
    tv_app = tv_root / "App.tsx"
    tv_readme = tv_root / "README.md"

    for path in (
        device_route,
        device_backend,
        backend_http,
        backend_schema,
        tv_app,
        tv_readme,
    ):
        assert path.exists(), f"Expected feature 14 scaffolded file: {path}"

    tv_manifest = json.loads((tv_root / "package.json").read_text(encoding="utf-8"))
    tv_dependencies = tv_manifest.get("dependencies", {})
    assert tv_dependencies.get("react-native-qrcode-svg") == "^6.3.21"
    assert tv_dependencies.get("react-native-svg") == "^15.15.4"

    btca_config = json.loads(
        (output_dir / "btca.config.jsonc").read_text(encoding="utf-8")
    )
    btca_resource_names = [resource["name"] for resource in btca_config["resources"]]
    assert "react-native-qrcode-svg" in btca_resource_names
    assert "react-native-svg" in btca_resource_names

    btca_docs = (output_dir / "docs" / "BTCA_RESOURCES.md").read_text(encoding="utf-8")
    assert "<name>react-native-qrcode-svg</name>" in btca_docs
    assert "<name>react-native-svg</name>" in btca_docs

    tv_app_text = tv_app.read_text(encoding="utf-8")
    assert "QRCode" in tv_app_text
    assert "verification_uri_complete" in tv_app_text
    assert "verification_uri" in tv_app_text
    assert "user_code" in tv_app_text
    assert "authorization_pending" in tv_app_text
    assert "slow_down" in tv_app_text
    assert "Refresh code" in tv_app_text
    assert "TVFocusRail" not in tv_app_text

    device_route_text = device_route.read_text(encoding="utf-8")
    assert 'createFileRoute("/device")' in device_route_text
    assert "activeAuthConfig.provider" in device_route_text
    assert "user_code" in device_route_text
    assert "Approve This TV" in device_route_text

    backend_http_text = backend_http.read_text(encoding="utf-8")
    backend_schema_text = backend_schema.read_text(encoding="utf-8")
    device_backend_text = device_backend.read_text(encoding="utf-8")
    assert "/device/code" in backend_http_text
    assert "/device/approve" in backend_http_text
    assert "/device/token" in backend_http_text
    assert "deviceLinks" in backend_schema_text
    assert "verificationUriComplete" in backend_schema_text
    assert "userCode" in backend_schema_text
    assert "DeviceLinkStatus" in device_backend_text
    assert "verification_uri_complete" in device_backend_text


def test_web_backend_without_tv_omits_device_link_scaffold(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fullstack-no-tv-device-link"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    assert not (
        output_dir / "apps" / "web" / "web" / "src" / "routes" / "device.tsx"
    ).exists()
    assert not (
        output_dir / "apps" / "backend" / "backend" / "convex" / "deviceLink.ts"
    ).exists()

    btca_config = json.loads(
        (output_dir / "btca.config.jsonc").read_text(encoding="utf-8")
    )
    btca_resource_names = [resource["name"] for resource in btca_config["resources"]]
    assert "react-native-qrcode-svg" not in btca_resource_names
    assert "react-native-svg" not in btca_resource_names


def test_nurt_add_tv_retrofits_existing_fullstack_repo_with_device_link_assets(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fullstack-then-tv"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "better-auth",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert scaffold_result.returncode == 0, (
        "Expected initial web+backend scaffold command to succeed.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    add_result = run_nurt_command(
        cwd=output_dir,
        args=["add", "--target", "tv", "--no-interactive"],
    )

    assert add_result.returncode == 0, (
        "Expected `nurt add --target tv` to retrofit device-link assets.\n"
        f"stdout:\n{add_result.stdout}\n"
        f"stderr:\n{add_result.stderr}"
    )

    assert (output_dir / "apps" / "tv" / "tv" / "App.tsx").exists()
    assert (
        output_dir / "apps" / "web" / "web" / "src" / "routes" / "device.tsx"
    ).exists()
    assert (
        output_dir / "apps" / "backend" / "backend" / "convex" / "deviceLink.ts"
    ).exists()

    tv_manifest = json.loads(
        (output_dir / "apps" / "tv" / "tv" / "package.json").read_text(encoding="utf-8")
    )
    tv_dependencies = tv_manifest.get("dependencies", {})
    assert tv_dependencies.get("react-native-qrcode-svg") == "^6.3.21"
    assert tv_dependencies.get("react-native-svg") == "^15.15.4"

    btca_config = json.loads(
        (output_dir / "btca.config.jsonc").read_text(encoding="utf-8")
    )
    btca_resource_names = [resource["name"] for resource in btca_config["resources"]]
    assert "react-native-qrcode-svg" in btca_resource_names
    assert "react-native-svg" in btca_resource_names

    combined_output = f"{add_result.stdout}\n{add_result.stderr}"
    assert "docs/BTCA_RESOURCES.md" in combined_output or "BTCA" in combined_output
