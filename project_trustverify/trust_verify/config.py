import os

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Benchmark Settings
DEFAULT_TEMPERATURE = 0.0

# Supported Models
MODELS = {
    "openai": ["gpt-4o-mini", "gpt-4o"],
    "gemini": ["gemini-1.5-flash", "gemini-1.5-pro"],
    "mock": ["mock-model"]
}

# CSV Metrics Log File
METRICS_CSV_FILE = "security_metrics.csv"

# HTML Report File
HTML_REPORT_FILE = "security_dashboard.html"
