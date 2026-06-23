<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Snapshot History</h1>
        <p class="text-muted">Manage your raw liability snapshots.</p>
      </div>
      <button class="btn btn-primary" @click="openModal()">+ Add Snapshot</button>
    </header>

    <div class="card" style="margin-bottom: 1.5rem;">
      <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Month</label>
          <input v-model="filters.month" type="number" min="1" max="12" class="form-input" placeholder="All Months" />
        </div>
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Year</label>
          <input v-model="filters.year" type="number" min="2000" max="2100" class="form-input" placeholder="All Years" />
        </div>
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Category</label>
          <select v-model="filters.category" class="form-input">
            <option value="">All Categories</option>
            <option v-for="c in categories" :key="c.id" :value="c.name">{{ c.name }}</option>
          </select>
        </div>
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Lender</label>
          <select v-model="filters.lender" class="form-input">
            <option value="">All Lenders</option>
            <option v-for="l in lenders" :key="l.id" :value="l.name">{{ l.name }}</option>
          </select>
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
              <th>Date (MM/YYYY)</th>
              <th>Category</th>
              <th>Lender</th>
              <th>Principal</th>
              <th>Payment</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredHistory.length === 0">
              <td colspan="6" class="text-center text-muted" style="text-align: center;">No snapshots match your filters.</td>
            </tr>
            <tr v-for="item in filteredHistory" :key="item.id">
              <td>{{ item.month.toString().padStart(2, '0') }}/{{ item.year }}</td>
              <td>{{ item.category_name }}</td>
              <td>{{ item.lender_name }}</td>
              <td style="font-weight: 600;">RM{{ formatCurrency(item.remaining_principal) }}</td>
              <td>RM{{ formatCurrency(item.monthly_payment) }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="editSnapshot(item)">Edit</button>
                  <button class="btn btn-danger" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="deleteSnapshot(item.id)">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <Modal :show="showModal" :title="editMode ? 'Edit Liability Snapshot' : 'Add Liability Snapshot'" @close="showModal = false">
      <form @submit.prevent="submitSnapshot">
        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1">
            <label class="form-label">Month</label>
            <input v-model="form.month" type="number" min="1" max="12" class="form-input" required />
          </div>
          <div class="form-group" style="flex: 1">
            <label class="form-label">Year</label>
            <input v-model="form.year" type="number" min="2000" max="2100" class="form-input" required />
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">Lender</label>
          <select v-model="form.lenderId" class="form-input" required>
            <option value="" disabled>Select a Lender</option>
            <option v-for="l in lenders" :key="l.id" :value="l.id">{{ l.name }}</option>
          </select>
          <div class="text-muted" style="font-size: 0.75rem; margin-top: 0.25rem;">
            New lenders and categories can be created in the "Manage" page.
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Remaining Principal (Leave empty to auto-calculate)</label>
          <input v-model="form.remainingPrincipal" type="number" step="0.01" class="form-input" />
        </div>

        <div class="form-group">
          <label class="form-label">Monthly Payment</label>
          <input v-model="form.monthlyPayment" type="number" step="0.01" class="form-input" required />
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : (editMode ? 'Update Snapshot' : 'Save Snapshot') }}
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

const categories = ref([])
const lenders = ref([])


const filters = ref({
  month: '',
  year: '',
  category: '',
  lender: ''
})

const clearFilters = () => {
  filters.value = { month: '', year: '', category: '', lender: '' }
}

const filteredHistory = computed(() => {
  return history.value.filter(item => {
    if (filters.value.month && item.month !== parseInt(filters.value.month)) return false
    if (filters.value.year && item.year !== parseInt(filters.value.year)) return false
    if (filters.value.category && item.category_name !== filters.value.category) return false
    if (filters.value.lender && item.lender_name !== filters.value.lender) return false
    return true
  })
})

const getInitialForm = () => {
  const d = new Date()
  return {
    month: d.getMonth() + 1,
    year: d.getFullYear(),
    lenderId: null,
    remainingPrincipal: '',
    monthlyPayment: ''
  }
}

const form = ref(getInitialForm())

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchHistory = async () => {
  try {
    const res = await api.get('/liabilities/snapshots/')
    history.value = res.data.sort((a, b) => {
      if (b.year !== a.year) return b.year - a.year
      return b.month - a.month
    })
  } catch (e) {
    console.error(e)
  }
}

const fetchOptions = async () => {
  try {
    const [catRes, lendRes] = await Promise.all([
      api.get('/liabilities/categories/'),
      api.get('/liabilities/lenders/')
    ])
    categories.value = catRes.data
    lenders.value = lendRes.data
    
    if (lenders.value.length > 0 && !form.value.lenderId) {
      form.value.lenderId = lenders.value[0].id
    }
  } catch (e) {
    console.error(e)
  }
}

const openModal = () => {
  editMode.value = false
  editingId.value = null

  form.value = getInitialForm()
  fetchOptions()
  showModal.value = true
}

const editSnapshot = async (item) => {
  editMode.value = true
  editingId.value = item.id
  form.value = {
    month: item.month,
    year: item.year,
    lenderId: item.lender,
    remainingPrincipal: item.remaining_principal,
    monthlyPayment: item.monthly_payment
  }
  await fetchOptions()
  form.value.lenderId = item.lender
  showModal.value = true
}

const deleteSnapshot = async (id) => {
  if (confirm('Are you sure you want to delete this snapshot?')) {
    try {
      await api.delete(`/liabilities/snapshots/${id}/`)
      fetchHistory()
    } catch (e) {
      console.error(e)
      alert('Failed to delete snapshot')
    }
  }
}

const submitSnapshot = async () => {
  loading.value = true
  try {
    const payload = {
      month: form.value.month,
      year: form.value.year,
      lender: form.value.lenderId,
      monthly_payment: form.value.monthlyPayment
    }
    if (form.value.remainingPrincipal !== '' && form.value.remainingPrincipal !== null) {
      payload.remaining_principal = form.value.remainingPrincipal
    }

    if (editMode.value) {
      await api.put(`/liabilities/snapshots/${editingId.value}/`, payload)
    } else {
      await api.post('/liabilities/snapshots/', payload)
    }

    showModal.value = false
    await fetchHistory()
    await fetchOptions()
  } catch (e) {
    console.error(e)
    alert('Failed to save snapshot')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHistory()
  fetchOptions()
})
</script>
