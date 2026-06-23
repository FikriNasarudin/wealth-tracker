<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Liabilities Overview</h1>
        <p class="text-muted">Track your outstanding debts and loans.</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <span class="text-muted">Period:</span>
        <select v-model="selectedMonth" class="form-input" style="width: 120px;" @change="handleFilterChange">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <input v-model="selectedYear" type="number" min="2000" max="2100" class="form-input" style="width: 100px;" @change="handleFilterChange" />
        <select v-model="filterLender" class="form-input" style="width: 150px;" @change="handleFilterChange">
          <option value="">All Lenders</option>
          <option v-for="l in lenders" :key="l.id" :value="l.id">{{ l.name }}</option>
        </select>
        <button class="btn btn-primary" @click="showModal = true" style="margin-left: 1rem;">+ Add Snapshot</button>
      </div>
    </header>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Original Loan Amount</div>
        <div style="font-size: 2rem; font-weight: 700;">RM{{ formatCurrency(totalOriginal) }}</div>
        <div v-if="originalChange !== null" :class="originalChange > 0 ? 'text-danger' : (originalChange < 0 ? 'text-success' : 'text-muted')" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
          <svg v-if="originalChange > 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
          <svg v-else-if="originalChange < 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
          <span v-else style="margin-right: 0.25rem;">-</span>
          {{ Math.abs(originalChange).toFixed(2) }}% vs last month
        </div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Remaining Principal</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--danger);">RM{{ formatCurrency(totalRemaining) }}</div>
        <div v-if="remainingChange !== null" :class="remainingChange > 0 ? 'text-danger' : (remainingChange < 0 ? 'text-success' : 'text-muted')" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
          <svg v-if="remainingChange > 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
          <svg v-else-if="remainingChange < 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
          <span v-else style="margin-right: 0.25rem;">-</span>
          {{ Math.abs(remainingChange).toFixed(2) }}% vs last month
        </div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Total Debt Reduced</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--success);">RM{{ formatCurrency(totalReduced) }}</div>
        <div v-if="reducedChange !== null" :class="reducedChange >= 0 ? 'text-success' : 'text-danger'" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
          <svg v-if="reducedChange >= 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
          <svg v-else style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
          {{ Math.abs(reducedChange).toFixed(2) }}% vs last month
        </div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Debt Reduction Progress</h3>
        <div style="height: 300px;">
          <GraphLine v-if="yearlyData.length > 0" :labels="monthlyLabels" :datasets="progressDatasets" />
        </div>
      </div>

      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Original vs Remaining</h3>
        <div style="height: 300px;">
          <BarChart v-if="yearlyData.length > 0" :labels="monthlyLabels" :datasets="comparisonDatasets" />
        </div>
      </div>
      
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Liability Distribution (Current Month)</h3>
        <div v-if="distribution.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No liabilities recorded for this period.</div>
        <div v-else style="display: flex; justify-content: center; align-items: center; min-height: 250px;">
          <PieChart :labels="distribution.map(i => i.category)" :data="distribution.map(i => i.balance)" />
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Modal :show="showModal" title="Add Liability Snapshot" @close="showModal = false">
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
          <label class="form-label">Lender (e.g. Bank of America)</label>
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
          {{ loading ? 'Saving...' : 'Save Snapshot' }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import PieChart from '@/components/PieChart.vue'
import GraphLine from '@/components/GraphLine.vue'
import BarChart from '@/components/BarChart.vue'

const totalOriginal = ref(0)
const totalRemaining = ref(0)
const totalReduced = ref(0)
const prevTotalOriginal = ref(0)
const prevTotalRemaining = ref(0)
const prevTotalReduced = ref(0)
const distribution = ref([])
const yearlyData = ref([])

const calculateChange = (current, previous) => {
  if (!previous) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
}

const originalChange = computed(() => calculateChange(totalOriginal.value, prevTotalOriginal.value))
const remainingChange = computed(() => calculateChange(totalRemaining.value, prevTotalRemaining.value))
const reducedChange = computed(() => calculateChange(totalReduced.value, prevTotalReduced.value))

const monthlyLabels = computed(() => yearlyData.value.map(d => d.month))

const progressDatasets = computed(() => [
  { 
    label: 'Total Remaining Principal', 
    data: yearlyData.value.map(d => d.remainingPrincipal), 
    fill: true, 
    backgroundColor: 'rgba(239, 68, 68, 0.2)', 
    borderColor: '#EF4444', 
    tension: 0.4 
  }
])

const comparisonDatasets = computed(() => [
  { 
    label: 'Original Loan Amount', 
    data: yearlyData.value.map(d => d.originalAmount), 
    backgroundColor: '#3B82F6',
    borderRadius: 4
  },
  { 
    label: 'Remaining Principal', 
    data: yearlyData.value.map(d => d.remainingPrincipal), 
    backgroundColor: '#EF4444',
    borderRadius: 4
  }
])

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const filterLender = ref('')
const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const handleFilterChange = async () => {
  await fetchData()
}

const showModal = ref(false)
const loading = ref(false)

const lenders = ref([])

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

const fetchData = async () => {
  try {
    const res = await api.get(`/liabilities/snapshots/summary/?month=${selectedMonth.value}&year=${selectedYear.value}${filterLender.value ? '&lender_id=' + filterLender.value : ''}`)
    totalOriginal.value = res.data.total_original_loan_amount
    totalRemaining.value = res.data.total_remaining_principal
    totalReduced.value = res.data.total_debt_reduced
    prevTotalOriginal.value = res.data.prev_total_original_loan_amount
    prevTotalRemaining.value = res.data.prev_total_remaining_principal
    prevTotalReduced.value = res.data.prev_total_debt_reduced
    distribution.value = res.data.distribution_by_category
  } catch (e) {
    console.error(e)
  }

  try {
    const allRes = await api.get(`/liabilities/snapshots/${filterLender.value ? '?lender_id=' + filterLender.value : ''}`)
    const allSnaps = allRes.data
    
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const aggregated = Array(12).fill(null).map((_, i) => ({
      month: months[i],
      remainingPrincipal: 0,
      originalAmount: 0
    }))
    
    for (let m = 1; m <= 12; m++) {
      const priorSnaps = allSnaps.filter(s => {
         const snapY = Number(s.year)
         const snapM = Number(s.month)
         if (snapY < selectedYear.value) return true;
         if (snapY === selectedYear.value && snapM <= m) return true;
         return false;
      })
      
      const latestPerLiability = {}
      priorSnaps.forEach(s => {
        const key = `${s.category}_${s.lender}`
        if (!latestPerLiability[key]) {
          latestPerLiability[key] = s
        } else {
          const existing = latestPerLiability[key]
          if (s.year > existing.year || (s.year === existing.year && s.month > existing.month)) {
            latestPerLiability[key] = s
          }
        }
      })
      
      let tRemaining = 0
      let tOriginal = 0
      Object.values(latestPerLiability).forEach(s => {
        tRemaining += parseFloat(s.remaining_principal || 0)
        tOriginal += parseFloat(s.original_loan_amount || 0)
      })
      
      // Set values for all 12 months, we will truncate the array later
      aggregated[m-1].remainingPrincipal = tRemaining
      aggregated[m-1].originalAmount = tOriginal
    }
    
    const currentRealMonth = (new Date()).getMonth() + 1
    const currentRealYear = (new Date()).getFullYear()
    
    if (selectedYear.value === currentRealYear) {
      yearlyData.value = aggregated.slice(0, currentRealMonth)
    } else if (selectedYear.value > currentRealYear) {
      yearlyData.value = []
    } else {
      yearlyData.value = aggregated
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchOptions = async () => {
  try {
    const [lendRes] = await Promise.all([
      api.get('/liabilities/lenders/')
    ])
    lenders.value = lendRes.data
    
    if (lenders.value.length > 0 && !form.value.lenderId) {
      form.value.lenderId = lenders.value[0].id
    }
  } catch (e) {
    console.error(e)
  }
}

const submitSnapshot = async () => {
  loading.value = true
  try {
    if (!form.value.lenderId) {
      alert('Please select a lender.')
      loading.value = false
      return
    }

    const payload = {
      month: form.value.month,
      year: form.value.year,
      lender: form.value.lenderId,
      monthly_payment: form.value.monthlyPayment
    }
    if (form.value.remainingPrincipal !== '' && form.value.remainingPrincipal !== null) {
      payload.remaining_principal = form.value.remainingPrincipal
    }

    await api.post('/liabilities/snapshots/', payload)

    showModal.value = false
    
    // Automatically switch the view to the month/year of the newly added snapshot
    selectedMonth.value = form.value.month
    selectedYear.value = form.value.year
    
    form.value = getInitialForm()
    
    await fetchData()
    await fetchOptions()
  } catch (e) {
    console.error(e)
    alert('Failed to save snapshot')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await api.get('/liabilities/snapshots/')
    if (res.data && res.data.length > 0) {
      const latest = res.data.reduce((prev, current) => {
        if (current.year > prev.year) return current;
        if (current.year === prev.year && current.month > prev.month) return current;
        return prev;
      })
      selectedMonth.value = latest.month
      selectedYear.value = latest.year
    }
  } catch(e) {
    console.error(e)
  }

  await fetchData()
  await fetchOptions()
})
</script>
