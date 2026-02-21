<template>
  <div>
    <div class="section-header">
      <h1 class="section-title">🔢 基本玩法分析</h1>
      <PeriodSelector v-model="store.periodRange" @update:model-value="store.setPeriodRange" />
    </div>

    <div v-if="store.loading" class="loading-overlay">
      <div class="spinner"></div>載入中...
    </div>

    <template v-else-if="store.basic">
      <div class="grid-2">
        <!-- Top 10 排名 -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">🏆 Top 10 推薦號碼</span>
            <span class="badge badge-primary">{{ store.basic.method }}</span>
          </div>
          <div class="top-list">
            <div v-for="(item, i) in top10" :key="item[0]" class="top-item">
              <span :class="['rank', rankClass(i)]">{{ i + 1 }}</span>
              <span :class="['number-ball', rankBallClass(i)]">{{ item[0] }}</span>
              <div class="score-bar-wrap">
                <div class="score-bar" :style="{ width: scorePct(item[1]) + '%' }"></div>
              </div>
              <span class="score-val">{{ typeof item[1] === 'number' ? item[1].toFixed(1) : item[1] }}</span>
            </div>
          </div>
        </div>

        <!-- 頻率圖表 -->
        <div class="card">
          <FrequencyChart
            type="bar"
            title="號碼頻率分佈 (01-80)"
            :labels="chartLabels"
            :datasets="chartDatasets"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { usePredictionStore } from '../stores/prediction.js';
import PeriodSelector from '../components/PeriodSelector.vue';
import FrequencyChart from '../components/FrequencyChart.vue';

const store = usePredictionStore();

const top10 = computed(() => store.basic?.predictions?.slice(0, 10) || []);

const maxScore = computed(() => {
  if (!top10.value.length) return 1;
  return top10.value[0][1] || 1;
});

function scorePct(score) {
  return Math.round((score / maxScore.value) * 100);
}

function rankClass(i) {
  return ['gold', 'silver', 'bronze'][i] || '';
}

function rankBallClass(i) {
  return ['gold', 'silver', 'bronze', 'default', 'default', 'default', 'default', 'default', 'default', 'default'][i];
}

const chartLabels = computed(() => {
  if (!store.basic?.all_stats) return [];
  return Object.keys(store.basic.all_stats).sort();
});

const chartDatasets = computed(() => {
  if (!store.basic?.all_stats) return [];
  const stats = store.basic.all_stats;
  const labels = chartLabels.value;
  return [
    {
      label: '出現次數',
      data: labels.map((l) => stats[l]?.count || 0),
      backgroundColor: labels.map((l) => {
        const isTop = top10.value.some(([num]) => num === l);
        return isTop ? '#3498db' : '#bdc3c7';
      }),
      borderRadius: 2,
    },
  ];
});
</script>

<style scoped>
.top-list {
  display: flex;
  flex-direction: column;
  gap: var(--gap-sm);
}

.top-item {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
  padding: 6px 0;
}

.rank {
  width: 24px;
  font-weight: 700;
  font-size: 0.9rem;
  text-align: center;
}

.rank.gold { color: #d35400; }
.rank.silver { color: #7f8c8d; }
.rank.bronze { color: #e17055; }

.score-bar-wrap {
  flex: 1;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.score-bar {
  height: 100%;
  background: var(--primary);
  border-radius: 4px;
  transition: width 0.4s ease;
}

.score-val {
  width: 48px;
  text-align: right;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}
</style>
