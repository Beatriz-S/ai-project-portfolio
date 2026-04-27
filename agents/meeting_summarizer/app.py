import streamlit as st
from summarizer import summarize_meeting, format_summary_as_markdown

st.set_page_config(page_title="Meeting Summarizer", page_icon="📝", layout="wide")

st.title("📝 Meeting Summarizer")
st.caption("Powered by Claude — paste any transcript and get a structured summary in seconds")

with st.sidebar:
    st.header("How to use")
    st.markdown(
        "1. Paste your meeting transcript\n"
        "2. Or load the sample transcript\n"
        "3. Click **Summarize**\n"
        "4. Export as Markdown"
    )
    st.divider()
    st.markdown("**Works with:**")
    st.markdown("- Zoom / Teams / Meet transcripts\n- Manual notes\n- Voice-to-text output\n- Any raw conversation text")

    if st.button("Load Sample Transcript"):
        try:
            with open("sample_transcript.txt", "r") as f:
                st.session_state["transcript"] = f.read()
        except FileNotFoundError:
            st.error("sample_transcript.txt not found.")

transcript = st.text_area(
    "Meeting Transcript",
    value=st.session_state.get("transcript", ""),
    placeholder="Paste your meeting transcript here...",
    height=300,
)

if st.button("Summarize Meeting", type="primary", disabled=not transcript.strip()):
    with st.spinner("Analyzing transcript..."):
        try:
            summary = summarize_meeting(transcript.strip())

            # Header metrics
            sentiment_emoji = {
                "positive": "😊", "neutral": "😐", "mixed": "🤔", "tense": "😬"
            }.get(summary.get("sentiment", "neutral"), "😐")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Meeting", summary["meeting_title"])
            col2.metric("Participants", len(summary["participants"]))
            col3.metric("Action Items", len(summary.get("action_items", [])))
            col4.metric("Sentiment", f"{sentiment_emoji} {summary.get('sentiment', '').capitalize()}")

            st.divider()

            # Summary
            st.subheader("Summary")
            st.info(summary["summary"])

            # Participants
            with st.expander("Participants", expanded=False):
                for p in summary["participants"]:
                    st.markdown(f"- {p}")

            st.divider()

            # Two columns: decisions + action items
            col_left, col_right = st.columns(2)

            with col_left:
                st.subheader("Key Decisions")
                decisions = summary.get("key_decisions", [])
                if decisions:
                    for item in decisions:
                        st.markdown(f"**{item['decision']}**")
                        st.caption(item["context"])
                        st.markdown("---")
                else:
                    st.caption("No key decisions recorded.")

            with col_right:
                st.subheader("Action Items")
                action_items = summary.get("action_items", [])
                if action_items:
                    for item in action_items:
                        priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                            item["priority"], "⚪"
                        )
                        st.markdown(
                            f"{priority_color} **{item['task']}**  \n"
                            f"Owner: `{item['owner']}` | Due: `{item['deadline']}`"
                        )
                        st.markdown("---")
                else:
                    st.caption("No action items recorded.")

            # Open questions
            open_qs = summary.get("open_questions", [])
            if open_qs:
                st.subheader("❓ Open Questions")
                for q in open_qs:
                    st.markdown(f"- {q}")

            st.caption(f"Next Meeting: {summary.get('next_meeting', 'Not scheduled')}")

            # Export
            st.divider()
            st.subheader("Export as Markdown")
            st.code(format_summary_as_markdown(summary), language="markdown")

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Make sure your ANTHROPIC_API_KEY is set in the .env file.")
