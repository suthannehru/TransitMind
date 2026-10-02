import logging
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Sentence Transformer
# L6 means 6 transformer layers
model = SentenceTransformer('all-MiniLM-L6-v2')

def parse_route_query(query: str) -> tuple[str, str]:

    # Split the query string using to by searching in revers
    split_index = query.rfind(" to ")

    if split_index == -1:
        raise ValueError("Query not correctly formatted")
    
    start_vector = model.encode(query[:split_index])
    end_vector = model.encode(query[split_index + len(' to '):].strip(" ?.,!"))

    # Connect to the Qdrant Vector Database
    client = QdrantClient(host="localhost", port="6333")

    start_result = client.query_points(collection_name="stations", query=start_vector, limit=3)
    end_result = client.query_points(collection_name="stations", query=end_vector, limit=3)

    if len(start_result.points) and len(end_result.points):
        start_stop_id = start_result.points[0].payload["stop_id"]
        end_stop_id = end_result.points[0].payload["stop_id"]

        return(start_stop_id, end_stop_id)

    return ('', '')


if __name__ == "__main__":
    pass