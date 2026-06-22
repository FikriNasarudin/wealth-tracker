<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Snapshot History</h1>
        <p class="text-muted">Manage your raw investment snapshots.</p>
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
          <label class="form-label">Platform</label>
          <select v-model="filters.platform" class="form-input">
            <option value="">All Platforms</option>
            <option v-for="p in platforms" :key="p.id" :value="p.name">{{ p.name }}</option>
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
            <tr v-for="item in filteredHistory" :key="item.id">
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
    </div>

    <!-- Modal -->
    <Modal :show="showModal" :title="editMode ? 'Edit Investment Snapshot' : 'Add Investment Snapshot'" @close="showModal = false">
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
          <label class="form-label">Category (e.g. Stocks, Crypto)</label>
          <div style="display: flex; gap: 0.5rem;">
            <select v-if="!isNewCategory" v-model="form.categoryId" class="form-input">
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
            <input v-else v-model="form.newCategoryName" type="text" class="form-input" placeholder="New Category" />
            <button type="button" class="btn btn-secondary" @click="isNewCategory = !isNewCategory">
              {{ isNewCategory ? 'Cancel' : 'New' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Platform (e.g. Vanguard, Binance)</label>
          <div style="display: flex; gap: 0.5rem;">
            <select v-if="!isNewPlatform" v-model="form.platformId" class="form-input">
              <option v-for="p in platforms" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <input v-else v-model="form.newPlatformName" type="text" class="form-input" placeholder="New Platform" />
            <button type="button" class="btn btn-secondary" @click="isNewPlatform = !isNewPlatform">
              {{ isNewPlatform ? 'Cancel' : 'New' }}
            </button>
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
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'

const history = ref([])
const showModal = ref(false)
const loading = ref(false)
const editMode = ref(false)
const editingId = ref(null)

const categories = ref([])
const platforms = ref([])
const isNewCategory = ref(false)
const isNewPlatform = ref(false)

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

const getInitialForm = () => {
  const d = new Date()
  return {
    month: d.getMonth() + 1,
    year: d.getFullYear(),
    categoryId: null,
    newCategoryName: '',
    platformId: null,
    newPlatformName: '',
    totalInvested: '',
    currentBalance: ''
  }
}

const form = ref(getInitialForm())

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchHistory = async () => {
  try {
    const res = await api.get('/investments/snapshots/')
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
      api.get('/investments/categories/'),
      api.get('/investments/platforms/')
    ])
    categories.value = catRes.data
    platforms.value = platRes.data
    
    if (categories.value.length > 0 && !form.value.categoryId) {
      form.value.categoryId = categories.value[0].id
    }
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
  isNewCategory.value = false
  isNewPlatform.value = false
  form.value = getInitialForm()
  fetchOptions()
  showModal.value = true
}

const editSnapshot = async (item) => {
  editMode.value = true
  editingId.value = item.id
  isNewCategory.value = false
  isNewPlatform.value = false
  form.value = {
    month: item.month,
    year: item.year,
    categoryId: item.category,
    newCategoryName: '',
    platformId: item.platform,
    newPlatformName: '',
    totalInvested: item.total_invested,
    currentBalance: item.current_balance
  }
  await fetchOptions()
  form.value.categoryId = item.category
  form.value.platformId = item.platform
  showModal.value = true
}

const deleteSnapshot = async (id) => {
  if (confirm('Are you sure you want to delete this snapshot?')) {
    try {
      await api.delete(`/investments/snapshots/${id}/`)
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
    let categoryId = form.value.categoryId
    let platformId = form.value.platformId

    if (isNewCategory.value && form.value.newCategoryName) {
      const catRes = await api.post('/investments/categories/', { name: form.value.newCategoryName })
      categoryId = catRes.data.id
    }

    if (isNewPlatform.value && form.value.newPlatformName) {
      const platRes = await api.post('/investments/platforms/', { name: form.value.newPlatformName })
      platformId = platRes.data.id
    }

    const payload = {
      month: form.value.month,
      year: form.value.year,
      category: categoryId,
      platform: platformId,
      total_invested: form.value.totalInvested,
      current_balance: form.value.currentBalance
    }

    if (editMode.value) {
      await api.put(`/investments/snapshots/${editingId.value}/`, payload)
    } else {
      await api.post('/investments/snapshots/', payload)
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
