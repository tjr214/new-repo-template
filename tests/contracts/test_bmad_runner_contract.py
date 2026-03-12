from __future__ import annotations

import subprocess
from pathlib import Path

from new_repo_template import bmad_runner


def test_run_bmad_sync_dry_run_reports_command(tmp_path: Path, capsys) -> None:
    status = bmad_runner.run_bmad_sync(project_root=tmp_path, dry_run=True)

    captured = capsys.readouterr()
    assert status == 0
    assert "DRY RUN" in captured.out
    assert "npx bmad-method@latest install" in captured.out


def test_run_bmad_sync_fails_when_npx_is_missing(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    monkeypatch.setattr(bmad_runner.shutil, "which", lambda _: None)

    status = bmad_runner.run_bmad_sync(project_root=tmp_path, dry_run=False)

    captured = capsys.readouterr()
    assert status == 1
    assert "npx is required" in captured.out


def test_run_bmad_sync_executes_expected_command(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(bmad_runner.shutil, "which", lambda _: "/usr/bin/npx")

    def fake_run(
        command: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured["cwd"] = kwargs.get("cwd")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(bmad_runner.subprocess, "run", fake_run)

    status = bmad_runner.run_bmad_sync(project_root=tmp_path, dry_run=False)

    assert status == 0
    assert captured["command"] == ["npx", "bmad-method@latest", "install"]
    assert captured["cwd"] == tmp_path
