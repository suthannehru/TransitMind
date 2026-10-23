FROM python:3.11-slim

# Set the working directory
WORKDIR /transitmind

COPY pyproject.toml .

# Don't cache downloaded packages and built wheels
# Unnecessary space
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir .

# Copy the required files
COPY data/graph.pkl ./data/graph.pkl
COPY src ./src

CMD ["uvicorn", "transitmind.api.main:app", "--host", "0.0.0.0", "--port", "8000"]