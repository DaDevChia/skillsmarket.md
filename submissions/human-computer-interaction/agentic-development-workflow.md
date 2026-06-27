# Agentic Development Workflow

> Sanitized record of how SkillsMarket was built as an agent-orchestrated project. This document describes the human-computer interaction pattern, not private credentials or raw infrastructure secrets.

## Operating model

SkillsMarket was developed with **Hermes Agent as the primary computer interface**. The user interacted mainly through Telegram, using Hermes as the control plane for the machine, repository, shell, browser checks, session recall, and external coding agents.

The workflow was intentionally not a single “chatbot writes code” loop. It was closer to a small agent desk:

| Role | Tool / surface | Purpose |
|---|---|---|
| Human product lead | Telegram voice/text | Defines product, UX taste, priorities, corrections, and acceptance criteria |
| Orchestrator | Hermes Agent | Translates requirements into plans, starts/monitors agents, edits docs, verifies artifacts, commits/pushes |
| Main implementer | Claude Code in tmux | Long-running codebase implementation with `/goal` prompts |
| Reviewer / alternate agent | Codex CLI, when authenticated | Independent checks, reviews, or bounded tasks |
| Infrastructure runner | Hermes terminal tools | Installs packages, manages services, starts tunnels, inspects processes |
| Manual override | SSH/Termius-style terminal access | Lets the user attach directly when needed, while Hermes continues as the main driver |

## Hermes as the main driver

Hermes was used as the user’s remote hands on the computer:

- Receiving product direction over Telegram.
- Searching previous sessions for project context.
- Reading and writing project files.
- Starting and inspecting tmux panes.
- Running backend/frontend tests and health checks.
- Creating GitHub repository documentation.
- Setting up Cloudflare Tunnel notes and deployment commands.
- Coordinating Claude Code rather than doing every implementation step directly.

The user’s pattern was to specify the desired outcome, then ask Hermes to coordinate the machine and coding agents. This kept the human in product/control mode while the agents handled implementation and verification. Sensible, really; the meat does strategy, the silicon does chores.

## Persistent coding-agent pattern

### Claude Code lane

Claude Code was treated as the primary implementation worker for SkillsMarket.

Pattern:

1. Hermes created or reused a tmux session in the project directory.
2. Hermes launched Claude Code interactively inside tmux.
3. The user asked Hermes to give Claude Code a self-contained implementation goal.
4. Hermes sent the goal into the tmux pane.
5. Hermes captured the pane to verify the task actually started.
6. Hermes periodically inspected output and relayed follow-up requirements.
7. Hermes independently verified results through git diffs, tests, browser checks, and commits.

The user explicitly preferred this coordination style:

```text
Hermes coordinates Claude Code as the main implementer; Hermes should not quietly replace Claude Code by doing all the implementation itself.
```

### `/goal` strategy

The project used Claude Code’s `/goal` prompt as a durable task framing mechanism.

Instead of sending vague chat instructions, Hermes condensed requirements into a clear `/goal` with:

- Product outcome.
- Files/routes/components to inspect.
- Non-goals and naming constraints.
- Verification commands.
- Expected final report.

This became important when the user asked for large changes such as:

- Rebuilding the app into a multi-page Bloomberg-terminal experience.
- Adding resume upload and AI-style evidence highlighting.
- Expanding the skills universe.
- Clarifying methodology and data provenance.
- Preserving the canonical `SkillsMarket` name.

### Codex lane

Codex was evaluated as a secondary autonomous coding lane.

The setup conversation established:

- Codex CLI was installed.
- The CLI initially appeared logged in, but a real execution probe showed stale authentication.
- The stale session was re-authenticated through device login.
- A practical execution probe returned the expected success marker afterward.
- Codex is not “always in tmux” by default; Hermes must explicitly start it in tmux or background mode for long-running tasks.

Codex is therefore documented as an available reviewer/alternate agent lane, especially useful for independent review or bounded tasks after Hermes has framed the work.

## SSH / Termius-style inspection

The user’s broader workflow includes direct terminal access through an SSH client such as Termius when manual inspection is needed.

Design implication:

- Hermes remains the main orchestration layer.
- tmux sessions are attachable by either Hermes or the user.
- Long-running agents are not hidden black boxes; their panes can be captured, inspected, or attached to directly.
- The repository and service state remain observable through normal Unix tooling.

This is why tmux is central: it gives both the AI orchestrator and the human operator a shared, persistent terminal surface.

## Tooling pattern used during SkillsMarket

| Area | Tools / commands | Interaction value |
|---|---|---|
| Agent orchestration | `tmux`, Claude Code, Codex CLI | Persistent coding sessions and inspectable progress |
| Project files | Hermes file tools | Safer reads/writes/patches with line-level inspection |
| Build/test | `npm`, `uvicorn`, backend tests, Playwright-style checks | Verifies the app instead of trusting agent claims |
| GitHub | `git`, `gh` | Private repository, commits, push, README/license/HCI records |
| Deployment | `cloudflared`, local ports, systemd/tunnel notes | Public access through Cloudflare Tunnel without router port forwarding |
| Session memory | Hermes session search | Recalls prior setup chats and decisions without asking the user to repeat them |
| Communication | Telegram gateway | Lets the user drive development conversationally from mobile |

## Product-specification flow

The project started from a written product concept, then moved through increasingly concrete interaction loops:

1. User provided the SkillsMarket concept/spec.
2. Hermes created project structure and delegated implementation to Claude Code.
3. User critiqued product naming, mobile layout, UX density, and source honesty.
4. Hermes converted critique into implementation goals and documentation.
5. Claude Code implemented major codebase changes in tmux.
6. Hermes verified, documented, committed, and pushed changes.
7. The HCI folder recorded the sanitized design evolution.

## What this says about the HCI design

The application is not just the result of prompting an AI once. It is the result of a layered human-agent workflow:

- The human supplied taste, constraints, and judgement.
- Hermes acted as the operational interface to the computer.
- Claude Code acted as a persistent implementer.
- Codex was prepared as a second opinion / task lane.
- tmux made agent work observable and interruptible.
- Git and HCI records made the process auditable.

That is the interaction story worth preserving for hackathon review: SkillsMarket was built with the same thesis it demonstrates, namely that useful AI is most valuable when it augments human decision-making with transparent evidence, clear provenance, and executable next steps.
