"""
This file contains all constants that are not meant to be modified by the user.
"""

import os

# Base URL for API requests
BASE_URL = "https://api.hh.ru"

# URL for fetching area data
AREAS_URL = "https://api.hh.ru/areas"

# Data directory
DATA_DIR = os.path.join("src", "data")

# File paths
AREAS_FILE = os.path.join(DATA_DIR, "areas.json")
