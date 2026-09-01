#!/usr/bin/env python3
"""Instala e verifica dependências locais do repertório de IA do MedSync."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "docs" / "ai" / "skills-lock.json"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def load_lock() -> dict:
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def verify_file(relative_path: str, expected: str) -> tuple[bool, str]:
    path = ROOT / relative_path
    if not path.is_file():
        return False, f"ausente: {relative_path}"
    actual = git_blob_sha1(path.read_bytes())
    if actual != expected:
        return False, f"divergente: {relative_path} ({actual})"
    return True, f"ok: {relative_path}"


def verify_repository_files(lock: dict) -> bool:
    success = True
    for skill in lock["skills"].values():
        for relative_path, expected in skill.get("files", {}).items():
            valid, message = verify_file(relative_path, expected)
            print(message)
            success = success and valid
    return success


def graphify_tool_matches(lock: dict) -> tuple[bool, str]:
    expected = lock["skills"].get("graphify", {}).get("local_tool")
    if not expected:
        return True, "Graphify não é exigido neste repositório."
    uv = shutil.which("uv")
    if not uv:
        return False, "uv não encontrado."
    result = subprocess.run(
        [uv, "tool", "list"],
        check=False,
        capture_output=True,
        text=True,
    )
    package, version = expected.split("==", 1)
    matched = f"{package} v{version}" in result.stdout
    return matched, (
        f"ok: {expected}" if matched else f"ausente ou divergente: {expected}"
    )


def verify_local_files(lock: dict) -> bool:
    success = True
    for skill in lock["skills"].values():
        for relative_path, source in skill.get("local_files", {}).items():
            valid, message = verify_file(
                relative_path,
                source["git_blob_sha1"],
            )
            print(message)
            success = success and valid
    matched, message = graphify_tool_matches(lock)
    print(message)
    return success and matched


def download_local_files(lock: dict) -> None:
    for name, skill in lock["skills"].items():
        for relative_path, source in skill.get("local_files", {}).items():
            request = urllib.request.Request(
                source["url"],
                headers={"User-Agent": "MedSync-Agent-Skills-Setup/1.0"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
            actual = git_blob_sha1(data)
            expected = source["git_blob_sha1"]
            if actual != expected:
                raise SystemExit(
                    f"Checksum inválido para {name}: {actual} != {expected}"
                )
            target = ROOT / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            print(f"instalado: {relative_path}")


def install_local_tools(lock: dict) -> None:
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("Instale o uv antes de configurar o Graphify.")
    for name, skill in lock["skills"].items():
        package = skill.get("local_tool")
        if not package:
            continue
        print(f"instalando {name}: {package}")
        subprocess.run(
            [uv, "tool", "install", "--force", package],
            check=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gerencia as skills locais fixadas do MedSync.",
    )
    parser.add_argument(
        "command",
        choices=("check", "check-local", "install-local"),
        nargs="?",
        default="check",
    )
    args = parser.parse_args()
    lock = load_lock()

    shared_ok = verify_repository_files(lock)
    if args.command == "check":
        return 0 if shared_ok else 1
    if args.command == "install-local":
        install_local_tools(lock)
        download_local_files(lock)
    local_ok = verify_local_files(lock)
    return 0 if shared_ok and local_ok else 1


if __name__ == "__main__":
    sys.exit(main())
