from transitmind.graph.routing import find_route
from transitmind.live.feed import get_live_positions, get_service_alerts

tools_str_func = {
    "find_route": find_route,
    "get_live_positions": get_live_positions,
    "get_service_alerts": get_service_alerts,
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
                    "start_stop": {"type": "string", "description": "The stop name of the start station"},
                    "end_stop": {"type": "string", "description": "The stop name of the end station"}
                },
                "required": ["start_stop", "end_stop"]
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
]   