import importlib
from pathlib import Path


def test_backend_package_is_skillsmarket():
    assert importlib.import_module("skillsmarket.api")


def test_no_stale_product_or_package_names_in_source():
    checked = [
        *Path("backend").rglob("*.py"),
        *Path("tests").rglob("*.py"),
        *Path("src").rglob("*.tsx"),
        *Path("src").rglob("*.ts"),
        Path("index.html"),
        Path("README.md"),
        Path("skillsmarket.md"),
        Path("specs.md"),
    ]
    forbidden_terms = ["Skill" + "Ex", "skill" + "ex"]
    for path in checked:
        if path.exists():
            text = path.read_text(errors="ignore")
            for term in forbidden_terms:
                assert term not in text, f"{term} remains in {path}"
