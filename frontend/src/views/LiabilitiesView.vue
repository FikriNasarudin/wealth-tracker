<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Liabilities Overview</h1>
        <p class="text-muted">Track your outstanding debts and loans.</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <button class="btn btn-secondary" @click="startTour" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
          <svg style="width: 16px; height: 16px; display: inline; vertical-align: middle; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Help
        </button>
        <span class="text-muted">Period:</span>
        <select v-model="selectedMonth" class="form-input" style="width: 120px;" @change="handleFilterChange">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <input v-model="selectedYear" type="number" min="2000" max="2100" class="form-input" style="width: 100px;" @change="handleFilterChange" />
        <select v-model="filterLender" class="form-input" style="width: 150px;" @change="handleFilterChange">
          <option value="">All Lenders</option>
          <option v-for="l in lenders" :key="l.id" :value="l.id">{{ l.name }}</option>
        </select>
        
        <router-link to="/liabilities/manage" class="btn btn-secondary">Manage Cards & Lenders</router-link>
        
        <button id="tour-add-liability" class="btn btn-primary" @click="showModal = true" style="margin-left: 1rem;">+ Add Snapshot</button>
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
      <div id="tour-remaining-principal" class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Remaining Principal
          <Tooltip title="Remaining Principal" description="The total amount of debt you still owe to your lenders, not including future interest." example="RM100,000 borrowed - RM20,000 paid = RM80,000 Remaining" />
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--danger);">RM{{ formatCurrency(totalRemaining) }}</div>
        <div v-if="remainingChange !== null" :class="remainingChange > 0 ? 'text-danger' : (remainingChange < 0 ? 'text-success' : 'text-muted')" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
          <svg v-if="remainingChange > 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
          <svg v-else-if="remainingChange < 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
          <span v-else style="margin-right: 0.25rem;">-</span>
          {{ Math.abs(remainingChange).toFixed(2) }}% vs last month
        </div>
      </div>
      <div id="tour-debt-reduced" class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Total Debt Reduced
          <Tooltip title="Total Debt Reduced" description="The absolute amount of principal debt you have successfully paid off." example="RM100,000 Original - RM80,000 Remaining = RM20,000 Reduced" />
        </div>
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

      <div id="tour-payoff-tracker" class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">
          Debt Payoff Tracker
          <Tooltip title="Debt Payoff Tracker" description="Uses the Avalanche Method to show you how many months remain to clear each debt based on your interest rates and monthly payments." example="High interest loans are prioritized." />
        </h3>
        <div v-if="payoffPlans.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No debt payoff plans available.</div>
        <div v-else style="display: flex; flex-direction: column; gap: 1rem;">
          <div v-for="plan in payoffPlans" :key="plan.id" style="border: 1px solid var(--border-color); border-radius: 0.5rem; padding: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
              <span style="font-weight: 600;">{{ plan.lenderName }} ({{ plan.interestRate }}%)</span>
              <span class="text-muted">Est. {{ plan.monthsRemaining }} months left</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem;">
              <span>Balance: RM{{ formatCurrency(plan.remainingPrincipal) }}</span>
              <span>Payment: RM{{ formatCurrency(plan.monthlyPayment) }}/mo</span>
            </div>
            <div style="width: 100%; height: 8px; background: var(--bg-background); border-radius: 4px; overflow: hidden;">
              <div :style="{
                width: Math.min((1 - plan.remainingPrincipal / plan.originalAmount) * 100, 100) + '%',
                height: '100%',
                background: 'var(--success)'
              }"></div>
            </div>
          </div>
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
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import PieChart from '@/components/PieChart.vue'
import BarChart from '@/components/BarChart.vue'
import GraphLine from '@/components/GraphLine.vue'
import Tooltip from '@/components/Tooltip.vue'
import { driver } from 'driver.js'

const startTour = () => {
  const driverObj = driver({
    showProgress: true,
    steps: [
      { element: '#tour-remaining-principal', popover: { title: 'Remaining Debt', description: 'Monitor how much money you currently owe across all accounts.' } },
      { element: '#tour-debt-reduced', popover: { title: 'Debt Paid Off', description: 'Celebrate your progress! This is the total amount of debt you have cleared.' } },
      { element: '#tour-payoff-tracker', popover: { title: 'Avalanche Payoff Tracker', description: 'Automatically estimates how many months are left on your loans based on your interest rate and payments.' } },
      { element: '#tour-add-liability', popover: { title: 'Log a Payment', description: 'Click here to add a new snapshot for a month after making a payment.' } }
    ]
  });
  driverObj.drive();
}

const totalOriginal = ref(0)
const totalRemaining = ref(0)
const totalReduced = ref(0)
const prevTotalOriginal = ref(0)
const prevTotalRemaining = ref(0)
const prevTotalReduced = ref(0)
const distribution = ref([])
const yearlyData = ref([])
const payoffPlans = ref([])

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

    // Calculate Payoff Plans for selected month
    const currentPriorSnaps = allSnaps.filter(s => {
       const snapY = Number(s.year)
       const snapM = Number(s.month)
       if (snapY < selectedYear.value) return true;
       if (snapY === selectedYear.value && snapM <= selectedMonth.value) return true;
       return false;
    })
    
    const latestPerLiabilitySelected = {}
    currentPriorSnaps.forEach(s => {
      const key = `${s.category}_${s.lender}`
      if (!latestPerLiabilitySelected[key]) {
        latestPerLiabilitySelected[key] = s
      } else {
        const existing = latestPerLiabilitySelected[key]
        if (s.year > existing.year || (s.year === existing.year && s.month > existing.month)) {
          latestPerLiabilitySelected[key] = s
        }
      }
    })
    
    payoffPlans.value = Object.values(latestPerLiabilitySelected)
      .filter(s => parseFloat(s.remaining_principal) > 0)
      .map(s => {
        const lender = lenders.value.find(l => l.id === s.lender)
        const interestRate = lender ? parseFloat(lender.interest_rate || 0) : 0
        const principal = parseFloat(s.remaining_principal)
        const payment = parseFloat(s.monthly_payment)
        const original = parseFloat(s.original_loan_amount)
        
        let months = 0
        if (payment > 0) {
          if (interestRate === 0) {
            months = Math.ceil(principal / payment)
          } else {
            const r = interestRate / 100 / 12
            if (payment > r * principal) {
              months = Math.ceil(-Math.log(1 - (r * principal) / payment) / Math.log(1 + r))
            } else {
              months = 999 
            }
          }
        }
        
        return {
          id: s.id,
          lenderName: lender ? lender.name : 'Unknown',
          interestRate,
          remainingPrincipal: principal,
          originalAmount: original,
          monthlyPayment: payment,
          monthsRemaining: months > 900 ? '∞' : months
        }
      }).sort((a, b) => b.interestRate - a.interestRate)

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

  await fetchOptions()
  await fetchData()
})
</script>
