# AI Workshop App

Two small LLM apps built with **LangChain + OpenAI**, in one repo:

| Package | What it does |
|---|---|
| `diet_assistant/` | Streaming Diet Planning chatbot (Gradio UI) with conversations saved in SQLite |
| `feedback_analyzer/` | Turns free-text feedback about a place into validated structured JSON (Pydantic + `with_structured_output`). `analyzer.py` is the full schema; `streamlined.py` is the compact (<=10 fields) schema |
| `validation_demo/` | Small Pydantic demo: a strict `Review` model and the errors it reports for a bad payload |

Design docs (`docs/`):
- [`design-full.md`](docs/design-full.md) - full schema, implemented by `feedback_analyzer/analyzer.py`
- [`design-streamlined.md`](docs/design-streamlined.md) - compact schema, implemented by `feedback_analyzer/streamlined.py`
- [`design-v1-city-area.md`](docs/design-v1-city-area.md) - earlier city/area design, kept for reference only (not implemented)
The chatbot's behaviour is controlled entirely by [`diet_assistant/prompt.md`](diet_assistant/prompt.md).

## Run it in VS Code

1. `File > Open Folder…` and pick this folder (install the recommended extensions when prompted).
2. Create the environment (Terminal > New Terminal):
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```
3. Select the interpreter: `Ctrl/Cmd+Shift+P` > **Python: Select Interpreter** > `.venv`.
4. Add your key: `cp .env.example .env` and set `OPENAI_API_KEY`.
5. Press **F5** and choose **Diet Chatbot (Gradio)** or **Feedback Analyzer (examples)**
   (or run `python -m diet_assistant`, `python -m feedback_analyzer`, `python -m feedback_analyzer.streamlined`, `python -m validation_demo`).
   The chatbot opens at http://127.0.0.1:7860.
6. Tests: `pytest` (or the Testing panel). They use a fake model, so no API key or network is needed.

## Publish to GitHub

```bash
git init -b main
git add .
git commit -m "Initial commit"
# create an empty repo on github.com (no README), then:
git remote add origin https://github.com/<you>/ai-workshop-app.git
git push -u origin main
```
With the GitHub CLI instead: `gh repo create ai-workshop-app --public --source . --push`.

`.env` and `*.db` are git-ignored, so your key and chat history are never pushed.
`.github/workflows/ci.yml` runs the tests on every push and pull request.

## Deploying the chatbot so others can use it

GitHub itself only hosts the code (GitHub Pages can't run Python). Easiest options:

- **Hugging Face Spaces** (free, Gradio-native): create a Gradio Space, push this repo, add `OPENAI_API_KEY`
  as a Space secret, and add an `app.py` containing `from diet_assistant.__main__ import main; main()`.
- **Render / Railway / Fly.io**: connect the GitHub repo, start command `python -m diet_assistant`,
  set `OPENAI_API_KEY`. For these, change `launch()` to `launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", 7860)))`.

Note: SQLite on free hosts is wiped on restart; use a persistent disk or a hosted database for real use.

## Layout

```
diet_assistant/     config.py  logic.py  ui.py  prompt.md  __main__.py
feedback_analyzer/  analyzer.py  streamlined.py  __main__.py
validation_demo/    review.py  __main__.py
tests/              offline tests with fake models
.vscode/            settings, F5 launch configs, extension recommendations
.github/workflows/  CI
```
