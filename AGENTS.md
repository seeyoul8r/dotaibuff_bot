# Project Instructions

## 1. Initial Protocol (First Steps)
Before proposing or writing any code, execute these steps in order:
1. **Analyze Architecture**: Read and analyze `docs/README.md` to understand current project architecture, data flow, and relevant implementation notes.
2. **Server & MCP Rules**: This project is deployed on the `http://193.42.60.48/mcp` server. MCP server access is **read-only by default**. Do NOT modify files or data on MCP servers unless explicitly instructed (with specific server, files/data, and change details). Keep default workflows local to maintain consistency via GitHub.
3. **Propose First (Strict Rule)**: Describe your solution in plain text / bullet points first. **Do NOT write or apply any code until I explicitly confirm the plain-text solution.**

## 2. Code Modifications & Constraints
Apply these rules strictly when writing or modifying code:
- **Minimal Changes & No Extras**: Be concise. No extra methods, attributes, or checks unless explicitly asked.
- **Style & Consistency**: Match existing code style and logic exactly. Use current code as the primary reference.
- **Variable Protection**: Never rename existing variables, methods, or attributes unless explicitly asked.
- **No Fallbacks**: Avoid fallbacks unless explicitly requested.
- **Documentation in Code**: Add a short docstring to every new method. Comment every significant piece of new logic.

## 3. Communication, Style & Visual Artifacts
- **ASD-STE100 Writing Style**: Write explanations in English or Russian with ~80% strictness of ASD-STE100 (Simplified Technical English). Use short, clear, active-voice sentences (under 20 words). Eliminate fluff and polite intros/outros.
- **Explanations via Bullet Points**: Always explain code changes and technical concepts using concise bullet points.
- **Diagrams**: For flows, component interactions, or pipelines, provide a clean **Mermaid.js** diagram alongside the explanation so it renders directly in the IDE preview.
- **Interactive HTML Artifacts**: For multi-variable formulas, complex data structures, or visual algorithms, offer/generate a single standalone HTML file (with Tailwind CDN / JS Canvas) as an interactive GUI explanation.
- **Commit Message**: Always end your response with a single commit string formatted as: `TYPE (fix/feat/chore): SHORT DESC IN ENGLISH`.

## 4. Documentation & Maintenance Rules
When completing a task, update documentation based on these criteria:
- **User-Facing Behavior (Manuals)**: Update both `RU` and `EN` manuals in `docs/` ONLY when a change affects user-facing behavior, settings, buttons, commands, notifications, trading flow, or anything the user must know to use the bot. Do NOT document internal logging, refactoring, or dev-only details. Provide examples or references when useful.
- **Internal Architecture (`docs/README.md`)**: Update `docs/README.md` ONLY when a change affects internal architecture, important technical logic, service responsibilities, data flow, storage format, Redis/DB keys, or anything a developer or future model must know to work on the project.