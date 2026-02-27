<template>
  <div>
    <div class="section-header">
      <h1 class="section-title">🎱 BINGO BINGO 分析儀表板</h1>
      <PeriodSelector v-model="store.periodRange" @update:model-value="store.setPeriodRange" />
    </div>

    <div v-if="store.loading" class="loading-overlay">
      <div class="spinner"></div>載入資料中...
    </div>

    <template v-else>
      <!-- 五張快速預覽卡片 -->
      <div class="grid-5 mb">
        <PredictionCard
          title="智慧選號"
          icon="🧠"
          type="basic"
          link="/smart-pick"
          :numbers="smartPickTop3"
          numbers-label="綜合推薦 Top 3"
          :loading="smartPickLoading"
        />
        <PredictionCard
          title="基本玩法"
          icon="🔢"
          type="basic"
          link="/basic"
          :numbers="basicTop5"
          :numbers-label="basicNumbersLabel"
          :loading="store.loading"
        />
        <PredictionCard
          title="超級號碼"
          icon="⭐"
          type="super"
          link="/super"
          :numbers="superTop5"
          :loading="store.loading"
        />
        <PredictionCard
          title="猜大小"
          icon="📊"
          type="highlow"
          link="/trend"
          :prediction="store.highLow"
          :loading="store.loading"
        />
        <PredictionCard
          title="猜單雙"
          icon="🎯"
          type="oddeven"
          link="/trend"
          :prediction="store.oddEven"
          :loading="store.loading"
        />
      </div>

      <!-- 歷史開獎 -->
      <HistoryTable :draws="store.latestDraws" />
    </template>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { usePredictionStore } from '../stores/prediction.js';
import PeriodSelector from '../components/PeriodSelector.vue';
import PredictionCard from '../components/PredictionCard.vue';
import HistoryTable from '../components/HistoryTable.vue';

const store = usePredictionStore();
const smartPickLoading = ref(false);

const basicNumbersLabel = computed(() => `近 ${store.periodRange} 期分析號碼`);

const basicTop5 = computed(() => {
  if (!store.dashboardBasic?.predictions) return [];
  return store.dashboardBasic.predictions.slice(0, 5).map((item, i) => ({
    number: item.number,
    score: item.score,
    rank: item.rank ?? i + 1,
  }));
});

const superTop5 = computed(() => {
  if (!store.superNumber?.predictions) return [];
  return store.superNumber.predictions.slice(0, 5).map(([num, freq], i) => ({
    number: num,
    score: freq,
    rank: i + 1,
  }));
});

const smartPickTop3 = computed(() => {
  if (!store.smartPick?.picks) return [];
  return store.smartPick.picks.slice(0, 3).map((p, i) => ({
    number: p.number,
    score: p.final_score,
    rank: i + 1,
  }));
});

async function loadSmartPick() {
  smartPickLoading.value = true;
  try {
    await store.fetchSmartPick(10, 3);
  } catch {
    // silent
  } finally {
    smartPickLoading.value = false;
  }
}

watch(() => store.periodRange, () => {
  loadSmartPick();
});

onMounted(() => {
  loadSmartPick();
});
</script>

<style scoped>
.mb {
  margin-bottom: var(--gap-lg);
}
</style>
