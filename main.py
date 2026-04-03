from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(
    project="optimal-shard-492016-k6",
    location="us-central1"
)

print("Vertex AI initialized successfully!")