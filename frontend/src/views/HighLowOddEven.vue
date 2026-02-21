<template>
  <div>
    <div class="section-header">
      <h1 class="section-title">📊 猜大小 / 🎯 猜單雙</h1>
      <PeriodSelector v-model="store.periodRange" @update:model-value="store.setPeriodRange" />
    </div>

    <div v-if="store.loading" class="loading-overlay">
      <div class="spinner"></div>載入中...
    </div>

    <template v-else>
      <div class="grid-2">
        <!-- 猜大小 -->
        <div class="card" v-if="store.highLow">
          <div class="card-header">
            <span class="card-title">📊 猜大小分析</span>
          </div>

          <div class="trend-result">
            <div class="prediction-big">
              <span class="prediction-label">預測結果</span>
              <span :class="['prediction-value', store.highLow.prediction === '大' ? 'text-primary' : 'text-success']">
                {{ store.highLow.prediction || '—' }}
              </span>
            </div>
            <div class="confidence-section">
              <span class="confidence-label">信心度</span>
              <div class="confidence-bar large">
                <div
                  class="confidence-fill"
                  :style="{
                    width: (store.highLow.confidence || 0) * 100 + '%',
                    background: store.highLow.confidence >= 0.6 ? 'var(--secondary)' : 'var(--warning)',
                  }"
                ></div>
              </div>
              <span class="confidence-pct">{{ ((store.highLow.confidence || 0) * 100).toFixed(0) }}%</span>
            </div>
            <p class="reason">{{ store.highLow.reason }}</p>
          </div>

          <div class="stats-row" v-if="store.highLow.statistics">
            <div class="stat">
              <span class="stat-val text-primary">{{ store.highLow.statistics.high_count }}</span>
              <span class="stat-label">大</span>
            </div>
            <div class="stat">
              <span class="stat-val text-success">{{ store.highLow.statistics.low_count }}</span>
              <span class="stat-label">小</span>
            </div>
            <div class="stat">
              <span class="stat-val text-muted">{{ store.highLow.statistics.tie_count }}</span>
              <span class="stat-label">平</span>
            </div>
          </div>

          <div class="chart-section">
            <FrequencyChart
              type="doughnut"
              title="大小比例"
              :labels="['大', '小', '平']"
              :datasets="highLowDatasets"
            />
          </div>
        </div>

        <!-- 猜單雙 -->
        <div class="card" v-if="store.oddEven">
          <div class="card-header">
            <span class="card-title">🎯 猜單雙分析</span>
          </div>

          <div class="trend-result">
            <div class="prediction-big">
              <span class="prediction-label">預測結果</span>
              <span :class="['prediction-value', store.oddEven.prediction === '單' ? 'text-purple' : 'text-warning']">
                {{ store.oddEven.prediction || '—' }}
              </span>
            </div>
            <div class="confidence-section">
              <span class="confidence-label">信心度</span>
              <div class="confidence-bar large">
                <div
                  class="confidence-fill"
                  :style="{
                    width: (store.oddEven.confidence || 0) * 100 + '%',
                    background: store.oddEven.confidence >= 0.6 ? 'var(--secondary)' : 'var(--warning)',
                  }"
                ></div>
              </div>
              <span class="confidence-pct">{{ ((store.oddEven.confidence || 0) * 100).toFixed(0) }}%</span>
            </div>
            <p class="reason">{{ store.oddEven.reason }}</p>
          </div>

          <div class="stats-row" v-if="store.oddEven.statistics">
            <div class="stat">
              <span class="stat-val text-purple">{{ store.oddEven.statistics.odd_count }}</span>
              <span class="stat-label">單</span>
            </div>
            <div class="stat">
              <span class="stat-val text-warning">{{ store.oddEven.statistics.even_count }}</span>
              <span class="stat-label">雙</span>
            </div>
            <div class="stat">
              <span class="stat-val text-muted">{{ store.oddEven.statistics.tie_count }}</span>
              <span class="stat-label">平</span>
            </div>
          </div>

          <div class="chart-section">
            <FrequencyChart
              type="doughnut"
              title="單雙比例"
              :labels="['單', '雙', '平']"
              :datasets="oddEvenDatasets"
            />
          </div>
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

const highLowDatasets = computed(() => {
  const s = store.highLow?.statistics;
  if (!s) return [];
  return [
    {
      data: [s.high_count || 0, s.low_count || 0, s.tie_count || 0],
      backgroundColor: ['#3498db', '#2ecc71', '#bdc3c7'],
      borderWidth: 0,
    },
  ];
});

const oddEvenDatasets = computed(() => {
  const s = store.oddEven?.statistics;
  if (!s) return [];
  return [
    {
      data: [s.odd_count || 0, s.even_count || 0, s.tie_count || 0],
      backgroundColor: ['#9b59b6', '#008f15', '#bdc3c7'],
      borderWidth: 0,
    },
  ];
});
</script>

<style scoped>
.trend-result {
  text-align: center;
  padding: var(--gap-md) 0;
}

.prediction-big {
  margin-bottom: var(--gap-md);
}

.prediction-label {
  display: block;
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: var(--gap-xs);
}

.prediction-value {
  font-size: 3rem;
  font-weight: 700;
}

.text-primary { color: var(--primary); }
.text-success { color: var(--secondary); }
.text-purple { color: var(--purple); }
.text-warning { color: var(--warning); }
.text-muted { color: var(--text-secondary); }

.confidence-section {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
  justify-content: center;
  margin-bottom: var(--gap-sm);
}

.confidence-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.confidence-bar.large {
  width: 150px;
  height: 10px;
}

.confidence-pct {
  font-weight: 600;
  font-size: 0.95rem;
}

.reason {
  color: var(--text-secondary);
  font-style: italic;
  font-size: 0.9rem;
}

.stats-row {
  display: flex;
  justify-content: center;
  gap: var(--gap-xl);
  margin: var(--gap-lg) 0;
  padding: var(--gap-md) 0;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.stat {
  text-align: center;
}

.stat-val {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.chart-section {
  margin-top: var(--gap-md);
}
</style>
