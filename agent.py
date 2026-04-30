from agents import Agent, Runner
from agents.mcp import (
    MCPServerManager,
    MCPServerStreamableHttp,
    MCPServerStreamableHttpParams,
)
from config import MCP_SERVER_URL

MERIDIAN_INSTRUCTIONS = """
You are a customer support assistant for Meridian Electronics.

You help customers:
- Check product availability
- Place orders
- View order history
- Authenticate users

IMPORTANT RULES:
- Always use MCP tools for business data
- Never make up product or order information
- Ask for authentication if needed before accessing user data
- Be concise and helpful
- Maintain a good tone and be willing to help
"""

runner = Runner()


async def run_agent(user_input, history):
    # New client per request so connect/cleanup does not reuse a closed session stack.
    mcp_server = MCPServerStreamableHttp(
        params=MCPServerStreamableHttpParams(url=MCP_SERVER_URL),
    )

    messages = []
    for h in history:
        if isinstance(h, dict) and "role" in h and "content" in h:
            content = h["content"]
            if not isinstance(content, str):
                content = str(content)
            messages.append({"role": h["role"], "content": content})
        elif isinstance(h, (list, tuple)) and len(h) >= 2:
            messages.append({"role": "user", "content": str(h[0])})
            messages.append({"role": "assistant", "content": str(h[1])})

    messages.append({"role": "user", "content": user_input})

    async with MCPServerManager([mcp_server], strict=True) as manager:
        agent = Agent(
            name="Meridian Support Assistant",
            instructions=MERIDIAN_INSTRUCTIONS,
            mcp_servers=manager.active_servers,
        )
        result = await runner.run(agent, messages)

    return result.final_output
