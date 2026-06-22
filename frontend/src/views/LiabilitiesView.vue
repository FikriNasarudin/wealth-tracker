<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Liabilities Overview</h1>
        <p class="text-muted">Track your outstanding debts and loans.</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <span class="text-muted">Period:</span>
        <select v-model="selectedMonth" class="form-input" style="width: 120px;" @change="fetchData">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <input v-model="selectedYear" type="number" min="2000" max="2100" class="form-input" style="width: 100px;" @change="fetchData" />
        <button class="btn btn-primary" @click="showModal = true" style="margin-left: 1rem;">+ Add Snapshot</button>
      </div>
    </header>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Original Loan Amount</div>
        <div style="font-size: 2rem; font-weight: 700;">RM{{ formatCurrency(totalOriginal) }}</div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Remaining Principal</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--danger);">RM{{ formatCurrency(totalRemaining) }}</div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Total Debt Reduced</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--success);">RM{{ formatCurrency(totalReduced) }}</div>
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
          <DoughnutChart :labels="distribution.map(i => i.category)" :data="distribution.map(i => i.balance)" />
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
          <label class="form-label">Category (e.g. Mortgage, Car Loan)</label>
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
          <label class="form-label">Lender (e.g. Bank of America)</label>
          <div style="display: flex; gap: 0.5rem;">
            <select v-if="!isNewLender" v-model="form.lenderId" class="form-input">
              <option v-for="l in lenders" :key="l.id" :value="l.id">{{ l.name }}</option>
            </select>
            <input v-else v-model="form.newLenderName" type="text" class="form-input" placeholder="New Lender" />
            <button type="button" class="btn btn-secondary" @click="isNewLender = !isNewLender">
              {{ isNewLender ? 'Cancel' : 'New' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Original Loan Amount</label>
          <input v-model="form.originalAmount" type="number" step="0.01" class="form-input" required />
        </div>

        <div class="form-group">
          <label class="form-label">Remaining Principal</label>
          <input v-model="form.remainingPrincipal" type="number" step="0.01" class="form-input" required />
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
import DoughnutChart from '@/components/DoughnutChart.vue'
import GraphLine from '@/components/GraphLine.vue'
import BarChart from '@/components/BarChart.vue'

const totalOriginal = ref(0)
const totalRemaining = ref(0)
const totalReduced = ref(0)
const distribution = ref([])
const yearlyData = ref([])

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
const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const showModal = ref(false)
const loading = ref(false)

const categories = ref([])
const lenders = ref([])
const isNewCategory = ref(false)
const isNewLender = ref(false)

const getInitialForm = () => {
  const d = new Date()
  return {
    month: d.getMonth() + 1,
    year: d.getFullYear(),
    categoryId: null,
    newCategoryName: '',
    lenderId: null,
    newLenderName: '',
    originalAmount: '',
    remainingPrincipal: '',
    monthlyPayment: ''
  }
}

const form = ref(getInitialForm())

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchData = async () => {
  try {
    const res = await api.get(`/liabilities/snapshots/summary/?month=${selectedMonth.value}&year=${selectedYear.value}`)
    totalOriginal.value = res.data.total_original_loan_amount
    totalRemaining.value = res.data.total_remaining_principal
    totalReduced.value = res.data.total_debt_reduced
    distribution.value = res.data.distribution_by_category
  } catch (e) {
    console.error(e)
  }

  try {
    const allRes = await api.get('/liabilities/snapshots/')
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
      
      // Only plot if the month is not in the future
      const currentRealMonth = (new Date()).getMonth() + 1
      const currentRealYear = (new Date()).getFullYear()
      if (selectedYear.value < currentRealYear || (selectedYear.value === currentRealYear && m <= currentRealMonth)) {
         aggregated[m-1].remainingPrincipal = tRemaining
         aggregated[m-1].originalAmount = tOriginal
      }
    }
    
    yearlyData.value = aggregated
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
    
    if (categories.value.length > 0 && !form.value.categoryId) {
      form.value.categoryId = categories.value[0].id
    }
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
    let categoryId = form.value.categoryId
    let lenderId = form.value.lenderId

    if (isNewCategory.value && form.value.newCategoryName) {
      const catRes = await api.post('/liabilities/categories/', { name: form.value.newCategoryName })
      categoryId = catRes.data.id
    }

    if (isNewLender.value && form.value.newLenderName) {
      const lendRes = await api.post('/liabilities/lenders/', { name: form.value.newLenderName })
      lenderId = lendRes.data.id
    }

    await api.post('/liabilities/snapshots/', {
      month: form.value.month,
      year: form.value.year,
      category: categoryId,
      lender: lenderId,
      original_loan_amount: form.value.originalAmount,
      remaining_principal: form.value.remainingPrincipal,
      monthly_payment: form.value.monthlyPayment
    })

    showModal.value = false
    isNewCategory.value = false
    isNewLender.value = false
    
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
