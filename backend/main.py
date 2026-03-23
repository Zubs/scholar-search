from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch

app = FastAPI()

# Enable CORS so Vue (running on port 5173) can talk to FastAPI (running on port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "arxiv_papers"

@app.get("/search")
async def search_papers(
    q: str = Query("", description="Search query"),
    year_start: int = Query(1990, description="Start year"),
    year_end: int = Query(2026, description="End year"),
    sort_by: str = Query("Relevance", description="Sort criteria")
):
    es_query = {
        "bool": {
            "must": [],
            "filter": [
                {
                    "range": {
                        "update_date": {
                            "gte": f"{year_start}-01-01",
                            "lte": f"{year_end}-12-31"
                        }
                    }
                }
            ]
        }
    }

    if q:
        es_query["bool"]["must"].append({
            "multi_match": {
                "query": q,
                # Title matches are weighted 3x heavier
                "fields": ["title^3", "abstract", "authors"],
                "type": "best_fields"
            }
        })
    else:
        es_query["bool"]["must"].append({"match_all": {}})

    sort_config = []
    if sort_by == "Newest":
        sort_config.append({"update_date": {"order": "desc"}})
    elif sort_by == "Oldest":
        sort_config.append({"update_date": {"order": "asc"}})
    else:
        sort_config.append("_score") # Default BM25 Relevance

    response = es.search(
        index=INDEX_NAME,
        query=es_query,
        sort=sort_config,
        size=20 # Return top 20 results
    )

    hits = response["hits"]["hits"]
    total = response["hits"]["total"]["value"]

    formatted_results = [
        {
            "id": hit["_source"]["id"],
            "title": hit["_source"]["title"].replace('\n', ' '),
            "abstract": hit["_source"]["abstract"].replace('\n', ' '),
            "authors": hit["_source"]["authors"],
            "categories": hit["_source"]["categories"],
            "update_date": hit["_source"]["update_date"]
        }
        for hit in hits
    ]

    return {"total": total, "results": formatted_results}
