import streamlit as st
import os
from agents import (
    agent_keyword_analyzer,
    agent_resume_assembler,
    agent_resume_optimizer,
    load_all_resumes
)

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="ATS Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .sub-header { color: #888; font-size: 1rem; margin-bottom: 2rem; }
    .resume-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        border-left: 4px solid #667eea;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
    }
    .agent-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    # Load all resumes
    resumes = load_all_resumes("resumes")

    if resumes:
        st.success(f"✅ {len(resumes)} resume(s) loaded")
        st.markdown("#### 📁 Loaded Resumes")
        for fname, content in resumes.items():
            st.markdown(f"""
            <div class="resume-card">
                📄 <b>{fname}</b><br>
                <span style="color:#888">{len(content):,} chars</span>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"Preview {fname}"):
                st.code(content[:800] + "\n...[truncated]" if len(content) > 800 else content, language="latex")
    else:
        st.warning("⚠️ No resumes found")
        st.caption("Add .tex files to the `resumes/` folder")

    st.markdown("---")
    st.markdown("### 🤖 Pipeline")
    st.markdown("""
    **Agent 1** — Keyword Analyzer  
    Compares JD vs all resumes
    
    **Agent 3** — Resume Assembler  
    Picks best content from all resumes
    
    **Agent 2** — ATS Polisher  
    Final optimization pass
    """)
    st.markdown("---")

    # Upload new resume
    st.markdown("### ➕ Add Resume")
    uploaded = st.file_uploader("Upload a .tex resume", type=["tex"])
    if uploaded:
        save_path = os.path.join("resumes", uploaded.name)
        with open(save_path, "wb") as f:
            f.write(uploaded.read())
        st.success(f"Saved: {uploaded.name}")
        st.rerun()

    st.caption("Model: Llama 3.1 8B via NVIDIA API")

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
st.markdown('<div class="main-header">📄 ATS Resume Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Paste a Job Description → AI assembles the best resume from all your versions → ATS optimized</div>', unsafe_allow_html=True)

if not resumes:
    st.error("⚠️ No resumes found. Add `.tex` files to the `resumes/` folder or upload via sidebar.")
    st.stop()

# ──────────────────────────────────────────────
# JD INPUT
# ──────────────────────────────────────────────
st.markdown("### 📋 Job Description")
jd_col, info_col = st.columns([3, 1])

with jd_col:
    jd_text = st.text_area(
        "Paste JD",
        height=280,
        placeholder="Paste the complete job description here...",
        key="jd_input",
        label_visibility="collapsed"
    )

with info_col:
    st.markdown("#### 💡 Tips")
    st.markdown("- Paste the **full** JD\n- Include skills & requirements\n- More detail = better result")
    word_count = len(jd_text.split()) if jd_text else 0
    st.metric("Words", word_count)
    if word_count > 50:
        st.success("Good length ✅")
    elif word_count > 0:
        st.warning("Add more detail")

st.markdown("---")

# ──────────────────────────────────────────────
# WHICH RESUME TO USE AS BASE
# ──────────────────────────────────────────────
mode = st.radio(
    "Resume source",
    ["🧠 Auto-assemble from ALL resumes (recommended)", "📄 Use a single resume"],
    horizontal=True
)

single_resume = None
if "single" in mode:
    selected = st.selectbox("Select resume", list(resumes.keys()))
    single_resume = resumes[selected]

st.markdown("---")

# ──────────────────────────────────────────────
# BUTTONS
# ──────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    run_all = st.button("🚀 Analyze & Build Resume", type="primary", use_container_width=True, disabled=not jd_text.strip())
with col2:
    run_analysis = st.button("🔍 Keyword Analysis Only", use_container_width=True, disabled=not jd_text.strip())
with col3:
    if st.button("🗑️ Clear", use_container_width=True):
        for k in ["agent1_result", "assembled_latex", "final_latex", "jd_snapshot"]:
            st.session_state.pop(k, None)
        st.rerun()

# ──────────────────────────────────────────────
# AGENT 1
# ──────────────────────────────────────────────
if run_analysis or run_all:
    if not jd_text.strip():
        st.warning("Paste a Job Description first.")
        st.stop()

    st.markdown("---")
    st.markdown("## 🤖 Agent 1 — Keyword Analysis")

    # Use combined text of all resumes for analysis
    combined = "\n\n".join(resumes.values()) if not single_resume else single_resume

    with st.spinner("Analyzing keywords across all resumes..."):
        try:
            r1 = agent_keyword_analyzer(jd_text, combined)
            st.session_state["agent1_result"] = r1["raw"]
            st.session_state["jd_snapshot"] = jd_text
        except Exception as e:
            st.error(f"Agent 1 failed: {e}")
            st.stop()

if "agent1_result" in st.session_state:
    raw = st.session_state["agent1_result"]

    # Extract score
    import re
    score_val = None
    for line in raw.split("\n"):
        if "MATCH SCORE" in line.upper():
            nums = re.findall(r'\d+', line)
            if nums:
                score_val = int(nums[0])
                break

    if score_val is not None:
        s1, s2, s3 = st.columns(3)
        with s1:
            color = "#2ecc71" if score_val >= 70 else "#f39c12" if score_val >= 40 else "#e74c3c"
            st.markdown(f"""
            <div style="text-align:center;padding:1rem;background:#1e1e2e;border-radius:12px;">
                <div style="font-size:0.9rem;color:#888;">ATS Match Score</div>
                <div style="font-size:3rem;font-weight:800;color:{color};">{score_val}%</div>
                <div style="color:{color};font-size:0.85rem;">{'Strong' if score_val>=70 else 'Needs Work' if score_val>=40 else 'Low Match'}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("#### 📊 Analysis")
    st.markdown(raw)
    st.download_button("⬇️ Download Analysis", data=raw, file_name="ats_analysis.txt", mime="text/plain")

# ──────────────────────────────────────────────
# AGENT 3 — ASSEMBLE
# ──────────────────────────────────────────────
if run_all and "agent1_result" in st.session_state:
    st.markdown("---")

    if single_resume:
        # Skip assembly, use selected resume directly
        st.session_state["assembled_latex"] = single_resume
        st.info("📄 Using selected resume directly — skipping assembly.")
    else:
        st.markdown("## 🤖 Agent 3 — Assembling Best Resume from All Versions")
        with st.spinner(f"Reading {len(resumes)} resumes and assembling the best match..."):
            try:
                r3 = agent_resume_assembler(
                    st.session_state["jd_snapshot"],
                    resumes,
                    st.session_state["agent1_result"]
                )
                st.session_state["assembled_latex"] = r3["latex"]
                st.success(f"✅ Assembled from {len(resumes)} resumes")
            except Exception as e:
                st.error(f"Agent 3 failed: {e}")
                st.stop()

# ──────────────────────────────────────────────
# AGENT 2 — FINAL POLISH
# ──────────────────────────────────────────────
if run_all and "assembled_latex" in st.session_state:
    st.markdown("---")
    st.markdown("## 🤖 Agent 2 — Final ATS Polish")

    with st.spinner("Doing final ATS optimization pass..."):
        try:
            r2 = agent_resume_optimizer(
                st.session_state["jd_snapshot"],
                st.session_state["assembled_latex"],
                st.session_state["agent1_result"]
            )
            st.session_state["final_latex"] = r2["latex"]
        except Exception as e:
            st.error(f"Agent 2 failed: {e}")
            st.stop()

# ──────────────────────────────────────────────
# FINAL OUTPUT
# ──────────────────────────────────────────────
if "final_latex" in st.session_state:
    final = st.session_state["final_latex"]
    assembled = st.session_state.get("assembled_latex", "")

    st.markdown("### ✅ Final Optimized Resume")

    tab1, tab2, tab3 = st.tabs(["📄 Final LaTeX", "🔧 Assembled (pre-polish)", "🔍 Side by Side"])

    with tab1:
        st.code(final, language="latex")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Download main.tex", data=final, file_name="main.tex", mime="text/plain", type="primary", use_container_width=True)
        with c2:
            if st.button("💾 Save as main.tex", use_container_width=True):
                with open("main.tex", "w", encoding="utf-8") as f:
                    f.write(final)
                st.success("✅ Saved as main.tex!")

    with tab2:
        st.code(assembled, language="latex")
        st.download_button("⬇️ Download Assembled", data=assembled, file_name="assembled.tex", mime="text/plain")

    with tab3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Assembled**")
            st.text_area("", value=assembled, height=500, key="asm_view")
        with col_b:
            st.markdown("**Final Optimized**")
            st.text_area("", value=final, height=500, key="fin_view")

    st.info("💡 Copy LaTeX → paste into Overleaf → compile to PDF")

st.markdown("---")
st.caption("ATS Resume Optimizer | Multi-Resume Assembly | NVIDIA API")