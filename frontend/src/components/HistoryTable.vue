<template>
  <div class="card">
    <div class="card-header">
      <span class="card-title">📋 最近開獎紀錄</span>
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
          <tr v-for="d in draws" :key="d.draw_term">
            <td class="mono">{{ d.draw_term }}</td>
            <td>
              <div class="draw-numbers">
                <span v-for="n in d.numbers_sorted" :key="n" class="mini-ball">
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
              <span :class="['badge', d.high_low_result === '大' ? 'badge-primary' : 'badge-success']">
                {{ d.high_low_result }}
              </span>
            </td>
            <td>
              <span :class="['badge', d.odd_even_result === '單' ? 'badge-purple' : 'badge-warning']">
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
defineProps({
  draws: { type: Array, default: () => [] },
});
</script>

<style scoped>
.table-wrapper {
  overflow-x: auto;
}

.mono {
  font-family: var(--font-mono);
  font-size: 0.85rem;
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
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--bg);
  border: 1px solid var(--border);
  font-size: 0.7rem;
  font-weight: 500;
}
</style>
