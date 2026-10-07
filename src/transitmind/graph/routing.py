import structlog
import networkx as nx
import pickle

logger = structlog.getLogger(__name__)

# Load the binary pickle file and populate the station graph
with open("data/graph.pkl", "rb") as f:
    G = pickle.load(f)

def find_route(start_stop_id: str, end_stop_id: str) -> list[str]:
    """ Loads the station map and returns the shortest path between the stops as a list of station names """

    route = None

    if start_stop_id in G and end_stop_id in G:
        try:
            route = nx.shortest_path(G, start_stop_id, end_stop_id)
        except nx.NetworkXNoPath:
            raise ValueError(f"No route exists between {start_stop_id} and {end_stop_id}")
    else:
        raise ValueError("Start and/or End Stop ID is invalid")        

    result = []
    prev_stop_id = None

    for stop_id in route:
        station = G.nodes[stop_id]["name"]
        if prev_stop_id and G.edges[prev_stop_id, stop_id].get("transfer"):
            prev_station = G.nodes[prev_stop_id]["name"]
            if prev_station == station:
                result.pop()
            if len(result) > 0:
                result.append(f"{station} (transfer)")
            else:
                result.append(station)
        else:
            result.append(station)

        prev_stop_id = stop_id

    return result

    

if __name__ == "__main__":
    params = ('S01', 'F02')
    logger.info("find_route", params=params, output=find_route(*params))
    