"""Media UC3 — Concept page: Image Intelligence."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Image Intelligence — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- How AI can 'see' and 'read' an image in one step\n"
        "- What a vision-language model is and how it differs from regular AI\n"
        "- What you can extract from any image automatically\n"
        "- How to ask follow-up questions about an image interactively"
    )

    # ── Shift in modality ────────────────────────────────────────────────────
    st.markdown("### A New Type of Input — Images")

    st.markdown(
        "UC1 and UC2 work with **audio** (speech). UC3 introduces a completely different input: **images**.\n\n"
        "Traditional AI systems needed separate tools to process images:\n"
        "- One tool for OCR (reading text in images)\n"
        "- Another for object detection (identifying objects)\n"
        "- Another for scene description (understanding context)\n\n"
        "**Vision-language models do all of this in one single AI call.** "
        "They can 'see' the image and 'talk' about it — hence the name."
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Traditional approach**")
            st.markdown(
                "Image → OCR tool (reads text)\n"
                "Image → Object detector\n"
                "Image → Scene classifier\n"
                "→ Combine outputs manually\n\n"
                "- Multiple tools, multiple steps\n"
                "- Tools don't understand context\n"
                "- Hard to ask follow-up questions"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**Vision-language model (UC3)**")
            st.markdown(
                "Image → One VLM call → Everything\n\n"
                "- Describes the full scene\n"
                "- Reads all embedded text\n"
                "- Identifies objects and colours\n"
                "- Answers follow-up questions about the image"
            )

    # ── Visual ───────────────────────────────────────────────────────────────
    st.markdown("### How It Works — One Model, Multiple Outputs")

    st.graphviz_chart("""
    digraph ImageIntelligence {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        I  [label="🖼️ Your Image\n(.jpg / .png)" fillcolor="#fce7f3" color="#ec4899"]
        V  [label="Groq Vision LLM\n(llama-4-scout-17b)\nSees the image" fillcolor="#dbeafe" color="#3b82f6"]
        D  [label="Scene Description\nWhat's happening?" fillcolor="#f0fdf4" color="#22c55e"]
        T  [label="Text Extraction\nAll text visible" fillcolor="#fef9c3" color="#eab308"]
        O  [label="Object List\nWhat's in the image?" fillcolor="#fff7ed" color="#f97316"]
        Q  [label="💬 Follow-up Q&A\nAsk anything about\nthe image" fillcolor="#e0f2fe" color="#0ea5e9"]

        I -> V
        V -> D
        V -> T
        V -> O
        V -> Q
    }
    """)

    steps = [
        ("🖼️ Upload your image",
         "Upload any .jpg or .png image — a photo, a screenshot, a chart, a whiteboard, "
         "a diagram, a sign, a product label. Anything you can photograph."),
        ("👁️ Groq Vision analyses it",
         "**Groq Vision** (llama-4-scout-17b) is a vision-language model — "
         "it processes both pixels and text together in one model. "
         "Unlike traditional OCR, it understands the *context* of what it sees, not just the words."),
        ("📋 Four automatic outputs",
         "In one API call, the model returns:\n"
         "- **Scene description** — what's happening in the image\n"
         "- **All visible text** — every word it can read in the image\n"
         "- **Object list** — what items, people, or things it sees\n"
         "- **Dominant colours** — the main colours in the image"),
        ("💬 Follow-up Q&A",
         "After the automatic analysis, you can ask any question about the image: "
         "*'What does the sign on the right say?'*, "
         "*'How many people are in this photo?'*, "
         "*'What is the chart showing?'* "
         "The model answers interactively."),
    ]
    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    # ── Key terms ────────────────────────────────────────────────────────────
    st.markdown("### Key Terms (Plain English)")
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("**Vision-Language Model (VLM)**")
            st.write(
                "An AI model that can process *both* images and text together. "
                "It doesn't just see pixels — it understands what they mean and can describe, "
                "explain, and answer questions about them in natural language."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**OCR-free extraction**")
            st.write(
                "Traditional OCR (Optical Character Recognition) only reads text. "
                "A VLM reads text *and* understands the visual context around it — "
                "all in one step, without a separate OCR tool."
            )

    st.success(
        "**Ready to try it?** Go to **Upload** and load any image. "
        "The model will describe it, read all text in it, and list what it sees. "
        "Then ask your own follow-up questions in the Q&A section."
    )
