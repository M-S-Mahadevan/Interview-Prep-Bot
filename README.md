# Interview Prep Chatbot (OpenAI + Streamlit)

Domain-specific chatbot for interview preparation: mock interviews, rubric feedback (STAR/CAR), curated question sets, and a built-in temperature/top‑p comparison demo for your assessment report.

## Features
- Mock interview (one question at a time) + rubric feedback + follow-up questions
- Answer improvement (STAR/CAR) with scoring rubric
- Question generator (10 questions with difficulty tags)
- Temperature/top‑p demo tab (same prompt, two configs side-by-side)

## Tech stack
- Python
- Streamlit UI
- OpenAI API via the `openai` Python SDK

## Setup
1) Create a virtual environment (optional but recommended).

2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Set your API key (choose one):
- Create a `.env` file (copy from `.env.example`) and add:
  - `OPENAI_API_KEY=...`
- OR set an environment variable `OPENAI_API_KEY`.

## Run

```bash
python -m streamlit run app.py
```

## Assessment requirement mapping
- **Clear domain definition**: interview preparation (HR/behavioral/technical).
- **Generative AI API**: OpenAI Chat Completions.
- **Domain-constrained responses**: strict system prompt in `prompts.py`.
- **Working prototype**: Streamlit app with multiple modes.
- **Temperature + top‑p awareness**: “Temp / Top‑p Demo” tab produces two outputs for the same prompt using different settings (screenshot this for your report).

## Suggested report screenshots
- Mock Interview tab: question → your answer → rubric feedback
- Answer Improvement tab: pasted answer → improved STAR answer
- Temp / Top‑p Demo tab: Output A vs Output B with different controls
