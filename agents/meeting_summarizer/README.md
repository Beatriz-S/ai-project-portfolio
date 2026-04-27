# Meeting Summarizer

Paste any meeting transcript and instantly get a structured summary with key decisions, action items with owners and deadlines, open questions, and sentiment analysis — powered by Claude.

## Demo

```
Input: Raw Zoom/Teams/Meet transcript or manual notes

Output:
## Summary
Sprint planning meeting focused on shipping the user dashboard...

## Key Decisions
- Analytics tab pushed to next sprint (too risky to rush)

## Action Items
🔴 Fix auth token race condition — Owner: James | Due: Thursday
🟡 Finish notification panel — Owner: Priya | Due: End of sprint
🟢 Review onboarding designs — Owner: Priya | Due: Tuesday

## Open Questions
- Will auth fix require infrastructure changes?
```

## Run It

**CLI:**
```bash
cd agents/meeting_summarizer
pip install -r requirements.txt
python summarizer.py
# Paste transcript, type END when done
```

**Streamlit UI:**
```bash
streamlit run app.py
```

A sample transcript is included — click **Load Sample Transcript** in the sidebar to try it instantly.

## Features

- Extracts participants, decisions, action items, and open questions
- Assigns owners and deadlines to each action item
- Priority scoring (high / medium / low) per action item
- Meeting sentiment detection
- One-click Markdown export

## Files

| File | Description |
|------|-------------|
| `summarizer.py` | Core Claude agent logic |
| `app.py` | Streamlit UI |
| `sample_transcript.txt` | Example transcript to test with |
| `requirements.txt` | Python dependencies |
