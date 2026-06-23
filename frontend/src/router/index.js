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
      path: '/liabilities/manage',
      name: 'manage-liabilities',
      component: () => import('../views/ManageLiabilitiesView.vue'),
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
