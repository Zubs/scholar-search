import json
from elasticsearch import Elasticsearch, helpers

# Connect to local Elasticsearch
es = Elasticsearch(
    "http://localhost:9200",
    headers={"Accept": "application/json", "Content-Type": "application/json"}
)
INDEX_NAME = "arxiv_papers"
FILE_PATH = "../data/arxiv-metadata-oai-snapshot.json"

try:
    info = es.info()
    print(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
except Exception as e:
    print("Could not connect to Elasticsearch.")
    print(e)
    exit()

mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "english"},
            "abstract": {"type": "text", "analyzer": "english"},
            "authors": {"type": "text"},
            "categories": {"type": "keyword"},
            "update_date": {"type": "date", "format": "yyyy-MM-dd"}
        }
    }
}

try:
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Created index: {INDEX_NAME}")
    else:
        print(f"Index {INDEX_NAME} already exists, skipping index creation.")
except Exception as e:
    print(f"Error when checking/creating index: {e}")


def generate_actions(filepath, limit=17000):
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= limit:
                break

            doc = json.loads(line)

            # We now yield the ENTIRE doc to _source, keeping all fields
            yield {
                "_index": INDEX_NAME,
                "_id": doc["id"],
                "_source": doc
            }

print(f"Starting ingestion from {FILE_PATH}...")

try:
    # Use the bulk API to send data in chunks of 500, and limit to 17000 documents for testing
    success, failed = helpers.bulk(es, generate_actions(FILE_PATH, limit=17000), chunk_size=500)
    print(f"Successfully indexed {success} documents.")
except Exception as e:
    print(f"Error during indexing: {e}")
