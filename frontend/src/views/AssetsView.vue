<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem;">
      <div>
        <h1 style="font-weight: 600;">Assets Overview</h1>
        <p class="text-muted">Track your portfolio allocation and profits.</p>
      </div>
      <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;">
        <button class="btn btn-secondary" @click="startTour" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
          <svg style="width: 16px; height: 16px; display: inline; vertical-align: middle; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Help
        </button>
        <span class="text-muted" style="font-size: 0.875rem;">Period:</span>
        <select v-model="selectedMonth" class="form-input" style="width: 120px;" @change="handleFilterChange">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <select v-model="selectedYear" class="form-input" style="width: 95px;" @change="handleFilterChange">
          <option v-for="y in yearsList" :key="y" :value="y">{{ y }}</option>
        </select>
        <select v-model="filterPlatform" class="form-input" style="width: 140px;" @change="handleFilterChange">
          <option value="">All Platforms</option>
          <option v-for="p in platforms" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <button id="tour-add-asset" class="btn btn-primary" @click="showModal = true">+ Add Snapshot</button>
      </div>
    </header>

    <div id="tour-asset-metrics" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Total Invested
          <Tooltip title="Total Invested" description="The principal amount of money you have actually put into your investments." example="RM10,000 deposited to a broker" />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 50%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700;">RM{{ formatCurrency(totalInvested) }}</div>
          <div v-if="investedChange !== null" :class="investedChange >= 0 ? 'text-success' : 'text-danger'" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg v-if="investedChange >= 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            <svg v-else style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
            {{ Math.abs(investedChange).toFixed(2) }}% vs last month
          </div>
        </template>
      </div>

      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Current Balance</div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 45%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">RM{{ formatCurrency(totalBalance) }}</div>
          <div v-if="balanceChange !== null" :class="balanceChange >= 0 ? 'text-success' : 'text-danger'" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg v-if="balanceChange >= 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            <svg v-else style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
            {{ Math.abs(balanceChange).toFixed(2) }}% vs last month
          </div>
        </template>
      </div>

      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Absolute Profit
          <Tooltip title="Absolute Profit" description="The raw monetary difference between your current balance and total invested." example="RM12,000 Balance - RM10,000 Invested = RM2,000 Profit" />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 40%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700;" :class="absoluteProfit >= 0 ? 'text-success' : 'text-danger'">RM{{ formatCurrency(absoluteProfit) }}</div>
          <div v-if="profitChange !== null" :class="profitChange >= 0 ? 'text-success' : 'text-danger'" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg v-if="profitChange >= 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            <svg v-else style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
            {{ Math.abs(profitChange).toFixed(2) }}% vs last month
          </div>
        </template>
      </div>

      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          True ROI (%)
          <Tooltip title="True Return on Investment" description="Your absolute profit expressed as a percentage of your total invested amount. The ultimate metric of portfolio performance." example="(2,000 / 10,000) * 100 = 20%" />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 45%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700;" :class="profitPercentage >= 0 ? 'text-success' : 'text-danger'">{{ profitPercentage }}%</div>
          <div v-if="percentageChange !== null" :class="percentageChange >= 0 ? 'text-success' : 'text-danger'" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg v-if="percentageChange >= 0" style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            <svg v-else style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
            {{ Math.abs(percentageChange).toFixed(2) }}% vs last month
          </div>
        </template>
      </div>
    </div>
    
    <div v-if="maxConcentration" class="card" style="background: rgba(239, 68, 68, 0.1); border: 1px solid var(--danger); margin-bottom: 2rem;">
      <div style="display: flex; align-items: center; gap: 1rem;">
        <svg style="width: 32px; height: 32px; color: var(--danger);" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <div>
          <h3 style="color: var(--danger); font-weight: 600; margin: 0 0 0.25rem 0;">Diversification Risk Warning</h3>
          <p style="margin: 0; color: var(--text-primary); font-size: 0.875rem;">
            <strong>{{ maxConcentration.percentage.toFixed(1) }}%</strong> of your portfolio is concentrated in <strong>{{ maxConcentration.category }}</strong>. A healthy portfolio generally avoids having more than 75% of wealth tied to a single asset class.
          </p>
        </div>
      </div>
    </div>

    <div id="tour-asset-charts" class="grid-2col" style="margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">By Category</h3>
        <div v-if="byCategory.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No data available</div>
        <div v-else style="display: flex; justify-content: center; align-items: center; min-height: 250px;">
          <PieChart :labels="byCategory.map(i => i.category)" :data="byCategory.map(i => i.balance)" />
        </div>
      </div>
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">By Platform</h3>
        <div v-if="byPlatform.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No data available</div>
        <div v-else style="display: flex; justify-content: center; align-items: center; min-height: 250px;">
          <PieChart :labels="byPlatform.map(i => i.platform)" :data="byPlatform.map(i => i.balance)" />
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
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Asset Progress</h3>
        <div style="height: 300px;">
          <GraphLine v-if="yearlyData.length > 0" :labels="monthlyLabels" :datasets="progressDatasets" />
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Modal :show="showModal" title="Add Asset Snapshot" @close="showModal = false">
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
import SearchableSelect from '@/components/SearchableSelect.vue'

const startTour = () => {
  const driverObj = driver({
    showProgress: true,
    steps: [
      { element: '#tour-asset-metrics', popover: { title: 'Asset Metrics', description: 'See your principal invested vs your current balance to determine your real profits.' } },
      { element: '#tour-asset-charts', popover: { title: 'Portfolio Allocation', description: 'View exactly how your investments are distributed across different asset classes and platforms.' } },
      { element: '#tour-add-asset', popover: { title: 'Add Snapshot', description: 'Log your monthly investment performance here to build up your historical charts.' } }
    ]
  });
  driverObj.drive();
}

const totalInvested = ref(0)
const totalBalance = ref(0)
const absoluteProfit = ref(0)
const profitPercentage = ref(0)
const prevTotalInvested = ref(0)
const prevTotalBalance = ref(0)
const prevAbsoluteProfit = ref(0)
const prevProfitPercentage = ref(0)
const byCategory = ref([])
const byPlatform = ref([])
const yearlyData = ref([])
const dataLoading = ref(true)

const calculateChange = (current, previous) => {
  if (!previous) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
}

const investedChange = computed(() => calculateChange(totalInvested.value, prevTotalInvested.value))
const balanceChange = computed(() => calculateChange(totalBalance.value, prevTotalBalance.value))
const profitChange = computed(() => calculateChange(absoluteProfit.value, prevAbsoluteProfit.value))
const percentageChange = computed(() => {
  if (prevTotalInvested.value === 0) return null;
  return profitPercentage.value - prevProfitPercentage.value;
})

const maxConcentration = computed(() => {
  if (!byCategory.value || byCategory.value.length === 0 || totalBalance.value === 0) return null;
  let maxCat = null;
  let maxVal = 0;
  for (const cat of byCategory.value) {
    if (cat.balance > maxVal) {
      maxVal = cat.balance;
      maxCat = cat;
    }
  }
  const pct = (maxVal / totalBalance.value) * 100;
  if (pct > 75) {
    return { category: maxCat.category, percentage: pct };
  }
  return null;
})

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const filterPlatform = ref('')
const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const yearsList = computed(() => {
  const current = new Date().getFullYear()
  const years = []
  for (let y = current - 5; y <= current + 5; y++) {
    years.push(y)
  }
  return years
})

const handleFilterChange = async () => {
  dataLoading.value = true
  try {
    await Promise.all([fetchData(), fetchYearlyData()])
  } finally {
    dataLoading.value = false
  }
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
  },
  { 
    label: 'Current Balance', 
    data: yearlyData.value.map(d => d.totalBalance), 
    fill: false,
    stepped: true, 
    backgroundColor: '#3B82F6', 
    borderColor: '#3B82F6'
  }
])

const showModal = ref(false)
const loading = ref(false)

const categories = ref([])
const platforms = ref([])

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

const platformOptions = computed(() => {
  return platforms.value.map(p => ({ value: p.id, label: p.name }))
})

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchYearlyData = async () => {
  try {
    const res = await api.get(`/assets/snapshots/${filterPlatform.value ? '?platform_id=' + filterPlatform.value : ''}`)
    const yearSnaps = res.data.filter(s => s.year === selectedYear.value)
    
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
    
    const currentRealMonth = (new Date()).getMonth() + 1
    const currentRealYear = (new Date()).getFullYear()
    
    if (selectedYear.value === currentRealYear) {
      yearlyData.value = aggregated.slice(0, currentRealMonth)
    } else if (selectedYear.value > currentRealYear) {
      yearlyData.value = []
    } else {
      yearlyData.value = aggregated
    }
  } catch(e) {
    console.error(e)
  }
}

const fetchData = async () => {
  try {
    const res = await api.get(`/assets/snapshots/allocation/?month=${selectedMonth.value}&year=${selectedYear.value}${filterPlatform.value ? '&platform_id=' + filterPlatform.value : ''}`)
    totalInvested.value = res.data.total_invested
    totalBalance.value = res.data.total_portfolio_balance
    absoluteProfit.value = res.data.total_absolute_profit
    profitPercentage.value = res.data.total_profit_percentage
    prevTotalInvested.value = res.data.prev_total_invested
    prevTotalBalance.value = res.data.prev_total_portfolio_balance
    prevAbsoluteProfit.value = res.data.prev_total_absolute_profit
    prevProfitPercentage.value = res.data.prev_total_profit_percentage
    byCategory.value = res.data.allocation_by_category
    byPlatform.value = res.data.allocation_by_platform
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

const submitSnapshot = async () => {
  loading.value = true
  try {
    if (!form.value.platformId) {
      alert('Please select a platform.')
      loading.value = false
      return
    }

    await api.post('/assets/snapshots/', {
      month: form.value.month,
      year: form.value.year,
      platform: form.value.platformId,
      total_invested: form.value.totalInvested,
      current_balance: form.value.currentBalance
    })

    showModal.value = false
    
    // Automatically switch the view to the month/year of the newly added snapshot
    selectedMonth.value = form.value.month
    selectedYear.value = form.value.year
    
    form.value = getInitialForm()
    
    await fetchData()
    await fetchOptions()
    await fetchYearlyData()
  } catch (e) {
    console.error(e)
    alert('Failed to save snapshot')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  dataLoading.value = true
  try {
    try {
      const res = await api.get('/assets/snapshots/')
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
    await fetchYearlyData()
  } finally {
    dataLoading.value = false
  }
})
</script>
