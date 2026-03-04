# Project Planner Agent

Give it any project goal and get a structured, phased plan with tasks, subtasks, priorities, risks, and success metrics — powered by Claude.

## Demo

```
Input:  "Build a SaaS invoicing app for freelancers"

Output:
Phase 1: Research & Planning (Week 1)
  🔴 Define target users
     - Interview 5 freelancers
     - Document pain points
  🟡 Competitor analysis
     - Review FreshBooks, Wave, Bonsai
     ...
```

## Run It

**CLI:**
```bash
cd agents/project_planner
pip install -r requirements.txt
cp ../../.env.example ../../.env   # then add your ANTHROPIC_API_KEY
python planner.py
```

**Streamlit UI:**
```bash
streamlit run app.py
```

## How It Works

1. User inputs a goal + optional context
2. Prompt is sent to `claude-opus-4-6` with a strict JSON schema
3. Response is parsed and rendered as an interactive plan
4. User can export the plan as Markdown

## Files

| File | Description |
|------|-------------|
| `planner.py` | Core agent logic — Claude API call + JSON parsing |
| `app.py` | Streamlit UI |
| `requirements.txt` | Python dependencies |
