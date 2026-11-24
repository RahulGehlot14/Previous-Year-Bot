"""
Settings View for Previous Year Question Paper Analyzer.
Configures OpenAI API credentials, model choices, classification engines,
scoring formula parameters, and database management/sample data preloading.
"""

import streamlit as st
import os
from database.db_manager import DatabaseManager
from config import (
    DEFAULT_MODEL,
    AVAILABLE_MODELS,
    FREQUENCY_WEIGHT,
    YEARS_WEIGHT
)
from utils.styling import render_section_header, load_custom_css

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    render_section_header("Settings & Configuration", "Configure AI models, API keys, scoring parameters, and manage database", "⚙️")

    st.markdown("### 🤖 AI Classification Engine & Credentials")

    current_api_key = st.session_state.get("openai_api_key", os.getenv("OPENAI_API_KEY", ""))

    api_key_input = st.text_input(
        "OpenAI API Key",
        value=current_api_key,
        type="password",
        help="Your OpenAI API Key is kept in session memory and never shared or logged publicly."
    )

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        current_model = st.session_state.get("openai_model", DEFAULT_MODEL)
        selected_model = st.selectbox(
            "OpenAI Model",
            options=AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(current_model) if current_model in AVAILABLE_MODELS else 0,
            key="sett_model"
        )
    with col_m2:
        engine_mode = st.selectbox(
            "Classification Mode",
            options=[
                "Automatic (LLM if API Key valid, else Rule-based Demo)",
                "Force Rule-Based Engine (Demo Mode)",
                "Force OpenAI LLM Only"
            ],
            index=0,
            key="sett_engine"
        )

    col_save, col_test = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Settings", type="primary", use_container_width=True, key="btn_save_sett"):
            st.session_state["openai_api_key"] = api_key_input.strip()
            st.session_state["openai_model"] = selected_model
            st.session_state["engine_mode"] = engine_mode
            st.success("Settings saved successfully!")

    with col_test:
        if st.button("🔌 Test OpenAI API Connection", use_container_width=True, key="btn_test_sett"):
            if not api_key_input.strip():
                st.error("Please enter an OpenAI API Key to test.")
            else:
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key_input.strip())
                    response = client.models.list()
                    st.success("✅ Successfully connected to OpenAI API!")
                except Exception as e:
                    st.error(f"❌ OpenAI API connection failed: {str(e)}")

    st.markdown("---")

    st.markdown("### 🎯 Priority Scoring Weights")
    st.markdown("""
    The priority score formula balances topic recurrence frequency with multi-year consistency:  
    `Priority Score = (Topic Frequency / Max Frequency × Weight_Freq) + (Years Appeared / Total Years × Weight_Years)`
    """)

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        f_weight = st.slider("Topic Frequency Weight (%)", min_value=0.0, max_value=100.0, value=float(FREQUENCY_WEIGHT), step=5.0, key="sett_f_weight")
    with col_w2:
        y_weight = st.slider("Years Coverage Weight (%)", min_value=0.0, max_value=100.0, value=float(YEARS_WEIGHT), step=5.0, key="sett_y_weight")

    if (f_weight + y_weight) != 100.0:
        st.warning(f"⚠️ Sum of weights is currently {f_weight + y_weight}%. Typically weights should sum to 100%.")

    st.markdown("---")

    st.markdown("### 🗄️ Database Management")

    kpis = db.get_kpis()
    col_d1, col_d2, col_d3 = st.columns(3)
    col_d1.metric("Total Papers", kpis["total_papers"])
    col_d2.metric("Total Questions", kpis["total_questions"])
    col_d3.metric("Unique Topics", kpis["unique_topics"])

    st.markdown("<br>", unsafe_allow_html=True)
    col_seed, col_clear = st.columns(2)

    with col_seed:
        st.markdown("#### 🧪 Seed Sample Dataset")
        st.caption("Populates the database with real-world synthetic DBMS exam papers from 2022, 2023, and 2024.")
        if st.button("🚀 Load Sample DBMS Question Papers", type="primary", use_container_width=True, key="btn_seed_db_sett"):
            from sample_data.seed_data import seed_sample_database
            with st.spinner("Seeding database..."):
                count = seed_sample_database(db)
                st.success(f"Seeded {count} sample DBMS questions across 3 academic years!")
                st.rerun()

    with col_clear:
        st.markdown("#### ⚠️ Reset Database")
        st.caption("Permanently deletes all uploaded papers, extracted questions, and cached results.")
        if st.button("🗑️ Clear All Database Records", type="secondary", use_container_width=True, key="btn_clear_db_sett"):
            db.clear_all_data()
            st.warning("All records in database have been purged.")
            st.rerun()

if __name__ == "__main__" or True:
    render()
