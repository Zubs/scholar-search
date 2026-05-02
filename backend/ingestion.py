import json
import os
from elasticsearch import Elasticsearch, helpers

# Connect to local Elasticsearch
es = Elasticsearch(
    "http://localhost:9200",
    headers={"Accept": "application/json", "Content-Type": "application/json"},
)
INDEX_NAME = "arxiv_papers"

# Resolve path relative to this script's location for reliability
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(SCRIPT_DIR, "..", "data", "arxiv-metadata-oai-snapshot.json")

try:
    info = es.info()
    print(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
except Exception as e:
    print("Could not connect to Elasticsearch.")
    print(e)
    exit(1)

if not os.path.exists(FILE_PATH):
    print(f"ERROR: Dataset file not found at: {os.path.abspath(FILE_PATH)}")
    print("Please download the arXiv dataset from Kaggle and place it in the /data directory.")
    exit(1)

mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "english_custom": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "english_stop", "english_stemmer"],
                }
            },
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
            },
        },
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "english_custom"},
            "abstract": {"type": "text", "analyzer": "english_custom"},
            "authors": {"type": "text"},
            "categories": {"type": "keyword"},
            "update_date": {"type": "date", "format": "yyyy-MM-dd"},
        }
    },
}

try:
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Created index: {INDEX_NAME}")
    else:
        print(f"Index '{INDEX_NAME}' already exists, skipping creation.")
        print("To re-index, delete the index first: DELETE /arxiv_papers")
except Exception as e:
    print(f"Error when checking/creating index: {e}")
    exit(1)


def generate_actions(filepath):
    """Generator that yields bulk-index actions for each paper in the dataset."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
                # Only index documents that have the required fields
                if not doc.get("id") or not doc.get("title"):
                    continue
                yield {
                    "_index": INDEX_NAME,
                    "_id": doc["id"],
                    "_source": {
                        "id": doc.get("id"),
                        "title": doc.get("title", ""),
                        "abstract": doc.get("abstract", ""),
                        "authors": doc.get("authors", ""),
                        "categories": doc.get("categories", ""),
                        "update_date": doc.get("update_date", ""),
                    },
                }
            except json.JSONDecodeError as e:
                print(f"Skipping malformed JSON line: {e}")


print(f"Starting ingestion from: {os.path.abspath(FILE_PATH)}")

try:
    success, failed = helpers.bulk(
        es,
        generate_actions(FILE_PATH),
        chunk_size=500,
        raise_on_error=False,
        request_timeout=120,
    )

    print(f"\nIngestion complete!")
    print(f"  Successfully indexed: {success:,} documents")

    if failed:
        print(f"  Failed/skipped: {len(failed):,} documents")

except Exception as e:
    print(f"Error during indexing: {e}")
    exit(1)
