"""
Streamlit App for Mutual Fund FAQ Assistant

Provides a direct UI for the RAG pipeline to be deployed on Streamlit Community Cloud.
"""

import streamlit as st
import time

from src.query.intent_classifier import classify_intent
from src.query.retrieval import retrieve_chunks
from src.query.prompt_builder import build_prompt
from src.query.llm_client import call_llm
from src.query.response_formatter import format_response
from src.query.refusal_handler import generate_refusal

# --- Page Config ---
st.set_page_config(
    page_title="FundGuide",
    page_icon="🛡️",
    layout="centered"
)

# --- Custom Styling to match the brand somewhat ---
st.markdown("""
    <style>
    .stApp {
        background-color: #F9FAFB;
    }
    .disclaimer-box {
        background-color: #FEFBE8;
        border: 1px solid #FEF08A;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .disclaimer-text {
        color: #A16207;
        margin: 0;
        font-size: 14px;
    }
    .disclaimer-title {
        color: #A16207;
        font-weight: bold;
        margin: 0 0 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🛡️ FundGuide")
st.markdown("""
<div class="disclaimer-box">
    <p class="disclaimer-title">Facts-only. No investment advice.</p>
    <p class="disclaimer-text">This assistant only provides factual information retrieved from official public sources. It does not provide personalized recommendations or advisory services.</p>
</div>
""", unsafe_allow_html=True)

st.write("Ask factual questions about selected HDFC Mutual Fund schemes.")

# --- Helper functions ---
def submit_query(q):
    with st.chat_message("user"):
        st.write(q)
    
    with st.chat_message("assistant"):
        with st.spinner("Searching official sources..."):
            try:
                # 1. Classify Intent
                intent = classify_intent(q)
                
                # 2. Check Advisory/OOS
                if intent != "FACTUAL":
                    refusal = generate_refusal(q, intent)
                    st.error("🛡️ **Cannot Answer**")
                    st.write(refusal["data"]["answer"])
                    if refusal["data"]["source_url"]:
                        st.markdown(f"[Visit AMFI Website]({refusal['data']['source_url']})")
                    return
                
                # 3. Retrieve
                chunks = retrieve_chunks(q)
                
                # 4. Generate
                sys_prompt, user_prompt = build_prompt(q, chunks)
                raw_ans = call_llm(sys_prompt, user_prompt)
                
                # 5. Format
                res = format_response(raw_ans, chunks, intent)
                data = res["data"]
                
                # Display success
                st.success("✅ **Factual Answer**")
                
                # Highlight large percentages if found
                import re
                percent_match = re.search(r'(\d+\.\d+%)', data["answer"])
                if percent_match:
                    st.markdown(f"<h1 style='color: #1D4ED8; margin:0;'>{percent_match.group(1)}</h1>", unsafe_allow_html=True)
                    st.write(data["answer"].replace(percent_match.group(1), "").strip())
                else:
                    st.write(data["answer"])
                
                st.caption(f"🔗 Source: [{data['source_url']}]({data['source_url']})")
                st.caption(f"🕒 Last Updated: {data['last_updated']}")
                
            except Exception as e:
                st.error("System Error: Unable to process request. Check API configuration.")
                st.exception(e)

# --- Sample Pills (Streamlit native columns/buttons) ---
st.write("**Examples:**")
cols = st.columns(3)
if cols[0].button("Expense ratio of HDFC Large Cap?"):
    st.session_state.query = "What is the expense ratio of HDFC Large Cap Fund?"
if cols[1].button("Minimum SIP amount?"):
    st.session_state.query = "What is the minimum SIP amount?"
if cols[2].button("Exit load for HDFC Small Cap?"):
    st.session_state.query = "What is the exit load for HDFC Small Cap Fund?"

# --- Chat Input ---
prompt = st.chat_input("Ask a question...")

if "query" in st.session_state and st.session_state.query:
    q = st.session_state.query
    st.session_state.query = "" # reset
    submit_query(q)
elif prompt:
    submit_query(prompt)
