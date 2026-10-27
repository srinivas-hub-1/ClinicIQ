"""
ClinicIQ — AI-Powered Clinic Intelligence & Outreach Automation
"""

import streamlit as st
import pandas as pd
import json
from data.seed_clinics import INITIAL_CLINICS
from scraper import scrape_clinic_url, simulate_directory_search
from ai_engine import (
    analyze_clinic_with_ai,
    generate_outreach_email,
    SYSTEM_PROMPT,
    PROMPT_EVOLUTION
)

st.set_page_config(
    page_title="ClinicIQ | Clinic Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# No API key input: the engine runs in sandbox mode.
api_key_input = ""

# ---------------------------------------------------------
# Theme: one palette (navy + teal + neutral greys), high-contrast text
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --primary: #0E7C7B;
        --primary-dark: #0A5F5E;
        --primary-soft: #E6F4F3;
        --primary-line: #BFE0DE;
        --navy: #0F1F2E;
        --text: #14202E;
        --muted: #455567;
        --line: #DDE3EA;
        --bg: #F6F8FA;
        --card: #FFFFFF;
    }

    .stApp, .stMarkdown, button, input, textarea, label, h1, h2, h3, h4, p {
        font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
    }
    .stApp { background: var(--bg); }
    [data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }
    .main .block-container { max-width: 1280px; padding-top: 1.5rem; padding-bottom: 4rem; }

    /* ---- Text: always dark and readable ---- */
    .stApp p, .stApp li, .stApp span, .stApp label, .stApp div { color: var(--text); }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 { color: var(--navy); font-weight: 700; letter-spacing: -0.01em; }
    .stApp p, .stApp li { font-size: 0.97rem; line-height: 1.55; }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: var(--muted) !important; font-size: 0.88rem; }
    a { color: var(--primary-dark) !important; font-weight: 600; text-decoration: none; }
    a:hover { text-decoration: underline; }
    code { color: var(--primary-dark) !important; background: var(--primary-soft) !important; }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid var(--line); }
    .brand { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.03em; color: var(--navy); }
    .brand span { color: var(--primary); }
    .brand-sub { font-size: 0.85rem; color: var(--muted); }
    .side-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--primary-dark); margin: 6px 0 6px; }
    .side-role { font-size: 1rem; font-weight: 700; color: var(--navy); }
    .side-org { font-size: 0.88rem; color: var(--muted); margin-top: 2px; }
    .stack-chip {
        display: inline-block; padding: 4px 10px; margin: 0 6px 6px 0; border-radius: 8px;
        background: var(--primary-soft); color: var(--primary-dark) !important;
        font-size: 0.8rem; font-weight: 600; border: 1px solid var(--primary-line);
    }

    /* ---- Hero ---- */
    .hero { background: var(--navy); border-radius: 16px; padding: 26px 30px; margin-bottom: 1.25rem; }
    .hero .hero-tag { color: #7FD6D2 !important; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
    .hero .hero-title { color: #FFFFFF !important; font-size: 2rem; font-weight: 800; letter-spacing: -0.03em; }
    .hero .hero-sub { color: #D5DEE8 !important; font-size: 1rem; margin-top: 4px; }

    /* ---- Metrics ---- */
    [data-testid="stMetric"] { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color: var(--muted) !important; font-size: 0.85rem; font-weight: 600; }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * { color: var(--navy) !important; font-size: 1.8rem; font-weight: 800; }

    /* ---- Top navigation ---- */
    .st-key-page_navigation div[role="radiogroup"] {
        gap: 4px; background: #fff; border: 1px solid var(--line);
        padding: 4px; border-radius: 12px; width: fit-content; flex-wrap: wrap;
    }
    .st-key-page_navigation label { padding: 8px 18px; border-radius: 9px; border: 0; background: transparent; cursor: pointer; margin: 0; }
    .st-key-page_navigation label > div:first-child { display: none; }
    .st-key-page_navigation label p { font-weight: 600; font-size: 0.92rem; color: var(--text); }
    .st-key-page_navigation label:hover { background: var(--primary-soft); }
    .st-key-page_navigation label:has(input:checked) { background: var(--primary); }
    .st-key-page_navigation label:has(input:checked) p { color: #FFFFFF !important; }

    /* ---- Section headings ---- */
    .section-title { font-size: 1.4rem; font-weight: 800; color: var(--navy); letter-spacing: -0.02em; margin: 1.1rem 0 0.15rem; }
    .section-caption { color: var(--muted); font-size: 0.95rem; margin-bottom: 1rem; }

    /* ---- Cards ---- */
    [data-testid="stVerticalBlockBorderWrapper"] { background: var(--card); border-radius: 14px; }
    [data-testid="stVerticalBlockBorderWrapper"] > div { border-color: var(--line) !important; }
    .clinic-name { font-size: 1.2rem; font-weight: 800; color: var(--navy); margin-bottom: 4px; }
    .clinic-meta { color: var(--muted); font-size: 0.92rem; line-height: 1.65; }
    .clinic-meta b { color: var(--text); font-weight: 600; }
    .kv-label { font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); font-weight: 700; margin-bottom: 2px; }
    .kv-value { font-size: 0.97rem; color: var(--text); font-weight: 500; margin-bottom: 12px; }
    .opportunity { background: var(--primary-soft); border: 1px solid var(--primary-line); border-radius: 10px; padding: 10px 12px; font-size: 0.9rem; color: var(--primary-dark); }
    .opportunity b { color: var(--primary-dark); }

    /* ---- Badges: two tones only ---- */
    .pill { display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; margin: 8px 6px 0 0; }
    .pill-main { background: var(--primary-soft); color: var(--primary-dark); border: 1px solid var(--primary-line); }
    .pill-neutral { background: #EEF1F5; color: var(--muted); border: 1px solid var(--line); }
    .status { font-size: 0.82rem; font-weight: 700; padding: 4px 11px; border-radius: 8px; background: #EEF1F5; color: var(--text); display: inline-block; }
    .status-high { background: var(--primary); color: #FFFFFF !important; }

    /* ---- Buttons ---- */
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 10px; border: 1px solid var(--line); background: #fff;
        font-weight: 600; font-size: 0.9rem; padding: 0.5rem 1rem; transition: all .15s ease;
    }
    div.stButton > button p, div.stDownloadButton > button p { color: var(--navy) !important; font-weight: 600; }
    div.stButton > button:hover, div.stDownloadButton > button:hover { border-color: var(--primary); background: var(--primary-soft); }
    div.stButton > button[kind="primary"] { background: var(--primary); border: 0; }
    div.stButton > button[kind="primary"] p { color: #FFFFFF !important; }
    div.stButton > button[kind="primary"]:hover { background: var(--primary-dark); }

    /* ---- Inputs ---- */
    [data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {
        border-radius: 10px; border: 1px solid #C9D2DC; background: #FFFFFF;
    }
    input, textarea, [data-baseweb="select"] div { color: var(--text) !important; }
    input::placeholder, textarea::placeholder { color: #6B7A8A !important; }
    [data-testid="stWidgetLabel"] p { font-weight: 600; font-size: 0.9rem; color: var(--navy) !important; }

    /* ---- Tabs / expanders ---- */
    [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
    [data-baseweb="tab"] p { font-weight: 600; color: var(--muted); }
    [aria-selected="true"][data-baseweb="tab"] p { color: var(--primary-dark) !important; }
    [data-testid="stExpander"] { background: #fff; border: 1px solid var(--line); border-radius: 12px; }

    /* ---- Alerts: one neutral teal style (no mixed colours) ---- */
    [data-testid="stAlert"] { background: var(--primary-soft); border: 1px solid var(--primary-line); border-radius: 12px; }
    [data-testid="stAlert"] * { color: #0A3F3E !important; }

    hr { border-color: var(--line); margin: 1rem 0; }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
        /* ---- Inputs, dropdowns and menus: force white background + dark text ---- */
    [data-baseweb="select"] > div,
    [data-baseweb="input"],
    [data-baseweb="input"] > div,
    [data-baseweb="base-input"],
    [data-baseweb="textarea"],
    [data-baseweb="textarea"] > div,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #14202E !important;
        -webkit-text-fill-color: #14202E !important;
        border-color: #C9D2DC !important;
    }

    /* Selected value and typed text */
    [data-baseweb="select"] *,
    [data-baseweb="select"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        color: #14202E !important;
        -webkit-text-fill-color: #14202E !important;
        opacity: 1 !important;
    }

    /* Placeholders: clearly visible grey */
    input::placeholder,
    textarea::placeholder,
    [data-baseweb="select"] input::placeholder {
        color: #5B6B7C !important;
        -webkit-text-fill-color: #5B6B7C !important;
        opacity: 1 !important;
    }

    /* Dropdown arrow icon */
    [data-baseweb="select"] svg { fill: #455567 !important; color: #455567 !important; }

    /* Dropdown menu (opens in a separate popover layer) */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    ul[role="listbox"],
    div[role="listbox"] {
        background-color: #FFFFFF !important;
        color: #14202E !important;
        border: 1px solid #DDE3EA;
        border-radius: 10px;
    }
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li,
    li[role="option"],
    div[role="option"] {
        background-color: #FFFFFF !important;
        color: #14202E !important;
        -webkit-text-fill-color: #14202E !important;
    }
    [data-baseweb="popover"] li *,
    li[role="option"] *,
    div[role="option"] * {
        color: #14202E !important;
        -webkit-text-fill-color: #14202E !important;
    }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    div[role="option"]:hover,
    div[role="option"][aria-selected="true"] {
        background-color: #E6F4F3 !important;
    }

    /* Disabled inputs stay readable */
    input:disabled, textarea:disabled {
        -webkit-text-fill-color: #455567 !important;
        color: #455567 !important;
    }
        /* ===== FINAL OVERRIDE: force light inputs everywhere ===== */
    :root, html, body, .stApp { color-scheme: light !important; }

    html body .stApp [data-baseweb="select"],
    html body .stApp [data-baseweb="select"] div,
    html body .stApp [data-baseweb="input"],
    html body .stApp [data-baseweb="input"] div,
    html body .stApp [data-baseweb="base-input"],
    html body .stApp [data-baseweb="textarea"],
    html body .stApp [data-baseweb="textarea"] div,
    html body .stApp input,
    html body .stApp textarea {
        background-color: #FFFFFF !important;
        color: #14202E !important;
        -webkit-text-fill-color: #14202E !important;
        opacity: 1 !important;
    }

    html body .stApp [data-baseweb="select"] > div {
        border: 1px solid #C9D2DC !important;
        border-radius: 10px !important;
    }

    /* Placeholder text inside inputs */
    html body .stApp input::placeholder,
    html body .stApp textarea::placeholder {
        color: #5B6B7C !important;
        -webkit-text-fill-color: #5B6B7C !important;
        opacity: 1 !important;
    }

    /* Arrow icon */
    html body .stApp [data-baseweb="select"] svg {
        fill: #455567 !important;
        color: #455567 !important;
    }

    /* Open dropdown list (rendered outside .stApp, so no .stApp prefix) */
    html body [data-baseweb="popover"],
    html body [data-baseweb="popover"] div,
    html body [data-baseweb="menu"],
    html body [data-baseweb="menu"] div,
    html body ul[role="listbox"],
    html body li[role="option"],
    html body li[role="option"] div {
        background-color: #FFFFFF !important;
        color: #14202E !important;
        -webkit-text-fill-color: #14202E !important;
    }
    html body li[role="option"]:hover,
    html body li[role="option"]:hover div,
    html body li[aria-selected="true"],
    html body li[aria-selected="true"] div {
        background-color: #E6F4F3 !important;
    }

    /* Caption text like "6 practice(s)" */
    html body .stApp [data-testid="stCaptionContainer"],
    html body .stApp [data-testid="stCaptionContainer"] * {
        color: #455567 !important;
        opacity: 1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------
if "clinics" not in st.session_state:
    st.session_state.clinics = INITIAL_CLINICS.copy()
if "selected_clinic_id" not in st.session_state:
    st.session_state.selected_clinic_id = "GP-QLD-001"
if "generated_email" not in st.session_state:
    st.session_state.generated_email = None

PAGE_DIRECTORY = "Directory"
PAGE_SCRAPING = "Data Ingestion"
PAGE_OUTREACH = "Outreach Engine"
PAGE_PROMPTS = "Prompt Lab"
PAGE_ANALYTICS = "Analytics"
PAGES = [PAGE_DIRECTORY, PAGE_SCRAPING, PAGE_OUTREACH, PAGE_PROMPTS, PAGE_ANALYTICS]

if "page_navigation" not in st.session_state:
    st.session_state.page_navigation = PAGE_DIRECTORY


def open_outreach_for_clinic(clinic_id):
    st.session_state.selected_clinic_id = clinic_id
    st.session_state.page_navigation = PAGE_OUTREACH


def is_seven_day(clinic):
    return "7 Day" in clinic.get("operating_hours", "") or "7 Day" in clinic.get("clinic_name", "")


def section(title, caption=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-caption">{caption}</div>', unsafe_allow_html=True)


def kv(label, value):
    st.markdown(f'<div class="kv-label">{label}</div><div class="kv-value">{value}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# Sidebar: brand, role, tech stack, region
# ---------------------------------------------------------
st.sidebar.markdown('<div class="brand">Clinic<span>IQ</span></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="brand-sub">Clinic intelligence platform</div>', unsafe_allow_html=True)
st.sidebar.divider()

st.sidebar.markdown(
    '<div class="side-label">Role</div>'
    '<div class="side-role">AI Growth &amp; Automation Associate</div>'
    '<div class="side-org">Gokul Infocare Pty Ltd / Robina 7 Day Doctors</div>',
    unsafe_allow_html=True
)
st.sidebar.write("")
st.sidebar.markdown(
    '<div class="side-label">Tech stack</div>'
    '<span class="stack-chip">Python</span>'
    '<span class="stack-chip">Streamlit</span>'
    '<span class="stack-chip">BeautifulSoup</span>'
    '<span class="stack-chip">Pandas</span>'
    '<span class="stack-chip">Prompt Engineering</span>',
    unsafe_allow_html=True
)
st.sidebar.write("")
st.sidebar.markdown(
    '<div class="side-label">Regional focus</div>'
    '<div class="side-org">Queensland (Gold Coast, Robina, Brisbane) and Australian primary care networks.</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Hero + metrics
# ---------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-tag">Australian Primary Care</div>
    <div class="hero-title">ClinicIQ</div>
    <div class="hero-sub">Clinic research, lead intelligence and personalised outreach in one workspace.</div>
</div>
""", unsafe_allow_html=True)

clinics_all = st.session_state.clinics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Practices tracked", len(clinics_all))
m2.metric("High-priority leads", sum(1 for c in clinics_all if c.get("lead_status") == "High Priority"))
m3.metric("Open 7 days", sum(1 for c in clinics_all if is_seven_day(c)))
m4.metric("Telehealth enabled", sum(1 for c in clinics_all if c.get("telehealth_available")))

st.write("")
st.radio("Section", options=PAGES, key="page_navigation", horizontal=True, label_visibility="collapsed")
active_page = st.session_state.page_navigation

# =========================================================
# DIRECTORY
# =========================================================
if active_page == PAGE_DIRECTORY:
    section("Practice directory",
            "Filter and review Australian medical practices for recruitment, automation or partnerships.")

    f1, f2, f3 = st.columns(3)
    with f1:
        state_filter = st.selectbox("State", ["All", "QLD", "NSW", "VIC"])
    with f2:
        billing_filter = st.selectbox("Billing policy", ["All", "Bulk Billing", "Mixed Billing", "Private Billing"])
    with f3:
        search_query = st.text_input("Search", "", placeholder="Clinic name or suburb")

    filtered = st.session_state.clinics
    if state_filter != "All":
        filtered = [c for c in filtered if c.get("state") == state_filter]
    if billing_filter != "All":
        filtered = [c for c in filtered if c.get("billing_type") == billing_filter]
    if search_query:
        q = search_query.lower()
        filtered = [c for c in filtered if q in c.get("clinic_name", "").lower() or q in c.get("suburb", "").lower()]

    st.caption(f"{len(filtered)} practice(s)")

    for clinic in filtered:
        with st.container(border=True):
            left, mid, right = st.columns([4, 3, 2])

            with left:
                b_type = clinic.get("billing_type", "Mixed Billing")
                pills = f'<span class="pill {"pill-main" if b_type == "Bulk Billing" else "pill-neutral"}">{b_type}</span>'
                if is_seven_day(clinic):
                    pills += '<span class="pill pill-main">Open 7 days</span>'
                if clinic.get("telehealth_available"):
                    pills += '<span class="pill pill-neutral">Telehealth</span>'

                st.markdown(
                    f'<div class="clinic-name">{clinic["clinic_name"]}</div>'
                    f'<div class="clinic-meta">{clinic["address"]}<br>'
                    f'<b>{clinic["suburb"]}, {clinic["state"]} {clinic["postcode"]}</b><br>'
                    f'{clinic["phone"]} &nbsp;·&nbsp; <a href="{clinic["website"]}" target="_blank">Website</a>'
                    f'</div>{pills}',
                    unsafe_allow_html=True
                )

            with mid:
                kv("Hours", clinic["operating_hours"])
                kv("Doctors on staff", clinic["doctor_count"])
                st.markdown(
                    f'<div class="opportunity"><b>Opportunity:</b> '
                    f'{clinic.get("growth_opportunity", "Operational expansion")}</div>',
                    unsafe_allow_html=True
                )

            with right:
                status = clinic.get("lead_status", "Qualified")
                s_class = "status status-high" if status == "High Priority" else "status"
                st.markdown(f'<div class="kv-label">Lead status</div><span class="{s_class}">{status}</span>',
                            unsafe_allow_html=True)
                st.write("")
                if st.button("AI analysis", key=f"btn_ai_{clinic['id']}", use_container_width=True):
                    with st.spinner("Analysing clinic profile..."):
                        st.session_state[f"analysis_{clinic['id']}"] = analyze_clinic_with_ai(clinic, api_key_input)
                st.button(
                    "Draft outreach",
                    key=f"btn_email_{clinic['id']}",
                    type="primary",
                    use_container_width=True,
                    on_click=open_outreach_for_clinic,
                    args=(clinic["id"],),
                )

            if f"analysis_{clinic['id']}" in st.session_state:
                res = st.session_state[f"analysis_{clinic['id']}"]
                st.divider()
                a1, a2 = st.columns([1, 3])
                with a1:
                    st.metric("Lead score", f"{res.get('lead_score', 90)}/100")
                with a2:
                    st.markdown(f"**Pitch angle:** {res.get('recommended_pitch_angle', 'Recruitment')}")
                    st.write(res.get("score_reasoning", ""))
                    gaps = res.get("identified_gaps", [])
                    if gaps:
                        st.caption("Operational gaps: " + ", ".join(gaps))

# =========================================================
# DATA INGESTION
# =========================================================
elif active_page == PAGE_SCRAPING:
    section("Data ingestion",
            "Collect publicly available clinic information from a website, or run the directory simulator.")

    sub_tab1, sub_tab2 = st.tabs(["Clinic URL scraper", "Directory simulator"])

    with sub_tab1:
        col_url, col_btn = st.columns([5, 1])
        with col_url:
            scrape_url_input = st.text_input(
                "Clinic website URL",
                value="https://www.robina7daydoctors.com",
                key="clinic_scrape_url"
            )
        with col_btn:
            st.write("")
            st.write("")
            scrape_now = st.button("Scrape", key="scrape_clinic_button", type="primary", use_container_width=True)

        if "scraped_data" not in st.session_state:
            st.session_state.scraped_data = None

        if scrape_now:
            with st.spinner(f"Connecting to {scrape_url_input}..."):
                try:
                    result = scrape_clinic_url(scrape_url_input)
                    if result.get("success", False):
                        st.session_state.scraped_data = result
                    else:
                        st.session_state.scraped_data = None
                        st.error("The website could not be scraped.")
                except Exception as e:
                    st.session_state.scraped_data = None
                    st.error(f"Scraping failed: {e}")

        scraped_data = st.session_state.scraped_data

        if scraped_data:
            st.success(scraped_data.get("status_message", "Scraping completed."))

            sc1, sc2 = st.columns(2)
            with sc1:
                with st.container(border=True):
                    st.markdown("#### Extracted details")
                    kv("Name", scraped_data.get("clinic_name", "Not found"))
                    kv("Phone", scraped_data.get("phone", "Not found"))
                    kv("State", scraped_data.get("state", "Not found"))
                    kv("Postcode", scraped_data.get("postcode", "Not found"))
                    kv("Billing model", scraped_data.get("billing_type", "Unknown"))
                    kv("Operating hours", scraped_data.get("operating_hours", "Not found"))
                    kv("Telehealth", "Yes" if scraped_data.get("telehealth_available") else "No")
                    st.caption("Verify against the original website before using in outreach.")
            with sc2:
                with st.container(border=True):
                    st.markdown("#### Raw page content")
                    st.text_area("Cleaned text snippet", value=scraped_data.get("raw_text_snippet", ""),
                                 height=400, key="scraped_text_preview", label_visibility="collapsed")

            st.write("")
            if st.button("Add to intelligence database", key="add_scraped_clinic_button", type="primary"):
                clinics = st.session_state.clinics
                scraped_url = scraped_data.get("url", "").rstrip("/")
                scraped_name = scraped_data.get("clinic_name", "Unknown Medical Practice")

                already_exists = any(
                    c.get("website", "").rstrip("/") == scraped_url
                    or c.get("clinic_name", "").strip().lower() == scraped_name.strip().lower()
                    for c in clinics
                )

                if already_exists:
                    st.warning(f"{scraped_name} is already in the database.")
                else:
                    st.session_state.clinics.append({
                        "id": f"GP-SCRAPED-{len(clinics) + 1:03d}",
                        "clinic_name": scraped_name,
                        "suburb": "Not extracted",
                        "state": scraped_data.get("state", "Unknown"),
                        "postcode": scraped_data.get("postcode", ""),
                        "address": "Not extracted",
                        "phone": scraped_data.get("phone", "Contact via website"),
                        "website": scraped_data.get("url", ""),
                        "billing_type": scraped_data.get("billing_type", "Unknown"),
                        "operating_hours": scraped_data.get("operating_hours", "Not found"),
                        "doctor_count": 0,
                        "telehealth_available": scraped_data.get("telehealth_available", False),
                        "specialties": [],
                        "lead_status": "Needs Review",
                        "growth_opportunity": "Review verified clinic information to identify business opportunities.",
                        "raw_text_snippet": scraped_data.get("raw_text_snippet", "")
                    })
                    st.success(f"Added {scraped_name}. Find it in the Directory.")
        else:
            st.info("Enter a clinic website URL and click Scrape to begin.")

    with sub_tab2:
        st.caption("Demonstration mode: simulated records, not verified directory results.")
        d1, d2 = st.columns([5, 1])
        with d1:
            dir_query = st.text_input("Suburb or region", "Gold Coast", key="directory_search_query",
                                      placeholder="e.g. Robina, Brisbane, Southport")
        with d2:
            st.write("")
            st.write("")
            scan = st.button("Scan", key="scan_directory_button", type="primary", use_container_width=True)

        if scan:
            with st.spinner(f"Generating simulated results for '{dir_query}'..."):
                dir_results = simulate_directory_search(dir_query)
            st.success(f"Generated {len(dir_results)} simulated records for {dir_query}.")
            for d in dir_results:
                with st.expander(f"{d['clinic_name']} — {d['suburb']}, {d['state']}"):
                    st.write(f"**Address:** {d['address']}")
                    st.write(f"**Phone:** {d['phone']}")
                    st.write(f"**Billing:** {d['billing_type']}")
                    st.write(f"**Hours:** {d['operating_hours']}")
                    st.write(f"**Specialties:** {', '.join(d['specialties'])}")

# =========================================================
# OUTREACH
# =========================================================
elif active_page == PAGE_OUTREACH:
    section("Outreach engine",
            "Generate personalised, RACGP-aware outreach tailored to each clinic's bottleneck.")

    clinic_options = {c['id']: f"{c['clinic_name']} ({c['suburb']}, {c['state']})" for c in st.session_state.clinics}
    selected_id = st.selectbox(
        "Target practice",
        options=list(clinic_options.keys()),
        format_func=lambda x: clinic_options[x],
        index=list(clinic_options.keys()).index(st.session_state.selected_clinic_id)
        if st.session_state.selected_clinic_id in clinic_options else 0
    )
    target_clinic = next((c for c in st.session_state.clinics if c['id'] == selected_id),
                         st.session_state.clinics[0])

    o1, o2 = st.columns(2, gap="large")

    with o1:
        with st.container(border=True):
            st.markdown("#### Campaign objective")
            campaign_type = st.radio(
                "Outreach strategy",
                [
                    "GP Recruitment & Locum Roster Coverage (Solve Doctor Shortages)",
                    "AI Front-Desk & Patient Triage Automation (Solve Phone Queues)",
                    "Allied Health & Practice Expansion (Grow Clinic Revenue)"
                ],
                label_visibility="collapsed"
            )

            st.markdown("#### Clinic snapshot")
            kv("Practice", target_clinic["clinic_name"])
            kv("Location", f'{target_clinic["suburb"]}, {target_clinic["state"]} {target_clinic["postcode"]}')
            kv("Billing", target_clinic["billing_type"])
            kv("Hours", target_clinic["operating_hours"])
            st.markdown(
                f'<div class="opportunity"><b>Bottleneck:</b> '
                f'{target_clinic.get("growth_opportunity", "Capacity optimisation")}</div>',
                unsafe_allow_html=True
            )
            st.write("")
            generate_btn = st.button("Generate outreach", type="primary", use_container_width=True)

    with o2:
        with st.container(border=True):
            st.markdown("#### Generated email")

            if generate_btn:
                with st.spinner("Generating tailored outreach..."):
                    st.session_state.generated_email = generate_outreach_email(
                        target_clinic, campaign_type, api_key_input
                    )

            if st.session_state.generated_email:
                res = st.session_state.generated_email
                kv("Subject", res["subject"])
                st.text_area("Email body", res['body'], height=300, label_visibility="collapsed")
                kv("Day 3 follow-up", f"<i>{res['follow_up']}</i>")
                lead_data_json = json.dumps({
                    "target_clinic": target_clinic['clinic_name'],
                    "recipient_role": "Practice Manager",
                    "subject": res['subject'],
                    "body": res['body'],
                    "follow_up": res['follow_up']
                }, indent=2)
                st.download_button("Export CRM payload (JSON)", lead_data_json,
                                   file_name=f"lead_{target_clinic['id']}.json", mime="application/json")
            else:
                st.info("Choose an objective and click Generate outreach.")

# =========================================================
# PROMPT LAB
# =========================================================
elif active_page == PAGE_PROMPTS:
    section("Prompt lab",
            "Prompt architecture, system instructions and iterative refinement behind the outreach engine.")

    p1, p2 = st.columns(2, gap="large")

    with p1:
        with st.container(border=True):
            st.markdown("#### System prompt")
            st.text_area("System prompt", SYSTEM_PROMPT, height=240, label_visibility="collapsed")
            st.markdown("#### Parameter strategy")
            st.markdown("""
- **Temperature 0.3–0.4:** strict adherence to clinic data, minimal marketing fluff.
- **Vocabulary guardrails:** Australian terms (GP, RACGP, MBS, Bulk Billing, Practice Manager).
- **Output format:** `SUBJECT:`, `BODY:`, `FOLLOW_UP_NOTE:` blocks for CRM parsing.
            """)

    with p2:
        with st.container(border=True):
            st.markdown("#### Prompt evolution")
            selected_version = st.selectbox(
                "Prompt iteration", list(PROMPT_EVOLUTION.keys()),
                format_func=lambda k: PROMPT_EVOLUTION[k]['title']
            )
            ver = PROMPT_EVOLUTION[selected_version]
            st.code(ver['prompt'], language="markdown")
            st.markdown("**Results and failure modes**")
            st.warning(ver['failure_mode'])
            st.markdown(f"**Rating:** `{ver['rating']}`")

# =========================================================
# ANALYTICS
# =========================================================
elif active_page == PAGE_ANALYTICS:
    section("Practice analytics", "Aggregated view across tracked practices, with CRM export.")

    df = pd.DataFrame(st.session_state.clinics)

    a1, a2 = st.columns(2, gap="large")
    with a1:
        with st.container(border=True):
            st.markdown("#### Billing model")
            st.bar_chart(df["billing_type"].value_counts(), color="#0E7C7B")
    with a2:
        with st.container(border=True):
            st.markdown("#### By state")
            st.bar_chart(df["state"].value_counts(), color="#0E7C7B")

    st.markdown("#### Database")
    st.dataframe(
        df[["id", "clinic_name", "suburb", "state", "billing_type", "operating_hours", "doctor_count", "lead_status"]],
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="Download lead intelligence (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="australian_gp_leads.csv",
        mime="text/csv",
    )