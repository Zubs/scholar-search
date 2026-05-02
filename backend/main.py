import html
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch, exceptions as es_exceptions

app = FastAPI(title="ScholarSearch API", description="Search engine for STEM research papers")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "arxiv_papers"


def safe_highlight(raw: str) -> str:
    """
    Sanitise an Elasticsearch highlight fragment for safe use with v-html.
    Escapes all HTML, then restores only the <em>…</em> tags that
    Elasticsearch itself inserted — these are controlled server-side, not from
    user-supplied data, so they are safe to render.
    """
    escaped = html.escape(raw)
    escaped = escaped.replace("&lt;em&gt;", "<em>").replace("&lt;/em&gt;", "</em>")

    return escaped


@app.get("/health")
async def health_check():
    """Health check endpoint to verify API and Elasticsearch connectivity."""
    try:
        if not es.ping():
            raise HTTPException(status_code=503, detail="Elasticsearch is unreachable")

        return {"status": "ok", "elasticsearch": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/search")
async def search_papers(
        q: str = Query("", description="Search query"),
        year_start: int = Query(1991, description="Start year", ge=1991, le=2026),
        year_end: int = Query(2026, description="End year", ge=1991, le=2026),
        sort_by: str = Query("Relevance", description="Sort criteria: Relevance, Newest, Oldest"),
        page: int = Query(1, description="Page number", ge=1),
        page_size: int = Query(20, description="Results per page", ge=1, le=100),
):
    if year_start > year_end:
        raise HTTPException(status_code=400, detail="year_start must be <= year_end")

    from_offset = (page - 1) * page_size

    es_query = {
        "bool": {
            "must": [],
            "filter": [
                {
                    "range": {
                        "update_date": {
                            "gte": f"{year_start}-01-01",
                            "lte": f"{year_end}-12-31",
                        }
                    }
                }
            ],
        }
    }

    if q.strip():
        es_query["bool"]["must"].append(
            {
                "multi_match": {
                    "query": q,
                    "fields": ["title^3", "abstract", "authors"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            }
        )
    else:
        es_query["bool"]["must"].append({"match_all": {}})

    sort_config = []
    if sort_by == "Newest":
        sort_config.append({"update_date": {"order": "desc"}})
    elif sort_by == "Oldest":
        sort_config.append({"update_date": {"order": "asc"}})
    else:
        sort_config.append("_score")

    highlight_config = {
        "pre_tags": ["<em>"],
        "post_tags": ["</em>"],
        "fields": {
            "abstract": {"fragment_size": 250, "number_of_fragments": 1},
            "title": {"number_of_fragments": 0},
        },
    }

    try:
        response = es.search(
            index=INDEX_NAME,
            query=es_query,
            sort=sort_config,
            highlight=highlight_config,
            from_=from_offset,
            size=page_size,
        )
    except es_exceptions.NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Index '{INDEX_NAME}' not found. Run ingestion first.",
        )
    except es_exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Elasticsearch.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

    hits = response["hits"]["hits"]
    total = response["hits"]["total"]["value"]
    total_pages = max(1, -(-total // page_size))

    formatted_results = []
    for hit in hits:
        source = hit["_source"]
        snippet = ""
        raw_title = source.get("title", "").replace("\n", " ")
        # Default: HTML-escape the raw title (safe for v-html)
        highlighted_title = html.escape(raw_title)

        if "highlight" in hit:
            if "abstract" in hit["highlight"]:
                snippet = "... " + safe_highlight(hit["highlight"]["abstract"][0]) + " ..."
            if "title" in hit["highlight"]:
                highlighted_title = safe_highlight(hit["highlight"]["title"][0])

        formatted_results.append(
            {
                "id": source.get("id", ""),
                "title": highlighted_title,
                "abstract": html.escape(source.get("abstract", "").replace("\n", " ")),
                "authors": source.get("authors", ""),
                "categories": source.get("categories", ""),
                "update_date": source.get("update_date", ""),
                "snippet": snippet,
                "score": round(hit.get("_score") or 0, 4),
            }
        )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "results": formatted_results,
    }
