import os
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# Get API key from environment variable
# Set it using: export GOOGLE_API_KEY="your-key-here"
# Or create a .env file in the project root with: GOOGLE_API_KEY=your-key-here
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Please set it as an environment variable or in a .env file. "
        "Get your API key from: https://makersuite.google.com/app/apikey"
    )

