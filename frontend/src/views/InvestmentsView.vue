<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Investments Overview</h1>
        <p class="text-muted">Track your portfolio allocation and profits.</p>
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
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Total Invested</div>
        <div style="font-size: 2rem; font-weight: 700;">RM{{ formatCurrency(totalInvested) }}</div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Current Balance</div>
        <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">RM{{ formatCurrency(totalBalance) }}</div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Absolute Profit</div>
        <div style="font-size: 2rem; font-weight: 700;" :class="absoluteProfit >= 0 ? 'text-success' : 'text-danger'">RM{{ formatCurrency(absoluteProfit) }}</div>
      </div>
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">Profit Percentage</div>
        <div style="font-size: 2rem; font-weight: 700;" :class="profitPercentage >= 0 ? 'text-success' : 'text-danger'">{{ profitPercentage }}%</div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">By Category</h3>
        <div v-if="byCategory.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No data available</div>
        <div v-else style="display: flex; justify-content: center; align-items: center; min-height: 250px;">
          <DoughnutChart :labels="byCategory.map(i => i.category)" :data="byCategory.map(i => i.balance)" />
        </div>
      </div>
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">By Platform</h3>
        <div v-if="byPlatform.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No data available</div>
        <div v-else style="display: flex; justify-content: center; align-items: center; min-height: 250px;">
          <DoughnutChart :labels="byPlatform.map(i => i.platform)" :data="byPlatform.map(i => i.balance)" />
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

    <!-- Modal -->
    <Modal :show="showModal" title="Add Investment Snapshot" @close="showModal = false">
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
import DoughnutChart from '@/components/DoughnutChart.vue'
import BarChart from '@/components/BarChart.vue'
import GraphLine from '@/components/GraphLine.vue'

const totalInvested = ref(0)
const totalBalance = ref(0)
const absoluteProfit = ref(0)
const profitPercentage = ref(0)
const byCategory = ref([])
const byPlatform = ref([])
const yearlyData = ref([])

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

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

const showModal = ref(false)
const loading = ref(false)

const categories = ref([])
const platforms = ref([])
const isNewCategory = ref(false)
const isNewPlatform = ref(false)

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

const fetchYearlyData = async () => {
  try {
    const res = await api.get('/investments/snapshots/')
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
    
    yearlyData.value = aggregated
  } catch(e) {
    console.error(e)
  }
}

const fetchData = async () => {
  try {
    const res = await api.get(`/investments/snapshots/allocation/?month=${selectedMonth.value}&year=${selectedYear.value}`)
    totalInvested.value = res.data.total_invested
    totalBalance.value = res.data.total_portfolio_balance
    absoluteProfit.value = res.data.total_absolute_profit
    profitPercentage.value = res.data.total_profit_percentage
    byCategory.value = res.data.allocation_by_category
    byPlatform.value = res.data.allocation_by_platform
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

    await api.post('/investments/snapshots/', {
      month: form.value.month,
      year: form.value.year,
      category: categoryId,
      platform: platformId,
      total_invested: form.value.totalInvested,
      current_balance: form.value.currentBalance
    })

    showModal.value = false
    isNewCategory.value = false
    isNewPlatform.value = false
    
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

  await fetchData()
  await fetchOptions()
  await fetchYearlyData()
})
</script>
