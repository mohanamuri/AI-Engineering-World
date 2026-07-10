"""UC3 — Concept page: Structured Output."""

import streamlit as st
from applications.prompt_projects.services.prompt_service import DEFAULT_SCHEMA
import json


def render() -> None:
    st.subheader("📖 Structured Output")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- Why free-form AI output breaks software pipelines\n"
        "- How to tell the AI to return data in a fixed format every time\n"
        "- What JSON is and why it's the standard format for structured output\n"
        "- How to try structured vs free-form extraction in the Playground"
    )

    st.markdown(
        "Imagine you ask an AI to analyse a product review and extract the sentiment. "
        "Without structure, it might say: *'This review is quite positive overall, "
        "though there are some concerns about...'* — great for reading, useless for a database.\n\n"
        "**Structured output** means telling the AI exactly what format to use — "
        "like a form to fill in, not a blank page to write on."
    )
    st.write(
        "Freeform LLM output is great for humans to read but hard for code to process. "
        "Structured output techniques force the model to return valid JSON every time — "
        "making it a reliable data source for pipelines, dashboards, and APIs."
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("#### 📝 Freeform output")
            st.write(
                "The model answers in natural language. "
                "Parsing it requires regex, NLP, or manual handling — all fragile."
            )
            st.markdown("**Problems:**")
            st.markdown(
                "- Inconsistent structure across runs\n"
                "- Hard to parse programmatically\n"
                "- Field names change unpredictably\n"
                "- Downstream code breaks silently"
            )
            st.warning("**Risk:** One bad run crashes your pipeline.")

    with col2:
        with st.container(border=True):
            st.markdown("#### 🗂️ Structured output (JSON)")
            st.write(
                "The model is instructed to return only valid JSON matching an exact schema. "
                "Your code can `json.loads()` it reliably every time."
            )
            st.markdown("**Benefits:**")
            st.markdown(
                "- Predictable field names and types\n"
                "- `json.loads()` works every time\n"
                "- Schema serves as self-documentation\n"
                "- Drop-in for APIs, databases, dashboards"
            )
            st.success("**Result:** Production-ready data extraction.")

    st.divider()
    st.markdown("#### The schema pattern")

    tab_freeform, tab_struct = st.tabs(["Freeform prompt", "Structured prompt"])

    with tab_freeform:
        st.code(
            """# Freeform — unpredictable output structure
prompt = "Analyse this product review: 'Great battery but slow charging.'"

# Output might be:
# "This review is generally positive. The user likes the battery
#  life but is disappointed by the charging speed..."
""",
            language="python",
        )

    with tab_struct:
        st.code(
            f"""# Structured — always parseable
schema = {json.dumps(DEFAULT_SCHEMA, indent=2)}

prompt = (
    "Analyse this product review: 'Great battery but slow charging.'\\n\\n"
    "Return ONLY valid JSON matching this schema exactly:\\n"
    + json.dumps(schema, indent=2)
)

# Output:
# {{
#   "title": "Product Review Analysis",
#   "summary": "Positive overall with battery praise but charging criticism.",
#   "key_points": ["Strong battery life", "Slow charging speed"],
#   "sentiment": "positive",
#   "confidence": "high"
# }}
result = json.loads(output)  # Always works ✓
""",
            language="python",
        )

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Parse reliability", "~100%", "With good schema")
    c2.metric("Extra prompt tokens", "~50–100", "Worth the reliability")
    c3.metric("Downstream breakage", "Near zero", "vs freeform's fragility")
