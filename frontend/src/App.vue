<script setup>
import { ref } from 'vue';
import { searchPapers } from './services/api';

const query = ref('');
const results = ref([]);
const hasSearched = ref(false);
const filters = ref({
  yearStart: 2000,
  yearEnd: 2026,
  sortBy: 'Relevance'
});

const handleSearch = async () => {
  if (!query.value && !hasSearched.value) {
    return;
  }

  hasSearched.value = true;

  try {
    const data = await searchPapers(query.value, filters.value);

    results.value = data.results || [];
  } catch (error) {
    console.error("Error fetching search results:", error);

    alert("Unable to fetch search results. Please try again later.");
  }
};
</script>

<template>
  <div class="app-container">
    <header>
      <div class="brand">
        <span class="icon">🎓</span>
        <h1>ScholarSearch</h1>
      </div>
    </header>

    <div class="search-section">
      <div class="search-bar-wrapper">
        <input
            v-model="query"
            @keyup.enter="handleSearch"
            placeholder="Search for papers, authors, or topics..."
        />
        <button @click="handleSearch">Search</button>
      </div>
    </div>

    <div class="content-layout">
      <aside class="sidebar">
        <div class="filter-card">
          <h3>Filters</h3>
          <div class="filter-group">
            <label>Sort By</label>
            <select v-model="filters.sortBy">
              <option>Relevance</option>
              <option>Newest</option>
              <option>Oldest</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Year Range</label>
            <div class="year-inputs">
              <input type="number" v-model="filters.yearStart"/>
              <span>-</span>
              <input type="number" v-model="filters.yearEnd"/>
            </div>
          </div>
          <button class="apply-btn" @click="handleSearch">Apply Filters</button>
        </div>
      </aside>

      <main class="results-area">
        <div v-if="!hasSearched" class="placeholder-state">
          Enter a keyword to start searching through 1.7m papers.
        </div>

        <div v-else-if="results.length === 0" class="no-results">
          <p>No papers found for "<strong>{{ query }}</strong>".</p>
        </div>

        <div v-else class="results-list">
          <p class="stats">Found {{ results.length }} results</p>

          <div v-for="paper in results" :key="paper.id" class="result-card">
            <div class="card-header">
              <span class="category-tag">{{ paper.categories.split(' ')[0] }}</span>
              <span class="date">{{ paper.update_date }}</span>
            </div>

            <h2 class="paper-title">
              <a :href="`https://arxiv.org/abs/${paper.id}`" target="_blank">
                {{ paper.title }}
              </a>
            </h2>

            <div class="authors">
              {{ paper.authors }}
            </div>

            <p class="abstract">
              {{ paper.abstract.substring(0, 250) }}...
            </p>

            <div class="card-footer">
              <span class="id-badge">ID: {{ paper.id }}</span>

              <a :href="`https://arxiv.org/pdf/${paper.id}`" target="_blank" class="pdf-btn">
                Download PDF ⬇
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', sans-serif;
  color: #333;
}

header {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
}

.brand h1 {
  font-size: 2rem;
  margin: 0;
}

.brand .icon {
  font-size: 2rem;
}

.search-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

.search-bar-wrapper {
  display: flex;
  width: 100%;
  max-width: 700px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.search-bar-wrapper input {
  flex: 1;
  padding: 16px;
  border: none;
  font-size: 16px;
  outline: none;
}

.search-bar-wrapper button {
  padding: 0 30px;
  background-color: #42b983;
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.search-bar-wrapper button:hover {
  background-color: #3aa876;
}

.content-layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 40px;
  align-items: start;
}

.filter-card {
  background: white;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.filter-group {
  margin-bottom: 20px;
}

.filter-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.filter-group select, .filter-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.year-inputs {
  display: flex;
  gap: 5px;
  align-items: center;
}

.apply-btn {
  width: 100%;
  padding: 10px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.stats {
  color: #666;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.result-card {
  background: white;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #42b983;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.85rem;
  color: #666;
}

.category-tag {
  background: #eef2f5;
  padding: 2px 8px;
  border-radius: 4px;
  color: #2c3e50;
  font-weight: 600;
}

.paper-title {
  margin: 0 0 8px 0;
  font-size: 1.25rem;
}

.paper-title a {
  text-decoration: none;
  color: #1a0dab;
}

.paper-title a:hover {
  text-decoration: underline;
}

.authors {
  color: #006621;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.abstract {
  color: #4d5156;
  line-height: 1.6;
  font-size: 0.95rem;
  margin-bottom: 15px;
}

.card-footer {
  display: flex;
  justify-content: space-between; /* Pushes ID to left, PDF to right */
  align-items: center;
  font-size: 0.8rem;
  color: #888;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.pdf-btn {
  background-color: #b31b1b; /* Cornell Red (arXiv color) */
  color: white;
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.85rem;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.pdf-btn:hover {
  background-color: #900000;
}

.placeholder-state {
  text-align: center;
  color: #999;
  margin-top: 50px;
  font-size: 1.1rem;
}

.no-results {
  text-align: center;
  margin-top: 50px;
}

@media (max-width: 768px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    margin-bottom: 30px;
  }
}
</style>
