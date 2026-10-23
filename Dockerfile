FROM python:3.11-slim

# Set the working directory
WORKDIR /transitmind

COPY pyproject.toml .

# Don't cache downloaded packages and built wheels
# Unnecessary space
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy the data
COPY data/gtfs_subway ./data/gtfs_subway

# Copy the source code
COPY src ./src

# Install modules
RUN pip install --no-cache-dir .

# Download the model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Generate graph.pkl
RUN python3 -m transitmind.graph.station_graph

# Run uvicorn to start listening for requests 
CMD ["uvicorn", "transitmind.api.main:app", "--host", "0.0.0.0", "--port", "8000"]