import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api.js';

export const usePredictionStore = defineStore('prediction', () => {
    // State
    const periodRange = ref(30);
    const basic = ref(null);
    const superNumber = ref(null);
    const highLow = ref(null);
    const oddEven = ref(null);
    const latestDraws = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const lastUpdated = ref(null);

    // Polling
    let pollingTimer = null;
    let knownTimestamp = null;

    // Actions
    async function fetchAll() {
        loading.value = true;
        error.value = null;
        try {
            const [predRes, drawsRes] = await Promise.all([
                api.getAllPredictions(periodRange.value),
                api.getLatestDraws(10),
            ]);
            const data = predRes.data;
            basic.value = data.basic;
            superNumber.value = data.super_number;
            highLow.value = data.high_low;
            oddEven.value = data.odd_even;
            latestDraws.value = drawsRes.data;
        } catch (e) {
            error.value = e.message;
            console.error('fetchAll failed:', e);
        } finally {
            loading.value = false;
        }
    }

    function setPeriodRange(range) {
        periodRange.value = range;
        fetchAll();
    }

    // Polling: every 30s check /api/status/last-updated
    async function checkForUpdates() {
        try {
            const res = await api.getLastUpdated();
            const serverTs = res.data.last_updated;
            if (serverTs && serverTs !== knownTimestamp) {
                knownTimestamp = serverTs;
                lastUpdated.value = serverTs;
                await fetchAll();
            }
        } catch {
            // silent — backend might be down
        }
    }

    function startPolling() {
        if (pollingTimer) return;
        pollingTimer = setInterval(checkForUpdates, 30000);
    }

    function stopPolling() {
        if (pollingTimer) {
            clearInterval(pollingTimer);
            pollingTimer = null;
        }
    }

    return {
        periodRange,
        basic,
        superNumber,
        highLow,
        oddEven,
        latestDraws,
        loading,
        error,
        lastUpdated,
        fetchAll,
        setPeriodRange,
        startPolling,
        stopPolling,
    };
});
