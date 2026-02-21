import { createRouter, createWebHistory } from 'vue-router';

const routes = [
    { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
    { path: '/basic', name: 'BasicAnalysis', component: () => import('../views/BasicAnalysis.vue') },
    { path: '/super', name: 'SuperNumber', component: () => import('../views/SuperNumber.vue') },
    { path: '/trend', name: 'HighLowOddEven', component: () => import('../views/HighLowOddEven.vue') },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
