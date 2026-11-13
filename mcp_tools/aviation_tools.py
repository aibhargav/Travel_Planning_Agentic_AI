# ==========================================
# AviationStack MCP tools
# ==========================================


from mcp_client import client


aviation_tools = {}


async def initialize_flight_tools():
    global aviation_tools

    if aviation_tools:
        return

    # Load only AviationStack.
    # Tavily and Weather will not be initialized here.
    tools = await client.get_tools(
        server_name="aviationstack"
    )

    aviation_tools = {
        tool.name: tool
        for tool in tools
    }

    for tool in tools:
        print("\nTool name:", tool.name)
        print("Description:", tool.description)

    if not aviation_tools:
        raise RuntimeError(
            "AviationStack MCP connected but "
            "returned no tools."
        )


async def aviation_flight_tool(
    tool_name: str,
    tool_args: dict = None
):
    await initialize_flight_tools()

    tool = aviation_tools.get(tool_name)

    if tool is None:
        available_tools = ", ".join(
            sorted(aviation_tools.keys())
        )

        raise ValueError(
            f"AviationStack tool '{tool_name}' "
            "was not found. "
            f"Available tools: "
            f"{available_tools or 'none'}"
        )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result
