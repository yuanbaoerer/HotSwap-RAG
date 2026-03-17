"""Shared configuration for frontend pages."""

import os

# API Base URL - can be overridden via environment variable
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8001")