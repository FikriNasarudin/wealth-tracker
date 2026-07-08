<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Transaction History</h1>
        <p class="text-muted">Manage your raw transaction data.</p>
      </div>
      <button class="btn btn-primary" @click="openModal()">+ Add Transaction</button>
    </header>

    <div class="card" style="margin-bottom: 1.5rem; position: relative; z-index: 50;">
      <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Type</label>
          <select v-model="filters.type" class="form-input">
            <option value="">All Types</option>
            <option value="INCOME">Income</option>
            <option value="EXPENSE">Expense</option>
          </select>
        </div>
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Category</label>
          <select v-model="filters.category" class="form-input">
            <option value="">All Categories</option>
            <option v-for="c in categories" :key="c.id" :value="c.name">{{ c.name }}</option>
          </select>
        </div>
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Name</label>
          <input v-model="filters.name" type="text" class="form-input" placeholder="Search item name..." />
        </div>
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Description</label>
          <input v-model="filters.search" type="text" class="form-input" placeholder="Search description..." />
        </div>
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Period</label>
          <SearchableSelect v-model="filters.month" :options="periodOptions" placeholder="All Periods" />
        </div>
        <div style="display: flex; align-items: flex-end;">
          <button class="btn btn-secondary" @click="clearFilters">Clear Filters</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="transactions-list" style="display: flex; flex-direction: column; gap: 0.75rem;">
        <div v-if="filteredHistory.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No transactions match your filters.</div>
        <div v-else v-for="item in paginatedHistory" :key="item.id" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(255,255,255,0.015); border-radius: var(--border-radius-sm); border: 1px solid var(--border-color); transition: background var(--transition-fast);">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div :style="{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: item.type === 'INCOME' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              color: item.type === 'INCOME' ? 'var(--success)' : 'var(--danger)',
              fontWeight: '600'
            }">
              {{ item.type === 'INCOME' ? '↑' : '↓' }}
            </div>
            <div style="display: flex; flex-direction: column;">
              <span style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary);">
                {{ item.name }}
                <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 500; margin-left: 0.5rem;">
                  ({{ item.category_name || 'Uncategorized' }})
                </span>
              </span>
              <span style="font-size: 0.75rem; color: var(--text-muted);">
                Amount: <strong :class="item.type === 'INCOME' ? 'text-success' : 'text-danger'">RM{{ formatCurrency(item.amount) }}</strong> • {{ item.date }}
                <template v-if="item.description"> • <span style="font-style: italic;">{{ item.description }}</span></template>
              </span>
            </div>
          </div>
          
          <div style="display: flex; gap: 0.4rem;">
            <button class="btn btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="editTransaction(item)">Edit</button>
            <button class="btn btn-danger" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="deleteTransaction(item.id)">Delete</button>
          </div>
        </div>
        <Pagination v-model="currentPage" :totalItems="filteredHistory.length" :itemsPerPage="itemsPerPage" />
      </div>
    </div>

    <!-- Modal -->
    <Modal :show="showModal" :title="editMode ? 'Edit Transaction' : 'Add Transaction'" @close="showModal = false">
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
              <option :value="null">Uncategorized</option>
              <option v-for="c in categories.filter(c => c.type === form.type)" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
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

        <div class="form-group">
          <label class="form-label">Description (Optional)</label>
          <input v-model="form.description" type="text" class="form-input" />
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : (editMode ? 'Update Transaction' : 'Save Transaction') }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import Pagination from '@/components/Pagination.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'

const route = useRoute()

const history = ref([])
const showModal = ref(false)
const loading = ref(false)
const editMode = ref(false)
const editingId = ref(null)
const targets = ref([])
const categories = ref([])
const isNewCategory = ref(false)

const d = new Date()
const periodOptions = ref([])

const generatePeriodOptions = () => {
  let oldestY = null
  let oldestM = null
  
  if (history.value && history.value.length > 0) {
    history.value.forEach(item => {
      if (item.date) {
        const parts = item.date.split('-')
        const itemY = Number(parts[0])
        const itemM = Number(parts[1])
        if (itemY && itemM) {
          if (!oldestY || itemY < oldestY || (itemY === oldestY && itemM < oldestM)) {
            oldestY = itemY
            oldestM = itemM
          }
        }
      }
    })
  }
  
  const options = [{ value: '', label: 'All Periods' }]
  const currentY = d.getFullYear()
  const currentM = d.getMonth() + 1
  
  let startYear = oldestY || (currentY - 2)
  let startMonth = oldestM || 1
  
  const shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  
  let y = startYear
  let m = startMonth
  
  while (y < currentY || (y === currentY && m <= currentM)) {
    const val = `${y}-${String(m).padStart(2, '0')}`
    const lbl = `${shortMonths[m - 1]} ${y}`
    options.push({ value: val, label: lbl })
    m++
    if (m > 12) {
      m = 1
      y++
    }
  }
  
  periodOptions.value = options
}

const filters = ref({
  type: '',
  category: '',
  name: '',
  search: '',
  month: ''
})

const clearFilters = () => {
  filters.value = { type: '', category: '', name: '', search: '', month: '' }
}

const filteredHistory = computed(() => {
  return history.value.filter(item => {
    // Type Filter
    if (filters.value.type && item.type !== filters.value.type) return false
    // Category Filter
    if (filters.value.category && item.category_name !== filters.value.category) return false
    // Name Filter
    if (filters.value.name) {
      const nameLower = filters.value.name.toLowerCase()
      if (!item.name || !item.name.toLowerCase().includes(nameLower)) return false
    }
    // Search Filter
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      if (!item.description || !item.description.toLowerCase().includes(searchLower)) return false
    }
    // Month Filter (YYYY-MM)
    if (filters.value.month) {
      const itemMonth = item.date.substring(0, 7)
      if (itemMonth !== filters.value.month) return false
    }
    return true
  })
})

const currentPage = ref(1)
const itemsPerPage = 10

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredHistory.value.slice(start, start + itemsPerPage)
})

watch([filters, () => filteredHistory.value.length], () => {
  currentPage.value = 1
}, { deep: true })

const getInitialForm = () => ({
  type: 'EXPENSE',
  categoryId: null,
  newCategoryName: '',
  name: '',
  amount: '',
  date: new Date().toISOString().split('T')[0],
  description: ''
})

const form = ref(getInitialForm())

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchHistory = async () => {
  try {
    const res = await api.get('/budgeting/transactions/')
    history.value = res.data.sort((a, b) => new Date(b.date) - new Date(a.date))
    generatePeriodOptions()
  } catch (e) {
    console.error(e)
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/budgeting/categories/')
    categories.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchTargets = async () => {
  try {
    const res = await api.get('/budgeting/targets/')
    targets.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const openModal = () => {
  editMode.value = false
  editingId.value = null
  isNewCategory.value = false
  form.value = getInitialForm()
  showModal.value = true
}

const editTransaction = async (item) => {
  editMode.value = true
  editingId.value = item.id
  isNewCategory.value = false
  form.value = {
    type: item.type,
    categoryId: item.category,
    newCategoryName: '',
    name: item.name,
    amount: item.amount,
    date: item.date,
    description: item.description || ''
  }
  showModal.value = true
}

const deleteTransaction = async (id) => {
  if (confirm('Are you sure you want to delete this transaction?')) {
    try {
      await api.delete(`/budgeting/transactions/${id}/`)
      fetchHistory()
    } catch (e) {
      console.error(e)
      alert('Failed to delete transaction')
    }
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

    const payload = {
      category: categoryId,
      name: form.value.name,
      type: form.value.type,
      amount: form.value.amount,
      date: form.value.date,
      description: form.value.description
    }

    if (editMode.value) {
      if (!confirm('Are you sure you want to update this transaction?')) return
      await api.put(`/budgeting/transactions/${editingId.value}/`, payload)
    } else {
      await api.post('/budgeting/transactions/', payload)
    }

    showModal.value = false
    await fetchHistory()
  } catch (e) {
    console.error(e)
    alert('Failed to save transaction')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHistory()
  fetchCategories()
  fetchTargets()
  if (route.query.add === 'true') {
    openModal()
  }
})

watch(() => route.query.add, (newVal) => {
  if (newVal === 'true') {
    openModal()
  }
})
</script>
