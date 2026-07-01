<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem;">
      <div>
        <h1 style="font-weight: 600;">Snapshot History</h1>
        <p class="text-muted">Manage your raw asset snapshots.</p>
      </div>
      <button class="btn btn-primary" @click="openModal()">+ Add Snapshot</button>
    </header>

    <div class="card" style="margin-bottom: 1.5rem;">
      <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Month</label>
          <select v-model="filters.month" class="form-input">
            <option value="">All Months</option>
            <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
          </select>
        </div>
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Year</label>
          <select v-model="filters.year" class="form-input">
            <option value="">All Years</option>
            <option v-for="y in yearsList" :key="y" :value="y">{{ y }}</option>
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
          <label class="form-label">Platform</label>
          <select v-model="filters.platform" class="form-input">
            <option value="">All Platforms</option>
            <option v-for="p in platforms" :key="p.id" :value="p.name">{{ p.name }}</option>
          </select>
        </div>
        <div style="display: flex; align-items: flex-end; flex: 1; min-width: 150px;">
          <button class="btn btn-secondary" @click="clearFilters" style="width: 100%;">Clear Filters</button>
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
              <th>Platform</th>
              <th>Invested</th>
              <th>Balance</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredHistory.length === 0">
              <td colspan="6" class="text-center text-muted" style="text-align: center;">No snapshots match your filters.</td>
            </tr>
            <tr v-for="item in paginatedHistory" :key="item.id">
              <td>{{ item.month.toString().padStart(2, '0') }}/{{ item.year }}</td>
              <td>{{ item.category_name }}</td>
              <td>{{ item.platform_name }}</td>
              <td>RM{{ formatCurrency(item.total_invested) }}</td>
              <td style="font-weight: 600;">RM{{ formatCurrency(item.current_balance) }}</td>
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
      <Pagination v-model="currentPage" :totalItems="filteredHistory.length" :itemsPerPage="itemsPerPage" />
    </div>

    <!-- Modal -->
    <Modal :show="showModal" :title="editMode ? 'Edit Asset Snapshot' : 'Add Asset Snapshot'" @close="showModal = false">
      <form @submit.prevent="submitSnapshot">
        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1">
            <label class="form-label">Month</label>
            <select v-model="form.month" class="form-input" required>
              <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
            </select>
          </div>
          <div class="form-group" style="flex: 1">
            <label class="form-label">Year</label>
            <select v-model="form.year" class="form-input" required>
              <option v-for="y in yearsList" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">Platform</label>
          <SearchableSelect 
            v-model="form.platformId" 
            :options="platformOptions" 
            placeholder="Search platform..." 
          />
          <div class="text-muted" style="font-size: 0.75rem; margin-top: 0.25rem;">
            New platforms and categories can be created in the "Manage" page.
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Total Invested (Principal)</label>
          <input v-model="form.totalInvested" type="number" step="0.01" class="form-input" required />
        </div>

        <div class="form-group">
          <label class="form-label">Current Balance</label>
          <input v-model="form.currentBalance" type="number" step="0.01" class="form-input" required />
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : (editMode ? 'Update Snapshot' : 'Save Snapshot') }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'
import Pagination from '@/components/Pagination.vue'

const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const yearsList = computed(() => {
  const current = new Date().getFullYear()
  const years = []
  for (let y = current - 5; y <= current + 5; y++) {
    years.push(y)
  }
  return years
})

const history = ref([])
const showModal = ref(false)
const loading = ref(false)
const editMode = ref(false)
const editingId = ref(null)

const categories = ref([])
const platforms = ref([])

const platformOptions = computed(() => {
  return platforms.value.map(p => ({ value: p.id, label: p.name }))
})


const filters = ref({
  month: '',
  year: '',
  category: '',
  platform: ''
})

const clearFilters = () => {
  filters.value = { month: '', year: '', category: '', platform: '' }
}

const filteredHistory = computed(() => {
  return history.value.filter(item => {
    if (filters.value.month && item.month !== parseInt(filters.value.month)) return false
    if (filters.value.year && item.year !== parseInt(filters.value.year)) return false
    if (filters.value.category && item.category_name !== filters.value.category) return false
    if (filters.value.platform && item.platform_name !== filters.value.platform) return false
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

const getInitialForm = () => {
  const d = new Date()
  return {
    month: d.getMonth() + 1,
    year: d.getFullYear(),
    platformId: null,
    totalInvested: '',
    currentBalance: ''
  }
}

const form = ref(getInitialForm())

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchHistory = async () => {
  try {
    const res = await api.get('/assets/snapshots/')
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
    const [catRes, platRes] = await Promise.all([
      api.get('/assets/categories/'),
      api.get('/assets/platforms/')
    ])
    categories.value = catRes.data
    platforms.value = platRes.data
    
    if (platforms.value.length > 0 && !form.value.platformId) {
      form.value.platformId = platforms.value[0].id
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
    platformId: item.platform,
    totalInvested: item.total_invested,
    currentBalance: item.current_balance
  }
  await fetchOptions()
  form.value.platformId = item.platform
  showModal.value = true
}

const deleteSnapshot = async (id) => {
  if (confirm('Are you sure you want to delete this snapshot?')) {
    try {
      await api.delete(`/assets/snapshots/${id}/`)
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
      platform: form.value.platformId,
      total_invested: form.value.totalInvested,
      current_balance: form.value.currentBalance
    }

    if (editMode.value) {
      await api.put(`/assets/snapshots/${editingId.value}/`, payload)
    } else {
      await api.post('/assets/snapshots/', payload)
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
