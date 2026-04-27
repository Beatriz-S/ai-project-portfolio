import os
import sys
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert project manager and strategic planner.

When given a project goal, you break it down into a clear, actionable plan.
You MUST respond with valid JSON only — no markdown, no extra text.

The JSON structure must be:
{
  "project_title": "string",
  "summary": "string (2-3 sentences describing the project)",
  "estimated_duration": "string (e.g. '6 weeks')",
  "phases": [
    {
      "phase_number": 1,
      "phase_name": "string",
      "duration": "string (e.g. 'Week 1-2')",
      "objective": "string",
      "tasks": [
        {
          "task": "string",
          "subtasks": ["string", "string"],
          "priority": "high | medium | low"
        }
      ]
    }
  ],
  "risks": ["string"],
  "success_metrics": ["string"]
}
"""


def _call_claude(user_message: str, api_key: str = "") -> str:
    """Route to API key mode or Claude Code SDK mode automatically."""
    key = api_key.strip() or os.getenv("ANTHROPIC_API_KEY", "")
    if key:
        return _call_via_api(user_message, key)
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
    if not response.content:
        raise ValueError("API returned no content. Check model name and API status.")
    first_block = response.content[0]
    text = getattr(first_block, "text", None)
    if not text or not text.strip():
        raise ValueError("API returned empty text. Check model name (e.g. claude-3-5-sonnet-20241022).")
    return text.strip()


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
        out = loop.run_until_complete(_async())
        if not out:
            raise ValueError(
                "Claude Code SDK returned no text. "
                "Set ANTHROPIC_API_KEY to use the API instead, or run from a Claude Code session."
            )
        return out
    finally:
        loop.close()
        asyncio.set_event_loop(None)


def _parse_json(raw: str) -> dict:
    """Strip markdown fences if present, then parse JSON."""
    raw = (raw or "").strip()
    if not raw:
        raise ValueError(
            "Received empty response from the model. "
            "Check ANTHROPIC_API_KEY and that the model name is valid."
        )
    if raw.startswith("```"):
        lines = raw.splitlines()
        # Remove first line (``` or ```json) and optional closing ```
        start = 1
        end = len(lines)
        if end > 1 and lines[-1].strip() == "```":
            end -= 1
        raw = "\n".join(lines[start:end])
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model response was not valid JSON. {e}. "
            f"First 400 chars: {raw[:400]!r}"
        ) from e


def generate_plan(goal: str, context: str = "", num_phases: int = 4, api_key: str = "") -> dict:
    """
    Generate a structured project plan for a given goal using Claude.

    Args:
        goal: The project goal or objective
        context: Optional additional context (team size, constraints, etc.)
        num_phases: Suggested number of phases (default 4)

    Returns:
        Parsed plan as a Python dict
    """
    user_message = f"Project Goal: {goal}"
    if context:
        user_message += f"\n\nAdditional Context: {context}"
    user_message += f"\n\nCreate a plan with approximately {num_phases} phases."

    raw = _call_claude(user_message, api_key=api_key)
    return _parse_json(raw)


def format_plan_as_markdown(plan: dict) -> str:
    """Convert a plan dict to a readable markdown string."""
    lines = []
    lines.append(f"# {plan['project_title']}")
    lines.append(f"\n{plan['summary']}")
    lines.append(f"\n**Estimated Duration:** {plan['estimated_duration']}")

    lines.append("\n---\n## Phases\n")
    for phase in plan["phases"]:
        lines.append(f"### Phase {phase['phase_number']}: {phase['phase_name']} ({phase['duration']})")
        lines.append(f"**Objective:** {phase['objective']}\n")
        for task in phase["tasks"]:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "⚪")
            lines.append(f"- {priority_emoji} **{task['task']}**")
            for sub in task.get("subtasks", []):
                lines.append(f"  - {sub}")
        lines.append("")

    if plan.get("risks"):
        lines.append("---\n## Risks")
        for risk in plan["risks"]:
            lines.append(f"- ⚠️ {risk}")

    if plan.get("success_metrics"):
        lines.append("\n## Success Metrics")
        for metric in plan["success_metrics"]:
            lines.append(f"- ✅ {metric}")

    return "\n".join(lines)


if __name__ == "__main__":
    goal = input("Enter your project goal: ").strip()
    context = input("Any additional context (or press Enter to skip): ").strip()

    print("\nGenerating your project plan...\n")
    try:
        plan = generate_plan(goal, context)
        print(format_plan_as_markdown(plan))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
