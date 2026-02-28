<template>
  <div>
    <div class="section-header">
      <h1 class="section-title">🧠 智慧選號</h1>
      <PeriodSelector v-model="store.periodRange" @update:model-value="store.setPeriodRange" />
    </div>

    <!-- Star level & pick count selectors -->
    <div class="ctrl-panel">
      <div class="ctrl-group">
        <span class="ctrl-label">星級</span>
        <div class="ctrl-buttons ctrl-buttons--stars">
          <button
            v-for="s in [1, 2, 3, 4, 5]"
            :key="s"
            type="button"
            :class="['star-ball', { 'star-ball--active': starLevel === s }]"
            :aria-pressed="starLevel === s"
            :aria-label="`${s} 星`"
            @click="changeStarLevel(s)"
          >
            <span class="star-ball-emoji" aria-hidden="true">⭐</span>
            <span class="star-ball-digit">{{ s }}</span>
          </button>
        </div>
      </div>
      <div class="ctrl-group">
        <span class="ctrl-label">選號數</span>
        <div class="ctrl-buttons ctrl-buttons--balls">
          <button
            v-for="c in [5, 8, 10, 15]"
            :key="c"
            type="button"
            :class="['pool-ball', { 'pool-ball--active': pickCount === c }]"
            :aria-pressed="pickCount === c"
            :aria-label="`${c} 碼`"
            @click="changePickCount(c)"
          >
            <span class="pool-ball-digit">{{ c }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>分析中...
    </div>

    <template v-else-if="data">
      <!-- Anchors -->
      <div class="card anchor-card">
        <div class="card-header">
          <span class="card-title">🎯 主隻號碼（核心錨定）</span>
          <span class="badge badge-danger">攻略一</span>
        </div>
        <div class="anchor-row">
          <span v-for="a in data.anchors" :key="a" class="number-ball anchor-ball">{{ a }}</span>
        </div>
        <p class="anchor-hint">從近期熱號與連莊號碼交集中選出的強勢號碼</p>
      </div>

      <div class="grid-2 sp-grid">
        <!-- Picks ranking -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">🏆 推薦號碼排行</span>
            <span class="badge badge-primary">Top {{ data.picks.length }}</span>
          </div>
          <div class="pick-list">
            <div v-for="(pick, i) in data.picks" :key="pick.number" class="pick-item">
              <span :class="['rank', rankClass(i)]">{{ i + 1 }}</span>
              <span :class="['number-ball', rankBallClass(i)]">{{ pick.number }}</span>
              <div class="pick-detail">
                <div class="score-bar-wrap">
                  <div class="score-bar" :style="{ width: scorePct(pick.final_score) + '%' }"></div>
                </div>
                <div class="pick-tags">
                  <span v-for="b in pick.bonuses" :key="b" :class="['tag', tagClass(b)]">{{ b }}</span>
                </div>
              </div>
              <span class="score-val">{{ pick.final_score.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- Star combos -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">⭐ {{ starLevel }} 星組合建議</span>
            <span class="badge badge-purple">Top 5</span>
          </div>
          <div class="combo-list">
            <div v-for="(combo, i) in data.star_combos" :key="i" class="combo-item">
              <span class="combo-rank">#{{ i + 1 }}</span>
              <div class="combo-balls">
                <span v-for="n in combo" :key="n" class="number-ball default">{{ n }}</span>
              </div>
              <button class="quick-bet-btn" @click="gotoBet(combo)">立即下注</button>
            </div>
          </div>
          <p v-if="!data.star_combos.length" class="empty-hint">尚無足夠資料產生組合</p>
        </div>
      </div>
    </template>

    <div v-else class="loading-overlay">按上方期數開始分析</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { usePredictionStore } from '../stores/prediction.js';
import { useSimulationStore } from '../stores/simulation.js';
import PeriodSelector from '../components/PeriodSelector.vue';

const store = usePredictionStore();
const simStore = useSimulationStore();
const starLevel = ref(3);
const pickCount = ref(10);
const loading = ref(false);
const data = ref(null);

async function loadData() {
  loading.value = true;
  try {
    const result = await store.fetchSmartPick(pickCount.value, starLevel.value);
    data.value = result;
  } catch {
    data.value = null;
  } finally {
    loading.value = false;
  }
}

function changeStarLevel(s) {
  starLevel.value = s;
  loadData();
}

function changePickCount(c) {
  pickCount.value = c;
  loadData();
}

function scorePct(score) {
  if (!data.value?.picks?.length) return 0;
  const max = data.value.picks[0].final_score || 1;
  return Math.round((score / max) * 100);
}

function rankClass(i) {
  return ['gold', 'silver', 'bronze'][i] || '';
}

function rankBallClass(i) {
  return ['gold', 'silver', 'bronze', 'default', 'default', 'default', 'default', 'default', 'default', 'default'][i];
}

function tagClass(bonus) {
  if (bonus.includes('連開')) return 'tag-consecutive';
  if (bonus.includes('共現')) return 'tag-cooccur';
  if (bonus.includes('尾號')) return 'tag-tail';
  if (bonus.includes('冷號')) return 'tag-cold';
  if (bonus.includes('區間')) return 'tag-zone';
  return 'tag-consecutive';
}

function gotoBet(combo) {
  simStore.openWidget({
    type: 'basic',
    star: starLevel.value,
    numbers: [...combo],
  });
}

watch(() => store.periodRange, () => {
  loadData();
});

onMounted(() => {
  loadData();
});
</script>

<style scoped>
/* Control panel: star level & pick count */
.ctrl-panel {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--gap-xl);
  margin-bottom: var(--gap-lg);
  padding: var(--gap-lg);
  background: linear-gradient(145deg, var(--surface) 0%, var(--surface-soft) 100%);
  border: 1px solid var(--border);
  border-radius: var(--card-radius);
}

.ctrl-group {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
  flex-wrap: wrap;
}

.ctrl-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.ctrl-buttons {
  display: flex;
  gap: var(--gap-sm);
  flex-wrap: wrap;
}

.ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: #1a2736;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-main);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.ctrl-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(88, 166, 255, 0.15);
}

.ctrl-btn--active {
  background: linear-gradient(135deg, var(--primary), #7ac2ff);
  border-color: var(--primary);
  color: #08121d;
  box-shadow: 0 2px 10px rgba(88, 166, 255, 0.35);
}

.ctrl-btn--active:hover {
  color: #08121d;
  transform: translateY(-1px);
  box-shadow: 0 3px 12px rgba(88, 166, 255, 0.4);
}

/* Star ball buttons */
.star-ball {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border: none;
  background: none;
  cursor: pointer;
  padding: 0;
  transition: transform 0.2s ease;
}

.star-ball:hover {
  transform: scale(1.15);
}

.star-ball:active {
  transform: scale(0.92);
}

.star-ball-emoji {
  position: absolute;
  font-size: 2.8rem;
  line-height: 1;
  opacity: 0.35;
  transition: opacity 0.2s ease, filter 0.2s ease;
  filter: grayscale(0.8);
}

.star-ball:hover .star-ball-emoji {
  opacity: 0.6;
  filter: grayscale(0.3);
}

.star-ball--active .star-ball-emoji {
  opacity: 1;
  filter: grayscale(0) drop-shadow(0 2px 6px rgba(247, 185, 85, 0.5));
}

.star-ball-digit {
  position: relative;
  z-index: 1;
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-secondary);
  font-family: var(--font-main);
  transition: color 0.2s ease, text-shadow 0.2s ease;
  pointer-events: none;
}

.star-ball--active .star-ball-digit {
  color: #fff;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
}

/* Pool ball buttons */
.pool-ball {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  background:
    radial-gradient(circle at 35% 30%, rgba(255, 255, 255, 0.25) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, #3a4a5c 0%, #2a3a4c 60%, #1a2736 100%);
  box-shadow:
    inset 0 2px 4px rgba(255, 255, 255, 0.12),
    inset 0 -3px 6px rgba(0, 0, 0, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.pool-ball:hover {
  transform: scale(1.12);
  box-shadow:
    inset 0 2px 4px rgba(255, 255, 255, 0.15),
    inset 0 -3px 6px rgba(0, 0, 0, 0.4),
    0 4px 12px rgba(88, 166, 255, 0.2);
}

.pool-ball:active {
  transform: scale(0.93);
}

.pool-ball--active {
  background:
    radial-gradient(circle at 35% 30%, rgba(255, 255, 255, 0.4) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, #3498db 0%, #2176ad 60%, #165a85 100%);
  box-shadow:
    inset 0 2px 5px rgba(255, 255, 255, 0.25),
    inset 0 -4px 8px rgba(0, 0, 0, 0.35),
    0 3px 10px rgba(52, 152, 219, 0.45);
}

.pool-ball--active:hover {
  box-shadow:
    inset 0 2px 5px rgba(255, 255, 255, 0.25),
    inset 0 -4px 8px rgba(0, 0, 0, 0.35),
    0 4px 14px rgba(52, 152, 219, 0.55);
}

.pool-ball-digit {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-secondary);
  font-family: var(--font-main);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
  transition: color 0.2s ease;
}

.pool-ball--active .pool-ball-digit {
  color: #fff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

.anchor-card {
  margin-bottom: var(--gap-lg);
  text-align: center;
}

.anchor-row {
  display: flex;
  justify-content: center;
  gap: var(--gap-lg);
  margin: var(--gap-lg) 0;
}

.anchor-ball {
  width: 64px;
  height: 64px;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #ff6b81, #ee5a24);
  border-color: #c0392b;
  color: #fff;
  animation: pulse 2s infinite;
}

.anchor-hint {
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-style: italic;
}

.sp-grid {
  margin-top: 0;
}

.pick-list {
  display: flex;
  flex-direction: column;
  gap: var(--gap-sm);
}

.pick-item {
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

.pick-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.score-bar-wrap {
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

.pick-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.score-val {
  width: 48px;
  text-align: right;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.combo-list {
  display: flex;
  flex-direction: column;
  gap: var(--gap-md);
}

.combo-item {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
  padding: var(--gap-sm) 0;
  border-bottom: 1px solid var(--border);
}

.combo-item:last-child {
  border-bottom: none;
}

.combo-rank {
  font-weight: 700;
  color: var(--text-secondary);
  font-size: 0.9rem;
  width: 30px;
}

.combo-balls {
  display: flex;
  gap: var(--gap-sm);
  flex-wrap: wrap;
}

.quick-bet-btn {
  margin-left: auto;
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid var(--secondary);
  background: transparent;
  color: var(--secondary);
  font-family: var(--font-main);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.quick-bet-btn:hover {
  background: var(--secondary);
  color: #08121d;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(48, 196, 141, 0.3);
}

.empty-hint {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--gap-xl);
}
</style>
