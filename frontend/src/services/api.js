import axios from 'axios';

const baseURL = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api`;

const api = axios.create({
    baseURL,
    timeout: 10000,
});

export default {
    // 開獎資料
    getLatestDraws(limit = 20) {
        return api.get('/draws/latest', { params: { limit } });
    },

    getDrawByTerm(term) {
        return api.get(`/draws/${term}`);
    },

    // 預測
    getAllPredictions(periodRange = 30) {
        return api.get('/predictions/all', { params: { period_range: periodRange } });
    },

    getBasicPrediction(periodRange = 30, topN = 10) {
        return api.get('/predictions/basic', { params: { period_range: periodRange, top_n: topN } });
    },

    getBasicBatch(periodRanges = [10, 20, 30, 50, 100]) {
        return api.get('/predictions/basic/batch', { params: { period_ranges: periodRanges } });
    },

    getSuperNumber(periodRange = 30, topN = 10) {
        return api.get('/predictions/super-number', { params: { period_range: periodRange, top_n: topN } });
    },

    getHighLow(periodRange = 30) {
        return api.get('/predictions/high-low', { params: { period_range: periodRange } });
    },

    getOddEven(periodRange = 30) {
        return api.get('/predictions/odd-even', { params: { period_range: periodRange } });
    },

    // 狀態
    getLastUpdated() {
        return api.get('/status/last-updated');
    },
};
