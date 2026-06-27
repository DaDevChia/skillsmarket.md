from pathlib import Path


def test_no_real_secrets_in_tracked_docs_or_source():
    forbidden = ["apify" + "_api_", "sk-or" + "-v1-"]
    checked_suffixes = {".py", ".md", ".ts", ".tsx", ".json", ".toml", ".yml", ".yaml"}
    for path in Path(".").rglob("*"):
        if ".venv" in path.parts or "node_modules" in path.parts or path.name == ".env" or path.is_dir():
            continue
        if path.suffix not in checked_suffixes:
            continue
        text = path.read_text(errors="ignore")
        for secret in forbidden:
            assert secret not in text, f"secret-like token leaked in {path}"
