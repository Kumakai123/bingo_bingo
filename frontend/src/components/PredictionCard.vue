<template>
  <div :class="['card', 'prediction-card', `card-${type}`]">
    <div class="card-header">
      <div>
        <span class="card-icon">{{ icon }}</span>
        <span class="card-title">{{ title }}</span>
      </div>
      <router-link :to="link" class="card-link">詳細 →</router-link>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>載入中...
    </div>

    <!-- Basic / Super Number: show number balls -->
    <template v-else-if="type === 'basic' || type === 'super'">
      <div class="number-row" v-if="numbers.length">
        <span
          v-for="(n, i) in numbers.slice(0, 5)"
          :key="n.number"
          :class="['number-ball', rankClass(i)]"
        >
          {{ n.number }}
        </span>
      </div>
      <p class="card-sub" v-if="numbers.length">Top 5 推薦號碼</p>
      <p class="card-sub empty" v-else>暫無資料</p>
    </template>

    <!-- High/Low, Odd/Even: show prediction result -->
    <template v-else>
      <div class="result-display" v-if="prediction">
        <span class="result-value">{{ prediction.prediction || '—' }}</span>
        <div class="confidence-bar">
          <div
            class="confidence-fill"
            :style="{
              width: (prediction.confidence || 0) * 100 + '%',
              background: confidenceColor(prediction.confidence),
            }"
          ></div>
        </div>
        <span class="confidence-text">
          信心度 {{ ((prediction.confidence || 0) * 100).toFixed(0) }}%
        </span>
        <p class="reason-text">{{ prediction.reason }}</p>
      </div>
      <p class="card-sub empty" v-else>暫無資料</p>
    </template>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  icon: String,
  type: String,
  link: String,
  numbers: { type: Array, default: () => [] },
  prediction: { type: Object, default: null },
  loading: Boolean,
});

function rankClass(index) {
  return ['gold', 'silver', 'bronze', 'default', 'default'][index] || 'default';
}

function confidenceColor(c) {
  if (c >= 0.7) return 'var(--secondary)';
  if (c >= 0.55) return 'var(--primary)';
  return 'var(--warning)';
}
</script>

<style scoped>
.prediction-card {
  position: relative;
}

.card-link {
  font-size: 0.85rem;
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.card-link:hover {
  text-decoration: underline;
}

.number-row {
  display: flex;
  gap: var(--gap-sm);
  margin: var(--gap-md) 0;
  flex-wrap: wrap;
}

.card-sub {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.card-sub.empty {
  text-align: center;
  padding: var(--gap-lg);
}

.result-display {
  text-align: center;
  padding: var(--gap-sm) 0;
}

.result-value {
  font-size: 2.2rem;
  font-weight: 700;
  display: block;
  margin-bottom: var(--gap-sm);
}

.confidence-text {
  display: block;
  margin-top: var(--gap-xs);
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.reason-text {
  margin-top: var(--gap-sm);
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-style: italic;
}

.card-basic .result-value { color: var(--primary); }
.card-super .result-value { color: var(--accent); }
.card-highlow .result-value { color: var(--secondary); }
.card-oddeven .result-value { color: var(--purple); }
</style>
