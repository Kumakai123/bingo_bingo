import { createRouter, createWebHistory } from 'vue-router';

const routes = [
    { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
    { path: '/basic', name: 'BasicAnalysis', component: () => import('../views/BasicAnalysis.vue') },
    { path: '/super', name: 'SuperNumber', component: () => import('../views/SuperNumber.vue') },
    { path: '/trend', name: 'HighLowOddEven', component: () => import('../views/HighLowOddEven.vue') },
    { path: '/smart-pick', name: 'SmartPick', component: () => import('../views/SmartPick.vue') },
    { path: '/advanced', name: 'AdvancedAnalysis', component: () => import('../views/AdvancedAnalysis.vue') },
    { path: '/simulation', name: 'Simulation', component: () => import('../views/Simulation.vue') },
];

const router = createRouter({
    history: createWebHistory('/bingo_bingo/'),
    routes,
});

export default router;
