import streamlit as st
import pandas as pd
import asyncio
from main_agentic import main  # Importing the async function
from tools.neo4j_connector import retrieve_knowledge

st.title("Stock Analysis App")

# Main stock symbol query input
stock_symbol = st.text_input(
    "Enter Stock related query e.g. What is the recommendation for IBM based on technical indicators?:", "")

# Knowledge base search bar
knowledge_query = st.text_input("🔍 Search Knowledge Base", "")

async def fetch_stock_analysis(stock_symbol):
    """Run the async main function properly within Streamlit."""
    return await main(stock_symbol)

# async def fetch_knowledge_base(knowledge_query):
#     """Fetch only Neo4j-based market knowledge without checking stock symbols."""
#     from tools.neo4j_connector import retrieve_knowledge  # Ensure correct import
#
#     knowledge_result = retrieve_knowledge(knowledge_query)  # Direct Neo4j call
#     return {"market_knowledge": knowledge_result}

    async def fetch_knowledge_base(knowledge_query):
        """Fetch only Neo4j-based market knowledge and send it to GPT."""
        from tools.neo4j_connector import retrieve_knowledge
        from main_agentic import get_final_recommendation  # Import the function that triggers LLM processing

        # Retrieve knowledge from Neo4j
        knowledge_result = retrieve_knowledge(knowledge_query)

        # Convert Neo4j result into structured input for GPT
        knowledge_text = "\n".join([f"{item['name']}: {item['description']}" for item in knowledge_result])

        # Prepare an empty data dictionary (since no stock info is available)
        data_for_gpt = {
            "stock_data": {},  # Empty stock data
            "news_data": {},  # No news
            "technical_analysis": {},  # No technical indicators
            "neo4j_knowledge": knowledge_text  # Only Neo4j knowledge is available
        }

        # Process with GPT via main_agentic.py
        gpt_response = get_final_recommendation(data_for_gpt)

        return {"market_knowledge": knowledge_result, "gpt_response": gpt_response}

    # Retrieve knowledge from Neo4j
    knowledge_result = retrieve_knowledge(knowledge_query)

    # Convert Neo4j result into formatted text for GPT
    knowledge_text = "\n".join([f"{item['name']}: {item['description']}" for item in knowledge_result])

    # Call GPT with knowledge only (since no stock symbol is provided)
    gpt_response = generate_gpt_recommendation({"neo4j_knowledge": knowledge_text})

    return {"market_knowledge": knowledge_result, "gpt_response": gpt_response}


# If user enters a stock-related query
if stock_symbol:
    st.subheader("Stock Price Analysis")

    with st.spinner("Fetching stock analysis..."):
        result = asyncio.run(fetch_stock_analysis(stock_symbol))

    if result and "error" not in result:
        # Stock Price Data
        st.subheader("Stock Price Data")
        if "stock_data" in result:
            st.dataframe(result["stock_data"].get("price_data", "No stock data available."))

        # Technical Analysis
        st.subheader("Technical Analysis")
        if "stock_data" in result and "technical_analysis" in result["stock_data"]:
            st.dataframe(result["stock_data"]["technical_analysis"])
        else:
            st.write("No technical analysis available.")

        # Financial News
        st.subheader("Latest Financial News")
        if "stock_data" in result and "financial_news" in result["stock_data"]:
            news_data = result["stock_data"]["financial_news"]
            if news_data:
                news_df = pd.DataFrame(news_data, columns=["Title", "URL"])
                st.dataframe(news_df)
            else:
                st.write("No news available.")
        else:
            st.write("No news available.")

        # Market Knowledge Section
        st.subheader("📚 Market Knowledge from Neo4j")
        market_knowledge = result.get("market_knowledge", [])

        if isinstance(market_knowledge, list):
            market_knowledge = [item for item in market_knowledge if item != "No additional market knowledge available."]

        if market_knowledge:
            formatted_knowledge = [
                f"- {item.split(': ', 1)[-1]}" if ": " in item else f"- {item} "
                for item in market_knowledge
            ]
            knowledge_str = "\n".join(formatted_knowledge)
            st.markdown(knowledge_str)
        else:
            st.write("No additional market knowledge available.")

        # Sentiment Analysis
        st.subheader("Sentiment Analysis")
        if "stock_data" in result:
            sentiment_score = result["stock_data"].get("sentiment", "No sentiment data available.")
            st.write(f"Reddit Sentiment Score: {sentiment_score}")

        # Recommendations
        st.subheader("Recommendations")
        st.write(f"**Internal Recommendation:** {result.get('recommendation_agent_output', 'No recommendation')}")
        st.write(f"**GPT Recommendation:** {result.get('final_recommendation', 'No GPT recommendation')}")

    else:
        st.error(result.get("error", "Error fetching data. Please try again."))

# If user enters a knowledge base query
if knowledge_query:
    st.subheader("📚 Market Knowledge Base Results")

    with st.spinner("Fetching market knowledge..."):
        knowledge_result = asyncio.run(retrieve_knowledge(knowledge_query))

    if knowledge_result and "error" not in knowledge_result:
        market_knowledge = knowledge_result.get("market_knowledge", [])

        if isinstance(market_knowledge, list):
            market_knowledge = [item for item in market_knowledge if item != "No additional market knowledge available."]

        if market_knowledge:
            formatted_knowledge = [
                f"- {item.split(': ', 1)[-1]}" if ": " in item else f"- {item} "
                for item in market_knowledge
            ]
            knowledge_str = "\n".join(formatted_knowledge)
            st.markdown(knowledge_str)
        else:
            st.write("No additional market knowledge available.")

    else:
        st.error(knowledge_result.get("error", "Error fetching knowledge. Please try again."))

if not stock_symbol and not knowledge_query:
    st.write("Please enter a stock symbol or search for market knowledge to begin.")
