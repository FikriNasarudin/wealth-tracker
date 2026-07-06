<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem;">
      <div>
        <h1 style="font-weight: 600;">Snapshot History</h1>
        <p class="text-muted">Manage your raw liability snapshots.</p>
      </div>
      <button class="btn btn-primary" @click="openModal()">+ Add Snapshot</button>
    </header>

    <div class="card" style="margin-bottom: 1.5rem; position: relative; z-index: 50;">
      <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 150px;">
          <label class="form-label">Period</label>
          <SearchableSelect v-model="filters.period" :options="periodOptions" placeholder="All Periods" />
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
        <div style="display: flex; align-items: flex-end; flex: 1; min-width: 150px;">
          <button class="btn btn-secondary" @click="clearFilters" style="width: 100%;">Clear Filters</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="snapshots-list" style="display: flex; flex-direction: column; gap: 0.75rem;">
        <div v-if="filteredHistory.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No snapshots match your filters.</div>
        <div v-else v-for="item in paginatedHistory" :key="item.id" class="snapshot-item" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(255,255,255,0.015); border-radius: var(--border-radius-sm); border: 1px solid var(--border-color); transition: all var(--transition-fast);">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div :style="{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'rgba(239, 68, 68, 0.1)',
              color: 'var(--danger)',
              fontWeight: '600'
            }">
              💸
            </div>
            <div style="display: flex; flex-direction: column;">
              <span style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary);">
                {{ item.lender_name }}
                <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 500; margin-left: 0.5rem;">
                  ({{ item.category_name }})
                </span>
              </span>
              <span style="font-size: 0.75rem; color: var(--text-muted);">
                Principal: <strong style="color: var(--text-primary);">RM{{ formatCurrency(item.remaining_principal) }}</strong> (Monthly Payment: RM{{ formatCurrency(item.monthly_payment) }}) • {{ item.month.toString().padStart(2, '0') }}/{{ item.year }}
              </span>
            </div>
          </div>
          
          <div style="display: flex; gap: 0.4rem;">
            <button class="btn btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="editSnapshot(item)">Edit</button>
            <button class="btn btn-danger" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="deleteSnapshot(item.id)">Delete</button>
          </div>
        </div>
        <Pagination v-model="currentPage" :totalItems="filteredHistory.length" :itemsPerPage="itemsPerPage" />
      </div>
    </div>

    <!-- Modal -->
    <Modal :show="showModal" :title="editMode ? 'Edit Liability Snapshot' : 'Add Liability Snapshot'" @close="showModal = false">
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
          <label class="form-label">Lender</label>
          <SearchableSelect 
            v-model="form.lenderId" 
            :options="lenderOptions" 
            placeholder="Search lender..." 
          />
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
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'
import Pagination from '@/components/Pagination.vue'

const route = useRoute()

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
const lenders = ref([])

const lenderOptions = computed(() => {
  return lenders.value.map(l => ({ value: l.id, label: l.name }))
})

const d = new Date()
const periodOptions = ref([])

const generatePeriodOptions = () => {
  let oldestY = null
  let oldestM = null
  
  if (history.value && history.value.length > 0) {
    history.value.forEach(item => {
      const itemY = Number(item.year)
      const itemM = Number(item.month)
      if (itemY && itemM) {
        if (!oldestY || itemY < oldestY || (itemY === oldestY && itemM < oldestM)) {
          oldestY = itemY
          oldestM = itemM
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
  period: '',
  category: '',
  lender: ''
})

const clearFilters = () => {
  filters.value = { period: '', category: '', lender: '' }
}

const filteredHistory = computed(() => {
  return history.value.filter(item => {
    if (filters.value.period) {
      const [y, m] = filters.value.period.split('-').map(Number)
      if (item.year !== y || item.month !== m) return false
    }
    if (filters.value.category && item.category_name !== filters.value.category) return false
    if (filters.value.lender && item.lender_name !== filters.value.lender) return false
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
    generatePeriodOptions()
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

<style scoped>
.snapshot-item:hover {
  background: rgba(255, 255, 255, 0.035) !important;
  border-color: rgba(99, 102, 241, 0.25) !important;
  transform: translateX(4px);
}
</style>
