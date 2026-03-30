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


def test_web_backend_clerk_scaffolds_real_tanstack_start_and_convex_wiring(
    tmp_path: Path,
) -> None:
    """Clerk fullstack scaffold should include real Start and Convex files."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fullstack-clerk"

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
        "Expected web+backend+clerk scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    web_root = output_dir / "apps" / "web" / "web"
    backend_root = output_dir / "apps" / "backend" / "backend"
    web_client = web_root / "src" / "client.tsx"
    web_router = web_root / "src" / "router.tsx"
    web_root_route = web_root / "src" / "routes" / "__root.tsx"
    web_index_route = web_root / "src" / "routes" / "index.tsx"
    web_route_tree = web_root / "src" / "routeTree.gen.ts"
    web_vite_config = web_root / "vite.config.ts"
    web_tsconfig = web_root / "tsconfig.json"
    web_components = web_root / "components.json"
    backend_http = backend_root / "convex" / "http.ts"
    backend_schema = backend_root / "convex" / "schema.ts"
    backend_auth = backend_root / "convex" / "auth.config.ts"
    web_auth = web_root / "src" / "auth-provider.ts"
    web_app_auth = web_root / "src" / "app-auth.ts"
    web_auth_runtime = web_root / "src" / "auth-runtime.ts"
    shared_package = output_dir / "packages" / "shared" / "package.json"
    shared_index = output_dir / "packages" / "shared" / "src" / "index.ts"
    design_tokens_package = output_dir / "packages" / "design-tokens" / "package.json"
    design_tokens_index = output_dir / "packages" / "design-tokens" / "src" / "index.ts"
    ui_package = output_dir / "packages" / "ui" / "package.json"
    ui_button = output_dir / "packages" / "ui" / "src" / "components" / "button.tsx"

    for path in (
        web_client,
        web_router,
        web_root_route,
        web_index_route,
        web_route_tree,
        web_vite_config,
        web_tsconfig,
        web_components,
        backend_http,
        backend_schema,
        backend_auth,
        web_auth,
        web_app_auth,
        web_auth_runtime,
        shared_package,
        shared_index,
        design_tokens_package,
        design_tokens_index,
        ui_package,
        ui_button,
    ):
        assert path.exists(), f"Expected scaffolded file: {path}"

    assert not (web_root / "src" / "main.tsx").exists()
    assert not (web_root / "app.config.ts").exists()
    assert not (web_root / "index.html").exists()

    assert "StartClient" in web_client.read_text(encoding="utf-8")
    assert "hydrateRoot" in web_client.read_text(encoding="utf-8")
    assert "createRouter" in web_router.read_text(encoding="utf-8")
    assert "export function getRouter()" in web_router.read_text(encoding="utf-8")
    assert "routeTree" in web_route_tree.read_text(encoding="utf-8")
    assert "@tanstack/react-start" in web_route_tree.read_text(encoding="utf-8")
    assert "@tanstack/react-start/plugin/vite" in web_vite_config.read_text(
        encoding="utf-8"
    )
    assert "tanstackStart()" in web_vite_config.read_text(encoding="utf-8")
    assert "viteReact()" in web_vite_config.read_text(encoding="utf-8")
    assert "createRootRoute" in web_root_route.read_text(encoding="utf-8")
    assert "HeadContent" in web_root_route.read_text(encoding="utf-8")
    assert "Scripts" in web_root_route.read_text(encoding="utf-8")
    assert 'createFileRoute("/")' in web_index_route.read_text(encoding="utf-8")
    assert "@generated/ui/components/button" in web_index_route.read_text(
        encoding="utf-8"
    )
    assert "nurtDesignTokens" in web_index_route.read_text(encoding="utf-8")
    assert "@generated/ui/components" in web_components.read_text(encoding="utf-8")
    assert 'local: "clerk"' in backend_auth.read_text(encoding="utf-8")
    assert 'prod: "clerk"' in backend_auth.read_text(encoding="utf-8")
    assert "CLERK_JWT_ISSUER_DOMAIN_LOCAL" in backend_auth.read_text(encoding="utf-8")
    assert "VITE_CLERK_PUBLISHABLE_KEY_LOCAL" in web_auth.read_text(encoding="utf-8")
    assert 'provider: "clerk"' in web_app_auth.read_text(encoding="utf-8")

    web_package_data = json.loads(
        (web_root / "package.json").read_text(encoding="utf-8")
    )
    backend_package_data = json.loads(
        (backend_root / "package.json").read_text(encoding="utf-8")
    )
    assert web_package_data["dependencies"]["@generated/design-tokens"] == "workspace:*"
    assert web_package_data["dependencies"]["@generated/shared"] == "workspace:*"
    assert web_package_data["dependencies"]["@generated/ui"] == "workspace:*"
    assert "@tanstack/react-start" in web_package_data["dependencies"]
    assert backend_package_data["dependencies"]["@generated/shared"] == "workspace:*"


def test_web_backend_better_auth_scaffolds_concrete_tanstack_and_convex_wiring(
    tmp_path: Path,
) -> None:
    """Better Auth fullstack scaffold should include concrete web/backend wiring."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fullstack-better-auth"

    result = run_scaffold_command(
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

    assert result.returncode == 0, (
        "Expected web+backend+better-auth scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    web_index_route = (
        output_dir / "apps" / "web" / "web" / "src" / "routes" / "index.tsx"
    )
    backend_http = output_dir / "apps" / "backend" / "backend" / "convex" / "http.ts"
    backend_auth = (
        output_dir / "apps" / "backend" / "backend" / "convex" / "auth.config.ts"
    )
    web_auth = output_dir / "apps" / "web" / "web" / "src" / "auth-client.ts"
    web_app_auth = output_dir / "apps" / "web" / "web" / "src" / "app-auth.ts"
    web_auth_runtime = output_dir / "apps" / "web" / "web" / "src" / "auth-runtime.ts"
    shared_package = output_dir / "packages" / "shared" / "package.json"
    design_tokens_package = output_dir / "packages" / "design-tokens" / "package.json"
    ui_package = output_dir / "packages" / "ui" / "package.json"
    web_client = output_dir / "apps" / "web" / "web" / "src" / "client.tsx"
    web_router = output_dir / "apps" / "web" / "web" / "src" / "router.tsx"
    web_root_route = (
        output_dir / "apps" / "web" / "web" / "src" / "routes" / "__root.tsx"
    )
    web_vite_config = output_dir / "apps" / "web" / "web" / "vite.config.ts"

    for path in (
        web_index_route,
        web_client,
        web_router,
        web_root_route,
        web_vite_config,
        backend_http,
        backend_auth,
        web_auth,
        web_app_auth,
        web_auth_runtime,
        shared_package,
        design_tokens_package,
        ui_package,
    ):
        assert path.exists(), f"Expected scaffolded file: {path}"

    web_index_text = web_index_route.read_text(encoding="utf-8")
    assert 'createFileRoute("/")' in web_index_text
    assert "@generated/shared" in web_index_text
    assert "@generated/ui/components/button" in web_index_text
    assert "StartClient" in web_client.read_text(encoding="utf-8")
    assert "export function getRouter()" in web_router.read_text(encoding="utf-8")
    assert "HeadContent" in web_root_route.read_text(encoding="utf-8")
    assert "Scripts" in web_root_route.read_text(encoding="utf-8")
    assert "tanstackStart()" in web_vite_config.read_text(encoding="utf-8")
    assert "getAuthConfigProvider" in backend_auth.read_text(encoding="utf-8")
    assert "SITE_URL" in web_auth.read_text(encoding="utf-8")
    assert "better auth" in web_auth.read_text(encoding="utf-8").lower()
    assert 'provider: "better-auth"' in web_app_auth.read_text(encoding="utf-8")


def test_web_backend_dry_run_lists_real_start_framework_wiring_paths(
    tmp_path: Path,
) -> None:
    """Dry-run plan should include real Start and Convex wiring files."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fullstack-dry-run"

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
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/web/web/src/client.tsx" in combined_output
    assert "apps/web/web/src/router.tsx" in combined_output
    assert "apps/web/web/src/routes/__root.tsx" in combined_output
    assert "apps/web/web/src/routes/index.tsx" in combined_output
    assert "apps/web/web/src/routeTree.gen.ts" in combined_output
    assert "apps/web/web/vite.config.ts" in combined_output
    assert "apps/web/web/tsconfig.json" in combined_output
    assert "apps/web/web/components.json" in combined_output
    assert "apps/backend/backend/convex/http.ts" in combined_output
    assert "apps/backend/backend/convex/schema.ts" in combined_output
    assert "packages/shared/package.json" in combined_output
    assert "packages/design-tokens/package.json" in combined_output
    assert "packages/ui/package.json" in combined_output
    assert "apps/web/web/src/main.tsx" not in combined_output
    assert "apps/web/web/app.config.ts" not in combined_output
    assert "apps/web/web/index.html" not in combined_output
