<script setup>
import { ref, onMounted } from 'vue';

const query = ref('');
const history = ref([]);
const showHistory = ref(false);

const emit = defineEmits(['search']);

// Load history from LocalStorage on startup
onMounted(() => {
  const saved = localStorage.getItem('searchHistory');
  if (saved) {
    history.value = JSON.parse(saved);
  }
});

const handleSearch = () => {
  if (!query.value.trim()) {
    return;
  }

  // Save to history (unique values only, keep last 5)
  if (!history.value.includes(query.value)) {
    history.value.unshift(query.value);
    if (history.value.length > 5) {
      history.value.pop();
    }

    localStorage.setItem('searchHistory', JSON.stringify(history.value));
  }

  showHistory.value = false;
  emit('search', query.value);
};

const selectHistory = (item) => {
  query.value = item;
  handleSearch();
};
</script>

<template>
  <div class="search-container">
    <div class="input-wrapper">
      <input
          v-model="query"
          @keyup.enter="handleSearch"
          @focus="showHistory = true"
          placeholder="Search for 'agentic ai', 'neural networks'..."
          class="search-input"
      />
      <button @click="handleSearch" class="search-btn">Search</button>
    </div>

    <div v-if="showHistory && history.length" class="history-dropdown">
      <div v-for="item in history" :key="item" @click="selectHistory(item)" class="history-item">
        🕒 {{ item }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.input-wrapper {
  display: flex;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-btn {
  padding: 0 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

.history-dropdown {
  position: absolute;
  width: 100%;
  background: white;
  border: 1px solid #ddd;
  z-index: 10;
  margin-top: 5px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.history-item {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  text-align: left;
}

.history-item:hover {
  background-color: #f5f5f5;
}
</style>
