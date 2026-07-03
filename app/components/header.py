"""Home-page hero for AI Engineering World."""

import streamlit as st


def show_header() -> None:
    """Render a compact, product-focused platform hero."""
    st.markdown(
        """
        <section class="aiew-hero">
            <div class="aiew-eyebrow">◈ AI Engineering Portfolio</div>
            <h1>Build intelligent systems.<br>
                <span class="aiew-gradient-text">Engineer them for the real world.</span>
            </h1>
            <p class="aiew-hero-copy">
                A hands-on portfolio of production-minded machine learning,
                deep learning, and generative AI systems—from data and
                experimentation to evaluation and deployment.
            </p>
            <div class="aiew-chip-row">
                <span class="aiew-chip">Machine Learning</span>
                <span class="aiew-chip">Deep Learning</span>
                <span class="aiew-chip">Generative AI</span>
                <span class="aiew-chip">MLOps</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
