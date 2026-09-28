import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

def load_vector_db() -> None:
    # Retrieve the relevant data
    df_routes = pd.read_csv("data/gtfs_subway/routes.txt")
    df_stops = pd.read_csv("data/gtfs_subway/stops.txt")
    df_stop_times = pd.read_csv("data/gtfs_subway/stop_times.txt")
    df_trips = pd.read_csv("data/gtfs_subway/trips.txt")

    # Sentence Transformer
    # L6 means 6 transformer layers
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Only take the northbound stop of every station (Avoid Duplicates)
    stops = df_stops[df_stops["stop_id"].str.endswith(('N', 'S'))]

    stations = {}
    for stop_info in stops.itertuples():

        stop = stop_info.stop_id
        stop_trips = df_stop_times[df_stop_times['stop_id'] == stop]['trip_id']
        matched = df_trips[df_trips['trip_id'].isin(stop_trips)]

        parent_stop_id = stop[:-1]

        if parent_stop_id not in stations:
            stop_name = stops[stops['stop_id'] == stop]['stop_name'].iloc[0]
            stations[parent_stop_id] = {'stop_id': parent_stop_id, 'stop_name': stop_name, 'lines': set()}

        lines = stations[parent_stop_id]['lines']
        for line in matched['route_id'].unique():
            route_info = df_routes[df_routes['route_id'] == line]
            route_long_name = route_info['route_long_name'].iloc[0]
            if line.endswith('X'):
                lines.add(f"{line[:-1]} Express ({route_long_name})")
            else:
                lines.add(f"{line} ({route_long_name})")


    station_description = []

    for station, info in stations.items():
        name = info['stop_name']
        num_lines = 'lines' if len(info['lines']) > 1 else 'line'
        descript = f"{name} is on {num_lines} " + ', '.join(info['lines'])
        station_description.append(descript)
        info['description'] = descript

    # Takes the list of sentences and breaks it up into tokens and then
    # runs it through a trained neural network in batches.
    # Each string is returned a vector of fixed-amount of numbers. The fixed-amount is the dimensions.
    # Semantic search will check for similar strings in these dimension
    embeddings = model.encode(station_description)

    # Connect to the Qdrant Vector Database
    client = QdrantClient(host="localhost", port="6333")

    # Create a collection in the vector database called "stations" where each value has a fixed-amount parameters/dimensions
    # Distance between input is computed using the Distance.COSINE function

    if not client.collection_exists(collection_name="stations"):
        client.recreate_collection(collection_name="stations", vectors_config=VectorParams(size=embeddings.shape[1], distance=Distance.COSINE))

    client.upsert(collection_name="stations", 
                points=[PointStruct(
                    id=index, 
                    vector=embeddings[index].tolist(), payload=stations[ID]) for index, ID in enumerate(stations.keys())])

if __name__ == "__main__":
    load_vector_db()


