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
        section[data-testid="stSidebar"] button,
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
            padding: 3rem 2.75rem 2.75rem;
            border-radius: 1.5rem;
            background:
                radial-gradient(ellipse at 90% -20%, rgba(99,102,241,.45) 0%, transparent 55%),
                radial-gradient(ellipse at -5% 110%, rgba(8,145,178,.35) 0%, transparent 50%),
                linear-gradient(145deg, #0f172a 0%, #1e1b4b 55%, #0c1a3e 100%);
            box-shadow: 0 24px 64px rgba(15,23,42,.35);
        }

        .aiew-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background-image:
                radial-gradient(circle, rgba(255,255,255,.04) 1px, transparent 1px);
            background-size: 28px 28px;
            pointer-events: none;
        }

        .aiew-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            color: #a5b4fc;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
            margin-bottom: .85rem;
            background: rgba(99,102,241,.18);
            padding: .3rem .75rem;
            border-radius: 999px;
            border: 1px solid rgba(165,180,252,.25);
        }

        .aiew-hero h1 {
            max-width: 820px;
            margin: 0;
            color: #f8fafc;
            font-size: clamp(2rem, 4vw, 3.4rem);
            line-height: 1.05;
            letter-spacing: -.045em;
        }

        .aiew-hero-title {
            max-width: 820px;
            margin: .3rem 0 0;
            color: #f8fafc;
            font-size: clamp(2rem, 4vw, 3.4rem);
            line-height: 1.05;
            letter-spacing: -.045em;
        }

        .aiew-agenda {
            margin-top: .75rem;
        }

        .aiew-agenda-toggle {
            cursor: pointer;
            color: #a5b4fc;
            font-size: .8rem;
            font-weight: 700;
            letter-spacing: .04em;
            text-transform: uppercase;
            list-style: none;
            user-select: none;
        }

        .aiew-agenda-toggle::-webkit-details-marker { display: none; }

        .aiew-agenda-toggle::before {
            content: "▸ ";
        }

        .aiew-agenda[open] .aiew-agenda-toggle::before {
            content: "▾ ";
        }

        .aiew-gradient-text {
            background: linear-gradient(90deg, #4f46e5, #0891b2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .aiew-hero-copy {
            max-width: 720px;
            margin: 1rem 0 1.15rem;
            color: #cbd5e1;
            font-size: 1.02rem;
            line-height: 1.7;
        }

        .aiew-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: .55rem;
        }

        .aiew-chip {
            color: #e2e8f0;
            font-size: .76rem;
            font-weight: 650;
            padding: .42rem .7rem;
            border: 1px solid rgba(165,180,252,.3);
            border-radius: 999px;
            background: rgba(99,102,241,.18);
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
            padding: 1rem 1.05rem 1rem 1.3rem;
            border: 1px solid var(--aiew-border);
            border-radius: .95rem;
            background: rgba(255,255,255,.95);
            box-shadow: 0 8px 25px rgba(15,23,42,.05);
            border-left: 4px solid var(--aiew-primary);
        }

        .aiew-kpi-t1 { border-left-color: #4f46e5 !important; }
        .aiew-kpi-t2 { border-left-color: #7c3aed !important; }
        .aiew-kpi-t3 { border-left-color: #0891b2 !important; }
        .aiew-kpi-t4 { border-left-color: #d97706 !important; }

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

        /* ── Sidebar: force ALL buttons to be visible on dark background ──── */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button,
        section[data-testid="stSidebar"] div[data-testid="stBaseButton-secondary"] > button,
        section[data-testid="stSidebar"] button {
            background: rgba(255,255,255,.09) !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(148,163,184,.28) !important;
            border-radius: .6rem !important;
            font-size: .84rem !important;
            font-weight: 500 !important;
            transition: background .15s ease, border-color .15s ease !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover,
        section[data-testid="stSidebar"] button:hover {
            background: rgba(255,255,255,.16) !important;
            border-color: rgba(148,163,184,.55) !important;
            color: #f8fafc !important;
        }

        section[data-testid="stSidebar"] button:disabled {
            background: transparent !important;
            border-color: rgba(148,163,184,.1) !important;
            color: #475569 !important;
        }

        /* ── Sidebar nav buttons (active state override) ──────────────────── */
        section[data-testid="stSidebar"] .aiew-nav-btn--active div[data-testid="stButton"] > button,
        section[data-testid="stSidebar"] .aiew-nav-btn--active button {
            background: rgba(79,70,229,.35) !important;
            border-color: rgba(99,102,241,.7) !important;
            color: #e0e7ff !important;
            font-weight: 700 !important;
        }

        div.stButton > button, div.stDownloadButton > button {
            border-radius: .65rem;
            font-weight: 650;
            min-height: 2.5rem;
        }

        /* ── Tier card clickable overlay ──────────────────────────────────── */

        /* Stack the card + its button so the button sits right under the card */
        .aiew-tier-card + div[data-testid="stButton"] {
            margin-top: -0.1rem;
        }

        /* Make the overlay button invisible — only the card is visually shown */
        .aiew-tier-live + div[data-testid="stButton"] > button,
        .aiew-tier-live ~ div[data-testid="stButton"] > button {
            opacity: 0 !important;
            height: 0.1px !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            overflow: hidden !important;
            position: absolute !important;
            width: 100% !important;
            top: -100% !important;
            cursor: pointer !important;
        }

        /* Make the CARD itself show pointer cursor and capture the click area */
        .aiew-tier-live {
            cursor: pointer !important;
        }

        .aiew-tier-live:hover {
            border-color: #4f46e5 !important;
            box-shadow: 0 6px 20px rgba(79,70,229,.18) !important;
            transform: translateY(-3px) !important;
        }

        .aiew-tier-soon {
            cursor: default !important;
        }

        /* Remove the old hover hint CSS since we no longer use it */
        .aiew-tier-hint { display: none; }

        /* ── Author card (sidebar) ────────────────────────────────────────── */
        .aiew-author-card {
            display: flex;
            align-items: center;
            gap: .65rem;
            padding: .7rem .5rem;
        }

        .aiew-author-avatar {
            flex: 0 0 auto;
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5, #0891b2);
            color: white;
            font-size: .6rem;
            font-weight: 800;
            letter-spacing: .03em;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .aiew-author-name {
            color: #f1f5f9;
            font-size: .82rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .aiew-author-title {
            color: #94a3b8;
            font-size: .7rem;
            margin-top: .1rem;
        }

        .aiew-author-links {
            margin-top: .25rem;
            font-size: .68rem;
        }

        .aiew-author-link {
            color: #818cf8;
            text-decoration: none;
            font-weight: 600;
        }

        .aiew-author-link:hover {
            color: #a5b4fc;
            text-decoration: underline;
        }

        .aiew-author-sep {
            color: #475569;
            margin: 0 .2rem;
        }

        /* ── Hero byline ──────────────────────────────────────────────────── */
        .aiew-hero-byline {
            margin-top: 1.2rem;
            font-size: .78rem;
            color: #94a3b8;
        }

        .aiew-byline-link {
            color: #a5b4fc;
            text-decoration: none;
            font-weight: 600;
        }

        .aiew-byline-link:hover {
            color: #c7d2fe;
            text-decoration: underline;
        }

        .aiew-stack-row {
            display: flex;
            flex-wrap: wrap;
            gap: .3rem;
            margin-top: .55rem;
        }

        .aiew-stack-chip {
            font-size: .64rem;
            font-weight: 600;
            padding: .18rem .5rem;
            border-radius: 999px;
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }

        /* ── Card hover effect ────────────────────────────────────────────── */
        [data-testid="stVerticalBlockBorderWrapper"] {
            transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(79,70,229,.35);
            box-shadow: 0 6px 28px rgba(79,70,229,.10);
            transform: translateY(-2px);
        }

        /* ── Tier-specific card colors ───────────────────────────────────── */
        .aiew-tier-t1-live { border-color: #4f46e5 !important; background: #eef2ff !important; }
        .aiew-tier-t2-live { border-color: #7c3aed !important; background: #f5f3ff !important; }
        .aiew-tier-t3-live { border-color: #0891b2 !important; background: #ecfeff !important; }
        .aiew-tier-t4-live { border-color: #d97706 !important; background: #fffbeb !important; }
        .aiew-tier-t5-live { border-color: #e11d48 !important; background: #fff1f2 !important; }
        .aiew-tier-t6-live { border-color: #059669 !important; background: #ecfdf5 !important; }

        .aiew-tier-t1-live:hover { border-color: #4338ca !important; box-shadow: 0 6px 20px rgba(79,70,229,.22) !important; }
        .aiew-tier-t2-live:hover { border-color: #6d28d9 !important; box-shadow: 0 6px 20px rgba(124,58,237,.22) !important; }
        .aiew-tier-t3-live:hover { border-color: #0e7490 !important; box-shadow: 0 6px 20px rgba(8,145,178,.22) !important; }
        .aiew-tier-t4-live:hover { border-color: #b45309 !important; box-shadow: 0 6px 20px rgba(217,119,6,.22) !important; }
        .aiew-tier-t5-live:hover { border-color: #be123c !important; box-shadow: 0 6px 20px rgba(225,29,72,.22) !important; }
        .aiew-tier-t6-live:hover { border-color: #047857 !important; box-shadow: 0 6px 20px rgba(5,150,105,.22) !important; }

        /* ── Dark section band (principles) ─────────────────────────────── */
        .aiew-dark-band {
            margin: 2rem -2.25rem -1rem;
            padding: 2.5rem 2.25rem;
            background:
                radial-gradient(ellipse at 100% 0%, rgba(79,70,229,.2) 0%, transparent 50%),
                linear-gradient(135deg, #0b1220 0%, #111827 100%);
        }

        .aiew-dark-band .aiew-section-kicker {
            color: #818cf8 !important;
        }

        .aiew-dark-band .aiew-section-title {
            color: #f1f5f9 !important;
        }

        .aiew-dark-band .aiew-section-copy {
            color: #64748b !important;
        }

        .aiew-principle-card {
            padding: 1.4rem 1.3rem;
            border: 1px solid rgba(148,163,184,.15);
            border-radius: 1rem;
            background: rgba(255,255,255,.05);
            height: 100%;
        }

        .aiew-principle-number {
            font-size: .7rem;
            font-weight: 800;
            letter-spacing: .1em;
            color: #818cf8;
            margin-bottom: .5rem;
        }

        .aiew-principle-title {
            font-size: .95rem;
            font-weight: 750;
            color: #f1f5f9;
            margin-bottom: .4rem;
            letter-spacing: -.02em;
        }

        .aiew-principle-copy {
            font-size: .8rem;
            color: #94a3b8;
            line-height: 1.6;
        }

        /* ── Footer ──────────────────────────────────────────────────────── */
        .aiew-footer {
            position: relative;
            margin: 2.5rem -2.25rem -3rem;
            padding: 1.5rem 2.25rem;
            background: linear-gradient(135deg, #0b1220 0%, #0f172a 100%);
            border-top: 1px solid rgba(148,163,184,.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: .5rem;
        }

        .aiew-footer-brand {
            color: #f1f5f9;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: -.01em;
        }

        .aiew-footer-desc {
            color: #64748b;
            font-size: .76rem;
        }

        .aiew-footer-sep {
            color: #334155;
            font-size: .76rem;
            margin: 0 .25rem;
        }

        .aiew-footer-meta {
            color: #64748b;
            font-size: .75rem;
        }

        .aiew-footer-link {
            color: #818cf8;
            font-size: .75rem;
            font-weight: 600;
            text-decoration: none;
        }

        .aiew-footer-link:hover {
            color: #a5b4fc;
            text-decoration: underline;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .aiew-hero {
                padding: 2rem 1.5rem;
                border-radius: 1rem;
            }
            .aiew-section-copy {
                display: none;
            }
            .aiew-footer {
                flex-direction: column;
                align-items: flex-start;
                gap: .3rem;
                margin: 2.5rem -1rem -3rem;
                padding: 1.25rem 1rem;
            }
            .aiew-dark-band {
                margin: 2rem -1rem -1rem;
                padding: 2rem 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
