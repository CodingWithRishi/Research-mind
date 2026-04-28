import time
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain


st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

STEPS = ["search", "reader", "writer", "critic"]


def inject_styles() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}
.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 3rem; max-width: 1200px; }

.hero { text-align: center; padding: 3rem 0 2rem; }
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    margin: 0 0 1rem;
    color: #f0ebe0;
}
.hero h1 span { color: #ff8c32; }
.hero-sub {
    font-size: 1.03rem;
    font-weight: 300;
    color: #a09890;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.65;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 1.7rem 0 1.6rem;
}
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0ebe0;
    margin: 0 0 1rem;
}
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px;
    padding: 1.7rem 1.9rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
}
.chip {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    font-size: 0.75rem;
    color: #a09890;
    margin: 0.2rem 0.2rem 0 0;
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important;
    color: #111111 !important;
    padding: 0.74rem 1rem !important;
}
.stTextInput > div > div > input::placeholder {
    color: #2d2d2d !important;
    opacity: 0.75 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 1.5rem !important;
    width: 100%;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
}

.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.9rem;
    position: relative;
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.06);
}
.step-card.active {
    border-color: rgba(255,140,50,0.4);
    background: rgba(255,140,50,0.04);
}
.step-card.active::before { background: #ff8c32; }
.step-card.done {
    border-color: rgba(80,200,120,0.3);
    background: rgba(80,200,120,0.03);
}
.step-card.done::before { background: #50c878; }
.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    color: #ff8c32;
    opacity: 0.8;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #f0ebe0;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
}
.status-waiting { color: #696157; }
.status-running { color: #ff8c32; }
.status-done { color: #50c878; }
.step-desc {
    font-size: 0.82rem;
    color: #7f776e;
    margin-top: 0.35rem;
}

.panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 0.8rem;
}
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #605850;
    text-align: center;
    margin-top: 2rem;
    letter-spacing: 0.08em;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "results": {},
        "running": False,
        "done": False,
        "current_step_index": 0,
        "topic_input": "",
        "last_topic": "",
        "run_started_at": "",
        "error": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_all() -> None:
    st.session_state.results = {}
    st.session_state.running = False
    st.session_state.done = False
    st.session_state.current_step_index = 0
    st.session_state.last_topic = ""
    st.session_state.run_started_at = ""
    st.session_state.error = ""


def render_hero() -> None:
    st.markdown(
        """
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, reading, writing,
        and critiquing — to produce a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
        """,
        unsafe_allow_html=True,
    )


def status_for(step: str) -> str:
    completed = st.session_state.results.keys()
    if step in completed:
        return "done"
    if st.session_state.running:
        current = STEPS[st.session_state.current_step_index]
        if step == current:
            return "running"
    return "waiting"


def render_step_card(num: str, title: str, state: str, desc: str) -> None:
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("RUNNING", "status-running"),
        "done": ("DONE", "status-done"),
    }
    label, cls = status_map[state]
    card_cls = "active" if state == "running" else ("done" if state == "done" else "")
    st.markdown(
        f"""
<div class="step-card {card_cls}">
    <div class="step-header">
        <span class="step-num">{num}</span>
        <span class="step-title">{title}</span>
        <span class="step-status {cls}">{label}</span>
    </div>
    <div class="step-desc">{desc}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_input_column() -> tuple[bool, bool]:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        disabled=st.session_state.running,
    )
    col_run, col_reset = st.columns(2)
    with col_run:
        run_clicked = st.button("Run Research Pipeline", use_container_width=True, disabled=st.session_state.running)
    with col_reset:
        reset_clicked = st.button("Reset", use_container_width=True, disabled=st.session_state.running)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
<div style="font-family:'DM Mono', monospace;font-size:0.68rem;color:#6f665d;letter-spacing:0.1em;margin-bottom:0.4rem;">TRY</div>
<span class="chip">LLM agents 2026</span>
<span class="chip">CRISPR gene editing</span>
<span class="chip">Fusion energy progress</span>
        """,
        unsafe_allow_html=True,
    )
    return run_clicked, reset_clicked


def render_pipeline_column() -> None:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)
    render_step_card("01", "Search Agent", status_for("search"), "Gathers recent web information")
    render_step_card("02", "Reader Agent", status_for("reader"), "Scrapes and extracts deeper source content")
    render_step_card("03", "Writer Chain", status_for("writer"), "Drafts a structured research report")
    render_step_card("04", "Critic Chain", status_for("critic"), "Reviews, scores, and suggests improvements")

    if st.session_state.last_topic:
        st.caption(f"Topic: {st.session_state.last_topic}")
    if st.session_state.run_started_at:
        st.caption(f"Started: {st.session_state.run_started_at}")


def run_current_step() -> None:
    step = STEPS[st.session_state.current_step_index]
    topic = st.session_state.last_topic
    results = dict(st.session_state.results)

    if step == "search":
        with st.spinner("Search Agent is working..."):
            agent = build_search_agent()
            response = agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
            })
            results["search"] = response["messages"][-1].content

    elif step == "reader":
        with st.spinner("Reader Agent is scraping top resources..."):
            agent = build_reader_agent()
            response = agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic}', "
                    "pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                )]
            })
            results["reader"] = response["messages"][-1].content

    elif step == "writer":
        with st.spinner("Writer Chain is drafting the report..."):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic,
                "research": research_combined,
            })

    elif step == "critic":
        with st.spinner("Critic Chain is reviewing the report..."):
            results["critic"] = critic_chain.invoke({"report": results["writer"]})

    st.session_state.results = results
    st.session_state.current_step_index += 1

    if st.session_state.current_step_index >= len(STEPS):
        st.session_state.running = False
        st.session_state.done = True
        st.session_state.current_step_index = 0


def handle_run_actions(run_clicked: bool, reset_clicked: bool) -> None:
    if reset_clicked:
        reset_all()
        st.rerun()

    if run_clicked:
        topic = st.session_state.topic_input.strip()
        if not topic:
            st.warning("Please enter a research topic first.")
            return
        st.session_state.results = {}
        st.session_state.error = ""
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.current_step_index = 0
        st.session_state.last_topic = topic
        st.session_state.run_started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()

    if st.session_state.running:
        try:
            run_current_step()
            time.sleep(0.15)
            st.rerun()
        except Exception as exc:
            st.session_state.error = str(exc)
            st.session_state.running = False
            st.session_state.done = False


def copy_report_button(report: str) -> None:
    if st.button("Copy Report", use_container_width=True):
        escaped = report.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        components.html(
            f"""
            <script>
            navigator.clipboard.writeText(`{escaped}`);
            </script>
            """,
            height=0,
        )
        st.success("Report copied to clipboard.")


def render_results() -> None:
    r = st.session_state.results
    if not r:
        return

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("Search Results (raw)", expanded=False):
            st.code(r["search"], language="text")

    if "reader" in r:
        with st.expander("Scraped Content (raw)", expanded=False):
            st.code(r["reader"], language="text")

    if "writer" in r:
        st.markdown(
            """
<div class="panel">
    <div class="panel-title">Final Research Report</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(r["writer"])
        actions_left, actions_right = st.columns(2)
        with actions_left:
            st.download_button(
                label="Download Report (.md)",
                data=r["writer"],
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with actions_right:
            copy_report_button(r["writer"])

    if "critic" in r:
        st.markdown(
            """
<div class="panel">
    <div class="panel-title">Critic Feedback</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(r["critic"])


def render_footer() -> None:
    st.markdown(
        """
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    init_state()
    render_hero()

    col_input, _, col_pipeline = st.columns([5, 0.4, 4])
    with col_input:
        run_clicked, reset_clicked = render_input_column()
    with col_pipeline:
        render_pipeline_column()

    handle_run_actions(run_clicked, reset_clicked)

    if st.session_state.error:
        st.error(f"Pipeline failed: {st.session_state.error}")

    render_results()
    render_footer()


if __name__ == "__main__":
    main()
