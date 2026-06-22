import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/budgeting',
      name: 'budgeting',
      component: () => import('../views/BudgetingView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/budgeting/history',
      name: 'budgeting-history',
      component: () => import('../views/BudgetingHistoryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/investments',
      name: 'investments',
      component: () => import('../views/InvestmentsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/investments/history',
      name: 'investments-history',
      component: () => import('../views/InvestmentsHistoryView.vue'),
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
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.name === 'login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
