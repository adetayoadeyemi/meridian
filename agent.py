from agents import Agent, Runner
from agents.mcp import (
    MCPServerManager,
    MCPServerStreamableHttp,
    MCPServerStreamableHttpParams,
)
from config import MCP_SERVER_URL
import asyncio


MERIDIAN_INSTRUCTIONS = """
You are a customer support assistant for Meridian Electronics.

You help customers:
- Check product availability
- Place orders
- View order history
- Authenticate users

IMPORTANT RULES:
- Always use MCP tools for business data
- Always show product SKU in your response
- Always request product SKU from the user before using the MCP tools
- Do not infer order history, always use the MCP tools to get the order history
- Never make up product or order information
- Ask for authentication if needed before accessing user data
"""


runner = Runner()


def normalize_history(history):
    messages = []

    for h in history:
        if isinstance(h, dict):
            messages.append({
                "role": h["role"],
                "content": str(h["content"])
            })
        elif isinstance(h, (list, tuple)) and len(h) == 2:
            messages.append({"role": "user", "content": str(h[0])})
            messages.append({"role": "assistant", "content": str(h[1])})

    return messages


async def run_agent(user_input, history):
    messages = normalize_history(history)
    messages.append({"role": "user", "content": user_input})

    mcp_server = MCPServerStreamableHttp(
        params=MCPServerStreamableHttpParams(url=MCP_SERVER_URL),
    )

    try:
        async with MCPServerManager([mcp_server], strict=True) as manager:
            agent = Agent(
                name="Meridian Support Assistant",
                instructions=MERIDIAN_INSTRUCTIONS,
                mcp_servers=manager.active_servers,
            )

            result = await asyncio.wait_for(
                runner.run(agent, messages),
                timeout=25
            )

            return result.final_output or "I couldn't process that request."

    except asyncio.TimeoutError:
        return "The request took too long. Please try again."

    except Exception as e:
        return f"Something went wrong. Please try again."