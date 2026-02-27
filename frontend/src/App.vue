<template>
  <div class="app-container">
    <nav class="navbar">
      <router-link to="/" class="navbar-brand">
        <span>🎱</span> BINGO 分析
      </router-link>
      <div class="navbar-right">
        <ul class="navbar-links">
          <li><router-link to="/">儀表板</router-link></li>
          <li><router-link to="/smart-pick">智慧選號</router-link></li>
          <li><router-link to="/basic">基本玩法</router-link></li>
          <li><router-link to="/super">超級號碼</router-link></li>
          <li><router-link to="/trend">大小單雙</router-link></li>
          <li><router-link to="/advanced">進階分析</router-link></li>
        </ul>
        <button class="refresh-btn" :disabled="store.loading || store.refreshing" @click="handleManualRefresh">
          <span>{{ store.refreshing ? '抓新資料中...' : (store.loading ? '更新中...' : '手動刷新') }}</span>
        </button>
      </div>
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

async function handleManualRefresh() {
  await store.manualRefresh();
}

onMounted(() => {
  store.fetchAll();
  store.startPolling();
});

onUnmounted(() => {
  store.stopPolling();
});
</script>
