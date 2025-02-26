import csv
import datetime
from agents.stock_agent import StockAgent  # Ensure StockAgent is imported

class RecommendationAgent:
    def __init__(self, stock_agent=None):
        """Initialize the agent with an optional StockAgent instance."""
        self.stock_agent = stock_agent or StockAgent()  # Fallback to creating a StockAgent if not passed
        self.log_file = "storage/recommendation_log.csv"

    async def generate_recommendation(self, asset_symbol, company_name, technical_analysis=None):
        """Generates buy/sell/hold recommendation using technical analysis."""
        print(f"\n📌 Generating Recommendation for {asset_symbol}...")

        # Ensure technical analysis is passed and is a valid dictionary
        if not technical_analysis or not isinstance(technical_analysis, dict):
            print(f"❌ No valid technical analysis available for {asset_symbol}.")
            return None  # Ensure function returns None if no recommendation is made

        print(f"\n📊 Latest Technical Analysis for {asset_symbol}: {technical_analysis}")

        # Ensure required indicators are present
        required_keys = {"RSI", "macd_signal"}
        missing_keys = required_keys - technical_analysis.keys()
        if missing_keys:
            print(f"❌ Missing required indicators in technical analysis: {missing_keys}")
            return None  # Return None if required data is missing

        # Extract the latest (most recent) values from the lists
        latest_rsi = technical_analysis["RSI"][-1]  # Get the most recent RSI value
        latest_macd_signal = technical_analysis["macd_signal"][-1]  # Get the most recent MACD signal

        # Generate recommendation
        recommendation, confidence, reasoning = self.make_decision(latest_rsi, latest_macd_signal)

        print(f"\n📌 Recommendation: {recommendation} (Confidence: {confidence:.2f})")
        print(f"💡 Reasoning: {reasoning}\n")

        # Log recommendation
        self.log_recommendation(asset_symbol, company_name, recommendation, confidence, reasoning)

        return recommendation  # Return recommendation for further use

    def make_decision(self, latest_rsi, latest_macd_signal):
        """Decision logic for stock recommendation."""
        if latest_rsi < 30 and latest_macd_signal == "bullish":
            return "BUY", 0.85, "RSI indicates oversold & MACD is bullish."
        elif latest_rsi > 70 and latest_macd_signal == "bearish":
            return "SELL", 0.90, "RSI indicates overbought & MACD is bearish."
        return "HOLD", 0.60, "No strong trend detected."

    def log_recommendation(self, asset_symbol, company_name, recommendation, confidence, reasoning):
        """Logs the recommendation in a CSV file, ensuring a header exists."""
        file_exists = False
        try:
            with open(self.log_file, mode="r") as file:
                file_exists = bool(file.readline())
        except FileNotFoundError:
            pass

        with open(self.log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Timestamp", "Asset", "Company Name", "Recommendation", "Confidence", "Reasoning"])
            writer.writerow([datetime.datetime.now(), asset_symbol, company_name, recommendation, confidence, reasoning])

# Example usage for testing:
if __name__ == "__main__":
    # Create an instance of StockAgent and RecommendationAgent
    stock_agent = StockAgent()
    agent = RecommendationAgent(stock_agent)

    asset = input("Enter stock/crypto symbol: ").strip().upper()
    company = input("Enter company name (optional): ").strip()

    # Example of how the technical_analysis data would look like
    technical_analysis = {
        "RSI": [75.56075409384893, 75.6478815302345, 75.05968262884429, 57.70421528935465, 56.77132146204316],
        "macd_signal": ["bullish", "bullish", "bullish", "bullish", "bullish"],
        "SMA_50": [233.0018, 233.6832, 234.2998, 234.8996, 235.3684],
        "SMA_200": [227.03479166666668, 227.4062886597938, 227.78295918367346, 228.15626262626265, 228.48950000000002],
        "MACD": [8.871293284944272, 9.032020246238972, 9.154732022224948, 9.180050570108847, 8.835214098278755],
        "MACD_Signal": [8.036933635353925, 8.235950957530935, 8.419707170469739, 8.571775850397561, 8.6244634999738],
    }

    import asyncio
    recommendation = asyncio.run(agent.generate_recommendation(asset, company, technical_analysis))

    # Print the recommendation if available
    if recommendation:
        print(f"\n📢 Final Recommendation for {asset}: {recommendation}")
    else:
        print(f"\n⚠️ No valid recommendation generated for {asset}.")
