# Architecture Notes: 2D Python Game Coding Environment

## Pipeline

```text
Code Editor -> Sandbox Executor -> Game Engine State Update -> Rendered Output + Terminal/Debugger
```

## Components

- In-browser code editor
- Restricted/sandboxed code execution
- Terminal output panel
- Debugger support
- Live game state visualization
- Django backend for session management

## Design Notes

- Keep provider/model choices swappable behind interfaces (see `multi-llm-router`
  and similar projects in this portfolio for the general pattern).
- Prefer configuration-driven pipelines (YAML/JSON in `configs/`) over hardcoded
  parameters so experiments are reproducible.
