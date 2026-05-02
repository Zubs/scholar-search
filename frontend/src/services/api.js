import axios from 'axios';

const API_URL = 'http://localhost:8000';

/**
 * Search for papers using the ScholarSearch backend.
 * @param {string} query - The search query string
 * @param {Object} filters - Filter options (yearStart, yearEnd, sortBy)
 * @param {number} page - Page number (1-indexed)
 * @param {number} pageSize - Number of results per page
 * @returns {Promise<{total: number, page: number, total_pages: number, results: Array}>}
 */
export const searchPapers = async (
    query,
    filters = {},
    page = 1,
    pageSize = 20
) => {
    try {
        const response = await axios.get(`${API_URL}/search`, {
            params: {
                q: query,
                year_start: filters.yearStart ?? 1991,
                year_end: filters.yearEnd ?? 2026,
                sort_by: filters.sortBy ?? 'Relevance',
                page,
                page_size: pageSize,
            },
        });

        return response.data;
    } catch (error) {
        if (error.response) {
            // Server responded with an error status
            const detail = error.response.data?.detail || 'Unknown server error';
            throw new Error(`Search failed: ${detail}`);
        } else if (error.request) {
            // Request was made but no response received
            throw new Error('Cannot reach the server. Is the backend running on port 8000?');
        } else {
            throw new Error(`Request error: ${error.message}`);
        }
    }
};

/**
 * Check if the backend API is reachable.
 * @returns {Promise<boolean>}
 */
export const checkHealth = async () => {
    try {
        const response = await axios.get(`${API_URL}/health`, {timeout: 3000});

        return response.data?.status === 'ok';
    } catch {
        return false;
    }
};
