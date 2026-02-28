<template>
  <div>
    <div class="section-header">
      <h1 class="section-title">📋 投注紀錄</h1>
      <button class="refresh-btn" :disabled="store.settling" @click="handleSettle">
        {{ store.settling ? '兌獎中...' : '手動兌獎' }}
      </button>
    </div>

    <!-- Stats summary -->
    <div class="grid-4 mb" v-if="store.stats">
      <div class="card stat-card">
        <div class="stat-label">總投注</div>
        <div class="stat-value">{{ store.stats.total_bets + store.stats.pending }} 注</div>
        <div class="stat-sub">待開獎 {{ store.stats.pending }} 注</div>
      </div>
      <div class="card stat-card">
        <div class="stat-label">勝率</div>
        <div class="stat-value">{{ store.stats.win_rate }}%</div>
        <div class="stat-sub">{{ store.stats.wins }} 勝 / {{ store.stats.losses }} 負</div>
      </div>
      <div class="card stat-card">
        <div class="stat-label">總花費 / 總獎金</div>
        <div class="stat-value">${{ store.stats.total_cost.toLocaleString() }} / ${{ store.stats.total_prize.toLocaleString() }}</div>
      </div>
      <div class="card stat-card">
        <div class="stat-label">淨盈虧</div>
        <div :class="['stat-value', store.stats.net_profit >= 0 ? 'profit' : 'loss']">
          {{ store.stats.net_profit >= 0 ? '+' : '' }}${{ store.stats.net_profit.toLocaleString() }}
        </div>
      </div>
    </div>

    <p v-if="settleMsg" class="settle-msg">{{ settleMsg }}</p>

    <!-- Bet history -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">投注明細</span>
        <div class="filter-tabs">
          <button :class="['filter-tab', { active: filterStatus === null }]" @click="filterStatus = null; reload()">全部</button>
          <button :class="['filter-tab', { active: filterStatus === 'pending' }]" @click="filterStatus = 'pending'; reload()">待開獎</button>
          <button :class="['filter-tab', { active: filterStatus === 'won' }]" @click="filterStatus = 'won'; reload()">中獎</button>
          <button :class="['filter-tab', { active: filterStatus === 'lost' }]" @click="filterStatus = 'lost'; reload()">未中</button>
        </div>
      </div>

      <div v-if="store.loading" class="loading-overlay"><div class="spinner"></div>載入中...</div>

      <table v-else-if="store.bets.length" class="data-table">
        <thead>
          <tr>
            <th>玩法</th>
            <th>選號/選項</th>
            <th>倍數</th>
            <th>費用</th>
            <th>目標期號</th>
            <th>狀態</th>
            <th>命中</th>
            <th>獎金</th>
            <th>盈虧</th>
            <th>下注時間</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="bet in store.bets" :key="bet.id">
            <td>
              <span class="badge badge-primary" v-if="bet.bet_type === 'basic'">{{ bet.star_level }}星</span>
              <span class="badge badge-danger" v-else-if="bet.bet_type === 'super'">超級</span>
              <span class="badge badge-success" v-else-if="bet.bet_type === 'high_low'">大小</span>
              <span class="badge badge-purple" v-else>單雙</span>
            </td>
            <td>
              <template v-if="bet.selected_numbers">
                <span v-for="n in bet.selected_numbers" :key="n" :class="['number-ball-sm', { matched: bet.matched_numbers && bet.matched_numbers.includes(n) }]">{{ n }}</span>
              </template>
              <template v-else>{{ bet.selected_option }}</template>
            </td>
            <td class="mono">{{ bet.multiplier }}x</td>
            <td>${{ bet.total_cost }}</td>
            <td class="mono term-col">{{ bet.target_draw_term || '—' }}</td>
            <td>
              <span :class="['status-badge', `status-${bet.status}`]">
                {{ statusLabel(bet.status) }}
              </span>
            </td>
            <td>{{ bet.matched_count ?? '—' }}</td>
            <td>${{ bet.prize_amount.toLocaleString() }}</td>
            <td :class="profitClass(bet)">
              {{ bet.status === 'pending' ? '—' : (bet.net_profit >= 0 ? '+' : '') + '$' + bet.net_profit.toLocaleString() }}
            </td>
            <td class="time-col">{{ formatBetTime(bet.created_at) }}</td>
            <td>
              <button v-if="bet.status === 'pending'" class="cancel-btn" @click="handleCancel(bet.id)">取消</button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="empty-hint">暫無投注紀錄，點擊右下角按鈕開始下注</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useSimulationStore } from '../stores/simulation.js';

const store = useSimulationStore();
const filterStatus = ref(null);
const settleMsg = ref('');

async function handleSettle() {
  try {
    const res = await store.settleBets();
    if (res.settled_count > 0) {
      settleMsg.value = `已結算 ${res.settled_count} 筆投注 (期號: ${res.draw_term})`;
    } else {
      settleMsg.value = '沒有待結算的投注';
    }
    setTimeout(() => { settleMsg.value = ''; }, 4000);
  } catch {
    // error handled in store
  }
}

async function handleCancel(id) {
  await store.cancelBet(id);
}

function reload() {
  store.fetchBets(filterStatus.value);
}

function statusLabel(s) {
  return { pending: '待開獎', won: '中獎', lost: '未中' }[s] || s;
}

function profitClass(bet) {
  if (bet.status === 'pending') return '';
  return bet.net_profit >= 0 ? 'profit' : 'loss';
}

function formatBetTime(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  const mo = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const h = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  return `${mo}/${day} ${h}:${mi}`;
}

onMounted(() => {
  store.fetchBets();
  store.fetchStats();
});
</script>

<style scoped>
.mb { margin-bottom: var(--gap-lg); }

.stat-card { text-align: center; }
.stat-label { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: var(--gap-xs); }
.stat-value { font-size: 1.4rem; font-weight: 700; }
.stat-sub { font-size: 0.8rem; color: var(--text-secondary); margin-top: var(--gap-xs); }
.profit { color: var(--secondary); }
.loss { color: var(--accent); }

.settle-msg {
  color: var(--secondary);
  font-size: 0.85rem;
  margin-bottom: var(--gap-md);
  text-align: center;
}

.filter-tabs {
  display: flex;
  gap: var(--gap-xs);
}
.filter-tab {
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  font-family: var(--font-main);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}
.filter-tab.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #08121d;
}

.mono {
  font-family: var(--font-mono);
  font-size: 0.82rem;
}

.term-col {
  font-size: 0.78rem;
  white-space: nowrap;
}

.time-col {
  font-size: 0.78rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.number-ball-sm {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-weight: 600;
  font-size: 0.72rem;
  background: #223243;
  border: 1.5px solid #334a63;
  color: #dce8f7;
  margin-right: 3px;
}
.number-ball-sm.matched {
  background: var(--secondary);
  border-color: var(--secondary);
  color: #fff;
}

.status-badge {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.78rem;
  font-weight: 600;
}
.status-pending { background: rgba(247, 185, 85, 0.15); color: var(--warning); border: 1px solid rgba(247, 185, 85, 0.3); }
.status-won { background: rgba(48, 196, 141, 0.15); color: var(--secondary); border: 1px solid rgba(48, 196, 141, 0.3); }
.status-lost { background: rgba(255, 107, 129, 0.1); color: var(--text-secondary); border: 1px solid var(--border); }

.cancel-btn {
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid var(--accent);
  background: transparent;
  color: var(--accent);
  font-family: var(--font-main);
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition);
}
.cancel-btn:hover { background: var(--accent); color: #fff; }

.empty-hint {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--gap-xl);
}
</style>
