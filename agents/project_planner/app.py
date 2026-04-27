import streamlit as st
from planner import generate_plan, format_plan_as_markdown

st.set_page_config(page_title="AI Project Planner", page_icon="🗂️", layout="wide")

st.title("🗂️ AI Project Planner")
st.caption("Powered by Claude — turn any goal into a phased action plan")

with st.sidebar:
    st.header("Settings")
    num_phases = st.slider("Number of phases", min_value=2, max_value=6, value=4)
    st.divider()
    st.markdown("**Claude API Key** *(optional)*")
    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Leave blank to use your active Claude Code session (no key needed). Enter a key to use the Anthropic API directly.",
        label_visibility="collapsed",
    )
    if api_key_input:
        st.caption("Using provided API key.")
    else:
        st.caption("Using Claude Code session (no key required).")
    st.divider()
    st.markdown("**How to use:**")
    st.markdown("1. Enter your project goal\n2. Add optional context\n3. Click Generate")

st.subheader("Your Project Goal")
goal = st.text_area(
    "What do you want to build or achieve?",
    placeholder="e.g. Build a SaaS product for freelance invoicing",
    height=80,
)

context = st.text_area(
    "Additional context (optional)",
    placeholder="e.g. Solo developer, 3 month timeline, using Python and React",
    height=60,
)

if st.button("Generate Plan", type="primary", disabled=not goal.strip()):
    with st.spinner("Generating your project plan..."):
        try:
            plan = generate_plan(goal.strip(), context.strip(), num_phases, api_key=api_key_input)

            col1, col2, col3 = st.columns(3)
            col1.metric("Project", plan["project_title"])
            col2.metric("Duration", plan["estimated_duration"])
            col3.metric("Phases", len(plan["phases"]))

            st.divider()

            for phase in plan["phases"]:
                with st.expander(
                    f"Phase {phase['phase_number']}: {phase['phase_name']} — {phase['duration']}",
                    expanded=True,
                ):
                    st.markdown(f"**Objective:** {phase['objective']}")
                    for task in phase["tasks"]:
                        priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                            task["priority"], "⚪"
                        )
                        st.markdown(f"{priority_color} **{task['task']}**")
                        for sub in task.get("subtasks", []):
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• {sub}")

            st.divider()
            col_risk, col_metrics = st.columns(2)

            with col_risk:
                if plan.get("risks"):
                    st.subheader("⚠️ Risks")
                    for risk in plan["risks"]:
                        st.markdown(f"- {risk}")

            with col_metrics:
                if plan.get("success_metrics"):
                    st.subheader("✅ Success Metrics")
                    for metric in plan["success_metrics"]:
                        st.markdown(f"- {metric}")

            st.divider()
            st.subheader("Export as Markdown")
            st.code(format_plan_as_markdown(plan), language="markdown")

        except Exception as e:
            st.error(f"Error generating plan: {e}")
            st.info(
                "No API key? Make sure you're running inside a Claude Code session. "
                "Alternatively, enter your Anthropic API key in the sidebar."
            )
