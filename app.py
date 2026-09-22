import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from src.parser import load_all, load_guide
from src.retrieval import retrieve
from src.llm import answer as llm_answer, themes as llm_themes
from src.analysis import fallback_answer, fallback_themes

load_dotenv()

st.set_page_config(
    page_title="Hasamex AI Research Assistant",
    page_icon="🔎",
    layout="wide",
)

@st.cache_data
def load_data():
    chunks = load_all("data")
    guide = load_guide("data/Interview_Guide.txt")
    return chunks, guide

chunks, guide = load_data()

st.title("🔎 Hasamex — Robotic Surgery Market Intelligence")
st.caption("Evidence-grounded analysis of three expert interviews | France • Germany • UK")

with st.sidebar:
    st.header("Project")
    st.write("Technical case: analyse expert-call transcripts, preserve traceability, and support cross-transcript Q&A.")
    api_status = "Connected" if os.getenv("OPENAI_API_KEY") else "Demo / fallback mode"
    st.metric("AI status", api_status)
    st.divider()
    st.write(f"**Transcripts:** {len({c['source_file'] for c in chunks})}")
    st.write(f"**Evidence segments:** {len(chunks)}")
    st.write(f"**Interview-guide questions:** {len(guide)}")

tabs = st.tabs(["Interview Guide", "Themes & Differences", "Ask Across Transcripts", "Evidence Explorer", "Architecture"])

with tabs[0]:
    st.subheader("Interview-guide answers")
    q = st.selectbox("Select a question", guide)
    evidence = retrieve(q, chunks, k=6)
    if st.button("Generate evidence-grounded answer", type="primary"):
        with st.spinner("Retrieving evidence and generating answer..."):
            ai = llm_answer(q, evidence)
            answer = ai if ai else fallback_answer(q, evidence)
        st.markdown("### Answer")
        st.write(answer)

        st.markdown("### Supporting evidence")
        for c in evidence[:4]:
            with st.expander(f"{c['market']} · {c['expert']} · {c['timestamp']}"):
                st.markdown(f"**Speaker:** {c['speaker']}")
                st.markdown(f"> {c['text']}")
                st.caption(f"Source: {c['source_file']} | Timestamp: {c['timestamp']}")

with tabs[1]:
    st.subheader("Common themes and differences")
    if st.button("Analyse all three interviews", type="primary"):
        with st.spinner("Comparing transcript evidence..."):
            ai = llm_themes(chunks)
            report = ai if ai else fallback_themes(chunks)
        st.markdown(report)
        st.info("The comparison is based only on the three supplied interviews; it is not presented as an independently verified market study.")
    else:
        st.write("Click the button to generate a cross-transcript analysis.")

with tabs[2]:
    st.subheader("Ask a question across all transcripts")
    q = st.text_area(
        "Question",
        placeholder="e.g. What are the main barriers to adoption across the three interviews?",
        height=100,
    )
    if st.button("Ask", type="primary", disabled=not q.strip()):
        evidence = retrieve(q, chunks, k=8)
        with st.spinner("Searching transcript evidence..."):
            ai = llm_answer(q, evidence)
            answer = ai if ai else fallback_answer(q, evidence)
        st.markdown("### Answer")
        st.write(answer)
        st.markdown("### Sources used")
        for c in evidence:
            st.write(f"- **{c['market']} — {c['expert']} — {c['timestamp']}**")

with tabs[3]:
    st.subheader("Evidence Explorer")
    market = st.selectbox("Filter by market", ["All", "France", "Germany", "United Kingdom"])
    query = st.text_input("Search transcript text", placeholder="e.g. training, ROI, utilisation")
    filtered = chunks if market == "All" else [c for c in chunks if c["market"] == market]
    if query.strip():
        filtered = retrieve(query, filtered, k=20)
    for c in filtered:
        with st.expander(f"{c['market']} · {c['timestamp']} · {c['expert']}"):
            st.write(c["text"])
            st.caption(f"{c['speaker']} | {c['source_file']} | {c['timestamp']}")

with tabs[4]:
    st.subheader("Architecture")
    st.code(
"""Transcript files
      ↓
Parser
      ↓
Evidence chunks + metadata
(country / expert / timestamp / speaker)
      ↓
Transparent retrieval
      ↓
LLM synthesis
      ↓
Answer + independently displayed source evidence

Hallucination controls:
• Only retrieved transcript evidence is supplied to the model
• Exact quotes come directly from source chunks
• Expert, market and timestamp metadata are retained
• No-answer path when evidence is insufficient
• Cross-market analysis is explicitly framed as interview evidence""",
        language="text",
    )
    st.markdown("### Scaling to 30+ transcripts")
    st.write(
        "For a larger corpus, replace the transparent lexical retriever with an embedding/vector index, "
        "keep the same metadata model, add metadata filters, and retrieve a small evidence set before LLM synthesis."
    )
    st.markdown("### AI disclosure")
    st.write(
        "AI tools may be used during development for coding support, debugging, and implementation discussion. "
        "The submitted candidate should disclose the actual tools used, review the implementation, test it, and be able to explain it."
    )
