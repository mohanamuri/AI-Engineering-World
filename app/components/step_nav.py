"""
Step navigation component.

Provides two functions called from each app's run():
  - render_stepper()    — horizontal progress bar at top of content area
  - render_page_nav()   — ← Prev / Next → buttons at bottom of content area
"""

import streamlit as st

_CSS = """
<style>
.aiew-stepper {
    display: flex;
    align-items: center;
    margin: 0.75rem 0 1.5rem 0;
    padding: 1rem 1.5rem;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.07);
    flex-wrap: wrap;
    gap: 0.25rem;
}
.aiew-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
    min-width: 72px;
}
.aiew-step-dot {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    flex-shrink: 0;
}
.aiew-step--done   .aiew-step-dot { background:#22c55e; color:#fff; border:2px solid #22c55e; }
.aiew-step--active .aiew-step-dot { background:#6366f1; color:#fff; border:2px solid #818cf8;
                                     box-shadow:0 0 0 4px rgba(99,102,241,0.2); }
.aiew-step--pending .aiew-step-dot { background:transparent; color:rgba(255,255,255,0.25);
                                      border:2px solid rgba(255,255,255,0.12); }
.aiew-step-lbl {
    font-size: 0.65rem;
    text-align: center;
    line-height: 1.25;
    max-width: 80px;
}
.aiew-step--done    .aiew-step-lbl { color:#86efac; }
.aiew-step--active  .aiew-step-lbl { color:#a5b4fc; font-weight:600; }
.aiew-step--pending .aiew-step-lbl { color:rgba(255,255,255,0.25); }
.aiew-step-conn {
    flex: 1;
    height: 2px;
    background: rgba(255,255,255,0.08);
    margin-bottom: 20px;
    min-width: 16px;
    max-width: 60px;
}
.aiew-step-conn--done { background: #22c55e; }
</style>
"""


def render_stepper(pages: list[str], current: str) -> None:
    """Render a horizontal step progress bar at the top of the content area."""
    steps = list(pages)
    try:
        current_idx = steps.index(current)
    except ValueError:
        current_idx = 0

    parts = [_CSS]
    parts.append('<div class="aiew-stepper">')

    for i, label in enumerate(steps):
        if i < current_idx:
            state, circle = "done", "✓"
        elif i == current_idx:
            state, circle = "active", str(i + 1)
        else:
            state, circle = "pending", str(i + 1)

        parts.append(f"""
            <div class="aiew-step aiew-step--{state}">
                <div class="aiew-step-dot">{circle}</div>
                <div class="aiew-step-lbl">{label}</div>
            </div>
        """)

        if i < len(steps) - 1:
            conn_cls = "aiew-step-conn--done" if i < current_idx else ""
            parts.append(f'<div class="aiew-step-conn {conn_cls}"></div>')

    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_page_nav(pages: list[str], current: str, nav_key: str) -> None:
    """Render ← Prev / Next → buttons at the bottom of the content area."""
    steps = list(pages)
    try:
        current_idx = steps.index(current)
    except ValueError:
        current_idx = 0

    has_prev = current_idx > 0
    has_next = current_idx < len(steps) - 1

    if not has_prev and not has_next:
        return

    st.divider()
    col_prev, _, col_next = st.columns([2, 6, 2])

    if has_prev:
        with col_prev:
            if st.button(
                f"← {steps[current_idx - 1]}",
                use_container_width=True,
                key=f"_snav_prev_{nav_key}",
            ):
                st.session_state[nav_key] = steps[current_idx - 1]
                st.rerun()

    if has_next:
        with col_next:
            if st.button(
                f"{steps[current_idx + 1]} →",
                use_container_width=True,
                type="primary",
                key=f"_snav_next_{nav_key}",
            ):
                st.session_state[nav_key] = steps[current_idx + 1]
                st.rerun()
