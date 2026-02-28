<template>
  <div class="card">
    <div class="card-header">
      <span class="card-title">📋 最近開獎紀錄</span>
      <span class="today-date">{{ todayStr }}</span>
    </div>
    <div v-if="!draws.length" class="loading-overlay">暫無資料</div>
    <div v-else class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>期號</th>
            <th>開獎號碼</th>
            <th>超級號碼</th>
            <th>大/小</th>
            <th>單/雙</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in drawRows" :key="d.draw_term">
            <td class="term-cell">
              <span class="mono">{{ d.draw_term }}</span>
              <span class="draw-time">{{ formatTime(d.draw_datetime) }}</span>
            </td>
            <td>
              <div class="draw-numbers">
                <span
                  v-for="n in d.numbers_sorted"
                  :key="n"
                  :class="['mini-ball', d.repeatSet.has(n) ? 'repeat' : 'normal']"
                >
                  {{ n }}
                </span>
              </div>
            </td>
            <td>
              <span class="number-ball super" style="width:32px;height:32px;font-size:0.8rem;">
                {{ d.super_number }}
              </span>
            </td>
            <td>
              <span :class="['badge', d.high_low_result === '大' ? 'badge-primary' : d.high_low_result === '小' ? 'badge-success' : 'badge-tie']">
                {{ d.high_low_result }}
              </span>
            </td>
            <td>
              <span :class="['badge', d.odd_even_result === '單' ? 'badge-purple' : d.odd_even_result === '雙' ? 'badge-even' : 'badge-tie']">
                {{ d.odd_even_result }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  draws: { type: Array, default: () => [] },
});

const drawRows = computed(() =>
  props.draws.map((draw, idx) => {
    const previousDraw = props.draws[idx + 1];
    const repeatSet = new Set(previousDraw?.numbers_sorted || []);
    return { ...draw, repeatSet };
  })
);

const todayStr = (() => {
  const now = new Date();
  const y = now.getFullYear();
  const mo = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${y}/${mo}/${day}`;
})();

function formatTime(dt) {
  if (!dt) return '';
  const d = new Date(dt);
  const h = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  return `${h}:${mi}`;
}
</script>

<style scoped>
.table-wrapper {
  overflow-x: auto;
}

.today-date {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.term-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.mono {
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.draw-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.draw-numbers {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
  max-width: 500px;
}

.mini-ball {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 1px solid;
  font-size: 21px;
  font-weight: 700;
  line-height: 1;
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
  box-shadow:
    inset 0 2px 5px rgba(255, 255, 255, 0.35),
    inset 0 -4px 8px rgba(0, 0, 0, 0.4);
}

.mini-ball.normal {
  background: radial-gradient(circle at 30% 28%, #7e8dff 0%, #2f45e8 38%, #0a1cb6 72%, #06128c 100%);
  border-color: #2942e0;
}

.mini-ball.repeat {
  background: radial-gradient(circle at 30% 28%, #ff8b8b 0%, #ee3f3f 40%, #ce1e1e 72%, #a70f0f 100%);
  border-color: #d63737;
}

.badge-even {
  background: linear-gradient(135deg, #2f84ff, #1a4fc8);
  color: #ffffff;
}

.badge-tie {
  background: linear-gradient(135deg, #7f8c9a, #5f6b79);
  color: #ffffff;
}

@media (max-width: 768px) {
  .mini-ball {
    width: 36px;
    height: 36px;
    font-size: 17px;
  }
}
</style>
