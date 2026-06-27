# How AI tools were used creatively, effectively and responsibly

We used AI as a build partner, but not as the final judge.

## The human decided

- What problem was worth solving.
- What the app should feel like.
- Whether the outputs were clear or confusing.
- Whether the data explanations were honest.
- What should be included in the final demo.

## AI was used for

- Turning rough ideas into specs.
- Building parts of the frontend and backend.
- Writing tests and documentation.
- Summarising design discussions.
- Coordinating coding agents through Hermes Agent, Claude Code, and Codex.

## AI inside the product (at runtime)

The shipped app uses an LLM (via OpenRouter) in three tightly-bounded, grounded ways:

- **Resume analyst readout** — narrates a candidate summary, strongest/high-upside skills, role fit, and
  next moves. Skills are intersected with the live market vocabulary and every quote is verified verbatim
  against the resume, so it cannot invent facts.
- **Add-skill live research** — when you type a skill that isn't on the board, the agent estimates its
  sector, scarcity, and salary, labelled clearly as *AI-researched estimate — not market data*.
- **Plain-English explanations** of computed skill quotes.

Every one of these **fails closed**: no key, a network error, or malformed output falls back to the
deterministic, data-driven result. The LLM narrates and researches; it never sets the index.

## Responsible use

We tried to use AI responsibly by being clear about what is real and what is demo data. The app does not ask an LLM to invent skill prices. The skill index is based on job and course data first. AI is used to explain the results and improve the workflow.

We also kept private information out of the public logs. Sensitive details like credentials, auth links, private account information, and raw resumes were removed from the HCI folder.

Related logs:

https://github.com/DaDevChia/skillsmarket.md/tree/main/submissions/human-computer-interaction
