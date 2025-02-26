import streamlit as st
import asyncio
from main_agentic import main as generate_full_context

# Set page config at the very top
st.set_page_config(page_title="Stock Analysis", layout="wide")

# Title
st.title("Stock Analysis & Recommendation")

# User input box
user_input = st.text_input(
    "Enter stock-related query (e.g., 'What is the recommendation for IBM based on technical indicators?'):"
)

# Submit button
if st.button("Analyze Stock") and user_input:
    with st.spinner("Fetching data... Please wait."):
        # Run the main processing pipeline
        stock_analysis = asyncio.run(generate_full_context(user_input))

        # Extract relevant data
        stock_data = stock_analysis.get("stock_data", {})
        market_knowledge = stock_analysis.get("market_knowledge", {})
        final_recommendation = stock_analysis.get("final_recommendation", "")

        # --- Display Results ---
        st.subheader("📊 Stock Data")
        if stock_data:
            st.write(stock_data)

        st.subheader("📰 Financial News & Market Knowledge")
        if market_knowledge:
            st.write(market_knowledge)

        st.subheader("🤖 Recommendation Agent Output")
        st.write(stock_analysis.get("recommendation_agent_output", "No output available."))

        # Highlighted LLM Recommendation
        st.markdown("### 🏆 Final GPT-4 Recommendation")
        st.markdown(f"**{final_recommendation}**")
