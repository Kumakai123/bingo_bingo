<template>
  <div class="period-selector">
    <span class="period-label">分析期數：</span>
    <div class="period-options">
      <button
        v-for="p in options"
        :key="p"
        :class="['period-btn', { active: modelValue === p }]"
        @click="selectOption(p)"
      >
        {{ p }} 期
      </button>
      <button
        :class="['period-btn', 'custom-toggle', { active: isCustomActive || showCustom }]"
        @click="openCustom"
      >
        自訂
      </button>
    </div>

    <div v-if="showCustom" class="custom-controls">
      <input
        v-model="customValue"
        class="custom-input"
        type="number"
        :min="min"
        :max="max"
        :placeholder="`${min}-${max}`"
        @keydown.enter.prevent="applyCustom"
      />
      <button class="custom-apply" @click="applyCustom">套用</button>
    </div>

    <span v-if="errorMessage" class="custom-error">{{ errorMessage }}</span>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  modelValue: { type: Number, default: 5 },
  options: { type: Array, default: () => [5, 10, 20, 30, 50, 100] },
  min: { type: Number, default: 5 },
  max: { type: Number, default: 500 },
});
const emit = defineEmits(['update:modelValue']);

const showCustom = ref(false);
const customValue = ref('');
const errorMessage = ref('');

const isCustomActive = computed(() => !props.options.includes(props.modelValue));

function selectOption(period) {
  errorMessage.value = '';
  showCustom.value = false;
  emit('update:modelValue', period);
}

function openCustom() {
  errorMessage.value = '';
  showCustom.value = true;
  customValue.value = String(props.modelValue || props.min);
}

function applyCustom() {
  const parsed = Number(customValue.value);
  if (!Number.isFinite(parsed) || !Number.isInteger(parsed)) {
    errorMessage.value = '請輸入整數期數';
    return;
  }
  if (parsed < props.min || parsed > props.max) {
    errorMessage.value = `請輸入 ${props.min} 到 ${props.max} 之間`;
    return;
  }
  errorMessage.value = '';
  showCustom.value = false;
  emit('update:modelValue', parsed);
}
</script>

<style scoped>
.period-selector {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--gap-md);
}

.period-label {
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}

.period-options {
  display: flex;
  gap: var(--gap-xs);
}

.period-btn {
  padding: 6px 16px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: #1a2736;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition);
  font-family: var(--font-main);
}

.period-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.period-btn.active {
  background: linear-gradient(135deg, var(--primary), #7ac2ff);
  border-color: var(--primary);
  color: #08121d;
}

.custom-toggle {
  border-style: dashed;
}

.custom-controls {
  display: flex;
  align-items: center;
  gap: var(--gap-xs);
}

.custom-input {
  width: 100px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: #111a26;
  color: var(--text);
  padding: 0 10px;
  font-family: var(--font-main);
}

.custom-input:focus {
  outline: none;
  border-color: var(--primary);
}

.custom-apply {
  height: 34px;
  border: 1px solid #2d4761;
  background: linear-gradient(135deg, #15324d, #1f4061);
  color: #dbe9fb;
  border-radius: 10px;
  padding: 0 12px;
  font-family: var(--font-main);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.custom-apply:hover {
  border-color: #3f6386;
}

.custom-error {
  color: #ff9aa8;
  font-size: 0.82rem;
  align-self: center;
}
</style>
