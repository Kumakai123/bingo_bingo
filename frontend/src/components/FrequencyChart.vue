<template>
  <div class="chart-container">
    <Bar v-if="type === 'bar'" :data="chartData" :options="barOptions" />
    <Doughnut v-else :data="chartData" :options="doughnutOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Bar, Doughnut } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const props = defineProps({
  type: { type: String, default: 'bar' },
  labels: { type: Array, default: () => [] },
  datasets: { type: Array, default: () => [] },
  title: { type: String, default: '' },
});

const chartData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets,
}));

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: {
      display: true,
      text: props.title,
      font: { size: 14, family: 'Noto Sans TC' },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#ecf0f1' },
    },
    x: {
      grid: { display: false },
      ticks: { font: { size: 10 } },
    },
  },
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { font: { size: 13, family: 'Noto Sans TC' }, padding: 16 },
    },
    title: {
      display: true,
      text: props.title,
      font: { size: 14, family: 'Noto Sans TC' },
    },
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 320px;
  width: 100%;
}
</style>
