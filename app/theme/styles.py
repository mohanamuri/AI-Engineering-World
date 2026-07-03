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
        /* ── Design tokens ─────────────────────────────────────────────── */
        :root {
            --aiew-ink:          #0f172a;
            --aiew-muted:        #64748b;
            --aiew-primary:      #4f46e5;
            --aiew-primary-soft: #eef2ff;
            --aiew-cyan:         #0891b2;
            --aiew-border:       #e2e8f0;
            --aiew-surface:      #ffffff;
            --aiew-canvas:       #f8fafc;
            --aiew-sidebar:      #0b1220;
            --aiew-success:      #059669;
        }

        /* ── App background ─────────────────────────────────────────────── */
        .stApp {
            background:
                radial-gradient(circle at 78% -10%, rgba(79,70,229,.07), transparent 28rem),
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

        /* ── Sidebar ────────────────────────────────────────────────────── */
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

        /* ── Main typography ────────────────────────────────────────────── */
        .stMain h1, .stMain h2, .stMain h3,
        .stMain h4, .stMain h5 {
            color: var(--aiew-ink);
            letter-spacing: -.025em;
        }

        .stMain h2 { margin-top: .35rem; }

        .stMain hr {
            margin: 1.35rem 0;
            border-color: var(--aiew-border);
        }

        [data-testid="stVerticalBlock"] { gap: .8rem; }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--aiew-border);
            border-radius: 1rem;
            background: rgba(255,255,255,.88);
            box-shadow: 0 1px 2px rgba(15,23,42,.03);
        }

        /* ── Buttons ────────────────────────────────────────────────────── */
        div.stButton > button, div.stDownloadButton > button {
            border-radius: .65rem;
            font-weight: 650;
            min-height: 2.5rem;
        }

        /* Sidebar buttons */
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

        section[data-testid="stSidebar"] .aiew-nav-btn--active div[data-testid="stButton"] > button,
        section[data-testid="stSidebar"] .aiew-nav-btn--active button {
            background: rgba(79,70,229,.35) !important;
            border-color: rgba(99,102,241,.7) !important;
            color: #e0e7ff !important;
            font-weight: 700 !important;
        }

        /* ── Hero banner (dashboard home) ───────────────────────────────── */
        .aiew-hero {
            position: relative;
            overflow: hidden;
            padding: 3rem 2.75rem 2.75rem;
            border-radius: 1.5rem;
            background:
                radial-gradient(ellipse at 90% -20%, rgba(99,102,241,.45) 0%, transparent 55%),
                radial-gradient(ellipse at -5% 110%, rgba(8,145,178,.35) 0%, transparent 50%),
                linear-gradient(145deg, #0f172a 0%, #1e1b4b 55%, #0c1a3e 100%);
            box-shadow: 0 24px 64px rgba(15,23,42,.3), 0 0 0 1px rgba(99,102,241,.2);
        }

        .aiew-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background-image: radial-gradient(circle, rgba(255,255,255,.035) 1px, transparent 1px);
            background-size: 28px 28px;
            pointer-events: none;
        }

        .aiew-gradient-word {
            background: linear-gradient(90deg, #818cf8 0%, #22d3ee 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
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

        .aiew-hero-title {
            max-width: 820px;
            margin: .3rem 0 0;
            color: #f8fafc;
            font-size: clamp(2rem, 4vw, 3.4rem);
            line-height: 1.05;
            letter-spacing: -.045em;
        }

        .aiew-hero-copy {
            max-width: 720px;
            margin: 1rem 0 1.15rem;
            color: #cbd5e1;
            font-size: 1.02rem;
            line-height: 1.7;
        }

        .aiew-agenda { margin-top: .75rem; }

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
        .aiew-agenda-toggle::before { content: "▸ "; }
        .aiew-agenda[open] .aiew-agenda-toggle::before { content: "▾ "; }

        .aiew-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: .5rem;
            margin-top: 1rem;
        }

        .aiew-chip {
            color: #e2e8f0;
            font-size: .75rem;
            font-weight: 650;
            padding: .4rem .75rem;
            border: 1px solid rgba(165,180,252,.25);
            border-radius: 999px;
            background: rgba(99,102,241,.18);
        }

        /* Author card inside hero */
        .aiew-hero-author {
            display: flex;
            align-items: center;
            gap: .75rem;
            margin-top: 1.4rem;
            padding: .75rem 1rem;
            background: rgba(255,255,255,.06);
            border: 1px solid rgba(255,255,255,.1);
            border-radius: .85rem;
            max-width: 480px;
        }

        .aiew-hero-avatar {
            flex: 0 0 auto;
            width: 2.6rem;
            height: 2.6rem;
            border-radius: 50%;
            background: linear-gradient(135deg, #818cf8, #22d3ee);
            color: white;
            font-size: .62rem;
            font-weight: 800;
            letter-spacing: .02em;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .aiew-hero-author-name {
            color: #f1f5f9;
            font-size: .85rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .aiew-hero-author-title {
            color: #94a3b8;
            font-size: .72rem;
            margin-top: .1rem;
        }

        .aiew-hero-author-links {
            margin-top: .3rem;
        }

        .aiew-byline-link {
            color: #38bdf8;
            text-decoration: none;
            font-weight: 700;
            font-size: .72rem;
        }

        .aiew-byline-link:hover {
            color: #7dd3fc;
            text-decoration: underline;
        }

        /* Live indicator */
        .aiew-live-dot {
            display: inline-block;
            width: .5rem;
            height: .5rem;
            border-radius: 50%;
            background: #34d399;
            box-shadow: 0 0 0 3px rgba(52,211,153,.2);
            margin-right: .3rem;
            vertical-align: middle;
        }

        /* ── Dashboard section headers ──────────────────────────────────── */
        .aiew-section-head {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin: 1.8rem 0 .85rem;
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

        /* ── KPI cards ──────────────────────────────────────────────────── */
        .aiew-kpi {
            padding: 1.1rem 1rem 1rem 1.35rem;
            border: 1px solid var(--aiew-border);
            border-left-width: 4px;
            border-radius: .95rem;
            background: #ffffff;
            box-shadow: 0 4px 16px rgba(15,23,42,.05);
            min-height: 7rem;
        }

        .aiew-kpi-t1 { border-left-color: #4f46e5; }
        .aiew-kpi-t2 { border-left-color: #7c3aed; }
        .aiew-kpi-t3 { border-left-color: #0891b2; }
        .aiew-kpi-t4 { border-left-color: #d97706; }

        .aiew-kpi-label {
            color: var(--aiew-muted);
            font-size: .75rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: .04em;
        }

        .aiew-kpi-value {
            color: var(--aiew-ink);
            font-size: 1.9rem;
            line-height: 1.15;
            font-weight: 760;
            letter-spacing: -.045em;
            margin: .4rem 0 .15rem;
        }

        .aiew-kpi-caption {
            color: #94a3b8;
            font-size: .7rem;
        }

        /* ── Project cards on dashboard ─────────────────────────────────── */
        .aiew-app-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 auto;
            width: 2.65rem;
            height: 2.65rem;
            border-radius: .8rem;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .02em;
            background: linear-gradient(135deg, #6366f1, #0891b2);
            color: white;
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

        /* ── Tier cards (capability ladder) ─────────────────────────────── */
        .aiew-tier-card {
            border-radius: .9rem;
            padding: .75rem .75rem;
            text-align: center;
            position: relative;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }

        .aiew-tier-live  { cursor: pointer; }
        .aiew-tier-soon  { cursor: default; }
        .aiew-tier-hint  { display: none; }

        /* Per-tier live colors */
        .aiew-tier-t1-live { border: 2px solid #4f46e5 !important; background: #eef2ff !important; }
        .aiew-tier-t2-live { border: 2px solid #7c3aed !important; background: #f5f3ff !important; }
        .aiew-tier-t3-live { border: 2px solid #0891b2 !important; background: #ecfeff !important; }
        .aiew-tier-t4-live { border: 2px solid #d97706 !important; background: #fffbeb !important; }
        .aiew-tier-t5-live { border: 2px solid #e11d48 !important; background: #fff1f2 !important; }
        .aiew-tier-t6-live { border: 2px solid #059669 !important; background: #ecfdf5 !important; }

        .aiew-tier-t1-live:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(79,70,229,.22) !important; }
        .aiew-tier-t2-live:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(124,58,237,.22) !important; }
        .aiew-tier-t3-live:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(8,145,178,.22) !important; }
        .aiew-tier-t4-live:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(217,119,6,.22) !important; }
        .aiew-tier-t5-live:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(225,29,72,.22) !important; }
        .aiew-tier-t6-live:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(5,150,105,.22) !important; }

        /* Hide the invisible overlay button */
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

        /* ── Tier app banners ───────────────────────────────────────────── */
        .aiew-tier-banner {
            position: relative;
            overflow: hidden;
            padding: 1.75rem 2rem;
            border-radius: 1.25rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 16px 40px rgba(15,23,42,.25), 0 0 0 1px rgba(255,255,255,.06);
        }

        .aiew-tier-banner::before {
            content: "";
            position: absolute;
            inset: 0;
            background-image: radial-gradient(circle, rgba(255,255,255,.04) 1px, transparent 1px);
            background-size: 22px 22px;
            pointer-events: none;
        }

        /* Per-tier gradients */
        .aiew-tb--t1 { background: linear-gradient(135deg, #1e1b4b 0%, #312e81 55%, #1e3a5f 100%); }
        .aiew-tb--t2 { background: linear-gradient(135deg, #2e1065 0%, #4c1d95 55%, #1e1b4b 100%); }
        .aiew-tb--t3 { background: linear-gradient(135deg, #083344 0%, #155e75 55%, #0a2740 100%); }
        .aiew-tb--t4 { background: linear-gradient(135deg, #451a03 0%, #7c2d12 55%, #1c1009 100%); }
        .aiew-tb--t5 { background: linear-gradient(135deg, #4c0519 0%, #881337 55%, #2d030e 100%); }
        .aiew-tb--t6 { background: linear-gradient(135deg, #022c22 0%, #064e3b 55%, #011c17 100%); }

        .aiew-tier-banner-inner {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: flex-start;
            gap: 1.25rem;
        }

        .aiew-tier-badge-lg {
            flex: 0 0 auto;
            width: 3rem;
            height: 3rem;
            border-radius: .75rem;
            background: rgba(255,255,255,.12);
            border: 1px solid rgba(255,255,255,.2);
            color: #ffffff;
            font-size: .72rem;
            font-weight: 900;
            letter-spacing: .04em;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .aiew-tb--t1 .aiew-tier-badge-lg { background: rgba(129,140,248,.25); border-color: rgba(129,140,248,.4); color: #c7d2fe; }
        .aiew-tb--t2 .aiew-tier-badge-lg { background: rgba(167,139,250,.25); border-color: rgba(167,139,250,.4); color: #ddd6fe; }
        .aiew-tb--t3 .aiew-tier-badge-lg { background: rgba(34,211,238,.2);   border-color: rgba(34,211,238,.35); color: #a5f3fc; }
        .aiew-tb--t4 .aiew-tier-badge-lg { background: rgba(251,191,36,.2);   border-color: rgba(251,191,36,.35); color: #fde68a; }
        .aiew-tb--t5 .aiew-tier-badge-lg { background: rgba(251,113,133,.2);  border-color: rgba(251,113,133,.35); color: #fecdd3; }
        .aiew-tb--t6 .aiew-tier-badge-lg { background: rgba(52,211,153,.2);   border-color: rgba(52,211,153,.35); color: #a7f3d0; }

        .aiew-tb-cap {
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .3rem;
            opacity: .7;
            color: #e2e8f0;
        }

        .aiew-tb-title {
            font-size: 1.45rem;
            font-weight: 760;
            letter-spacing: -.035em;
            line-height: 1.15;
            color: #f8fafc;
            margin-bottom: .3rem;
        }

        .aiew-tb-desc {
            font-size: .82rem;
            color: #cbd5e1;
            line-height: 1.55;
            max-width: 680px;
            margin-bottom: .55rem;
        }

        .aiew-tb-flow {
            font-size: .72rem;
            color: rgba(255,255,255,.5);
            font-weight: 600;
            letter-spacing: .03em;
            margin-bottom: .6rem;
        }

        .aiew-tech-pill {
            display: inline-block;
            padding: .2rem .6rem;
            border-radius: 999px;
            font-size: .64rem;
            font-weight: 650;
            background: rgba(255,255,255,.1);
            color: rgba(255,255,255,.8);
            border: 1px solid rgba(255,255,255,.18);
            margin-right: .25rem;
            margin-top: .2rem;
        }

        /* ── Principle cards (dark) ─────────────────────────────────────── */
        .aiew-principle-card {
            padding: 1.5rem 1.35rem;
            border: 1px solid rgba(148,163,184,.15);
            border-radius: 1rem;
            background: linear-gradient(145deg, #0f172a, #1a1f35);
            height: 100%;
            box-shadow: 0 4px 16px rgba(0,0,0,.3);
        }

        .aiew-principle-number {
            font-size: .65rem;
            font-weight: 900;
            letter-spacing: .12em;
            text-transform: uppercase;
            color: #818cf8;
            margin-bottom: .55rem;
        }

        .aiew-principle-title {
            font-size: .98rem;
            font-weight: 750;
            color: #f1f5f9;
            margin-bottom: .45rem;
            letter-spacing: -.02em;
        }

        .aiew-principle-copy {
            font-size: .8rem;
            color: #94a3b8;
            line-height: 1.6;
        }

        /* ── Card hover ─────────────────────────────────────────────────── */
        [data-testid="stVerticalBlockBorderWrapper"] {
            transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(79,70,229,.35);
            box-shadow: 0 6px 28px rgba(79,70,229,.10);
            transform: translateY(-2px);
        }

        /* ── Sidebar misc ───────────────────────────────────────────────── */
        .aiew-dot {
            width: .48rem;
            height: .48rem;
            border-radius: 999px;
            background: #34d399;
            box-shadow: 0 0 0 4px rgba(52,211,153,.1);
        }

        /* ── Author card (sidebar) ──────────────────────────────────────── */
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

        .aiew-author-name  { color: #f1f5f9; font-size: .82rem; font-weight: 700; line-height: 1.2; }
        .aiew-author-title { color: #94a3b8; font-size: .7rem; margin-top: .1rem; }
        .aiew-author-links { margin-top: .25rem; font-size: .68rem; }
        .aiew-author-link  { color: #818cf8; text-decoration: none; font-weight: 600; }
        .aiew-author-link:hover { color: #a5b4fc; text-decoration: underline; }
        .aiew-author-sep   { color: #475569; margin: 0 .2rem; }

        /* ── Footer ─────────────────────────────────────────────────────── */
        .aiew-footer {
            position: relative;
            margin-top: 3rem;
            padding: 1.25rem 0 .75rem;
        }

        .aiew-footer::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #4f46e5, #7c3aed 30%, #0891b2 60%, #059669 85%, #d97706);
            border-radius: 999px;
        }

        .aiew-footer-inner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: .5rem;
            padding-top: 1rem;
        }

        .aiew-footer-brand { color: var(--aiew-ink); font-size: .8rem; font-weight: 750; }
        .aiew-footer-desc  { color: var(--aiew-muted); font-size: .76rem; }
        .aiew-footer-sep   { color: var(--aiew-border); font-size: .8rem; margin: 0 .3rem; }
        .aiew-footer-meta  { color: var(--aiew-muted); font-size: .75rem; }
        .aiew-footer-link  { color: var(--aiew-primary); font-size: .75rem; font-weight: 650; text-decoration: none; }
        .aiew-footer-link:hover { text-decoration: underline; }

        /* ── Responsive ─────────────────────────────────────────────────── */
        @media (max-width: 900px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .aiew-hero { padding: 2rem 1.5rem; border-radius: 1rem; }
            .aiew-section-copy { display: none; }
            .aiew-footer-inner { flex-direction: column; align-items: flex-start; gap: .3rem; }
            .aiew-tier-banner { padding: 1.25rem 1.25rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
