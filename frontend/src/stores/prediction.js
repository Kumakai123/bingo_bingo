import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api.js';

export const usePredictionStore = defineStore('prediction', () => {
    // State
    const periodRange = ref(5);
    const basic = ref(null);
    const dashboardBasic = ref(null);
    const superNumber = ref(null);
    const highLow = ref(null);
    const oddEven = ref(null);
    const coOccurrence = ref(null);
    const tailNumber = ref(null);
    const zoneDistribution = ref(null);
    const coldHotCycle = ref(null);
    const consecutive = ref(null);
    const smartPick = ref(null);
    const latestDraws = ref([]);
    const loading = ref(false);
    const refreshing = ref(false);
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
            const [predRes, drawsRes, dashboardBasicRes] = await Promise.all([
                api.getAllPredictions(periodRange.value),
                api.getLatestDraws(10),
                api.getBasicPrediction(periodRange.value, 5),
            ]);
            const data = predRes.data;
            basic.value = data.basic;
            dashboardBasic.value = dashboardBasicRes.data;
            superNumber.value = data.super_number;
            highLow.value = data.high_low;
            oddEven.value = data.odd_even;
            coOccurrence.value = data.co_occurrence || null;
            tailNumber.value = data.tail_number || null;
            zoneDistribution.value = data.zone_distribution || null;
            coldHotCycle.value = data.cold_hot_cycle || null;
            consecutive.value = data.consecutive || null;
            latestDraws.value = drawsRes.data;
        } catch (e) {
            error.value = e.message;
            console.error('fetchAll failed:', e);
        } finally {
            loading.value = false;
        }
    }

    async function fetchSmartPick(pickCount = 10, starLevel = 3) {
        try {
            const res = await api.getSmartPick(periodRange.value, pickCount, starLevel);
            smartPick.value = res.data;
            return res.data;
        } catch (e) {
            console.error('fetchSmartPick failed:', e);
            throw e;
        }
    }

    function setPeriodRange(range) {
        const parsed = Number(range);
        if (!Number.isFinite(parsed) || parsed < 5) return;
        periodRange.value = parsed;
        fetchAll();
    }

    async function manualRefresh() {
        refreshing.value = true;
        error.value = null;
        try {
            const res = await api.triggerRefresh();
            const serverTs = res?.data?.last_updated;
            if (serverTs) {
                knownTimestamp = serverTs;
                lastUpdated.value = serverTs;
            }
            await fetchAll();
            return res?.data;
        } catch (e) {
            error.value = e.message;
            console.error('manualRefresh failed:', e);
            throw e;
        } finally {
            refreshing.value = false;
        }
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
        dashboardBasic,
        superNumber,
        highLow,
        oddEven,
        coOccurrence,
        tailNumber,
        zoneDistribution,
        coldHotCycle,
        consecutive,
        smartPick,
        latestDraws,
        loading,
        refreshing,
        error,
        lastUpdated,
        fetchAll,
        fetchSmartPick,
        manualRefresh,
        setPeriodRange,
        startPolling,
        stopPolling,
    };
});
