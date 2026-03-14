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


def test_web_backend_clerk_scaffolds_concrete_tanstack_and_convex_wiring(
    tmp_path: Path,
) -> None:
    """Clerk fullstack scaffold should include concrete web/backend framework files."""

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
    web_main = web_root / "src" / "main.tsx"
    web_router = web_root / "src" / "router.tsx"
    web_root_route = web_root / "src" / "routes" / "__root.tsx"
    web_route_tree = web_root / "src" / "routeTree.gen.ts"
    web_app_config = web_root / "app.config.ts"
    web_vite_config = web_root / "vite.config.ts"
    web_tsconfig = web_root / "tsconfig.json"
    web_index_html = web_root / "index.html"
    backend_http = backend_root / "convex" / "http.ts"
    backend_schema = backend_root / "convex" / "schema.ts"
    backend_auth = backend_root / "convex" / "auth.config.ts"
    web_auth = web_root / "src" / "auth-provider.ts"
    shared_package = output_dir / "packages" / "shared" / "package.json"
    shared_index = output_dir / "packages" / "shared" / "src" / "index.ts"

    for path in (
        web_main,
        web_router,
        web_root_route,
        web_route_tree,
        web_app_config,
        web_vite_config,
        web_tsconfig,
        web_index_html,
        backend_http,
        backend_schema,
        backend_auth,
        web_auth,
        shared_package,
        shared_index,
    ):
        assert path.exists(), f"Expected scaffolded file: {path}"

    assert "RouterProvider" in web_main.read_text(encoding="utf-8")
    assert "createRouter" in web_router.read_text(encoding="utf-8")
    assert "routeTree" in web_route_tree.read_text(encoding="utf-8")
    assert "name" in web_app_config.read_text(encoding="utf-8")
    assert "defineConfig" in web_vite_config.read_text(encoding="utf-8")
    assert "createRootRoute" in web_root_route.read_text(encoding="utf-8")
    assert 'provider: "clerk"' in backend_auth.read_text(encoding="utf-8")
    assert "CLERK_FRONTEND_API_URL" in backend_auth.read_text(encoding="utf-8")
    assert "VITE_CLERK_PUBLISHABLE_KEY" in web_auth.read_text(encoding="utf-8")

    web_package_data = json.loads(
        (web_root / "package.json").read_text(encoding="utf-8")
    )
    backend_package_data = json.loads(
        (backend_root / "package.json").read_text(encoding="utf-8")
    )
    assert web_package_data["dependencies"]["@generated/shared"] == "workspace:*"
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
    shared_package = output_dir / "packages" / "shared" / "package.json"

    for path in (web_index_route, backend_http, backend_auth, web_auth, shared_package):
        assert path.exists(), f"Expected scaffolded file: {path}"

    assert "createFileRoute" in web_index_route.read_text(encoding="utf-8")
    assert "@generated/shared" in web_index_route.read_text(encoding="utf-8")
    assert 'provider: "better-auth"' in backend_auth.read_text(encoding="utf-8")
    assert "SITE_URL" in backend_auth.read_text(encoding="utf-8")
    assert "better auth" in web_auth.read_text(encoding="utf-8").lower()


def test_web_backend_dry_run_lists_concrete_framework_wiring_paths(
    tmp_path: Path,
) -> None:
    """Dry-run plan should include concrete TanStack and Convex wiring files."""

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
    assert "apps/web/web/src/main.tsx" in combined_output
    assert "apps/web/web/src/router.tsx" in combined_output
    assert "apps/web/web/src/routes/__root.tsx" in combined_output
    assert "apps/web/web/src/routeTree.gen.ts" in combined_output
    assert "apps/web/web/app.config.ts" in combined_output
    assert "apps/web/web/vite.config.ts" in combined_output
    assert "apps/web/web/tsconfig.json" in combined_output
    assert "apps/web/web/index.html" in combined_output
    assert "apps/backend/backend/convex/http.ts" in combined_output
    assert "apps/backend/backend/convex/schema.ts" in combined_output
    assert "packages/shared/package.json" in combined_output
