import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const searchPapers = async (query, filters = {}, page = 1) => {
    try {
        const response = await axios.get(`${API_URL}/search`, {
            params: {
                q: query,
                year_start: filters.yearStart,
                year_end: filters.yearEnd,
                sort_by: filters.sortBy,
                page: page,
                limit: 12
            }
        });

        return response.data;
    } catch (error) {
        console.error("Search failed:", error);

        return { results: [], total: 0 };
    }
};
