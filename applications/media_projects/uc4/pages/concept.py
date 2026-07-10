"""Media UC4 — Concept page: Document Scanner."""

import streamlit as st


def render() -> None:
    st.subheader("📖 Document Scanner — Read This First")

    st.info(
        "**What you'll learn in this app**\n\n"
        "- How to turn a photo of any document into structured, searchable data\n"
        "- Why 'structured extraction' is more useful than free-form description\n"
        "- What document digitisation means and where it's used in real life\n"
        "- How to export your scanned document as JSON or plain text"
    )

    # ── Problem ──────────────────────────────────────────────────────────────
    st.markdown("### The Problem — Physical Documents Stuck in Photos")

    st.markdown(
        "You have a photo of a whiteboard from a meeting. "
        "Or a picture of a printed contract. Or a snapshot of handwritten notes. "
        "Or a slide from a presentation you couldn't copy.\n\n"
        "The text is *in* the image — but it's not searchable, not copyable, "
        "not shareable as a document. "
        "You'd need to type it all out manually.\n\n"
        "**UC4 converts any document photo into clean, structured, exportable data — in seconds.**"
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Without Document Scanner**")
            st.markdown(
                "- Photo stays as an image — not searchable\n"
                "- Someone types the content out manually\n"
                "- Traditional OCR only reads text, loses structure\n"
                "- Tables, headings, sections all get flattened into one blob"
            )
    with col2:
        with st.container(border=True):
            st.markdown("**With Document Scanner**")
            st.markdown(
                "- Upload the photo — done in one step\n"
                "- AI reads the document and preserves its structure\n"
                "- Title, sections, headings, text all extracted separately\n"
                "- Export as clean JSON or plain text — ready to file or process"
            )

    # ── Build on UC3 ─────────────────────────────────────────────────────────
    st.markdown("### How It Builds on UC3")

    st.markdown(
        "UC3 (Image Intelligence) gives a general description of any image — "
        "scene, text, objects, colours.\n\n"
        "UC4 is **focused on documents specifically**: instead of describing the image generally, "
        "it extracts the document's *structure* — like a reader who fills in a template:\n"
        "*Document type? Title? Sections with headings? All body text? Tables? Language?*"
    )

    st.graphviz_chart("""
    digraph DocumentScanner {
        rankdir=LR
        node [shape=box style=filled fontname="Arial" fontsize=11]
        edge [fontsize=10]

        P  [label="📸 Photo of\nDocument / Whiteboard\n/ Slide" fillcolor="#fce7f3" color="#ec4899"]
        V  [label="Groq Vision LLM\nReads image as\na document" fillcolor="#dbeafe" color="#3b82f6"]
        S  [label="Structured JSON\nType · Title · Sections\nText · Tables · Language" fillcolor="#fef9c3" color="#eab308"]
        E  [label="📥 Export\nJSON or Plain Text" fillcolor="#f0fdf4" color="#22c55e"]

        P -> V -> S -> E
    }
    """)

    steps = [
        ("📸 Upload a document photo",
         "Any photo of a document works:\n"
         "- Printed contracts, letters, invoices\n"
         "- Handwritten notes or whiteboards\n"
         "- Presentation slides\n"
         "- Business cards, forms, reports\n"
         "- Screenshots of documents"),
        ("👁️ Groq Vision reads it as a document",
         "The vision model is prompted specifically to treat the image as a document, "
         "not just an image. It looks for document structure — not just raw text."),
        ("📋 Structured JSON output",
         "The model extracts a structured report:\n"
         "- **Document type** — contract, whiteboard, slide, form, etc.\n"
         "- **Title** — the document's heading\n"
         "- **Sections** — each section with its heading and body text\n"
         "- **All text** — verbatim text preserved\n"
         "- **Tables** — table data if present\n"
         "- **Language** — detected document language\n\n"
         "This is not free-form description — it's structured, consistent, and machine-readable."),
        ("📥 Export",
         "Download the extracted content as:\n"
         "- **JSON** — for programmatic use, databases, or APIs\n"
         "- **Plain text** — for reading, filing, or pasting elsewhere"),
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
            st.markdown("**Document Digitisation**")
            st.write(
                "Converting a physical or photographic document into a digital, "
                "searchable, structured format. "
                "What used to require manual typing or fragile OCR pipelines "
                "now happens in one AI call."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("**Structured vs Free-form**")
            st.write(
                "Free-form: the AI describes what it sees in natural language. "
                "Structured: the AI fills in a specific template — "
                "title here, sections here, tables here — every time. "
                "Structured output is consistent and programmable."
            )

    st.success(
        "**Ready to try it?** Go to **Upload** and load a photo of any document. "
        "The AI will extract its full structure. "
        "Then export as JSON or plain text — your document is now digitised."
    )
