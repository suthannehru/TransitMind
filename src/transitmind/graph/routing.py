import networkx as nx
import pickle

def find_route(start_stop_id: str, end_stop_id: str):

    # Load the binary pickle file and populate the station graph
    with open("data/graph.pkl", "rb") as f:
        G = pickle.load(f)

    route = None

    if start_stop_id in G and end_stop_id in G:
        try:
            route = nx.shortest_path(G, start_stop_id, end_stop_id)
        except nx.NetworkXNoPath:
            raise ValueError(f"No route exists between {start_stop_id} and {end_stop_id}")
    else:
        raise ValueError("Start and/or End Stop ID is invalid")        

    return [G.nodes[stop_id]["name"] for stop_id in route]

    

if __name__ == "__main__":
    print(find_route('S01', 'F02'))
    