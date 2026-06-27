from pathlib import Path


def test_frontend_shell_files_exist():
    assert Path("package.json").exists()
    assert Path("src/App.tsx").exists()
    assert Path("tests/e2e/skillsmarket.spec.ts").exists()
