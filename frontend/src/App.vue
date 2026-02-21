<template>
  <div class="app-container">
    <nav class="navbar">
      <router-link to="/" class="navbar-brand">
        <span>🎱</span> BINGO 分析
      </router-link>
      <ul class="navbar-links">
        <li><router-link to="/">儀表板</router-link></li>
        <li><router-link to="/basic">基本玩法</router-link></li>
        <li><router-link to="/super">超級號碼</router-link></li>
        <li><router-link to="/trend">大小單雙</router-link></li>
      </ul>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import { usePredictionStore } from './stores/prediction.js';

const store = usePredictionStore();

onMounted(() => {
  store.fetchAll();
  store.startPolling();
});

onUnmounted(() => {
  store.stopPolling();
});
</script>
