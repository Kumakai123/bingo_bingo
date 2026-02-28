<template>
  <div class="bet-widget-container">
    <!-- Floating panel -->
    <transition name="panel">
      <div v-if="store.widgetOpen" class="bet-panel">
        <div class="panel-header">
          <span class="panel-title">🎰 快速下注</span>
          <div class="panel-header-right">
            <span v-if="nextDraw" class="next-draw-info">
              #{{ nextDraw.next_draw_term }} · {{ nextDraw.estimated_time_short }}
            </span>
            <button class="panel-close" @click="store.closeWidget()">✕</button>
          </div>
        </div>

        <!-- Bet type tabs -->
        <div class="w-tabs">
          <button
            v-for="t in betTypes"
            :key="t.value"
            :class="['w-tab', { active: betType === t.value }]"
            @click="switchBetType(t.value)"
          >{{ t.label }}</button>
        </div>

        <div class="panel-body">
          <!-- Basic play -->
          <template v-if="betType === 'basic'">
            <div class="w-row">
              <span class="w-label">星級</span>
              <div class="w-star-selector">
                <button
                  v-for="s in 10"
                  :key="s"
                  :class="['w-star', { active: starLevel === s }]"
                  @click="setStarLevel(s)"
                >{{ s }}</button>
              </div>
            </div>
            <div class="w-row">
              <span class="w-label">選號 ({{ selectedNumbers.length }}/{{ starLevel }})</span>
            </div>
            <div class="w-number-grid">
              <button
                v-for="n in 80"
                :key="n"
                :class="['w-num', { selected: selectedNumbers.includes(pad(n)) }]"
                :disabled="!selectedNumbers.includes(pad(n)) && selectedNumbers.length >= starLevel"
                @click="toggleNumber(pad(n))"
              >{{ pad(n) }}</button>
            </div>
          </template>

          <!-- Super number -->
          <template v-if="betType === 'super'">
            <div class="w-row">
              <span class="w-label">選 1 個超級號碼</span>
            </div>
            <div class="w-number-grid">
              <button
                v-for="n in 80"
                :key="n"
                :class="['w-num', { selected: selectedNumbers.includes(pad(n)) }]"
                :disabled="!selectedNumbers.includes(pad(n)) && selectedNumbers.length >= 1"
                @click="toggleNumber(pad(n))"
              >{{ pad(n) }}</button>
            </div>
          </template>

          <!-- High/Low -->
          <template v-if="betType === 'high_low'">
            <div class="w-row">
              <span class="w-label">猜大小</span>
            </div>
            <div class="w-options">
              <button :class="['w-opt', 'w-opt-big', { active: selectedOption === '大' }]" @click="selectedOption = '大'">大 (41-80)</button>
              <button :class="['w-opt', 'w-opt-small', { active: selectedOption === '小' }]" @click="selectedOption = '小'">小 (01-40)</button>
            </div>
          </template>

          <!-- Odd/Even -->
          <template v-if="betType === 'odd_even'">
            <div class="w-row">
              <span class="w-label">猜單雙</span>
            </div>
            <div class="w-options">
              <button :class="['w-opt', 'w-opt-odd', { active: selectedOption === '單' }]" @click="selectedOption = '單'">單</button>
              <button :class="['w-opt', 'w-opt-even', { active: selectedOption === '雙' }]" @click="selectedOption = '雙'">雙</button>
            </div>
          </template>
        </div>

        <!-- Footer -->
        <div class="panel-footer">
          <!-- Period + Multiplier row -->
          <div class="w-ctrl-row">
            <div class="w-ctrl-group">
              <span class="w-ctrl-label">期數</span>
              <div class="w-mult-ctrl">
                <button class="w-mult-btn" @click="betPeriods = Math.max(1, betPeriods - 1)">−</button>
                <span class="w-mult-val">{{ betPeriods }}</span>
                <button class="w-mult-btn" @click="betPeriods = Math.min(10, betPeriods + 1)">+</button>
              </div>
            </div>
            <div class="w-ctrl-group">
              <span class="w-ctrl-label">倍數</span>
              <div class="w-mult-ctrl">
                <button class="w-mult-btn" @click="multiplier = Math.max(1, multiplier - 1)">−</button>
                <span class="w-mult-val">{{ multiplier }}x</span>
                <button class="w-mult-btn" @click="multiplier = Math.min(50, multiplier + 1)">+</button>
              </div>
            </div>
            <span class="w-cost">${{ totalCost.toLocaleString() }}</span>
          </div>
          <button class="w-place-btn" :disabled="!canPlace || store.placing" @click="handlePlace">
            {{ store.placing ? '下注中...' : `確認下注 (${betPeriods}期)` }}
          </button>
          <p v-if="store.error" class="w-error">{{ store.error }}</p>
          <p v-if="successMsg" class="w-success">{{ successMsg }}</p>
        </div>
      </div>
    </transition>

    <!-- FAB button -->
    <button class="bet-fab" @click="toggleWidget" :class="{ 'fab-open': store.widgetOpen }">
      <span class="fab-icon">{{ store.widgetOpen ? '✕' : '🎰' }}</span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useSimulationStore } from '../stores/simulation.js';
import api from '../services/api.js';

const store = useSimulationStore();

const betTypes = [
  { value: 'basic', label: '猜號' },
  { value: 'super', label: '超級' },
  { value: 'high_low', label: '大小' },
  { value: 'odd_even', label: '單雙' },
];

const betType = ref('basic');
const starLevel = ref(3);
const selectedNumbers = ref([]);
const selectedOption = ref(null);
const multiplier = ref(1);
const betPeriods = ref(1);
const successMsg = ref('');
const nextDraw = ref(null);

const totalCost = computed(() => 25 * multiplier.value * betPeriods.value);

const canPlace = computed(() => {
  if (betType.value === 'basic') return selectedNumbers.value.length === starLevel.value;
  if (betType.value === 'super') return selectedNumbers.value.length === 1;
  if (betType.value === 'high_low' || betType.value === 'odd_even') return !!selectedOption.value;
  return false;
});

function pad(n) {
  return String(n).padStart(2, '0');
}

function toggleWidget() {
  if (store.widgetOpen) {
    store.closeWidget();
  } else {
    store.openWidget();
  }
}

function switchBetType(type) {
  betType.value = type;
  selectedNumbers.value = [];
  selectedOption.value = null;
  successMsg.value = '';
  store.error = null;
}

function setStarLevel(s) {
  starLevel.value = s;
  if (selectedNumbers.value.length > s) {
    selectedNumbers.value = selectedNumbers.value.slice(0, s);
  }
}

function toggleNumber(n) {
  const idx = selectedNumbers.value.indexOf(n);
  if (idx >= 0) {
    selectedNumbers.value.splice(idx, 1);
  } else {
    selectedNumbers.value.push(n);
  }
}

async function fetchNextDraw() {
  try {
    const res = await api.getNextDraw();
    nextDraw.value = res.data;
  } catch {
    nextDraw.value = null;
  }
}

async function handlePlace() {
  successMsg.value = '';
  const data = {
    bet_type: betType.value,
    multiplier: multiplier.value,
    bet_periods: betPeriods.value,
  };
  if (betType.value === 'basic') {
    data.star_level = starLevel.value;
    data.selected_numbers = [...selectedNumbers.value].sort();
  } else if (betType.value === 'super') {
    data.selected_numbers = [...selectedNumbers.value];
  } else {
    data.selected_option = selectedOption.value;
  }
  try {
    await store.placeBet(data);
    successMsg.value = `下注成功！共 ${betPeriods.value} 期`;
    selectedNumbers.value = [];
    selectedOption.value = null;
    fetchNextDraw();
    setTimeout(() => { successMsg.value = ''; }, 2500);
  } catch {
    // error handled in store
  }
}

// Apply preset when widget opens with data
watch(() => store.widgetPreset, (preset) => {
  if (!preset) return;
  if (preset.type) betType.value = preset.type;
  if (preset.star) starLevel.value = Number(preset.star);
  if (preset.numbers) selectedNumbers.value = [...preset.numbers];
  successMsg.value = '';
  store.error = null;
}, { immediate: true });

// Fetch next draw info when widget opens
watch(() => store.widgetOpen, (open) => {
  if (open) fetchNextDraw();
});

onMounted(() => {
  fetchNextDraw();
});
</script>

<style scoped>
.bet-widget-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9000;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

/* FAB */
.bet-fab {
  pointer-events: auto;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--secondary), #4dd9a5);
  box-shadow: 0 4px 16px rgba(48, 196, 141, 0.4);
  transition: all 0.3s ease;
}

.bet-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 24px rgba(48, 196, 141, 0.5);
}

.bet-fab.fab-open {
  background: linear-gradient(135deg, #e74c3c, #ff6b81);
  box-shadow: 0 4px 16px rgba(255, 107, 129, 0.4);
}

.fab-icon {
  line-height: 1;
}

/* Panel */
.bet-panel {
  pointer-events: auto;
  width: 360px;
  max-height: calc(100vh - 120px);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--surface-soft);
}

.panel-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.next-draw-info {
  font-size: 0.72rem;
  color: var(--primary);
  font-weight: 600;
  font-family: var(--font-mono);
  background: rgba(88, 166, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.panel-title {
  font-weight: 700;
  font-size: 0.95rem;
}

.panel-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.panel-close:hover {
  background: var(--border);
  color: var(--text);
}

/* Tabs */
.w-tabs {
  display: flex;
  padding: 10px 12px 0;
  gap: 4px;
}

.w-tab {
  flex: 1;
  padding: 7px 0;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  font-family: var(--font-main);
  font-weight: 600;
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.w-tab:hover { border-color: var(--primary); color: var(--text); }

.w-tab.active {
  background: linear-gradient(135deg, var(--primary), #7ac2ff);
  border-color: var(--primary);
  color: #08121d;
}

/* Body */
.panel-body {
  padding: 12px;
  overflow-y: auto;
  flex: 1;
}

.w-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.w-label {
  font-weight: 600;
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Star selector */
.w-star-selector {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
}

.w-star {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1.5px solid var(--border);
  background: var(--surface-soft);
  color: var(--text-secondary);
  font-weight: 700;
  font-size: 0.72rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-main);
}

.w-star:hover { border-color: var(--primary); }

.w-star.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #08121d;
}

/* Number grid */
.w-number-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 3px;
  margin-bottom: 8px;
}

.w-num {
  aspect-ratio: 1;
  border-radius: 50%;
  border: 1.5px solid var(--border);
  background: var(--surface-soft);
  color: var(--text);
  font-weight: 600;
  font-size: 0.65rem;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: var(--font-main);
  padding: 0;
}

.w-num:hover:not(:disabled) {
  border-color: var(--primary);
  transform: scale(1.12);
}

.w-num.selected {
  background: linear-gradient(135deg, var(--primary), #7ac2ff);
  border-color: var(--primary);
  color: #08121d;
  box-shadow: 0 1px 4px rgba(88, 166, 255, 0.35);
}

.w-num:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}

/* Options (big/small, odd/even) */
.w-options {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.w-opt {
  flex: 1;
  padding: 14px 0;
  border-radius: 10px;
  border: 2px solid var(--border);
  background: var(--surface-soft);
  color: var(--text);
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-main);
}

.w-opt:hover { border-color: var(--primary); }

.w-opt.active.w-opt-big,
.w-opt.active.w-opt-odd {
  background: linear-gradient(135deg, #e74c3c, #ff6b81);
  border-color: #e74c3c;
  color: #fff;
}

.w-opt.active.w-opt-small,
.w-opt.active.w-opt-even {
  background: linear-gradient(135deg, #3498db, #58a6ff);
  border-color: #3498db;
  color: #fff;
}

/* Footer */
.panel-footer {
  padding: 10px 12px 14px;
  border-top: 1px solid var(--border);
  background: var(--surface-soft);
}

.w-ctrl-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  gap: 8px;
}

.w-ctrl-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.w-ctrl-label {
  font-size: 0.72rem;
  color: var(--text-secondary);
  font-weight: 600;
  white-space: nowrap;
}

.w-mult-ctrl {
  display: flex;
  align-items: center;
  gap: 4px;
}

.w-mult-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-main);
  display: flex;
  align-items: center;
  justify-content: center;
}

.w-mult-btn:hover { border-color: var(--primary); }

.w-mult-val {
  font-weight: 700;
  font-size: 0.82rem;
  min-width: 24px;
  text-align: center;
}

.w-cost {
  color: var(--warning);
  font-weight: 600;
  font-size: 0.85rem;
  white-space: nowrap;
}

.w-place-btn {
  width: 100%;
  padding: 10px 0;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--secondary), #4dd9a5);
  color: #08121d;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--font-main);
}

.w-place-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(48, 196, 141, 0.35);
  transform: translateY(-1px);
}

.w-place-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.w-error { color: var(--accent); font-size: 0.78rem; margin-top: 6px; text-align: center; }
.w-success { color: var(--secondary); font-size: 0.78rem; margin-top: 6px; text-align: center; }

/* Panel transition */
.panel-enter-active { transition: all 0.25s ease-out; }
.panel-leave-active { transition: all 0.2s ease-in; }
.panel-enter-from { opacity: 0; transform: translateY(20px) scale(0.95); }
.panel-leave-to { opacity: 0; transform: translateY(20px) scale(0.95); }

/* Responsive */
@media (max-width: 480px) {
  .bet-panel { width: calc(100vw - 32px); }
  .bet-widget-container { right: 16px; bottom: 16px; }
}
</style>
