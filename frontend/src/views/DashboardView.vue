<template>
  <div class="main-content">
    <header style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <h1 style="font-weight: 600;">Dashboard</h1>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <span class="text-muted">Viewing Period:</span>
        <select v-model="selectedMonth" class="form-input" style="width: 120px;" @change="fetchData">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <input v-model="selectedYear" type="number" min="2000" max="2100" class="form-input" style="width: 100px;" @change="fetchData" />
      </div>
    </header>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <!-- Total Investments Card -->
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Total Investments</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">RM{{ formatCurrency(totalInvestments) }}</div>
        <div class="text-success" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
          <svg style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          +{{ profitPercentage }}% Profit
        </div>
      </div>

      <!-- Total Liabilities Card -->
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Total Liabilities</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">RM{{ formatCurrency(totalLiabilities) }}</div>
        <div class="text-warning" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
          <svg style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
          </svg>
          Outstanding Debt
        </div>
      </div>

      <!-- Net Worth Card -->
      <div class="card" style="background: var(--accent-gradient); border: none;">
        <div style="color: rgba(255, 255, 255, 0.8); margin-bottom: 0.5rem; font-weight: 500;">Estimated Net Worth</div>
        <div style="font-size: 2rem; font-weight: 700; color: #fff;">RM{{ formatCurrency(netWorth) }}</div>
        <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.875rem; margin-top: 0.5rem;">
          Investments - Liabilities
        </div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Compound Effect (Invested vs Profit)</h3>
        <div style="height: 300px;">
          <BarChart v-if="yearlyData.length > 0" :labels="monthlyLabels" :datasets="compoundDatasets" />
        </div>
      </div>
      
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Total Assets Over Time</h3>
        <div style="height: 300px;">
          <GraphLine v-if="yearlyData.length > 0" :labels="monthlyLabels" :datasets="assetDatasets" />
        </div>
      </div>

      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Investment Progress</h3>
        <div style="height: 300px;">
          <GraphLine v-if="yearlyData.length > 0" :labels="monthlyLabels" :datasets="progressDatasets" />
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../services/api'
import BarChart from '@/components/BarChart.vue'
import GraphLine from '@/components/GraphLine.vue'

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const totalInvestments = ref(0)
const profitPercentage = ref(0)
const totalLiabilities = ref(0)
const yearlyData = ref([])

const netWorth = computed(() => {
  return totalInvestments.value - totalLiabilities.value
})

const formatCurrency = (val) => {
  return Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const monthlyLabels = computed(() => yearlyData.value.map(d => d.month))

const compoundDatasets = computed(() => [
  { 
    label: 'Total Invested', 
    data: yearlyData.value.map(d => d.totalInvested), 
    backgroundColor: '#3B82F6',
    borderRadius: 4
  },
  { 
    label: 'Profit/Loss', 
    data: yearlyData.value.map(d => d.profit), 
    backgroundColor: yearlyData.value.map(d => d.profit >= 0 ? '#10B981' : '#EF4444'),
    borderRadius: 4
  }
])

const assetDatasets = computed(() => [
  { 
    label: 'Total Balance', 
    data: yearlyData.value.map(d => d.totalBalance), 
    fill: true, 
    backgroundColor: 'rgba(59, 130, 246, 0.2)', 
    borderColor: '#3B82F6', 
    tension: 0.4 
  }
])

const progressDatasets = computed(() => [
  { 
    label: 'Total Invested', 
    data: yearlyData.value.map(d => d.totalInvested), 
    fill: true, 
    stepped: true, 
    backgroundColor: 'rgba(16, 185, 129, 0.2)', 
    borderColor: '#10B981' 
  }
])

const fetchData = async () => {
  const month = selectedMonth.value
  const year = selectedYear.value

  try {
    const invRes = await api.get(`/investments/snapshots/allocation/?month=${month}&year=${year}`)
    totalInvestments.value = invRes.data.total_portfolio_balance || 0
    profitPercentage.value = invRes.data.total_profit_percentage || 0
  } catch (e) {
    console.error(e)
  }

  try {
    const liabRes = await api.get('/liabilities/snapshots/')
    const currentY = Number(year)
    const currentM = Number(month)
    
    const priorSnaps = liabRes.data.filter(s => {
       const snapY = Number(s.year)
       const snapM = Number(s.month)
       if (snapY < currentY) return true;
       if (snapY === currentY && snapM <= currentM) return true;
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
    
    let liabilities = 0
    Object.values(latestPerLiability).forEach(s => {
      liabilities += parseFloat(s.remaining_principal || 0)
    })
    
    totalLiabilities.value = liabilities
  } catch (e) {
    console.error(e)
  }

  try {
    const res = await api.get('/investments/snapshots/')
    const yearSnaps = res.data.filter(s => s.year === year)
    
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const aggregated = Array(12).fill(null).map((_, i) => ({
      month: months[i],
      totalInvested: 0,
      totalBalance: 0,
      profit: 0
    }))
    
    yearSnaps.forEach(snap => {
      const mIdx = snap.month - 1
      aggregated[mIdx].totalInvested += parseFloat(snap.total_invested)
      aggregated[mIdx].totalBalance += parseFloat(snap.current_balance)
    })
    
    aggregated.forEach(a => {
      if (a.totalInvested > 0) {
        a.profit = a.totalBalance - a.totalInvested
      }
    })
    
    yearlyData.value = aggregated
  } catch(e) {
    console.error(e)
  }
}

onMounted(async () => {
  try {
    const res = await api.get('/investments/snapshots/')
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

  fetchData()
})
</script>
