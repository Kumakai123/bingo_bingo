import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api.js';

export const useSimulationStore = defineStore('simulation', () => {
    const bets = ref([]);
    const totalBets = ref(0);
    const stats = ref(null);
    const loading = ref(false);
    const placing = ref(false);
    const settling = ref(false);
    const error = ref(null);

    // Widget state
    const widgetOpen = ref(false);
    const widgetPreset = ref(null);

    function openWidget(preset = null) {
        widgetPreset.value = preset;
        widgetOpen.value = true;
    }

    function closeWidget() {
        widgetOpen.value = false;
        widgetPreset.value = null;
    }

    async function placeBet(data) {
        placing.value = true;
        error.value = null;
        try {
            const res = await api.placeBet(data);
            await fetchBets();
            await fetchStats();
            return res.data;
        } catch (e) {
            error.value = e.response?.data?.detail || e.message;
            throw e;
        } finally {
            placing.value = false;
        }
    }

    async function fetchBets(status = null, limit = 50, offset = 0) {
        loading.value = true;
        try {
            const res = await api.getBets(status, limit, offset);
            bets.value = res.data.bets;
            totalBets.value = res.data.total;
        } catch (e) {
            console.error('fetchBets failed:', e);
        } finally {
            loading.value = false;
        }
    }

    async function fetchStats() {
        try {
            const res = await api.getBetStats();
            stats.value = res.data;
        } catch (e) {
            console.error('fetchStats failed:', e);
        }
    }

    async function settleBets() {
        settling.value = true;
        error.value = null;
        try {
            const res = await api.settleBets();
            await fetchBets();
            await fetchStats();
            return res.data;
        } catch (e) {
            error.value = e.response?.data?.detail || e.message;
            throw e;
        } finally {
            settling.value = false;
        }
    }

    async function cancelBet(betId) {
        try {
            await api.cancelBet(betId);
            await fetchBets();
            await fetchStats();
        } catch (e) {
            error.value = e.response?.data?.detail || e.message;
            throw e;
        }
    }

    return {
        bets,
        totalBets,
        stats,
        loading,
        placing,
        settling,
        error,
        widgetOpen,
        widgetPreset,
        openWidget,
        closeWidget,
        placeBet,
        fetchBets,
        fetchStats,
        settleBets,
        cancelBet,
    };
});
