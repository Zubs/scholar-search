<script setup>
import { reactive } from 'vue';

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
});

// Sort values MUST match the backend's expected strings: Relevance | Newest | Oldest
const filters = reactive({
  yearStart: 1991,
  yearEnd: 2026,
  sortBy: 'Relevance',
});

const emit = defineEmits(['update']);
const applyFilters = () => {
  if (filters.yearStart > filters.yearEnd) {
    alert('Start year cannot be greater than end year.');

    return;
  }

  emit('update', {...filters});
};
</script>

<template>
  <div class="filters-panel">
    <h3>Filters</h3>

    <div class="filter-group">
      <label>Sort By</label>
      <select v-model="filters.sortBy" @change="applyFilters" :disabled="disabled">
        <option value="Relevance">Relevance</option>
        <option value="Newest">Newest First</option>
        <option value="Oldest">Oldest First</option>
      </select>
    </div>

    <div class="filter-group">
      <label>Year Range</label>
      <div class="range-inputs">
        <input
            type="number"
            v-model.number="filters.yearStart"
            placeholder="From"
            :min="1991"
            :max="2026"
            :disabled="disabled"
        />
        <span>–</span>
        <input
            type="number"
            v-model.number="filters.yearEnd"
            placeholder="To"
            :min="1991"
            :max="2026"
            :disabled="disabled"
        />
      </div>
      <button @click="applyFilters" class="apply-btn" :disabled="disabled">
        Apply Filters
      </button>
    </div>
  </div>
</template>

<style scoped>
.filters-panel {
  background: white;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  height: fit-content;
}

.filters-panel h3 {
  margin: 0 0 20px 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #2c3e50;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #555;
}

.range-inputs {
  display: flex;
  gap: 6px;
  align-items: center;
}

.range-inputs span {
  color: #999;
}

input,
select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
  font-size: 0.9rem;
}

.range-inputs input {
  width: 80px;
  flex: 1;
}

.apply-btn {
  margin-top: 4px;
  background: #2c3e50;
  color: white;
  border: none;
  padding: 9px;
  cursor: pointer;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.apply-btn:hover:not(:disabled) {
  background: #3d5166;
}

.apply-btn:disabled,
select:disabled,
input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
