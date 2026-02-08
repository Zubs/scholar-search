<script setup>
import { reactive } from 'vue';

const filters = reactive({
  yearStart: 1800,
  yearEnd: 2025,
  sortBy: 'relevance'
});

const emit = defineEmits(['update']);

const applyFilters = () => {
  emit('update', { ...filters });
};
</script>

<template>
  <div class="filters-panel">
    <h3>Filters</h3>

    <div class="filter-group">
      <label>Sort By</label>
      <select v-model="filters.sortBy" @change="applyFilters">
        <option value="relevance">Relevance</option>
        <option value="date_desc">Newest First</option>
        <option value="date_asc">Oldest First</option>
      </select>
    </div>

    <div class="filter-group">
      <label>Year Range</label>
      <div class="range-inputs">
        <input type="number" v-model="filters.yearStart" placeholder="From"/>
        <span>-</span>
        <input type="number" v-model="filters.yearEnd" placeholder="To"/>
      </div>
      <button @click="applyFilters" class="apply-btn">Apply</button>
    </div>
  </div>
</template>

<style scoped>
.filters-panel {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  height: fit-content;
}

.filter-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.range-inputs {
  display: flex;
  gap: 5px;
  align-items: center;
}

input, select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.apply-btn {
  margin-top: 10px;
  background: #2c3e50;
  color: white;
  border: none;
  padding: 8px;
  cursor: pointer;
}
</style>
