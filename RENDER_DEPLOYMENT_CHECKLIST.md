# RABBIT Assistant - Render Deployment Checklist

## Render service settings

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --chdir 18_flask_chat_ui app:app --bind 0.0.0.0:$PORT`
- Health check path: `/health`

The included `render.yaml` already defines the build and start commands for a Render Blueprint deployment.

## Required environment variables

Set these in Render Dashboard > Environment. Do not upload the local `.env` file.

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_API_KEY`
- `AZURE_SEARCH_API_VERSION`
- `AZURE_SEARCH_INDEX_NAME`
- `FLASK_MODE_PASSWORD`

## Do not deploy

- `.env`
- `18_flask_chat_ui/.venv/`
- `__pycache__/` folders
- `18_flask_chat_ui/logs/`

These are covered by `.gitignore` for Git-based deployment.

## Quick local smoke test

```bash
cd /Users/jhonny001/Desktop/RABBIT_Assistant
python3 -m venv 18_flask_chat_ui/.venv
18_flask_chat_ui/.venv/bin/pip install -r requirements.txt
18_flask_chat_ui/.venv/bin/python 18_flask_chat_ui/app.py
```

Then open `http://127.0.0.1:8091/health`.
