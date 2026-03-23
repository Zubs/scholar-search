# ScholarSearch: A Search Engine for STEM Research

ScholarSearch is an advanced search engine designed to help researchers, students, and academics easily find scholarly articles, papers, and publications in the fields of Science, Technology, Engineering, and Mathematics (STEM).

## Setup (Running the Project)
1. Clone and navigate into the repository:
```bash
git clone https://github.com/Zubs/scholar-search

cd scholar-search
```

2. Install dependencies for the backend and frontend:
```bash
# Backend dependencies
cd backend

# Create a virtual environment (if not existing)
python3 -m venv venv

# activate it
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install
```

3. Setup Elasticsearch using Docker:
```bash
docker-compose up -d
```

4. Run the FastAPI backend:
```bash
cd backend && uvicorn main:app --reload
```

5. Run the Vue.js frontend:
```bash
cd frontend && npm run serve
```

6. Test backend API:
```bash
curl -X GET "http://localhost:8000/search?q=quantum+computing" -H "accept: application/json"
```

7. Test frontend:
Open a web browser and navigate to `http://localhost:5173`. Use the search bar to query for research articles (e.g., "quantum computing") and view the results.

## Dataset
[arXiv Dataset](https://www.kaggle.com/datasets/Cornell-University/arxiv/data): The dataset contains metadata for over 1.7 million research articles from arXiv, including titles, authors, abstracts, categories, and publication dates.

## Architecture (Structure)
Client-Server setup
* [Vue.js](https://vuejs.org/) for [frontend](./frontend)
* [Elasticsearch](https://www.elastic.co/elasticsearch) for text search
* FastAPI for backend.

## TODOs
- Reset filters on search
- Add pagination
- Add more filters (e.g., author, publication date)
