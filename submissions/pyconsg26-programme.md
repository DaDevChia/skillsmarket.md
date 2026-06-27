# What we learned from PyConSG26 and applied

PyConSG26 schedule:

https://pycon.sg/schedule.html

PyConSG26 homepage:

https://pycon.sg

The most useful parts for this project were the practical Python tooling sessions and the Hermes Agent lunch workshop.

## Adopting `uv` and `pyproject.toml` for mono-repo work

Talk:

```text
Adopting uv and pyproject.toml for mono-repo: Challenges and Approach
```

Speaker:

```text
Mou Yuan Yap, Machine Learning Engineer, Grab
```

Resource:

https://drive.google.com/file/d/1r5-vsbnFms8ESlKHcPp5BPZBHbytV-sC/view?usp=sharing

This talk was very useful because it was about a real Python problem: managing dependencies in a large mono-repo without everything becoming hidden inside Docker images.

We used the same idea in a smaller hackathon version. SkillsMarket keeps the Python backend, frontend, tests, data notes, and submission docs in one repo. For the Python side, we used:

- `pyproject.toml` for project dependencies and test config.
- `uv.lock` for reproducible installs.
- `uv sync` and `uv run` so the backend can be set up and tested locally.

Relevant files:

- https://github.com/DaDevChia/skillsmarket.md/blob/main/pyproject.toml
- https://github.com/DaDevChia/skillsmarket.md/blob/main/uv.lock

This made the project easier to rebuild and explain. It also kept the Python part of the stack visible instead of burying it under random setup steps.

## Hermes Agent lunchtime workshop

Workshop link:

http://pycon.sg/agent/

The Hermes Agent lunch workshop shaped how the project was built.

Instead of only chatting with an AI, I used Hermes Agent as the main way to operate my computer from Telegram. Hermes coordinated the repo, terminal, files, GitHub, deployment notes, and coding agents. Claude Code was used as the main implementation agent in tmux, with Codex prepared as another agent lane.

That workflow is documented here:

https://github.com/DaDevChia/skillsmarket.md/tree/main/submissions/human-computer-interaction

This changed how I thought about AI tooling. The useful part was not asking an AI for one-off answers. It was learning how to give direction, check the work, and keep the build moving through agents.

## How this changed the project

These sessions made the project more practical.

We paid attention to:

- Reproducible Python setup.
- Clear project structure.
- A repo that can be rebuilt by someone else.
- Agent-driven development with logs and human judgement.
- Separating real data, ingestion tools, and seeded demo data.

The main takeaway was simple: good tools should make the work easier to reproduce, not just faster to generate.
