"""Global visual system for AI Engineering World."""

import streamlit as st


def apply_theme() -> None:
    """Configure Streamlit and inject the shared product theme."""
    st.set_page_config(
        page_title="AI Engineering World",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        :root {
            --aiew-ink: #0f172a;
            --aiew-muted: #64748b;
            --aiew-primary: #4f46e5;
            --aiew-primary-soft: #eef2ff;
            --aiew-cyan: #0891b2;
            --aiew-border: #e2e8f0;
            --aiew-surface: #ffffff;
            --aiew-canvas: #f8fafc;
            --aiew-sidebar: #0b1220;
            --aiew-success: #059669;
        }

        .stApp {
            background:
                radial-gradient(circle at 78% -10%, rgba(79,70,229,.08), transparent 28rem),
                var(--aiew-canvas);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
            padding-left: 2.25rem;
            padding-right: 2.25rem;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        section[data-testid="stSidebar"] nav {
            display: none;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 20% 0%, rgba(79,70,229,.22), transparent 18rem),
                var(--aiew-sidebar);
            border-right: 1px solid rgba(148,163,184,.14);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: .75rem;
        }

        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] a,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] h5,
        section[data-testid="stSidebar"] h6 {
            color: #f8fafc !important;
        }

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: #94a3b8 !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(148,163,184,.16);
            margin: .8rem 0;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            padding: .38rem .5rem;
            border-radius: .6rem;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: rgba(255,255,255,.06);
        }

        .stMain h1, .stMain h2, .stMain h3,
        .stMain h4, .stMain h5 {
            color: var(--aiew-ink);
            letter-spacing: -.025em;
        }

        .stMain h2 {
            margin-top: .35rem;
        }

        .stMain hr {
            margin: 1.35rem 0;
            border-color: var(--aiew-border);
        }

        [data-testid="stVerticalBlock"] {
            gap: .8rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--aiew-border);
            border-radius: 1rem;
            background: rgba(255,255,255,.88);
            box-shadow: 0 1px 2px rgba(15,23,42,.03);
        }

        .aiew-app-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 auto;
            background: linear-gradient(135deg, #6366f1, #0891b2);
            color: white;
            font-weight: 800;
            box-shadow: 0 8px 24px rgba(79,70,229,.22);
        }

        .aiew-side-label {
            color: #64748b;
            font-size: .68rem;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin: .25rem 0 .1rem;
        }

        .aiew-dot {
            width: .48rem;
            height: .48rem;
            border-radius: 999px;
            background: #34d399;
            box-shadow: 0 0 0 4px rgba(52,211,153,.1);
        }

        .aiew-hero {
            position: relative;
            overflow: hidden;
            padding: 2.4rem 2.5rem;
            border: 1px solid #dbe3f0;
            border-radius: 1.35rem;
            background:
                radial-gradient(circle at 88% 18%, rgba(34,211,238,.18), transparent 16rem),
                linear-gradient(135deg, #ffffff 0%, #f7f8ff 60%, #eefbff 100%);
            box-shadow: 0 18px 45px rgba(15,23,42,.07);
        }

        .aiew-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            color: #4338ca;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .75rem;
        }

        .aiew-hero h1 {
            max-width: 790px;
            margin: 0;
            color: var(--aiew-ink);
            font-size: clamp(2.2rem, 4vw, 3.7rem);
            line-height: 1.04;
            letter-spacing: -.055em;
        }

        .aiew-gradient-text {
            background: linear-gradient(90deg, #4f46e5, #0891b2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .aiew-hero-copy {
            max-width: 720px;
            margin: 1rem 0 1.15rem;
            color: #475569;
            font-size: 1.02rem;
            line-height: 1.7;
        }

        .aiew-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: .55rem;
        }

        .aiew-chip {
            color: #334155;
            font-size: .76rem;
            font-weight: 650;
            padding: .42rem .7rem;
            border: 1px solid #dbe3f0;
            border-radius: 999px;
            background: rgba(255,255,255,.76);
        }

        .aiew-section-head {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin: 1.6rem 0 .8rem;
        }

        .aiew-section-kicker {
            color: #4f46e5;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
            margin-bottom: .2rem;
        }

        .aiew-section-title {
            color: var(--aiew-ink);
            font-size: 1.45rem;
            font-weight: 750;
            letter-spacing: -.035em;
        }

        .aiew-section-copy {
            color: var(--aiew-muted);
            font-size: .84rem;
        }

        .aiew-kpi {
            min-height: 7.5rem;
            padding: 1rem 1.05rem;
            border: 1px solid var(--aiew-border);
            border-radius: .95rem;
            background: rgba(255,255,255,.9);
            box-shadow: 0 8px 25px rgba(15,23,42,.04);
        }

        .aiew-kpi-label {
            color: var(--aiew-muted);
            font-size: .75rem;
            font-weight: 650;
        }

        .aiew-kpi-value {
            color: var(--aiew-ink);
            font-size: 1.75rem;
            line-height: 1.2;
            font-weight: 760;
            letter-spacing: -.045em;
            margin: .45rem 0 .15rem;
        }

        .aiew-kpi-caption {
            color: #94a3b8;
            font-size: .7rem;
        }

        .aiew-app-head {
            display: flex;
            align-items: center;
            gap: .8rem;
        }

        .aiew-app-icon {
            width: 2.65rem;
            height: 2.65rem;
            border-radius: .8rem;
            font-size: .72rem;
            letter-spacing: .02em;
        }

        .aiew-app-title {
            color: var(--aiew-ink);
            font-size: 1rem;
            font-weight: 750;
            line-height: 1.3;
        }

        .aiew-app-category {
            color: var(--aiew-muted);
            font-size: .72rem;
            margin-top: .12rem;
        }

        .aiew-app-copy {
            min-height: 2.8rem;
            color: #475569;
            font-size: .82rem;
            line-height: 1.55;
            margin: .8rem 0;
        }

        .aiew-card-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .5rem;
            margin-bottom: .7rem;
        }

        .aiew-badge {
            display: inline-flex;
            align-items: center;
            gap: .35rem;
            padding: .25rem .5rem;
            border-radius: 999px;
            font-size: .68rem;
            font-weight: 700;
            color: #047857;
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
        }

        .aiew-meta-text {
            color: #94a3b8;
            font-size: .68rem;
        }

        .aiew-loan-hero {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1.15rem 1.25rem;
            margin: .3rem 0 .5rem;
            border: 1px solid var(--aiew-border);
            border-radius: 1rem;
            background: linear-gradient(120deg, #fff, #f5f7ff);
        }

        .aiew-loan-hero h1 {
            font-size: 1.65rem;
            margin: 0 0 .2rem;
        }

        .aiew-loan-hero p {
            color: var(--aiew-muted);
            font-size: .82rem;
            margin: 0;
        }

        div.stButton > button, div.stDownloadButton > button {
            border-radius: .65rem;
            font-weight: 650;
            min-height: 2.5rem;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .aiew-hero {
                padding: 1.6rem;
            }
            .aiew-section-copy {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
