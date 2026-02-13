## Multi-agent workflow (Cursor)

- Use multiple agent chats for parallel work streams (e.g. “deploy”, “backend”, “docs”).
- There is **no repo-side “multi-agent config”** that automatically orchestrates agents; coordination is done in the Cursor UI.
- Put shared expectations here and in `.cursor/rules/` so every agent follows the same standards.

## Model guidance

- A strong model (like the one you’re using: “Opus 4.6”) is appropriate for multi-file refactors and deployment debugging.
- For quick grep/formatting/simple edits, a faster/cheaper model is fine.
- Ensure each agent is set to the intended model in the UI (agents can differ).

