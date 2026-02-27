<template>
  <div>
    <div class="section-header">
      <h1 class="section-title">📈 進階分析</h1>
      <PeriodSelector v-model="store.periodRange" @update:model-value="store.setPeriodRange" />
    </div>

    <!-- Tab navigation -->
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <div v-if="store.loading" class="loading-overlay">
      <div class="spinner"></div>載入中...
    </div>

    <template v-else>
      <!-- Co-occurrence -->
      <div v-if="activeTab === 'cooccurrence'" class="tab-content">
        <div class="card" v-if="store.coOccurrence">
          <div class="card-header">
            <span class="card-title">🔗 共現號碼對 Top 15</span>
            <span class="badge badge-primary">近 {{ store.coOccurrence.period_range }} 期</span>
          </div>
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>排名</th>
                  <th>號碼對</th>
                  <th>共現次數</th>
                  <th>共現率</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(pair, i) in store.coOccurrence.top_pairs" :key="i">
                  <td class="mono">{{ i + 1 }}</td>
                  <td>
                    <span class="number-ball default" style="width:32px;height:32px;font-size:0.8rem;">{{ pair.pair[0] }}</span>
                    <span class="pair-sep">+</span>
                    <span class="number-ball default" style="width:32px;height:32px;font-size:0.8rem;">{{ pair.pair[1] }}</span>
                  </td>
                  <td class="mono">{{ pair.count }}</td>
                  <td>
                    <div class="rate-bar-wrap">
                      <div class="rate-bar" :style="{ width: pair.co_rate + '%' }"></div>
                    </div>
                    <span class="rate-text">{{ pair.co_rate }}%</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else class="loading-overlay">暫無資料</div>
      </div>

      <!-- Tail Number -->
      <div v-if="activeTab === 'tail'" class="tab-content">
        <div class="grid-2" v-if="store.tailNumber">
          <div class="card">
            <div class="card-header">
              <span class="card-title">🔢 尾號出現統計</span>
            </div>
            <div class="tail-chart">
              <div v-for="t in 10" :key="t - 1" class="tail-row">
                <span class="tail-label">尾 {{ t - 1 }}</span>
                <div class="tail-bar-wrap">
                  <div
                    class="tail-bar"
                    :style="{ width: tailBarWidth(t - 1) + '%', background: isHotTail(t - 1) ? 'var(--accent)' : 'var(--primary)' }"
                  ></div>
                </div>
                <span class="tail-avg">{{ tailAvg(t - 1) }}</span>
              </div>
            </div>
            <p class="stat-note">
              單期尾碼集中 (≥5顆) 出現率：{{ store.tailNumber.high_tail_draw_rate }}%
            </p>
          </div>
          <div class="card">
            <div class="card-header">
              <span class="card-title">🔥 熱門尾號推薦號碼</span>
            </div>
            <div v-for="group in store.tailNumber.hot_tail_numbers" :key="group.tail" class="hot-tail-group">
              <div class="hot-tail-header">
                <span class="badge badge-hot">尾 {{ group.tail }}</span>
              </div>
              <div class="hot-tail-numbers">
                <div v-for="n in group.top_numbers" :key="n.number" class="hot-tail-item">
                  <span class="number-ball default" style="width:32px;height:32px;font-size:0.8rem;">{{ n.number }}</span>
                  <span class="hot-tail-count">{{ n.count }} 次</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="loading-overlay">暫無資料</div>
      </div>

      <!-- Zone Distribution -->
      <div v-if="activeTab === 'zone'" class="tab-content">
        <div v-if="store.zoneDistribution">
          <div class="grid-4 zone-grid">
            <div v-for="(stat, zone) in store.zoneDistribution.zone_stats" :key="zone" class="card zone-card">
              <div class="zone-header">
                <span class="zone-name">{{ zone }} 區</span>
                <span class="zone-range">{{ stat.range }}</span>
              </div>
              <div class="zone-avg">{{ stat.avg_per_draw }}</div>
              <div class="zone-expected">理論值 {{ stat.theoretical_avg }}</div>
              <div :class="['zone-deviation', stat.deviation_pct > 0 ? 'positive' : stat.deviation_pct < 0 ? 'negative' : '']">
                {{ stat.deviation_pct > 0 ? '+' : '' }}{{ stat.deviation_pct }}%
              </div>
            </div>
          </div>

          <div class="card" style="margin-top: var(--gap-lg);" v-if="Object.keys(store.zoneDistribution.pairing_tendency).length">
            <div class="card-header">
              <span class="card-title">📊 區間搭配傾向</span>
              <span class="badge badge-warning">某區 ≥ 7 顆時</span>
            </div>
            <div class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>主區間</th>
                    <th>出現次數</th>
                    <th>其他區間平均</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(info, zone) in store.zoneDistribution.pairing_tendency" :key="zone">
                    <td><span class="badge badge-primary">{{ zone }} 區 ≥ 7</span></td>
                    <td class="mono">{{ info.occurrences }} 次</td>
                    <td>
                      <span v-for="(avg, z) in info.avg_other_zones" :key="z" class="zone-avg-tag">
                        {{ z }}:{{ avg }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-else class="loading-overlay">暫無資料</div>
      </div>

      <!-- Cold/Hot Cycle -->
      <div v-if="activeTab === 'coldhot'" class="tab-content">
        <div class="grid-2" v-if="store.coldHotCycle">
          <!-- Hot numbers -->
          <div class="card">
            <div class="card-header">
              <span class="card-title">🔥 近期熱號 Top 10</span>
              <span class="badge badge-hot">近 {{ store.coldHotCycle.recent_window }} 期</span>
            </div>
            <div class="cycle-list">
              <div v-for="(h, i) in store.coldHotCycle.hot_numbers" :key="h.number" class="cycle-item">
                <span :class="['rank', rankClass(i)]">{{ i + 1 }}</span>
                <span class="number-ball default" style="width:36px;height:36px;font-size:0.85rem;">{{ h.number }}</span>
                <span class="cycle-info">出現 {{ h.recent_count }} 次</span>
                <span class="badge badge-hot" style="font-size:0.7rem;">HOT</span>
              </div>
            </div>

            <div v-if="store.coldHotCycle.streak_numbers.length" class="streak-section">
              <h3 class="sub-title">🔁 連莊號碼</h3>
              <div class="streak-list">
                <div v-for="s in store.coldHotCycle.streak_numbers" :key="s.number" class="streak-item">
                  <span class="number-ball default" style="width:32px;height:32px;font-size:0.8rem;">{{ s.number }}</span>
                  <span class="streak-count">連續 {{ s.streak }} 期</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Cold numbers -->
          <div class="card">
            <div class="card-header">
              <span class="card-title">❄️ 冷號 Top 10（即將回歸候選）</span>
              <span class="badge badge-cold">長期未出</span>
            </div>
            <div class="cycle-list">
              <div v-for="(c, i) in store.coldHotCycle.cold_numbers" :key="c.number" class="cycle-item">
                <span :class="['rank', rankClass(i)]">{{ i + 1 }}</span>
                <span class="number-ball default" style="width:36px;height:36px;font-size:0.85rem;">{{ c.number }}</span>
                <span class="cycle-info">已缺席 {{ c.current_gap }} 期</span>
                <span class="cycle-info-sub">平均間隔 {{ c.avg_interval }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="loading-overlay">暫無資料</div>
      </div>

      <!-- Consecutive Numbers -->
      <div v-if="activeTab === 'consecutive'" class="tab-content">
        <div v-if="store.consecutive">
          <div class="grid-3">
            <div class="card stat-card">
              <div class="stat-big">{{ store.consecutive.statistics.avg_pairs }}</div>
              <div class="stat-desc">平均連號對數</div>
            </div>
            <div class="card stat-card">
              <div class="stat-big">{{ store.consecutive.statistics.max_pairs }}</div>
              <div class="stat-desc">最高連號對數</div>
            </div>
            <div class="card stat-card">
              <div class="stat-big">{{ store.consecutive.statistics.min_pairs }}</div>
              <div class="stat-desc">最低連號對數</div>
            </div>
          </div>
          <div class="grid-2" style="margin-top: var(--gap-lg);">
            <div class="card stat-card">
              <div class="stat-big">{{ store.consecutive.statistics.zero_pair_rate }}%</div>
              <div class="stat-desc">零連號期數比例</div>
            </div>
            <div class="card stat-card">
              <div class="stat-big">{{ store.consecutive.statistics.high_pair_rate }}%</div>
              <div class="stat-desc">高連號 (≥4對) 比例</div>
            </div>
          </div>

          <div class="card" style="margin-top: var(--gap-lg);" v-if="store.consecutive.latest_draw">
            <div class="card-header">
              <span class="card-title">📋 最近一期連號</span>
              <span class="badge badge-primary">{{ store.consecutive.latest_draw.draw_term }}</span>
            </div>
            <div v-if="store.consecutive.latest_draw.pairs.length" class="consec-pairs">
              <div v-for="(pair, i) in store.consecutive.latest_draw.pairs" :key="i" class="consec-pair">
                <span class="number-ball default" style="width:36px;height:36px;font-size:0.85rem;">{{ String(pair[0]).padStart(2, '0') }}</span>
                <span class="pair-arrow">→</span>
                <span class="number-ball default" style="width:36px;height:36px;font-size:0.85rem;">{{ String(pair[1]).padStart(2, '0') }}</span>
              </div>
            </div>
            <p v-else class="empty-hint">本期無連號對</p>
          </div>
        </div>
        <div v-else class="loading-overlay">暫無資料</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { usePredictionStore } from '../stores/prediction.js';
import PeriodSelector from '../components/PeriodSelector.vue';

const store = usePredictionStore();
const activeTab = ref('coldhot');

const tabs = [
  { id: 'coldhot', icon: '🔥', label: '冷熱週期' },
  { id: 'cooccurrence', icon: '🔗', label: '共現分析' },
  { id: 'tail', icon: '🔢', label: '尾號分析' },
  { id: 'zone', icon: '📊', label: '區間分布' },
  { id: 'consecutive', icon: '🔀', label: '連號分析' },
];

function rankClass(i) {
  return ['gold', 'silver', 'bronze'][i] || '';
}

function tailAvg(tail) {
  const stats = store.tailNumber?.tail_stats?.[String(tail)];
  return stats ? stats.avg_per_draw : '0';
}

function tailBarWidth(tail) {
  const stats = store.tailNumber?.tail_stats?.[String(tail)];
  if (!stats) return 0;
  return Math.min(stats.avg_per_draw / 3 * 100, 100);
}

function isHotTail(tail) {
  const hotTails = store.tailNumber?.hot_tails || [];
  return hotTails.some(h => String(h.tail) === String(tail));
}
</script>

<style scoped>
.tab-bar {
  display: flex;
  gap: var(--gap-xs);
  margin-bottom: var(--gap-lg);
  overflow-x: auto;
  padding-bottom: var(--gap-xs);
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
  font-family: var(--font-main);
}

.tab-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.tab-btn.active {
  background: linear-gradient(135deg, var(--primary), #7ac2ff);
  border-color: var(--primary);
  color: #08121d;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Co-occurrence */
.pair-sep {
  display: inline-block;
  margin: 0 6px;
  color: var(--text-secondary);
  font-weight: 600;
}

.rate-bar-wrap {
  display: inline-block;
  width: 80px;
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
  vertical-align: middle;
  margin-right: 8px;
}

.rate-bar {
  height: 100%;
  background: var(--primary);
  border-radius: 3px;
}

.rate-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

/* Tail Number */
.tail-chart {
  display: flex;
  flex-direction: column;
  gap: var(--gap-sm);
}

.tail-row {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
}

.tail-label {
  width: 40px;
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.tail-bar-wrap {
  flex: 1;
  height: 10px;
  background: var(--border);
  border-radius: 5px;
  overflow: hidden;
}

.tail-bar {
  height: 100%;
  border-radius: 5px;
  transition: width 0.4s ease;
}

.tail-avg {
  width: 36px;
  text-align: right;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.stat-note {
  margin-top: var(--gap-md);
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-style: italic;
}

.hot-tail-group {
  margin-bottom: var(--gap-md);
  padding-bottom: var(--gap-md);
  border-bottom: 1px solid var(--border);
}

.hot-tail-group:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.hot-tail-header {
  margin-bottom: var(--gap-sm);
}

.hot-tail-numbers {
  display: flex;
  gap: var(--gap-md);
  flex-wrap: wrap;
}

.hot-tail-item {
  display: flex;
  align-items: center;
  gap: var(--gap-xs);
}

.hot-tail-count {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* Zone Distribution */
.zone-grid {
  margin-bottom: 0;
}

.zone-card {
  text-align: center;
}

.zone-header {
  margin-bottom: var(--gap-sm);
}

.zone-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary);
}

.zone-range {
  display: block;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.zone-avg {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text);
}

.zone-expected {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-top: var(--gap-xs);
}

.zone-deviation {
  font-size: 1rem;
  font-weight: 600;
  margin-top: var(--gap-xs);
}

.zone-deviation.positive { color: var(--accent); }
.zone-deviation.negative { color: var(--secondary); }

.zone-avg-tag {
  display: inline-block;
  background: var(--surface-soft);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2px 8px;
  font-size: 0.82rem;
  margin-right: 4px;
  font-family: var(--font-mono);
}

/* Cold/Hot Cycle */
.cycle-list {
  display: flex;
  flex-direction: column;
  gap: var(--gap-sm);
}

.cycle-item {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
  padding: 4px 0;
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

.cycle-info {
  font-size: 0.85rem;
  color: var(--text);
  font-weight: 500;
}

.cycle-info-sub {
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.streak-section {
  margin-top: var(--gap-lg);
  padding-top: var(--gap-lg);
  border-top: 1px solid var(--border);
}

.sub-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: var(--gap-md);
}

.streak-list {
  display: flex;
  gap: var(--gap-md);
  flex-wrap: wrap;
}

.streak-item {
  display: flex;
  align-items: center;
  gap: var(--gap-xs);
}

.streak-count {
  font-size: 0.82rem;
  color: var(--accent);
  font-weight: 600;
}

/* Consecutive */
.stat-card {
  text-align: center;
  padding: var(--gap-xl);
}

.stat-big {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
}

.stat-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-top: var(--gap-xs);
}

.consec-pairs {
  display: flex;
  gap: var(--gap-lg);
  flex-wrap: wrap;
  padding: var(--gap-md) 0;
}

.consec-pair {
  display: flex;
  align-items: center;
  gap: var(--gap-xs);
}

.pair-arrow {
  color: var(--accent);
  font-weight: 700;
}

.empty-hint {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--gap-xl);
}

.table-wrapper {
  overflow-x: auto;
}

.mono {
  font-family: var(--font-mono);
  font-size: 0.85rem;
}
</style>
