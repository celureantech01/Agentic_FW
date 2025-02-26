import numpy as np
import pandas as pd


def detect_unusual_volume(asset, historical_data):
    """ Detects unusual spikes in trading volume. """
    historical_data["Volume_MA"] = historical_data["volume"].rolling(window=20).mean()
    threshold = historical_data["Volume_MA"] * 1.5  # 50% above moving average

    unusual_spikes = historical_data[historical_data["volume"] > threshold]

    return unusual_spikes

