import networkx as nx
import pickle
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import structlog
from transitmind.config import settings

logger = structlog.getLogger(__name__)

# Sentence Transformer
# L6 means 6 transformer layers
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to the Qdrant Vector Database
client = QdrantClient(url=settings.qdrant_url)

# Load the binary pickle file and populate the station graph
with open("data/graph.pkl", "rb") as f:
    G = pickle.load(f)

def leg_sentence(start: str, end: str, legs: set, edge) -> str:
    head_sign = ", ".join(
        f"{l} toward {' / '.join(sorted(edge['head_sign'][l]))}"
        for l in sorted(legs)
    )
    return f"From {start} take {head_sign} to {end}." 

def find_stop_id(start_stop: str, end_stop: str) -> tuple[str, str]:

    start_vector = model.encode(start_stop)
    end_vector = model.encode(end_stop)

    start_result = client.query_points(collection_name="stations", query=start_vector, limit=3)
    end_result = client.query_points(collection_name="stations", query=end_vector, limit=3)

    if len(start_result.points) and len(end_result.points):
        start_stop_id = start_result.points[0].payload["stop_id"]
        end_stop_id = end_result.points[0].payload["stop_id"]

        return (start_stop_id, end_stop_id)
    
    return ('', '')

def find_route(start_stop: str, end_stop: str) -> list[str]:
    """ Loads the station map and returns the shortest path between the stops as a list """

    route = None

    start_stop_id, end_stop_id = find_stop_id(start_stop, end_stop)

    if start_stop_id in G and end_stop_id in G:
        try:
            route = nx.shortest_path(G, start_stop_id, end_stop_id)
        except nx.NetworkXNoPath:
            raise ValueError(f"No route exists between {start_stop_id} and {end_stop_id}")
    else:
        raise ValueError("Start and/or End Stop ID is invalid")        

    result = []
    legs = set()
    start_station = None
    end_station = None
    direction = None
    prev_edge = None
    
    for a, b in zip(route, route[1:]):
        # Handle transfer case
        if G.edges[a, b].get("transfer"):
            if start_station is None:
                continue
            if len(result):
                result.append(f"Transfer at {start_station}.")
            result.append(leg_sentence(start_station, end_station, legs, prev_edge))
            legs = set()
            start_station = None
            end_station = None
        else:
            # Get the lines between the two stations
            lines = G.edges[a, b].get("lines")
            if start_station is None:
                legs = lines
                start_station = G.nodes[a]["name"]
                direction = G.edges[a, b].get("direction")
            else:
                current_direction = G.edges[a, b].get("direction")
                if current_direction != direction:
                    result.append(leg_sentence(start_station, end_station, legs, prev_edge))
                    direction = current_direction
                    start_station = G.nodes[a]["name"]
                    legs = lines
                    end_station = G.nodes[b]["name"]
                    prev_edge = G.edges[a, b]
                    continue
                intersect_lines = lines.intersection(legs)
                if len(intersect_lines):
                    legs = intersect_lines
                else:
                    result.append(leg_sentence(start_station, end_station, legs, prev_edge))
                    legs = lines
                    start_station = G.nodes[a]["name"]
            end_station = G.nodes[b]["name"]
            prev_edge = G.edges[a, b]

    if start_station is not None:
        result.append(leg_sentence(start_station, end_station, legs, prev_edge))

    return result

    

if __name__ == "__main__":
    params = ('S01', 'F02')
    logger.info("find_route", params=params, output=find_route(*params))
    