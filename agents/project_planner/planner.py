import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

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


def generate_plan(goal: str, context: str = "", num_phases: int = 4) -> dict:
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

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    return json.loads(raw)


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
    plan = generate_plan(goal, context)
    print(format_plan_as_markdown(plan))
