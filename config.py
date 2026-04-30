import os
from dotenv import load_dotenv

load_dotenv()

def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is not set")
    return value


OPENAI_API_KEY = get_env("OPENAI_API_KEY")
MCP_SERVER_URL = get_env("MCP_SERVER_URL")