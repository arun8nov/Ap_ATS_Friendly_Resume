import streamlit as st
import os
from agents import agent_keyword_analyzer, agent_resume_optimizer

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="ATS Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .score-big {
        font-size: 3rem;
        font-weight: 800;
        color: #667eea;
    }
    .status-running {
        color: #f39c12;
        font-weight: 600;
    }
    .status-done {
        color: #2ecc71;
        font-weight: 600;
    }
    .stTextArea textarea {
        font-family: monospace;
        font-size: 0.85rem;
    }
    .keyword-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# LOAD RESUME
# ──────────────────────────────────────────────
def load_resume():
    resume_path = "main.tex"
    if os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    resume_content = load_resume()
    if resume_content:
        st.success("✅ main.tex loaded")
        st.caption(f"Characters: {len(resume_content):,}")
        with st.expander("👁️ Preview Resume LaTeX"):
            st.code(resume_content[:1500] + "\n...[truncated]" if len(resume_content) > 1500 else resume_content, language="latex")
    else:
        st.error("❌ main.tex not found")
        st.caption("Place your main.tex in the project folder")

    st.markdown("---")
    st.markdown("### 🤖 Agents")
    st.markdown("""
    **Agent 1** — Keyword Analyzer  
    Compares JD vs Resume, finds gaps
    
    **Agent 2** — Resume Optimizer  
    Rewrites LaTeX with ATS keywords
    """)
    st.markdown("---")
    st.caption("Model: Qwen3 235B via NVIDIA API")

# ──────────────────────────────────────────────
# MAIN HEADER
# ──────────────────────────────────────────────
st.markdown('<div class="main-header">📄 ATS Resume Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Paste a Job Description → Get an ATS-optimized LaTeX resume in seconds</div>', unsafe_allow_html=True)

if not resume_content:
    st.error("⚠️ Please place your `main.tex` file in the project folder and restart the app.")
    st.stop()

# ──────────────────────────────────────────────
# INPUT SECTION
# ──────────────────────────────────────────────
st.markdown("### 📋 Job Description")
jd_col, info_col = st.columns([3, 1])

with jd_col:
    jd_text = st.text_area(
        "Paste the full Job Description here",
        height=280,
        placeholder="Paste the complete job description here — include responsibilities, requirements, skills, qualifications...",
        key="jd_input",
        label_visibility="collapsed"
    )

with info_col:
    st.markdown("#### 💡 Tips")
    st.markdown("""
    - Paste the **full** JD
    - Include skills & requirements section
    - More detail = better optimization
    """)
    word_count = len(jd_text.split()) if jd_text else 0
    st.metric("Words", word_count)
    if word_count > 50:
        st.success("Good length ✅")
    elif word_count > 0:
        st.warning("Add more detail")

st.markdown("---")

# ──────────────────────────────────────────────
# RUN BUTTON
# ──────────────────────────────────────────────
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

with col_btn1:
    run_all = st.button("🚀 Analyze & Optimize Resume", type="primary", use_container_width=True, disabled=not jd_text.strip())

with col_btn2:
    run_agent1_only = st.button("🔍 Keyword Analysis Only", use_container_width=True, disabled=not jd_text.strip())

with col_btn3:
    if st.button("🗑️ Clear Results", use_container_width=True):
        for key in ["agent1_result", "agent2_result", "optimized_latex"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ──────────────────────────────────────────────
# AGENT 1 EXECUTION
# ──────────────────────────────────────────────
if run_agent1_only or run_all:
    if not jd_text.strip():
        st.warning("Please paste a Job Description first.")
        st.stop()

    st.markdown("---")
    st.markdown("## 🤖 Agent 1 — Keyword Analysis")

    with st.spinner("🔍 Agent 1 is analyzing your resume against the JD..."):
        try:
            result1 = agent_keyword_analyzer(jd_text, resume_content)
            st.session_state["agent1_result"] = result1["raw"]
            st.session_state["jd_snapshot"] = jd_text
        except Exception as e:
            st.error(f"Agent 1 failed: {str(e)}")
            st.stop()

# ──────────────────────────────────────────────
# DISPLAY AGENT 1 RESULTS
# ──────────────────────────────────────────────
if "agent1_result" in st.session_state:
    raw = st.session_state["agent1_result"]

    # Try to extract match score for big display
    score_val = None
    for line in raw.split("\n"):
        if "MATCH SCORE" in line.upper():
            import re
            nums = re.findall(r'\d+', line)
            if nums:
                score_val = int(nums[0])
                break

    # Score display
    if score_val is not None:
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            color = "#2ecc71" if score_val >= 70 else "#f39c12" if score_val >= 40 else "#e74c3c"
            st.markdown(f"""
            <div style="text-align:center; padding: 1rem; background:#1e1e2e; border-radius:12px;">
                <div style="font-size:0.9rem; color:#888;">ATS Match Score</div>
                <div style="font-size:3rem; font-weight:800; color:{color};">{score_val}%</div>
                <div style="color:{color}; font-size:0.85rem;">{'Strong Match' if score_val >= 70 else 'Needs Work' if score_val >= 40 else 'Low Match'}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### 📊 Full Analysis")
    st.markdown(raw)

    # Download agent 1 report
    st.download_button(
        "⬇️ Download Analysis Report",
        data=raw,
        file_name="ats_keyword_analysis.txt",
        mime="text/plain"
    )

# ──────────────────────────────────────────────
# AGENT 2 EXECUTION
# ──────────────────────────────────────────────
if run_all and "agent1_result" in st.session_state:
    st.markdown("---")
    st.markdown("## 🤖 Agent 2 — Resume Optimizer")

    with st.spinner("✍️ Agent 2 is rewriting your resume with ATS keywords..."):
        try:
            result2 = agent_resume_optimizer(
                st.session_state["jd_snapshot"],
                resume_content,
                st.session_state["agent1_result"]
            )
            st.session_state["optimized_latex"] = result2["latex"]
        except Exception as e:
            st.error(f"Agent 2 failed: {str(e)}")
            st.stop()

# ──────────────────────────────────────────────
# DISPLAY AGENT 2 RESULTS
# ──────────────────────────────────────────────
if "optimized_latex" in st.session_state:
    optimized = st.session_state["optimized_latex"]

    st.markdown("### ✅ Optimized LaTeX Resume")

    tab1, tab2 = st.tabs(["📄 LaTeX Code", "🔍 Diff Preview"])

    with tab1:
        st.code(optimized, language="latex")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                "⬇️ Download Optimized main.tex",
                data=optimized,
                file_name="main_optimized.tex",
                mime="text/plain",
                type="primary",
                use_container_width=True
            )
        with dl_col2:
            if st.button("💾 Save as main.tex (overwrite)", use_container_width=True):
                with open("main.tex", "w", encoding="utf-8") as f:
                    f.write(optimized)
                st.success("✅ main.tex saved!")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original**")
            st.text_area("Original LaTeX", value=resume_content, height=500, key="orig_preview")
        with c2:
            st.markdown("**Optimized**")
            st.text_area("Optimized LaTeX", value=optimized, height=500, key="opt_preview")

    st.info("💡 Copy the LaTeX code → paste into Overleaf → compile to PDF")

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.caption("Model: Llama 3.3 Nemotron 49B via NVIDIA API")
