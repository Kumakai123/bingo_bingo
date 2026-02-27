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

      <!-- 重複號 & 連開號 -->
      <div class="grid-2 extra-section">
        <!-- 重複號追蹤 -->
        <div class="card" v-if="repeatInfo">
          <div class="card-header">
            <span class="card-title">🔁 重複號追蹤</span>
            <span class="badge badge-danger">{{ repeatInfo.repeat_count }} 顆</span>
          </div>
          <p class="repeat-desc">
            最近一期 ({{ repeatInfo.latest_term }}) 與前一期 ({{ repeatInfo.previous_term }}) 重複的號碼：
          </p>
          <div class="repeat-balls" v-if="repeatInfo.repeat_numbers.length">
            <span
              v-for="n in repeatInfo.repeat_numbers"
              :key="n"
              class="number-ball repeat-ball"
            >{{ n }}</span>
          </div>
          <p v-else class="empty-note">本期無重複號碼</p>
        </div>

        <!-- 連開號碼 -->
        <div class="card" v-if="consecutiveHits.length">
          <div class="card-header">
            <span class="card-title">🔥 連開號碼</span>
            <span class="badge badge-warning">連續出現 ≥ 2 期</span>
          </div>
          <div class="consec-list">
            <div v-for="hit in consecutiveHits" :key="hit.number" class="consec-item">
              <span class="number-ball default">{{ hit.number }}</span>
              <span :class="['badge', hit.consecutive_draws >= 3 ? 'badge-danger' : 'badge-warning']">
                連開 {{ hit.consecutive_draws }} 期
              </span>
            </div>
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

const top10 = computed(() => store.basic?.predictions?.slice(0, 10) || []);

const repeatInfo = computed(() => store.basic?.repeat_info || null);

const consecutiveHits = computed(() => store.basic?.consecutive_hits || []);

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

/* Extra section */
.extra-section {
  margin-top: var(--gap-lg);
}

.repeat-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: var(--gap-md);
}

.repeat-balls {
  display: flex;
  gap: var(--gap-sm);
  flex-wrap: wrap;
}

.repeat-ball {
  background: radial-gradient(circle at 30% 28%, #ff8b8b 0%, #ee3f3f 40%, #ce1e1e 72%, #a70f0f 100%);
  border-color: #d63737;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
  box-shadow:
    inset 0 2px 5px rgba(255, 255, 255, 0.35),
    inset 0 -4px 8px rgba(0, 0, 0, 0.4);
}

.empty-note {
  color: var(--text-secondary);
  font-style: italic;
  font-size: 0.85rem;
}

.consec-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--gap-md);
}

.consec-item {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
}
</style>
