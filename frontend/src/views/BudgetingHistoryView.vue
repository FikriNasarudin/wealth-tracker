<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Transaction History</h1>
        <p class="text-muted">Manage your raw transaction data.</p>
      </div>
      <button class="btn btn-primary" @click="openModal()">+ Add Transaction</button>
    </header>

    <div class="card" style="margin-bottom: 1.5rem;">
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
          <label class="form-label">Month</label>
          <input v-model="filters.month" type="month" class="form-input" />
        </div>
        <div style="display: flex; align-items: flex-end;">
          <button class="btn btn-secondary" @click="clearFilters">Clear Filters</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Category</th>
              <th>Name</th>
              <th>Description</th>
              <th>Amount</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredHistory.length === 0">
              <td colspan="7" class="text-center text-muted" style="text-align: center;">No transactions match your filters.</td>
            </tr>
            <tr v-for="item in filteredHistory" :key="item.id">
              <td>{{ item.date }}</td>
              <td>
                <span :class="item.type === 'INCOME' ? 'text-success' : 'text-danger'">
                  {{ item.type === 'INCOME' ? 'Income' : 'Expense' }}
                </span>
              </td>
              <td>{{ item.category_name || 'Uncategorized' }}</td>
              <td style="font-weight: 500;">{{ item.name }}</td>
              <td>{{ item.description || '-' }}</td>
              <td style="font-weight: 600;">RM{{ formatCurrency(item.amount) }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="editTransaction(item)">Edit</button>
                  <button class="btn btn-danger" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="deleteTransaction(item.id)">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
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
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'

const history = ref([])
const showModal = ref(false)
const loading = ref(false)
const editMode = ref(false)
const editingId = ref(null)
const targets = ref([])
const categories = ref([])
const isNewCategory = ref(false)

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
})
</script>
