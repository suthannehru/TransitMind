from transitmind.graph.routing import find_route
from transitmind.live.feed import get_live_positions, get_service_alerts
from transitmind.resolver import parse_route_query

tools_str_func = {
    "find_route": find_route,
    "get_live_positions": get_live_positions,
    "get_service_alerts": get_service_alerts,
    "parse_route_query": parse_route_query
}

llm_tools = [
    {
        "type": "function",
        "function": {
            "name": "find_route",
            "description": """Loads the station map and returns the shortest path between the stops as a list of station names.
             Only call this function when the user needs the route between two stations""",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_stop_id": {"type": "string", "description": "The stop ID of the start station"},
                    "end_stop_id": {"type": "string", "description": "The stop ID of the end station"}
                },
                "required": ["start_stop_id", "end_stop_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_positions",
            "description": """Given a line, return a list of strings regarding the active trains for a line.
            Only call this function if the user asks about the whereabouts of the train for a given line.
            The Staten Island Railway is referenced as SI.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {"type": "string", "description": "The subway line for which you need the active train positions"},
                },
                "required": ["line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_service_alerts",
            "description": """Given a line, return a list of dictionaries for every service alert on that line.
            Only call this function if the user asks about delays or service alerts for a given line.
            The Staten Island Railway is referenced as SI.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {"type": "string", "description": "The subway line for which you need the service alerts for"},
                },
                "required": ["line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "parse_route_query",
            "description": "Splits a natural language question, 'X' to 'Y' and returns a tuple of start and end stop IDs",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The natural language question 'X' to 'Y'"},
                },
                "required": ["query"]
            }
        }
    },
]   