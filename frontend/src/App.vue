<script setup>
import { ref, computed, onMounted } from 'vue';
import SearchBar from './components/SearchBar.vue';
import SearchFilters from './components/SearchFilters.vue';
import { searchPapers, checkHealth } from './services/api';

const currentQuery = ref('');
const results = ref([]);
const totalResults = ref(0);
const currentPage = ref(1);
const totalPages = ref(1);
const hasSearched = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');
const backendDown = ref(false);

const filters = ref({
  yearStart: 1991,
  yearEnd: 2026,
  sortBy: 'Relevance',
});

const PAGE_SIZE = 20;
const formattedTotal = computed(() =>
    totalResults.value.toLocaleString('en-GB')
);

// Check backend connectivity on app load so users see the warning immediately
onMounted(async () => {
  const healthy = await checkHealth();
  if (!healthy) {
    backendDown.value = true;
  }
});

const executeSearch = async (query, page = 1) => {
  isLoading.value = true;
  errorMessage.value = '';
  backendDown.value = false;
  hasSearched.value = true;

  try {
    const data = await searchPapers(
        query,
        filters.value,
        page,
        PAGE_SIZE
    );
    results.value = data.results || [];
    totalResults.value = data.total || 0;
    currentPage.value = data.page || 1;
    totalPages.value = data.total_pages || 1;
  } catch (error) {
    errorMessage.value = error.message || 'An unexpected error occurred.';
    results.value = [];
    totalResults.value = 0;
  } finally {
    isLoading.value = false;
  }
};

const handleSearch = (query) => {
  currentQuery.value = query;
  currentPage.value = 1;
  executeSearch(query, 1);
};

const handleFilterUpdate = (newFilters) => {
  filters.value = newFilters;
  if (hasSearched.value) {
    currentPage.value = 1;
    executeSearch(currentQuery.value, 1);
  }
};

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) {
    return;
  }

  currentPage.value = page;
  executeSearch(currentQuery.value, page);
  window.scrollTo({top: 0, behavior: 'smooth'});
};

const visiblePages = computed(() => {
  const pages = [];
  const start = Math.max(1, currentPage.value - 2);
  const end = Math.min(totalPages.value, currentPage.value + 2);
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  return pages;
});

// Null-safe category display
const primaryCategory = (categories) =>
    (categories || '').split(' ')[0] || 'General';
</script>

<template>
  <div class="app-container">
    <header>
      <div class="brand">
        <span class="icon">🎓</span>
        <h1>ScholarSearch</h1>
        <span class="subtitle">STEM Research Explorer</span>
      </div>
    </header>

    <!-- Backend connectivity warning -->
    <div v-if="backendDown" class="backend-banner">
      ⚠️ Cannot reach the backend. Start it with:
      <code>cd backend && uvicorn main:app --reload</code>
    </div>

    <div class="search-section">
      <SearchBar @search="handleSearch"/>
    </div>

    <div class="content-layout">
      <aside class="sidebar">
        <SearchFilters :disabled="isLoading" @update="handleFilterUpdate"/>
      </aside>

      <main class="results-area">
        <!-- Initial state -->
        <div v-if="!hasSearched && !isLoading" class="placeholder-state">
          <div class="placeholder-icon">🔬</div>
          <p>Search across <strong>1.7 million+</strong> arXiv STEM papers</p>
          <p class="placeholder-sub">Physics, Mathematics, Computer Science, Biology, and more</p>
        </div>

        <!-- Loading -->
        <div v-else-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Searching papers...</p>
        </div>

        <!-- Error -->
        <div v-else-if="errorMessage" class="error-state">
          <span class="error-icon">⚠️</span>
          <p>{{ errorMessage }}</p>
          <p class="error-sub">Ensure the backend is running:
            <code>uvicorn main:app --reload</code>
          </p>
        </div>

        <!-- No results -->
        <div v-else-if="results.length === 0" class="no-results">
          <p>No papers found for "<strong>{{ currentQuery }}</strong>".</p>
          <p class="no-results-sub">Try broader search terms or adjust the year range.</p>
        </div>

        <!-- Results -->
        <div v-else class="results-list">
          <div class="results-header">
            <p class="stats">
              About <strong>{{ formattedTotal }}</strong> results
              <span v-if="currentQuery"> for "<em>{{ currentQuery }}</em>"</span>
              &nbsp;— Page {{ currentPage }} of {{ totalPages }}
            </p>
          </div>

          <div v-for="paper in results" :key="paper.id" class="result-card">
            <div class="card-header">
              <!-- null-safe: won't crash on empty categories -->
              <span class="category-tag">{{ primaryCategory(paper.categories) }}</span>
              <span class="date">{{ paper.update_date }}</span>
            </div>

            <h2 class="paper-title">
              <a
                  :href="`https://arxiv.org/abs/${paper.id}`"
                  target="_blank"
                  rel="noopener noreferrer"
                  v-html="paper.title"
              ></a>
            </h2>

            <div class="authors">{{ paper.authors }}</div>

            <p class="abstract"
               v-html="paper.snippet || paper.abstract.substring(0, 280) + '...'">
            </p>

            <div class="card-footer">
              <span class="id-badge">arXiv: {{ paper.id }}</span>
              <a
                  :href="`https://arxiv.org/pdf/${paper.id}`"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="pdf-btn"
              >PDF ⬇</a>
            </div>
          </div>

          <!-- Pagination -->
          <div class="pagination" v-if="totalPages > 1">
            <button class="page-btn" :disabled="currentPage === 1"
                    @click="goToPage(currentPage - 1)">← Prev
            </button>

            <button v-if="visiblePages[0] > 1" class="page-btn"
                    @click="goToPage(1)">1
            </button>
            <span v-if="visiblePages[0] > 2" class="ellipsis">…</span>

            <button v-for="page in visiblePages" :key="page" class="page-btn"
                    :class="{ active: page === currentPage }"
                    @click="goToPage(page)">{{ page }}
            </button>

            <span v-if="visiblePages[visiblePages.length - 1] < totalPages - 1"
                  class="ellipsis">…</span>
            <button v-if="visiblePages[visiblePages.length - 1] < totalPages"
                    class="page-btn" @click="goToPage(totalPages)">{{ totalPages }}
            </button>

            <button class="page-btn" :disabled="currentPage === totalPages"
                    @click="goToPage(currentPage + 1)">Next →
            </button>
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
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #2c3e50;
  flex-wrap: wrap;
  justify-content: center;
}

.brand h1 {
  font-size: 2rem;
  margin: 0;
}

.brand .icon {
  font-size: 2rem;
}

.subtitle {
  font-size: 0.9rem;
  color: #888;
  margin-left: 4px;
  align-self: flex-end;
  padding-bottom: 4px;
}

.backend-banner {
  background: #fff3cd;
  border: 1px solid #ffc107;
  color: #856404;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  margin-bottom: 20px;
  text-align: center;
}

.backend-banner code {
  background: rgba(0, 0, 0, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85rem;
}

.search-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

.content-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 30px;
  align-items: start;
}

.placeholder-state, .loading-state, .error-state, .no-results {
  text-align: center;
  margin-top: 60px;
  color: #888;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.placeholder-state p {
  font-size: 1.1rem;
  color: #555;
  margin: 4px 0;
}

.placeholder-sub {
  font-size: 0.9rem;
  color: #aaa !important;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 4px solid #e0e0e0;
  border-top-color: #42b983;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  color: #c0392b;
}

.error-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 8px;
}

.error-sub {
  font-size: 0.85rem;
  color: #888;
  margin-top: 8px;
}

.error-sub code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.no-results-sub {
  font-size: 0.9rem;
  color: #aaa;
}

.results-header {
  margin-bottom: 16px;
}

.stats {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.stats em {
  font-style: italic;
  color: #444;
}

.result-card {
  background: white;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 16px;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #42b983;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 0.85rem;
  color: #666;
}

.category-tag {
  background: #eef2f5;
  padding: 3px 10px;
  border-radius: 4px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.8rem;
}

.paper-title {
  margin: 0 0 8px 0;
  font-size: 1.15rem;
  line-height: 1.4;
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
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.abstract {
  color: #4d5156;
  line-height: 1.65;
  font-size: 0.92rem;
  margin-bottom: 14px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #888;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.id-badge {
  font-family: monospace;
  font-size: 0.78rem;
}

.pdf-btn {
  background-color: #b31b1b;
  color: white;
  text-decoration: none;
  padding: 5px 12px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.82rem;
  transition: background 0.2s;
}

.pdf-btn:hover {
  background-color: #900000;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.page-btn {
  padding: 7px 13px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.15s;
  color: #333;
}

.page-btn:hover:not(:disabled):not(.active) {
  border-color: #42b983;
  color: #42b983;
}

.page-btn.active {
  background: #42b983;
  border-color: #42b983;
  color: white;
  font-weight: 700;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ellipsis {
  color: #aaa;
  padding: 0 4px;
}

:deep(em) {
  font-weight: bold;
  font-style: normal;
  background: #fff3cd;
  color: #856404;
  padding: 0 3px;
  border-radius: 3px;
}

@media (max-width: 768px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    order: -1;
  }
}
</style>
