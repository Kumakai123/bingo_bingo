<template>
  <div class="period-selector">
    <span class="period-label">分析期數：</span>
    <div class="period-options">
      <button
        v-for="p in options"
        :key="p"
        :class="['period-btn', { active: modelValue === p }]"
        @click="$emit('update:modelValue', p)"
      >
        {{ p }} 期
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: Number, default: 30 },
  options: { type: Array, default: () => [10, 20, 30, 50, 100] },
});
defineEmits(['update:modelValue']);
</script>

<style scoped>
.period-selector {
  display: flex;
  align-items: center;
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
  border: 2px solid var(--border);
  border-radius: 20px;
  background: var(--surface);
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
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}
</style>
