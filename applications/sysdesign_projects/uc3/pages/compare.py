"""UC3 — Compare: Side-by-side comparison of two architecture patterns."""

import streamlit as st
import pandas as pd

from applications.sysdesign_projects.services.arch_patterns import PATTERNS


def render() -> None:
    st.subheader("⚖️ Compare — Two Architecture Patterns")

    st.markdown(
        "Select two patterns and compare them across all dimensions: "
        "components, cost, pros/cons, RPS range, and best-fit scenarios."
    )

    pattern_names = {p.name: key for key, p in PATTERNS.items()}
    display_names = list(pattern_names.keys())

    col_sel_a, col_sel_b = st.columns(2)
    with col_sel_a:
        name_a = st.selectbox("Pattern A", display_names, index=0, key="sysdesign_uc3_cmp_a")
    with col_sel_b:
        name_b = st.selectbox("Pattern B", display_names, index=1, key="sysdesign_uc3_cmp_b")

    pa = PATTERNS[pattern_names[name_a]]
    pb = PATTERNS[pattern_names[name_b]]

    st.divider()

    # High-level summary
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown(f"**{pa.name}**")
            st.caption(pa.description)
            st.markdown(f"- **RPS range:** {pa.rps_range}")
            st.markdown(f"- **Est. cost:** {pa.estimated_cost}")
            st.markdown(f"- **Best for:** {pa.best_for}")
            st.code(pa.diagram, language=None)

    with col2:
        with st.container(border=True):
            st.markdown(f"**{pb.name}**")
            st.caption(pb.description)
            st.markdown(f"- **RPS range:** {pb.rps_range}")
            st.markdown(f"- **Est. cost:** {pb.estimated_cost}")
            st.markdown(f"- **Best for:** {pb.best_for}")
            st.code(pb.diagram, language=None)

    st.divider()
    st.markdown("### Pros & Cons Comparison")

    col_p, col_c = st.columns(2)

    with col_p:
        st.markdown("**Pros**")
        max_pros = max(len(pa.pros), len(pb.pros))
        rows = []
        for i in range(max_pros):
            rows.append({
                pa.name[:20]: pa.pros[i] if i < len(pa.pros) else "—",
                pb.name[:20]: pb.pros[i] if i < len(pb.pros) else "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with col_c:
        st.markdown("**Cons**")
        max_cons = max(len(pa.cons), len(pb.cons))
        rows = []
        for i in range(max_cons):
            rows.append({
                pa.name[:20]: pa.cons[i] if i < len(pa.cons) else "—",
                pb.name[:20]: pb.cons[i] if i < len(pb.cons) else "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Component Comparison")

    max_comps = max(len(pa.components), len(pb.components))
    comp_rows = []
    for i in range(max_comps):
        ca = pa.components[i] if i < len(pa.components) else None
        cb = pb.components[i] if i < len(pb.components) else None
        comp_rows.append({
            f"A: {pa.name[:20]}": f"{ca.name} ({ca.cost_tier})" if ca else "—",
            f"B: {pb.name[:20]}": f"{cb.name} ({cb.cost_tier})" if cb else "—",
        })

    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### When to Choose Each")

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown(f"**Choose {pa.name} when:**")
            st.markdown(f"- Traffic fits {pa.rps_range}\n- Budget allows {pa.estimated_cost}\n- {pa.best_for}")

    with col_b:
        with st.container(border=True):
            st.markdown(f"**Choose {pb.name} when:**")
            st.markdown(f"- Traffic fits {pb.rps_range}\n- Budget allows {pb.estimated_cost}\n- {pb.best_for}")
