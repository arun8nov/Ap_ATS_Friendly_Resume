import sys
import os

# Add project root to path so agent imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from backend.agents.jd_extractor import extract_jd_keywords
from backend.agents.resume_comparator import compare_resume_to_jd
from backend.agents.project_selector import select_best_projects
from backend.agents.latex_writer import rewrite_resume_latex

st.set_page_config(page_title="ATS Resume Builder", layout="wide")

st.title("ATS Resume Builder")
st.markdown("Paste your Job Description below to generate a new LaTeX resume.")

jd_text = st.text_area("Job Description", height=200)

col1, col2 = st.columns(2)

if "latex_output" not in st.session_state:
    st.session_state.latex_output = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "projects_selected" not in st.session_state:
    st.session_state.projects_selected = None

with col1:
    if st.button("Analyze JD", use_container_width=True):
        if not jd_text.strip():
            st.error("Please paste a Job Description first.")
        else:
            with st.spinner("Extracting keywords from JD..."):
                jd_keywords = extract_jd_keywords(jd_text)
            with st.spinner("Comparing with your resume..."):
                gaps = compare_resume_to_jd(jd_keywords)
            st.session_state.analysis_result = {"keywords": jd_keywords, "gaps": gaps}
            st.success("Analysis complete!")

with col2:
    if st.button("Generate Resume", type="primary", use_container_width=True):
        if not jd_text.strip():
            st.error("Please paste a Job Description first.")
        else:
            with st.spinner("Step 1/4 — Extracting JD keywords..."):
                jd_keywords = extract_jd_keywords(jd_text)
            with st.spinner("Step 2/4 — Selecting best projects..."):
                selected_projects = select_best_projects(jd_text)
            with st.spinner("Step 3/4 — Comparing resume with JD..."):
                gap_report = compare_resume_to_jd(jd_keywords)
            with st.spinner("Step 4/4 — Writing new LaTeX resume..."):
                new_latex = rewrite_resume_latex(gap_report, selected_projects)

            st.session_state.latex_output = new_latex
            st.session_state.projects_selected = selected_projects
            st.session_state.analysis_result = {"keywords": jd_keywords, "gaps": gap_report}
            st.success("Resume generation complete!")

if st.session_state.analysis_result:
    st.divider()
    res = st.session_state.analysis_result
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Keywords found")
        keywords = res.get("keywords", {})
        if isinstance(keywords, dict) and "error" not in keywords:
            for key, val_list in keywords.items():
                if val_list and isinstance(val_list, list):
                    st.write(f"**{key}**: " + ", ".join(val_list))
        else:
            st.json(keywords, expanded=False)

    with colB:
        st.subheader("Gaps in your Resume")
        gaps = res.get("gaps", {})
        if isinstance(gaps, dict) and "error" not in gaps:
            for key, val_list in gaps.items():
                if val_list and isinstance(val_list, list):
                    st.write(f"**{key}**: " + ", ".join(str(v) for v in val_list))
        else:
            st.json(gaps, expanded=False)

if st.session_state.projects_selected:
    st.divider()
    st.subheader("Projects Selected")
    for proj in st.session_state.projects_selected:
        if isinstance(proj, dict):
            name = proj.get('name', '')
            link = proj.get('link', '')
            desc = proj.get('description', '')
            st.markdown(f"- **{name}** ([link]({link})): {desc}")
        elif isinstance(proj, str):
            st.markdown(f"- {proj}")

if st.session_state.latex_output:
    st.divider()
    st.subheader("New Resume LaTeX (copy this)")
    st.code(st.session_state.latex_output, language="latex")
