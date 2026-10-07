from mcp.server.mcpserver import MCPServer
from transitmind.graph.routing import find_route
from transitmind.live.feed import get_live_positions, get_service_alerts
from transitmind.resolver import parse_route_query

def initialize_mcp_server() -> None:
    # Create an MCP Server object 
    # Registers tools, prompts, resources. All the handling required for a mcp server
    server = MCPServer(name="transitmind")

    # Add the tools to the registry
    # Docustring added for each tool. LLM knows the description of each tool
    server.add_tool(find_route)
    server.add_tool(get_live_positions)
    server.add_tool(get_service_alerts)
    server.add_tool(parse_route_query)

    return server

if __name__ == "__main__":
    server = initialize_mcp_server()
    server.run()
