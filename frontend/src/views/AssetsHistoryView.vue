<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem;">
      <div>
        <h1 style="font-weight: 600;">Snapshot History</h1>
        <p class="text-muted">Manage your raw asset snapshots.</p>
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
              background: 'rgba(16, 185, 129, 0.1)',
              color: 'var(--success)',
              fontWeight: '600'
            }">
              💰
            </div>
            <div style="display: flex; flex-direction: column;">
              <span style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary);">
                {{ item.platform_name }}
                <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 500; margin-left: 0.5rem;">
                  ({{ item.category_name || 'Mixed' }})
                </span>
              </span>
              <span style="font-size: 0.75rem; color: var(--text-muted);">
                Balance: <strong style="color: var(--text-primary);">RM{{ formatCurrency(item.current_balance) }}</strong> (Invested: RM{{ formatCurrency(item.total_invested) }}) • {{ item.month.toString().padStart(2, '0') }}/{{ item.year }}
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
          <input v-model="form.currentBalance" type="number" step="0.01" class="form-input" required @input="recalculateAssetWeightValues" />
        </div>

        <!-- Multi-asset Select and Weights/Values Inputs -->
        <div class="form-group" style="border-top: 1px solid var(--border-color); padding-top: 1rem; margin-top: 1rem;">
          <label class="form-label" style="display: flex; justify-content: space-between; align-items: center;">
            <span>Asset Allocations (Optional)</span>
            <span class="text-muted" style="font-size: 0.75rem;">Total Allocated: {{ formatCurrency(totalAllocatedValue) }} / RM{{ formatCurrency(form.currentBalance || 0) }} ({{ totalAllocatedWeight.toFixed(1) }}%)</span>
          </label>
          
          <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
            <select v-model="selectedAssetToAdd" class="form-input" style="flex: 1;">
              <option :value="null" disabled>Select Asset to Add</option>
              <option v-for="a in activeAssets" :key="a.id" :value="a">{{ a.name }} ({{ a.category_name }})</option>
            </select>
            <button type="button" class="btn btn-secondary" @click="addAssetToSnapshotForm">Add Asset</button>
          </div>

          <div v-if="form.snapshotAssets.length > 0" style="display: flex; flex-direction: column; gap: 0.75rem; background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 6px; border: 1px solid var(--border-color);">
            <div v-for="(sa, idx) in form.snapshotAssets" :key="sa.asset" style="display: flex; gap: 0.5rem; align-items: center;">
              <span style="flex: 2; font-size: 0.875rem;">{{ sa.asset_name }}</span>
              <div style="flex: 3; display: flex; gap: 0.5rem; align-items: center;">
                <div style="position: relative; flex: 1;">
                  <span style="position: absolute; left: 8px; top: 50%; transform: translateY(-50%); font-size: 0.75rem; color: var(--text-muted);">RM</span>
                  <input v-model="sa.value" type="number" step="0.01" class="form-input" style="padding-left: 1.75rem; font-size: 0.8rem; height: 32px;" placeholder="Value" @input="onAssetValueInput(idx)" />
                </div>
                <div style="position: relative; flex: 1;">
                  <input v-model="sa.weight" type="number" step="0.01" class="form-input" style="padding-right: 1.25rem; font-size: 0.8rem; height: 32px;" placeholder="Weight" @input="onAssetWeightInput(idx)" />
                  <span style="position: absolute; right: 8px; top: 50%; transform: translateY(-50%); font-size: 0.75rem; color: var(--text-muted);">%</span>
                </div>
              </div>
              <button type="button" class="btn btn-danger" style="padding: 0.1rem 0.4rem; font-size: 0.75rem; height: 32px;" @click="removeAssetFromSnapshotForm(idx)">Remove</button>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-top: 0.25rem;" :class="isAllocationValid ? 'text-success' : 'text-danger'">
              <span>Allocation Status:</span>
              <span>{{ allocationStatusText }}</span>
            </div>
          </div>
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading || (form.snapshotAssets.length > 0 && !isAllocationValid)">
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
const platforms = ref([])
const assetsList = ref([])
const selectedAssetToAdd = ref(null)

const activeAssets = computed(() => assetsList.value.filter(a => a.is_active))

const platformOptions = computed(() => {
  return platforms.value.map(p => ({ value: p.id, label: p.name }))
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
  platform: ''
})

const clearFilters = () => {
  filters.value = { period: '', category: '', platform: '' }
}

const filteredHistory = computed(() => {
  return history.value.filter(item => {
    if (filters.value.period) {
      const [y, m] = filters.value.period.split('-').map(Number)
      if (item.year !== y || item.month !== m) return false
    }
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
    currentBalance: '',
    snapshotAssets: []
  }
}

const form = ref(getInitialForm())

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

// Form multi-asset allocation helpers
const addAssetToSnapshotForm = () => {
  if (!selectedAssetToAdd.value) return
  if (form.value.snapshotAssets.some(sa => sa.asset === selectedAssetToAdd.value.id)) {
    alert('Asset already added.')
    return
  }
  form.value.snapshotAssets.push({
    asset: selectedAssetToAdd.value.id,
    asset_name: selectedAssetToAdd.value.name,
    weight: '',
    value: ''
  })
  selectedAssetToAdd.value = null
}

const removeAssetFromSnapshotForm = (idx) => {
  form.value.snapshotAssets.splice(idx, 1)
}

const onAssetValueInput = (idx) => {
  const currentAsset = form.value.snapshotAssets[idx]
  const totalVal = parseFloat(form.value.currentBalance || 0)
  const val = parseFloat(currentAsset.value)

  if (isNaN(val) || val <= 0) {
    currentAsset.weight = ''
    return
  }

  if (totalVal > 0) {
    currentAsset.weight = ((val / totalVal) * 100).toFixed(2)
  }
}

const onAssetWeightInput = (idx) => {
  const currentAsset = form.value.snapshotAssets[idx]
  const totalVal = parseFloat(form.value.currentBalance || 0)
  const wt = parseFloat(currentAsset.weight)

  if (isNaN(wt) || wt <= 0) {
    currentAsset.value = ''
    return
  }

  if (totalVal > 0) {
    currentAsset.value = ((wt / 100) * totalVal).toFixed(2)
  }
}

const recalculateAssetWeightValues = () => {
  const totalVal = parseFloat(form.value.currentBalance || 0)
  form.value.snapshotAssets.forEach((sa, idx) => {
    if (sa.weight !== '') {
      onAssetWeightInput(idx)
    } else if (sa.value !== '') {
      onAssetValueInput(idx)
    }
  })
}

const totalAllocatedValue = computed(() => {
  return form.value.snapshotAssets.reduce((sum, sa) => sum + parseFloat(sa.value || 0), 0)
})

const totalAllocatedWeight = computed(() => {
  return form.value.snapshotAssets.reduce((sum, sa) => sum + parseFloat(sa.weight || 0), 0)
})

const isAllocationValid = computed(() => {
  if (form.value.snapshotAssets.length === 0) return true
  const totalWeightVal = totalAllocatedWeight.value
  return Math.abs(totalWeightVal - 100) <= 0.2
})

const allocationStatusText = computed(() => {
  if (form.value.snapshotAssets.length === 0) return 'No assets allocated yet.'
  const diff = totalAllocatedWeight.value - 100
  if (Math.abs(diff) <= 0.2) {
    return 'Allocation complete (100%).'
  }
  return diff < 0 ? `Under-allocated by ${Math.abs(diff).toFixed(1)}%.` : `Over-allocated by ${diff.toFixed(1)}%.`
})

const fetchHistory = async () => {
  try {
    const res = await api.get('/assets/snapshots/')
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
    const [catRes, platRes, assetRes] = await Promise.all([
      api.get('/assets/categories/'),
      api.get('/assets/platforms/'),
      api.get('/assets/assets/')
    ])
    categories.value = catRes.data
    platforms.value = platRes.data
    assetsList.value = assetRes.data
    
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
    currentBalance: item.current_balance,
    snapshotAssets: item.snapshot_assets ? item.snapshot_assets.map(sa => ({
      asset: sa.asset,
      asset_name: sa.asset_name,
      weight: sa.weight,
      value: sa.value
    })) : []
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
    const cleanAssets = form.value.snapshotAssets.map(sa => ({
      asset: sa.asset,
      weight: sa.weight === '' ? null : parseFloat(sa.weight),
      value: sa.value === '' ? null : parseFloat(sa.value)
    }))

    const payload = {
      month: form.value.month,
      year: form.value.year,
      platform: form.value.platformId,
      total_invested: form.value.totalInvested,
      current_balance: form.value.currentBalance,
      snapshot_assets: cleanAssets
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
  border-color: rgba(16, 185, 129, 0.25) !important;
  transform: translateX(4px);
}
</style>
