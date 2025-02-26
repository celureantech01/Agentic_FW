import logging

# Configure logging
logging.basicConfig(
    filename="storage/recommendation_log.csv",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_recommendation(asset, action, price, confidence):
    """ Logs buy/sell recommendations to the system. """
    logging.info(f"Recommendation: {action} {asset} at {price}, Confidence: {confidence}%")

def log_performance(asset, action, result, accuracy):
    """ Logs the performance of past recommendations. """
    logging.info(f"Performance: {asset} {action}, Result: {result}, Accuracy: {accuracy}%")

