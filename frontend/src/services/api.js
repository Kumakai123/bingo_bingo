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
    getAllPredictions(periodRange = 5) {
        return api.get('/predictions/all', { params: { period_range: periodRange } });
    },

    getBasicPrediction(periodRange = 5, topN = 10) {
        return api.get('/predictions/basic', { params: { period_range: periodRange, top_n: topN } });
    },

    getBasicBatch(periodRanges = [5, 10, 20, 30, 50, 100]) {
        return api.get('/predictions/basic/batch', { params: { period_ranges: periodRanges } });
    },

    getSuperNumber(periodRange = 5, topN = 10) {
        return api.get('/predictions/super-number', { params: { period_range: periodRange, top_n: topN } });
    },

    getHighLow(periodRange = 5) {
        return api.get('/predictions/high-low', { params: { period_range: periodRange } });
    },

    getOddEven(periodRange = 5) {
        return api.get('/predictions/odd-even', { params: { period_range: periodRange } });
    },

    // 進階分析
    getCoOccurrence(periodRange = 30, topN = 15, targetNumber = null) {
        const params = { period_range: periodRange, top_n: topN };
        if (targetNumber) params.target_number = targetNumber;
        return api.get('/predictions/co-occurrence', { params });
    },

    getTailNumber(periodRange = 30, topN = 3) {
        return api.get('/predictions/tail-number', { params: { period_range: periodRange, top_n: topN } });
    },

    getZoneDistribution(periodRange = 30) {
        return api.get('/predictions/zone-distribution', { params: { period_range: periodRange } });
    },

    getColdHotCycle(periodRange = 100, recentWindow = 10, topN = 10) {
        return api.get('/predictions/cold-hot-cycle', { params: { period_range: periodRange, recent_window: recentWindow, top_n: topN } });
    },

    getConsecutive(periodRange = 30) {
        return api.get('/predictions/consecutive', { params: { period_range: periodRange } });
    },

    getSmartPick(periodRange = 30, pickCount = 10, starLevel = 3) {
        return api.get('/predictions/smart-pick', { params: { period_range: periodRange, pick_count: pickCount, star_level: starLevel } });
    },

    // 狀態
    getLastUpdated() {
        return api.get('/status/last-updated');
    },

    triggerRefresh() {
        return api.post('/status/refresh');
    },
};
