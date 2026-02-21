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
      <!-- 四張快速預覽卡片 -->
      <div class="grid-4 mb">
        <PredictionCard
          title="基本玩法"
          icon="🔢"
          type="basic"
          link="/basic"
          :numbers="basicTop5"
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
import { computed } from 'vue';
import { usePredictionStore } from '../stores/prediction.js';
import PeriodSelector from '../components/PeriodSelector.vue';
import PredictionCard from '../components/PredictionCard.vue';
import HistoryTable from '../components/HistoryTable.vue';

const store = usePredictionStore();

const basicTop5 = computed(() => {
  if (!store.basic?.predictions) return [];
  return store.basic.predictions.slice(0, 5).map(([num, score], i) => ({
    number: num,
    score,
    rank: i + 1,
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
</script>

<style scoped>
.mb {
  margin-bottom: var(--gap-lg);
}
</style>
