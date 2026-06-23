<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Budgeting Overview</h1>
        <p class="text-muted">Monitor your cash flow and expenses.</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <span class="text-muted">Period:</span>
        <select v-model="selectedMonth" class="form-input" style="width: 120px;" @change="fetchData">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <input v-model="selectedYear" type="number" min="2000" max="2100" class="form-input" style="width: 100px;" @change="fetchData" />
        <button class="btn btn-primary" @click="showModal = true" style="margin-left: 1rem;">+ Add Transaction</button>
      </div>
    </header>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Total Income</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--success);">RM{{ formatCurrency(income) }}</div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Total Expenses</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--danger);">RM{{ formatCurrency(expenses) }}</div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Net Cash Flow</div>
        <div style="font-size: 2rem; font-weight: 700;" :class="netCashFlow >= 0 ? 'text-success' : 'text-danger'">RM{{ formatCurrency(netCashFlow) }}</div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Expense Breakdown</h3>
        <div v-if="expenseBreakdown.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No expenses recorded for this month.</div>
        <div v-else style="display: flex; justify-content: center; align-items: center; min-height: 250px;">
          <PieChart :labels="expenseBreakdown.map(i => i.category)" :data="expenseBreakdown.map(i => i.amount)" />
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
            <select v-if="!isNewCategory" v-model="form.categoryId" class="form-input">
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
            <input v-else v-model="form.newCategoryName" type="text" class="form-input" placeholder="New Category Name" />
            <button type="button" class="btn btn-secondary" @click="isNewCategory = !isNewCategory">
              {{ isNewCategory ? 'Cancel' : 'New' }}
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

        <div class="form-group">
          <label class="form-label">Description (Optional)</label>
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
import { ref, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import PieChart from '@/components/PieChart.vue'

const income = ref(0)
const expenses = ref(0)
const netCashFlow = ref(0)
const expenseBreakdown = ref([])

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const showModal = ref(false)
const loading = ref(false)
const categories = ref([])
const isNewCategory = ref(false)

const getInitialForm = () => ({
  type: 'EXPENSE',
  categoryId: null,
  newCategoryName: '',
  amount: '',
  date: new Date().toISOString().split('T')[0],
  description: ''
})

const form = ref(getInitialForm())

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchData = async () => {
  try {
    const res = await api.get(`/budgeting/transactions/summary/?month=${selectedMonth.value}&year=${selectedYear.value}`)
    income.value = res.data.total_income
    expenses.value = res.data.total_expenses
    netCashFlow.value = res.data.net_cash_flow
    expenseBreakdown.value = res.data.expense_breakdown
  } catch (e) {
    console.error(e)
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/budgeting/categories/')
    categories.value = res.data.filter(c => c.type === form.value.type)
    if (categories.value.length > 0 && !form.value.categoryId) {
      form.value.categoryId = categories.value[0].id
    }
  } catch (e) {
    console.error(e)
  }
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

    await api.post('/budgeting/transactions/', {
      category: categoryId,
      amount: form.value.amount,
      date: form.value.date,
      description: form.value.description
    })

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
})
</script>
