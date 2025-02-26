import pandas as pd
import numpy as np
from storage.performance_tracker import load_performance_data


def analyze_mistakes():
    """ Analyzes past buy/sell recommendations and finds areas for improvement. """
    df = load_performance_data()

    if df.empty:
        return "No data available for analysis."

    incorrect_recommendations = df[df['accuracy'] < 0.6]

    if incorrect_recommendations.empty:
        return "No significant mistakes found in past recommendations."

    common_mistakes = incorrect_recommendations['reason'].value_counts()

    return common_mistakes.to_dict()


def suggest_improvements():
    """ Suggests refinements based on past mistakes. """
    mistakes = analyze_mistakes()

    if isinstance(mistakes, str):
        return mistakes

    suggestions = {
        "Overestimating Momentum": "Use more conservative RSI/MACD thresholds.",
        "Ignoring Market Sentiment": "Factor in social media sentiment before confirming buy signals.",
        "Incorrect Trend Reversal Calls": "Adjust moving average crossover periods for better trend detection."
    }

    return {error: suggestions.get(error, "Review strategy") for error in mistakes}
