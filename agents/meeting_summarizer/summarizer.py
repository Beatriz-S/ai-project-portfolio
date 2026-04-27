import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert meeting analyst and executive assistant.

Given a meeting transcript, extract and structure the key information.
You MUST respond with valid JSON only — no markdown, no extra text.

The JSON structure must be:
{
  "meeting_title": "string (infer from context)",
  "date": "string (if mentioned, else 'Not specified')",
  "participants": ["string"],
  "duration_estimate": "string (e.g. '45 minutes', infer from transcript length/content)",
  "summary": "string (3-5 sentences capturing the essence of the meeting)",
  "key_decisions": [
    {
      "decision": "string",
      "context": "string (why this decision was made)"
    }
  ],
  "action_items": [
    {
      "task": "string",
      "owner": "string (person responsible, or 'Team' if unclear)",
      "deadline": "string (if mentioned, else 'Not specified')",
      "priority": "high | medium | low"
    }
  ],
  "open_questions": ["string (unresolved questions that need follow-up)"],
  "next_meeting": "string (if mentioned, else 'Not scheduled')",
  "sentiment": "positive | neutral | mixed | tense"
}
"""


def _call_claude(user_message: str) -> str:
    """Route to API key mode or Claude Code SDK mode automatically."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        return _call_via_api(user_message, api_key)
    return _call_via_claude_code(user_message)


def _call_via_api(user_message: str, api_key: str) -> str:
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()


def _call_via_claude_code(user_message: str) -> str:
    """Use Claude Code SDK — no API key required, uses your active Claude Code session."""
    async def _async():
        from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock
        result = ""
        async for message in query(
            prompt=user_message,
            options=ClaudeCodeOptions(max_turns=1, system_prompt=SYSTEM_PROMPT),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        result += block.text
        return result.strip()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async())
    finally:
        loop.close()
        asyncio.set_event_loop(None)


def _parse_json(raw: str) -> dict:
    """Strip markdown fences if present, then parse JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    return json.loads(raw.strip())


def summarize_meeting(transcript: str) -> dict:
    """
    Summarize a meeting transcript using Claude.

    Args:
        transcript: Raw meeting transcript text

    Returns:
        Parsed summary as a Python dict
    """
    user_message = f"Please analyze this meeting transcript:\n\n{transcript}"
    raw = _call_claude(user_message)
    return _parse_json(raw)


def format_summary_as_markdown(summary: dict) -> str:
    """Convert a summary dict to a readable markdown string."""
    lines = []

    lines.append(f"# Meeting Summary: {summary['meeting_title']}")
    lines.append(f"\n**Date:** {summary['date']}  ")
    lines.append(f"**Participants:** {', '.join(summary['participants'])}  ")
    lines.append(f"**Duration:** {summary['duration_estimate']}  ")
    sentiment_emoji = {
        "positive": "😊", "neutral": "😐", "mixed": "🤔", "tense": "😬"
    }.get(summary.get("sentiment", "neutral"), "😐")
    lines.append(f"**Sentiment:** {sentiment_emoji} {summary.get('sentiment', 'neutral').capitalize()}")

    lines.append(f"\n---\n## Summary\n{summary['summary']}")

    if summary.get("key_decisions"):
        lines.append("\n---\n## Key Decisions")
        for item in summary["key_decisions"]:
            lines.append(f"\n- **{item['decision']}**")
            lines.append(f"  _{item['context']}_")

    if summary.get("action_items"):
        lines.append("\n---\n## Action Items")
        for item in summary["action_items"]:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item["priority"], "⚪")
            lines.append(
                f"\n- {priority_emoji} **{item['task']}**  \n"
                f"  Owner: `{item['owner']}` | Due: `{item['deadline']}`"
            )

    if summary.get("open_questions"):
        lines.append("\n---\n## Open Questions")
        for q in summary["open_questions"]:
            lines.append(f"- ❓ {q}")

    lines.append(f"\n---\n**Next Meeting:** {summary.get('next_meeting', 'Not scheduled')}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Paste your meeting transcript below.")
    print("When done, enter a line with just 'END' and press Enter.\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    transcript = "\n".join(lines)
    if not transcript.strip():
        print("No transcript provided.")
    else:
        print("\nAnalyzing transcript...\n")
        summary = summarize_meeting(transcript)
        print(format_summary_as_markdown(summary))
