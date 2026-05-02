<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const query = ref('');
const history = ref([]);
const showHistory = ref(false);
const emit = defineEmits(['search']);

// Load history from LocalStorage on startup
onMounted(() => {
  const saved = localStorage.getItem('searchHistory');
  if (saved) {
    try {
      history.value = JSON.parse(saved);
    } catch {
      history.value = [];
    }
  }
  // Close dropdown when clicking outside
  document.addEventListener('click', handleOutsideClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick);
});

const containerRef = ref(null);
const handleOutsideClick = (event) => {
  if (containerRef.value && !containerRef.value.contains(event.target)) {
    showHistory.value = false;
  }
};

const handleSearch = () => {
  const trimmed = query.value.trim();
  if (!trimmed) {
    return;
  }

  // Save to history (case-insensitive dedup, keep last 5)
  const lowerTrimmed = trimmed.toLowerCase();
  history.value = history.value.filter((h) => h.toLowerCase() !== lowerTrimmed);
  history.value.unshift(trimmed);
  if (history.value.length > 5) {
    history.value = history.value.slice(0, 5);
  }

  localStorage.setItem('searchHistory', JSON.stringify(history.value));
  showHistory.value = false;
  emit('search', trimmed);
};

const selectHistory = (item) => {
  query.value = item;
  handleSearch();
};

const clearHistory = () => {
  history.value = [];
  localStorage.removeItem('searchHistory');
};
</script>

<template>
  <div class="search-container" ref="containerRef">
    <div class="input-wrapper">
      <input
          v-model="query"
          @keyup.enter="handleSearch"
          @focus="showHistory = true"
          placeholder="Search for 'agentic ai', 'neural networks', 'quantum computing'..."
          class="search-input"
          autocomplete="off"
      />
      <button @click="handleSearch" class="search-btn">Search</button>
    </div>

    <div v-if="showHistory && history.length" class="history-dropdown">
      <div class="history-header">
        <span>Recent searches</span>
        <button @click.stop="clearHistory" class="clear-btn">Clear</button>
      </div>
      <div
          v-for="item in history"
          :key="item"
          @click="selectHistory(item)"
          class="history-item"
      >
        🕒 {{ item }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
}

.input-wrapper {
  display: flex;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.search-input {
  flex: 1;
  padding: 16px;
  border: none;
  font-size: 16px;
  outline: none;
}

.search-btn {
  padding: 0 30px;
  background-color: #42b983;
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.search-btn:hover {
  background-color: #3aa876;
}

.history-dropdown {
  position: absolute;
  width: 100%;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 8px 8px;
  z-index: 100;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  font-size: 0.8rem;
  color: #999;
  border-bottom: 1px solid #f0f0f0;
}

.clear-btn {
  background: none;
  border: none;
  color: #42b983;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0;
}

.history-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f5f5f5;
  text-align: left;
  font-size: 0.95rem;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item:hover {
  background-color: #f5f5f5;
}
</style>
