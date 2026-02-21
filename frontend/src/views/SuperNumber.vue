<template>
  <div>
    <div class="section-header">
      <h1 class="section-title">⭐ 超級號碼分析</h1>
      <PeriodSelector v-model="store.periodRange" @update:model-value="store.setPeriodRange" />
    </div>

    <div v-if="store.loading" class="loading-overlay">
      <div class="spinner"></div>載入中...
    </div>

    <template v-else-if="store.superNumber">
      <div class="grid-2">
        <!-- Top 10 排名 -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">🏆 Top 10 超級號碼</span>
          </div>
          <div class="top-list">
            <div v-for="(item, i) in top10" :key="item[0]" class="top-item">
              <span :class="['rank', rankClass(i)]">{{ i + 1 }}</span>
              <span class="number-ball super" style="width:36px;height:36px;font-size:0.85rem;">
                {{ item[0] }}
              </span>
              <div class="freq-info">
                <span class="freq-count">{{ item[1] }} 次</span>
                <div class="score-bar-wrap">
                  <div
                    class="score-bar"
                    :style="{ width: scorePct(item[1]) + '%', background: 'var(--accent)' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 頻率圖表 -->
        <div class="card">
          <FrequencyChart
            type="bar"
            title="超級號碼出現頻率"
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

const top10 = computed(() => store.superNumber?.predictions?.slice(0, 10) || []);

const maxFreq = computed(() => {
  if (!top10.value.length) return 1;
  return top10.value[0][1] || 1;
});

function scorePct(freq) {
  return Math.round((freq / maxFreq.value) * 100);
}

function rankClass(i) {
  return ['gold', 'silver', 'bronze'][i] || '';
}

const chartLabels = computed(() => {
  if (!store.superNumber?.all_stats) return [];
  return Object.keys(store.superNumber.all_stats).sort();
});

const chartDatasets = computed(() => {
  if (!store.superNumber?.all_stats) return [];
  const stats = store.superNumber.all_stats;
  const labels = chartLabels.value;
  return [
    {
      label: '被選為超級號碼次數',
      data: labels.map((l) => stats[l] || 0),
      backgroundColor: labels.map((l) => {
        const isTop = top10.value.some(([num]) => num === l);
        return isTop ? '#e74c3c' : '#bdc3c7';
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

.freq-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--gap-md);
}

.freq-count {
  font-size: 0.85rem;
  font-weight: 500;
  min-width: 50px;
}

.score-bar-wrap {
  flex: 1;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.score-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}
</style>
