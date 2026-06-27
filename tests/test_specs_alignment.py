from pathlib import Path


def test_specs_use_goal_prompt_not_go():
    text = Path("specs.md").read_text()
    assert "/goal" in text
    assert "/go\n" not in text
