<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem;">
      <div>
        <h1 style="font-weight: 600;">Budgeting Overview</h1>
        <p class="text-muted">Monitor your cash flow and expenses.</p>
      </div>
      <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; justify-content: flex-end;">
        <button class="btn btn-secondary" @click="startTour" style="padding: 0.5rem 1rem; font-size: 0.875rem; display: flex; align-items: center; gap: 0.25rem;">
          <svg style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Help
        </button>
        <span class="text-muted" style="font-size: 0.875rem; margin-left: 0.5rem;">Period:</span>
        <select v-model="selectedMonth" class="form-input" style="width: 120px;" @change="fetchData">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <select v-model="selectedYear" class="form-input" style="width: 95px;" @change="fetchData">
          <option v-for="y in yearsList" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </header>

    <AIAdvisorCard v-if="enableAI" dashboardType="BUDGETING" :month="selectedMonth" :year="selectedYear" style="margin-bottom: 2rem;" />

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500; display: flex; justify-content: space-between;">
          <span>Total Income</span>
          <span v-if="forecastIncome > 0 && !dataLoading">Target: RM{{ formatCurrency(forecastIncome) }}</span>
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 50%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success); margin-bottom: 0.5rem;">RM{{ formatCurrency(income) }}</div>
          <div v-if="forecastIncome > 0" style="width: 100%; height: 6px; background: var(--bg-background); border-radius: 3px; overflow: hidden;">
            <div :style="{
              width: Math.min((income / forecastIncome) * 100, 100) + '%',
              height: '100%',
              background: 'var(--success)'
            }"></div>
          </div>
        </template>
      </div>

      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500; display: flex; justify-content: space-between;">
          <span>Total Expenses</span>
          <span v-if="forecastExpenses > 0 && !dataLoading">Target: RM{{ formatCurrency(forecastExpenses) }}</span>
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 45%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--danger); margin-bottom: 0.5rem;">RM{{ formatCurrency(expenses) }}</div>
          <div v-if="forecastExpenses > 0" style="width: 100%; height: 6px; background: var(--bg-background); border-radius: 3px; overflow: hidden; margin-bottom: 0.5rem;">
            <div :style="{
              width: Math.min((expenses / forecastExpenses) * 100, 100) + '%',
              height: '100%',
              background: expenses > forecastExpenses ? 'var(--danger)' : (expenses > forecastExpenses * 0.8 ? 'var(--warning)' : 'var(--success)')
            }"></div>
          </div>
          <div class="text-muted" style="font-size: 0.875rem; display: flex; align-items: center;">
            <svg style="width: 16px; height: 16px; margin-right: 0.25rem; color: var(--danger);" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
            Burn Rate: RM{{ formatCurrency(dailyBurnRate) }} / day
          </div>
        </template>
      </div>

      <div id="tour-cash-flow" class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500; display: flex; justify-content: space-between;">
          <span>
            Net Cash Flow
            <Tooltip title="Net Cash Flow" description="The difference between your total income and total expenses for the selected month." example="RM5,000 Income - RM3,000 Expenses = RM2,000" />
          </span>
          <span v-if="(forecastIncome > 0 || forecastExpenses > 0) && !dataLoading">Target: RM{{ formatCurrency(forecastIncome - forecastExpenses) }}</span>
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 40%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;" :class="netCashFlow >= 0 ? 'text-success' : 'text-danger'">RM{{ formatCurrency(netCashFlow) }}</div>
          <div class="text-muted" style="font-size: 0.875rem; display: flex; align-items: center;">
            <svg style="width: 16px; height: 16px; margin-right: 0.25rem;" :class="savingsRate >= 20 ? 'text-success' : (savingsRate >= 10 ? 'text-warning' : 'text-danger')" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            Savings Rate: <strong :class="savingsRate >= 20 ? 'text-success' : (savingsRate >= 10 ? 'text-warning' : 'text-danger')" style="margin-left: 0.25rem;">{{ savingsRate.toFixed(1) }}%</strong>
          </div>
        </template>
      </div>
    </div>

    <div class="grid-2col" style="margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Income vs Expense (6 Months)</h3>
        <div style="height: 300px;">
          <BarChart v-if="trendData.length > 0" :labels="trendLabels" :datasets="trendDatasets" />
        </div>
      </div>

      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">Category Targets</h3>
          <router-link to="/budgeting/targets" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Manage Targets</router-link>
        </div>
        
        <div style="margin-bottom: 1rem; display: flex; gap: 0.5rem; background: var(--bg-background); padding: 0.25rem; border-radius: 0.5rem; width: max-content;">
          <button class="btn" :class="activeTab === 'EXPENSE' ? 'btn-primary' : 'btn-secondary'" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="activeTab = 'EXPENSE'">Expenses</button>
          <button class="btn" :class="activeTab === 'INCOME' ? 'btn-primary' : 'btn-secondary'" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="activeTab = 'INCOME'">Income</button>
        </div>

        <div v-if="activeTab === 'EXPENSE'">
          <div v-if="expenseBreakdown.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No expenses recorded for this month.</div>
          <div v-else style="display: flex; flex-direction: column; gap: 1rem; max-height: 250px; overflow-y: auto; padding-right: 0.5rem;">
            <div v-for="item in expenseBreakdown" :key="item.category_id || 'uncat'" style="display: flex; flex-direction: column; gap: 0.5rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500;">{{ item.category }} ({{ item.weight_percentage }}%)</span>
                <span class="text-muted">RM{{ formatCurrency(item.amount) }} <span v-if="item.budget_limit">/ RM{{ formatCurrency(item.budget_limit) }}</span></span>
              </div>
              <div style="width: 100%; height: 8px; background: var(--bg-background); border-radius: 4px; overflow: hidden;">
                <div :style="{
                  width: item.budget_limit ? Math.min((item.amount / item.budget_limit) * 100, 100) + '%' : '100%',
                  height: '100%',
                  background: item.budget_limit ? (item.amount > item.budget_limit ? 'var(--danger)' : (item.amount > item.budget_limit * 0.8 ? 'var(--warning)' : 'var(--success)')) : 'var(--accent-primary)'
                }"></div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="activeTab === 'INCOME'">
          <div v-if="incomeBreakdown.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No income recorded for this month.</div>
          <div v-else style="display: flex; flex-direction: column; gap: 1rem; max-height: 250px; overflow-y: auto; padding-right: 0.5rem;">
            <div v-for="item in incomeBreakdown" :key="item.category_id || 'uncat'" style="display: flex; flex-direction: column; gap: 0.5rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500;">{{ item.category }} ({{ item.weight_percentage }}%)</span>
                <span class="text-muted">RM{{ formatCurrency(item.amount) }} <span v-if="item.budget_limit">/ RM{{ formatCurrency(item.budget_limit) }}</span></span>
              </div>
              <div style="width: 100%; height: 8px; background: var(--bg-background); border-radius: 4px; overflow: hidden;">
                <div :style="{
                  width: item.budget_limit ? Math.min((item.amount / item.budget_limit) * 100, 100) + '%' : '100%',
                  height: '100%',
                  background: 'var(--success)'
                }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid-2col" style="margin-bottom: 2rem;">
      <div id="tour-categories" class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-weight: 600; margin: 0;">Recent Transactions</h3>
          <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; align-items: center;">
            <button class="btn btn-secondary" style="padding: 0.35rem 0.7rem; font-size: 0.8rem;" @click="quickAdd('EXPENSE', 'Food')">🍕 Food</button>
            <button class="btn btn-secondary" style="padding: 0.35rem 0.7rem; font-size: 0.8rem;" @click="quickAdd('EXPENSE', 'Transport')">🚗 Transport</button>
            <button id="tour-add-txn" class="btn btn-primary" style="padding: 0.35rem 0.7rem; font-size: 0.8rem;" @click="showModal = true">+ Add Transaction</button>
          </div>
        </div>
        <div class="table-container">
          <table class="data-table" style="width: 100%; text-align: left; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid var(--border-color);">
                <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Date</th>
                <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Category</th>
                <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Name</th>
                <th style="padding: 0.75rem 0; text-align: right; color: var(--text-muted); font-weight: 500;">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="recentTransactions.length === 0">
                <td colspan="4" class="text-muted" style="text-align: center; padding: 2rem;">No recent transactions.</td>
              </tr>
              <tr v-for="txn in recentTransactions" :key="txn.id" style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 0.75rem 0;">{{ txn.date }}</td>
                <td style="padding: 0.75rem 0; color: var(--text-muted);">{{ txn.category_name || 'Uncategorized' }}</td>
                <td style="padding: 0.75rem 0; font-weight: 500;">{{ txn.name }}</td>
                <td style="padding: 0.75rem 0; text-align: right;" :class="txn.type === 'INCOME' ? 'text-success' : 'text-danger'">
                  {{ txn.type === 'INCOME' ? '+' : '-' }}RM{{ formatCurrency(txn.amount) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div id="tour-subscriptions" class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Fixed Income & Costs
            <Tooltip title="Recurring Items" description="Fixed income like salary, and fixed costs like Netflix, that happen automatically every month." example="Salary, Gym Membership" />
          </h3>
          <router-link to="/budgeting/recurring" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Manage Items</router-link>
        </div>
        <div v-if="activeUnloggedSubscriptions.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No pending recurring items this month.</div>
        <div v-else style="max-height: 300px; overflow-y: auto;">
        <div class="table-container">
          <table class="data-table" style="width: 100%; text-align: left; border-collapse: collapse;">
            <tbody>
              <tr v-for="sub in activeUnloggedSubscriptions" :key="sub.id" style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 0.75rem 0; font-weight: 500;">
                  <span :class="sub.type === 'INCOME' ? 'text-success' : 'text-danger'" style="margin-right: 0.5rem;">{{ sub.type === 'INCOME' ? '↑' : '↓' }}</span>
                  {{ sub.name }}
                </td>
                <td style="padding: 0.75rem 0; color: var(--text-muted); text-align: right;" :class="sub.type === 'INCOME' ? 'text-success' : 'text-danger'">
                  {{ sub.type === 'INCOME' ? '+' : '-' }}RM{{ formatCurrency(sub.amount) }} / {{ sub.billing_cycle === 'MONTHLY' ? 'mo' : 'yr' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
          <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; font-weight: 600;">
            <span>Monthly Equivalent:</span>
            <span>
              <span class="text-success" v-if="monthlyFixedIncome > 0">+RM{{ formatCurrency(monthlyFixedIncome) }}</span>
              <span style="margin: 0 0.5rem;" v-if="monthlyFixedIncome > 0 && monthlyFixedCosts > 0">|</span>
              <span class="text-danger" v-if="monthlyFixedCosts > 0">-RM{{ formatCurrency(monthlyFixedCosts) }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Debit Account Breakdown (Recurring Expenses)</h3>
        <div v-if="debitAccountBreakdown.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">
          No recurring expenses configured with debit accounts.
        </div>
        <div v-else class="table-container">
          <table class="data-table" style="width: 100%; text-align: left; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid var(--border-color);">
                <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Debit Account</th>
                <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500; text-align: right;">Monthly Value</th>
                <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500; text-align: right; width: 120px;">Percentage</th>
                <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500; width: 200px;">Share</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in debitAccountBreakdown" :key="item.name" style="border-bottom: 1px solid var(--border-color);">
                <td style="padding: 0.75rem 0; font-weight: 600;">{{ item.name }}</td>
                <td style="padding: 0.75rem 0; text-align: right; font-weight: 500; color: var(--danger);">
                  -RM{{ formatCurrency(item.amount) }}
                </td>
                <td style="padding: 0.75rem 0; text-align: right; font-weight: 600; color: var(--accent-primary);">
                  {{ item.percentage.toFixed(1) }}%
                </td>
                <td style="padding: 0.75rem 0; vertical-align: middle;">
                  <div style="width: 100%; height: 8px; background: var(--bg-background); border-radius: 4px; overflow: hidden;">
                    <div :style="{
                      width: item.percentage + '%',
                      height: '100%',
                      background: 'var(--accent-primary)'
                    }"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Modal :show="showModal" title="Add Transaction" @close="showModal = false">
      <form @submit.prevent="submitTransaction">
        <div class="form-group">
          <label class="form-label">Type</label>
          <select v-model="form.type" class="form-input" @change="fetchCategories">
            <option value="INCOME">Income</option>
            <option value="EXPENSE">Expense</option>
          </select>
        </div>
        
        <div class="form-group">
          <label class="form-label">Category</label>
          <div style="display: flex; gap: 0.5rem;">
            <SearchableSelect 
              v-if="!isNewCategory" 
              v-model="form.categoryId" 
              :options="categoryOptions" 
              placeholder="Search category..." 
              style="flex: 1;"
            />
            <input v-else v-model="form.newCategoryName" type="text" class="form-input" placeholder="New Category Name" />
            <button type="button" class="btn btn-secondary" @click="isNewCategory = !isNewCategory">
              {{ isNewCategory ? 'Cancel' : 'New' }}
            </button>
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">Item Name</label>
          <input v-model="form.name" type="text" class="form-input" placeholder="e.g. Groceries or Salary" required />
          
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;" v-if="targets && targets.length > 0">
            <button v-for="t in targets.filter(t => t.type === form.type && t.name)" :key="t.id" 
                    type="button" class="btn" 
                    :class="form.name.toLowerCase() === t.name.toLowerCase() ? 'btn-primary' : 'btn-secondary'"
                    @click="form.name = t.name" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">
              {{ t.name }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Amount</label>
          <input v-model="form.amount" type="number" step="0.01" class="form-input" required />
        </div>

        <div class="form-group">
          <label class="form-label">Date</label>
          <input v-model="form.date" type="date" class="form-input" required />
        </div>

        <div class="form-group" v-if="form.type === 'EXPENSE'">
          <label class="form-label">Payment Method / Account</label>
          <SearchableSelect 
            v-model="form.paymentAccount" 
            :options="paymentAccountOptions" 
            placeholder="Search payment account..."
          />
        </div>

        <div class="form-group">
          <label class="form-label">Description (Optional notes)</label>
          <input v-model="form.description" type="text" class="form-input" />
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Transaction' }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import BarChart from '@/components/BarChart.vue'
import Tooltip from '@/components/Tooltip.vue'
import AIAdvisorCard from '@/components/AIAdvisorCard.vue'
import { driver } from 'driver.js'
import SearchableSelect from '@/components/SearchableSelect.vue'

const enableAI = import.meta.env.VITE_ENABLE_AI_ADVISOR === 'true'

const startTour = () => {
  const driverObj = driver({
    showProgress: true,
    steps: [
      { element: '#tour-cash-flow', popover: { title: 'Net Cash Flow', description: 'This tracks whether you are earning more than you spend. It calculates all your logged transactions as well as your unlogged fixed income and costs.' } },
      { element: '#tour-categories', popover: { title: 'Recent Transactions', description: 'A quick overview of your latest spending. You can manage detailed targets and limits above.' } },
      { element: '#tour-subscriptions', popover: { title: 'Fixed Income & Costs', description: 'Add your recurring fixed income (e.g. salary) and costs (e.g. Netflix) here. They will automatically be factored into your disposable income calculation.' } },
      { element: '#tour-add-txn', popover: { title: 'Add Transaction', description: 'Click here to log a new income or expense. Use the quick add buttons for fast entry!' } }
    ]
  });
  driverObj.drive();
}

const income = ref(0)
const expenses = ref(0)
const forecastIncome = ref(0)
const forecastExpenses = ref(0)
const netCashFlow = ref(0)
const expenseBreakdown = ref([])
const incomeBreakdown = ref([])
const recentTransactions = ref([])
const trendData = ref([])
const activeTab = ref('EXPENSE')

const monthlyFixedCosts = ref(0)
const monthlyFixedIncome = ref(0)
const loggedSubscriptionIds = ref([])
const subscriptions = ref([])
const targets = ref([])
const categories = ref([])
const creditCards = ref([])
const isNewCategory = ref(false)

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const yearsList = computed(() => {
  const current = new Date().getFullYear()
  const years = []
  for (let y = current - 5; y <= current + 5; y++) {
    years.push(y)
  }
  return years
})

const showModal = ref(false)
const loading = ref(false)

const getInitialForm = () => ({
  type: 'EXPENSE',
  categoryId: null,
  newCategoryName: '',
  name: '',
  amount: '',
  date: new Date().toISOString().split('T')[0],
  description: '',
  paymentAccount: ''
})

const form = ref(getInitialForm())

const categoryOptions = computed(() => {
  return [
    { value: null, label: 'Uncategorized' },
    ...categories.value.map(c => ({ value: c.id, label: c.name }))
  ]
})

const paymentAccountOptions = computed(() => {
  return [
    { value: '', label: 'Cash / Default Account' },
    ...creditCards.value.map(cc => ({ value: cc.name, label: `${cc.name} (Credit Card)` }))
  ]
})

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const activeUnloggedSubscriptions = computed(() => {
  const currentMonthKey = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}`
  return subscriptions.value.filter(s => {
    const isArchived = s.status === 'ARCHIVED'
    const isLogged = loggedSubscriptionIds.value.includes(s.id)
    const isPaused = s.paused_months && s.paused_months.includes(currentMonthKey)
    return !isArchived && !isLogged && !isPaused
  })
})

const savingsRate = computed(() => {
  if (income.value <= 0) return 0;
  return (netCashFlow.value / income.value) * 100;
})

const debitAccountBreakdown = computed(() => {
  const activeExpenses = subscriptions.value.filter(s => s.status === 'ACTIVE' && s.type === 'EXPENSE')
  
  const breakdown = {}
  let total = 0
  
  activeExpenses.forEach(s => {
    const amt = parseFloat(s.amount)
    const monthlyEquivalent = s.billing_cycle === 'MONTHLY' ? amt : amt / 12
    const accountName = s.payment_account || 'None (Cash/Other)'
    
    if (!breakdown[accountName]) {
      breakdown[accountName] = 0
    }
    breakdown[accountName] += monthlyEquivalent
    total += monthlyEquivalent
  })
  
  return Object.keys(breakdown).map(name => ({
    name,
    amount: breakdown[name],
    percentage: total > 0 ? (breakdown[name] / total) * 100 : 0
  })).sort((a, b) => b.amount - a.amount)
})

const dailyBurnRate = computed(() => {
  if (expenses.value <= 0) return 0;
  const currentRealMonth = d.getMonth() + 1;
  const currentRealYear = d.getFullYear();
  let days = 1;
  
  if (selectedYear.value === currentRealYear && selectedMonth.value === currentRealMonth) {
    days = Math.max(d.getDate(), 1);
  } else {
    days = new Date(selectedYear.value, selectedMonth.value, 0).getDate();
  }
  return expenses.value / days;
})

const trendLabels = computed(() => trendData.value.map(d => d.label))
const trendDatasets = computed(() => [
  { 
    label: 'Income', 
    data: trendData.value.map(d => d.income), 
    backgroundColor: '#10B981',
    borderRadius: 4
  },
  { 
    label: 'Expense', 
    data: trendData.value.map(d => d.expense), 
    backgroundColor: '#EF4444',
    borderRadius: 4
  }
])

const dataLoading = ref(true)

const fetchData = async () => {
  dataLoading.value = true
  try {
    const res = await api.get(`/budgeting/transactions/summary/?month=${selectedMonth.value}&year=${selectedYear.value}`)
    income.value = res.data.total_income
    expenses.value = res.data.total_expenses
    forecastIncome.value = res.data.forecast_income || 0
    forecastExpenses.value = res.data.forecast_expenses || 0
    netCashFlow.value = res.data.net_cash_flow
    expenseBreakdown.value = res.data.expense_breakdown
    incomeBreakdown.value = res.data.income_breakdown || []
    recentTransactions.value = res.data.recent_transactions || []
    monthlyFixedCosts.value = res.data.monthly_fixed_costs || 0
    monthlyFixedIncome.value = res.data.monthly_fixed_income || 0
    loggedSubscriptionIds.value = res.data.logged_subscription_ids || []
    targets.value = res.data.targets || []
  } catch (e) {
    console.error(e)
  }
  
  try {
    const trendRes = await api.get('/budgeting/transactions/trend/')
    trendData.value = trendRes.data
  } catch(e) {
    console.error(e)
  } finally {
    dataLoading.value = false
  }
}

const fetchSubscriptions = async () => {
  try {
    const res = await api.get('/budgeting/subscriptions/')
    subscriptions.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/budgeting/categories/')
    categories.value = res.data.filter(c => c.type === form.value.type)
  } catch (e) {
    console.error(e)
  }
}

const fetchCreditCards = async () => {
  try {
    const res = await api.get('/liabilities/lenders/')
    const catRes = await api.get('/liabilities/categories/')
    const ccCat = catRes.data.find(c => c.name.toLowerCase() === 'credit cards')
    if (ccCat) {
      creditCards.value = res.data.filter(l => l.category === ccCat.id && l.is_active)
    } else {
      creditCards.value = []
    }
  } catch (e) {
    console.error("Failed to fetch credit cards", e)
  }
}

const quickAdd = (type, categoryName) => {
  form.value = getInitialForm()
  form.value.type = type
  fetchCategories().then(() => {
    const cat = categories.value.find(c => c.name.toLowerCase() === categoryName.toLowerCase())
    if (cat) {
      form.value.categoryId = cat.id
      isNewCategory.value = false
    } else {
      isNewCategory.value = true
      form.value.newCategoryName = categoryName
    }
    showModal.value = true
  })
}

const submitTransaction = async () => {
  loading.value = true
  try {
    let categoryId = form.value.categoryId

    if (isNewCategory.value && form.value.newCategoryName) {
      const catRes = await api.post('/budgeting/categories/', {
        name: form.value.newCategoryName,
        type: form.value.type
      })
      categoryId = catRes.data.id
    }

    const payload = {
      category: categoryId,
      name: form.value.name,
      type: form.value.type,
      amount: form.value.amount,
      date: form.value.date,
      description: form.value.description
    }

    if (form.value.paymentAccount) {
      payload.payment_account = form.value.paymentAccount
    }

    await api.post('/budgeting/transactions/', payload)

    showModal.value = false
    isNewCategory.value = false
    
    // Automatically switch the view to the month/year of the newly added transaction
    const dateParts = form.value.date.split('-')
    if (dateParts.length >= 2) {
      selectedYear.value = parseInt(dateParts[0])
      selectedMonth.value = parseInt(dateParts[1])
    }
    
    form.value = getInitialForm()
    
    await fetchData()
    await fetchCategories()
  } catch (e) {
    console.error(e)
    alert('Failed to save transaction')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await api.get('/budgeting/transactions/')
    if (res.data && res.data.length > 0) {
      const latest = res.data.reduce((prev, current) => {
        const prevDate = new Date(prev.date)
        const currDate = new Date(current.date)
        return currDate > prevDate ? current : prev
      })
      const d = new Date(latest.date)
      selectedMonth.value = d.getMonth() + 1
      selectedYear.value = d.getFullYear()
    }
  } catch(e) {
    console.error(e)
  }

  await fetchData()
  await fetchCategories()
  await fetchSubscriptions()
  await fetchCreditCards()
})
</script>
