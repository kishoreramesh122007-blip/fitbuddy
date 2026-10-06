import os

from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


GEMINI_WORKOUT_MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-3.5-flash-lite"
)


GEMINI_TIP_MODEL = os.getenv(
    "GEMINI_TIP_MODEL",
    "gemini-3.5-flash-lite"
)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fitbuddy.db"
)


DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "true"
).lower() == "true"