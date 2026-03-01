# Security Baseline

## Purpose

Define baseline secret-handling behavior for generated repositories from this template.

## Env File Convention

- Commit `.env.example` files with placeholder or empty values only.
- Do not commit real `.env` files or real credentials.
- Keep variable names in `.env.example` aligned with actual runtime requirements.

## Secret Handling Rules

- Never commit private keys, API keys, tokens, deploy keys, passwords, or certificate files.
- Treat all client-exposed env keys (`VITE_*`, `NEXT_PUBLIC_*`) as public configuration values.
- Keep server secrets in local `.env` files or secret managers outside source control.

## Generated Scaffold Requirements

- Root `.gitignore` must include baseline env/secret protections:
  - `.env`
  - `.env.*`
  - `!.env.example`
  - common key artifact globs (`*.pem`, `*.key`)
- Generated scaffolds should copy the template root `.gitignore` as the source-of-truth baseline rather than synthesizing a separate variant.
- Each selected app target must include a target-local `.env.example`.
- Auth variants (`web+backend+clerk` and `web+backend+better-auth`) must scaffold variant-appropriate placeholder keys.

## CI Status

- Lightweight secret scanning in CI is planned but not yet implemented.
