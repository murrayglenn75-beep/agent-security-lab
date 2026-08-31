from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = [
    ROOT / "src",
    ROOT / "scenarios",
    ROOT / "docs",
    ROOT / "tests",
    ROOT / "README.md",
    ROOT / "SECURITY.md",
    ROOT / ".env.example",
]
TEXT_SUFFIXES = {".py", ".yaml", ".yml", ".md", ".toml", ".txt", ".example"}

# Construct high-risk markers so this scanner does not match its own source text.
MARKERS = [
    "BEGIN " + "PRIVATE KEY",
    "sk-" + "ant-",
    "sk-" + "proj-",
    "service" + "_role_key",
    "AWS_" + "SECRET_ACCESS_KEY",
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for item in SCAN_ROOTS:
        if not item.exists():
            continue
        if item.is_file():
            files.append(item)
            continue
        files.extend(
            path
            for path in item.rglob("*")
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
        )
    return files


def main() -> int:
    findings: list[str] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in MARKERS:
            if marker in text:
                findings.append(f"{path.relative_to(ROOT)}: contains {marker!r}")

    if findings:
        print("Public release scan FAILED")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"Public release scan PASS ({len(iter_files())} files scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
