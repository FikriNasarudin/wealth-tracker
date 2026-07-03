import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import { Capacitor } from '@capacitor/core'

const router = createRouter({
  history: Capacitor.isNativePlatform() 
    ? createWebHashHistory(import.meta.env.BASE_URL) 
    : createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/banking',
      name: 'banking',
      component: () => import('../views/BankingView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/budgeting',
      name: 'budgeting',
      component: () => import('../views/BudgetingView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/budgeting/recurring',
      name: 'budgeting-recurring',
      component: () => import('../views/ManageRecurringView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/budgeting/targets',
      name: 'budgeting-targets',
      component: () => import('../views/ManageTargetsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/budgeting/history',
      name: 'budgeting-history',
      component: () => import('../views/BudgetingHistoryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/assets',
      name: 'assets',
      component: () => import('../views/AssetsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/assets/history',
      name: 'assets-history',
      component: () => import('../views/AssetsHistoryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/assets/manage',
      name: 'manage-assets',
      component: () => import('../views/ManageAssetsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/liabilities',
      name: 'liabilities',
      component: () => import('../views/LiabilitiesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/liabilities/history',
      name: 'liabilities-history',
      component: () => import('../views/LiabilitiesHistoryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/liabilities/credit-cards',
      name: 'credit-cards',
      component: () => import('../views/ManageCreditCardsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/liabilities/manage',
      name: 'manage-liabilities',
      component: () => import('../views/ManageLiabilitiesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/goals',
      name: 'goals',
      component: () => import('../views/GoalsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/server-settings',
      name: 'server-settings',
      component: () => import('../views/ServerSettingsView.vue')
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const backendUrl = localStorage.getItem('backend_url')
  const isNative = Capacitor.isNativePlatform()
  
  if (isNative && !backendUrl && to.name !== 'server-settings') {
    next('/server-settings')
  } else if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.name === 'login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
