# Contributing to ArenaMaxx

Thank you for your interest in contributing! This document outlines the development guidelines and workflow.

## 🌿 Branch Strategy

- `main` — Production-ready code (deployed to Cloud Run)
- `dev` — Development branch for feature integration
- `feature/<name>` — Individual feature branches

## 🔧 Development Setup

1. Fork the repository.
2. Clone your fork: `git clone https://github.com/<your-username>/ArenaMaxx.git`
3. Set up environment variables: `cp .env.example .env` and fill in your keys.
4. Install dependencies (see README.md for commands).

## ✅ Coding Standards

### Python (Backend)
- Follow **PEP 8** style guide.
- All functions must have **docstrings** and **type hints**.
- Maximum line length: **100 characters**.
- Use `logging` module — never `print()` in production code.

### JavaScript / React (Frontend)
- Use **ES2022+** syntax.
- All components must have **JSDoc** comments.
- Use `PropTypes` for component prop validation.
- Keep components focused — extract sub-components if a file exceeds 200 lines.

## 🧪 Testing Requirements

- All new **API endpoints** must have corresponding test cases in `test_app.py`.
- Tests must cover: happy path, missing fields, invalid input, and edge cases.
- Run tests before submitting a PR: `cd backend && pytest test_app.py -v`

## 🔐 Security Guidelines

- **Never** commit API keys or credentials — use `.env` and `.env.example`.
- All POST endpoints must validate input and reject injection payloads.
- Add rate limiting to any new endpoint using the `@limiter.limit()` decorator.

## 📝 Pull Request Process

1. Ensure all tests pass.
2. Update `README.md` if you've changed any API endpoints or setup steps.
3. Write a descriptive PR title and description.
4. Request review from a maintainer.
