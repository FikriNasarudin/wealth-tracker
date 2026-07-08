<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 50;">
      <div>
        <h1 style="font-weight: 600;">Liabilities Overview</h1>
        <p class="text-muted">Track your outstanding debts and loans.</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <SearchableSelect v-model="selectedPeriod" :options="trendOptions" @change="handleFilterChange" placeholder="Select Period" style="width: 140px;" />
        <select v-model="filterLender" class="form-input" style="width: 150px;" @change="handleFilterChange">
          <option value="">All Lenders</option>
          <option v-for="l in lenders" :key="l.id" :value="l.id">{{ l.name }}</option>
        </select>
        
        <button id="tour-add-liability" class="btn btn-primary" @click="showModal = true" style="margin-left: 1rem;">+ Add Snapshot</button>
      </div>
    </header>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card card-indigo">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Original Loan Amount
          <Tooltip title="Original Loan Amount" description="The initial principal amount you borrowed before making any repayments." example="Car loan principal of RM80,000" />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 50%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">RM{{ formatCurrency(totalOriginal) }}</div>
          <div v-if="originalChange !== null" :class="originalChange > 0 ? 'text-danger' : (originalChange < 0 ? 'text-success' : 'text-muted')" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.25rem;">
            <svg v-if="originalChange > 0" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            <svg v-else-if="originalChange < 0" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
            <span>
              {{ Math.abs(originalChange).toFixed(2) }}% vs last month
            </span>
          </div>
        </template>
      </div>

      <div id="tour-remaining-principal" class="card card-royal">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Remaining Principal
          <Tooltip title="Remaining Debt" description="The total amount of principal debt you still owe to your lenders, excluding future interest." example="Remaining mortgage or loan balance" />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 45%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--danger);">RM{{ formatCurrency(totalRemaining) }}</div>
          <div v-if="remainingChange !== null" :class="remainingChange > 0 ? 'text-danger' : (remainingChange < 0 ? 'text-success' : 'text-muted')" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.25rem;">
            <svg v-if="remainingChange > 0" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            <svg v-else-if="remainingChange < 0" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
            <span>
              {{ Math.abs(remainingChange).toFixed(2) }}% vs last month
            </span>
          </div>
        </template>
      </div>

      <div id="tour-debt-reduced" class="card card-emerald">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Total Debt Reduced
          <Tooltip title="Debt Paid Off" description="The cumulative amount of principal debt you have successfully paid off so far." example="Original RM50k - Remaining RM40k = RM10k paid off" />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 40%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">RM{{ formatCurrency(totalReduced) }}</div>
          <div v-if="reducedChange !== null" :class="reducedChange >= 0 ? 'text-success' : 'text-danger'" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.25rem;">
            <svg v-if="reducedChange >= 0" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            <svg v-else style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
            <span>
              {{ Math.abs(reducedChange).toFixed(2) }}% vs last month
            </span>
          </div>
        </template>
      </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
           Debt-to-Income (DTI)
           <Tooltip title="DTI Ratio" description="Percentage of gross monthly income spent on debt obligations. Keep under 36% for healthy standing." example="Ideal threshold: <36%" />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 50%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700;" :class="dtiRatio === null ? 'text-muted' : (dtiRatio <= 36 ? 'text-success' : (dtiRatio <= 43 ? 'text-warning' : 'text-danger'))">
             {{ dtiRatio === null ? 'N/A' : dtiRatio.toFixed(1) + '%' }}
          </div>
          <div v-if="dtiRatio !== null" class="text-muted" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="dtiRatio <= 36" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {{ dtiRatio <= 36 ? 'Healthy' : (dtiRatio <= 43 ? 'Elevated Risk' : 'High Risk') }}
          </div>
        </template>
      </div>

      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
           Cost of Debt (Avg Interest)
           <Tooltip title="Average Debt Cost" description="Weighted average interest rate based on the relative size of each of your loans." />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 45%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--warning);">
             {{ weightedAvgInterest.toFixed(2) }}%
          </div>
          <div class="text-muted" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            RM{{ formatCurrency(totalMonthlyDebtPayment) }}/mo Total Payment
          </div>
        </template>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-weight: 600; margin: 0; display: flex; align-items: center; gap: 0.25rem;">
            Debt Reduction Progress
            <Tooltip title="Debt Paydown Trend" description="Chart visualizing your outstanding liabilities decreasing month-over-month." />
          </h3>
          <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
            <SearchableSelect v-model="debtProgressStart" :options="trendOptions" placeholder="Start Month" />
            <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
            <SearchableSelect v-model="debtProgressEnd" :options="trendOptions" placeholder="End Month" />
          </div>
        </div>
        <div style="height: 300px;">
          <GraphLine v-if="debtProgressData.length > 0" :labels="debtProgressLabels" :datasets="progressDatasets" />
        </div>
      </div>

      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-weight: 600; margin: 0; display: flex; align-items: center; gap: 0.25rem;">
            Original vs Remaining
            <Tooltip title="Original vs. Current Balance" description="Compares the initial principal borrowed against the current remaining balance for each loan." />
          </h3>
          <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
            <SearchableSelect v-model="origVsRemStart" :options="trendOptions" placeholder="Start Month" />
            <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
            <SearchableSelect v-model="origVsRemEnd" :options="trendOptions" placeholder="End Month" />
          </div>
        </div>
        <div style="height: 300px;">
          <BarChart v-if="origVsRemData.length > 0" :labels="origVsRemLabels" :datasets="comparisonDatasets" />
        </div>
      </div>
      
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">
          Liability Distribution (Current Month)
          <Tooltip title="Lender/Debt Allocation" description="Breakdown of your current outstanding liabilities categorized by lender or loan type." />
        </h3>
        <div v-if="distribution.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No liabilities recorded for this period.</div>
        <div v-else style="display: flex; justify-content: center; align-items: center; min-height: 250px;">
          <PieChart :labels="distribution.map(i => i.category)" :data="distribution.map(i => i.balance)" />
        </div>
      </div>

      <div id="tour-payoff-tracker" class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">
          Debt Payoff Tracker
          <Tooltip title="Debt Snowball/Avalanche Tracker" description="Visualizes estimated months left to pay off each active debt based on interest rate and payment allocation." />
        </h3>
        <div v-if="payoffPlans.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No debt payoff plans available.</div>
        <div v-else style="display: flex; flex-direction: column; gap: 1rem; max-height: 310px; overflow-y: auto; padding-right: 0.25rem;">
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

      <!-- Credit Limit Usage Section -->
      <div v-if="creditLimitUsage.cards.length > 0" class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">
          Credit & Spending Limit Usage
          <Tooltip title="Credit Utilization Ratio" description="Calculates outstanding balances against total credit limit across active cards. Keep under 30%." />
        </h3>
        
        <!-- Overall Summary -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; background: rgba(255, 255, 255, 0.02); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color);">
          <div>
            <div class="text-muted" style="font-size: 0.85rem;">Overall Utilization</div>
            <div style="font-size: 1.5rem; font-weight: 700;" :class="creditLimitUsage.overallUsagePercent > 70 ? 'text-danger' : (creditLimitUsage.overallUsagePercent > 30 ? 'text-warning' : 'text-success')">
              {{ creditLimitUsage.overallUsagePercent.toFixed(1) }}%
            </div>
          </div>
          <div>
            <div class="text-muted" style="font-size: 0.85rem;">Total Limit</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">RM{{ formatCurrency(creditLimitUsage.totalLimit) }}</div>
          </div>
          <div>
            <div class="text-muted" style="font-size: 0.85rem;">Total Outstanding</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--danger);">RM{{ formatCurrency(creditLimitUsage.totalOutstanding) }}</div>
          </div>
          <div>
            <div class="text-muted" style="font-size: 0.85rem;">Total Available</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--success);">RM{{ formatCurrency(creditLimitUsage.totalAvailable) }}</div>
          </div>
        </div>

        <!-- Individual Cards -->
        <div style="display: flex; flex-direction: column; gap: 1.25rem; max-height: 310px; overflow-y: auto; padding-right: 0.25rem;">
          <div v-for="card in creditLimitUsage.cards" :key="card.id" style="border: 1px solid var(--border-color); border-radius: 0.5rem; padding: 1rem; background: rgba(255, 255, 255, 0.01);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
              <span style="font-weight: 600;">{{ card.name }} <span class="text-muted" style="font-size: 0.75rem; font-weight: normal;">({{ card.category }})</span></span>
              <span :style="{ color: card.usagePercent > 70 ? 'var(--danger)' : (card.usagePercent > 30 ? 'var(--warning)' : 'var(--success)') }" style="font-weight: 500;">
                {{ card.usagePercent.toFixed(1) }}% Utilized
              </span>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.75rem;">
              <span>Outstanding: RM{{ formatCurrency(card.outstanding) }}</span>
              <span>Limit: RM{{ formatCurrency(card.limit) }}</span>
            </div>
            
            <div style="width: 100%; height: 8px; background: var(--bg-background); border-radius: 4px; overflow: hidden; margin-bottom: 0.25rem;">
              <div :style="{
                width: card.usagePercent + '%',
                height: '100%',
                background: card.usagePercent > 70 ? 'var(--danger)' : (card.usagePercent > 30 ? 'var(--warning)' : 'var(--success)')
              }"></div>
            </div>
            <div class="text-muted" style="font-size: 0.75rem; text-align: right;">
              RM{{ formatCurrency(card.available) }} available
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




const totalOriginal = ref(0)
const totalRemaining = ref(0)
const totalReduced = ref(0)
const prevTotalOriginal = ref(0)
const prevTotalRemaining = ref(0)
const prevTotalReduced = ref(0)
const distribution = ref([])
const yearlyData = ref([])
const payoffPlans = ref([])

const totalMonthlyDebtPayment = ref(0)
const weightedAvgInterest = ref(0)
const currentMonthIncome = ref(0)

const calculateChange = (current, previous) => {
  if (!previous) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
}

const dtiRatio = computed(() => {
  if (currentMonthIncome.value <= 0) return null;
  return (totalMonthlyDebtPayment.value / currentMonthIncome.value) * 100;
})

const originalChange = computed(() => calculateChange(totalOriginal.value, prevTotalOriginal.value))
const remainingChange = computed(() => calculateChange(totalRemaining.value, prevTotalRemaining.value))
const reducedChange = computed(() => calculateChange(totalReduced.value, prevTotalReduced.value))

const originalDiff = computed(() => totalOriginal.value - prevTotalOriginal.value)
const remainingDiff = computed(() => totalRemaining.value - prevTotalRemaining.value)
const reducedDiff = computed(() => totalReduced.value - prevTotalReduced.value)

const creditLimitUsage = computed(() => {
  const cards = lenders.value.filter(l => {
    const isCc = l.category_name && (
      l.category_name.toLowerCase().includes('credit card') ||
      l.category_name.toLowerCase().includes('pay later') ||
      l.category_name.toLowerCase().includes('bnpl')
    )
    return isCc && l.is_active
  })
  
  let totalLimit = 0
  let totalOutstanding = 0
  
  const items = cards.map(c => {
    const limit = parseFloat(c.original_loan_amount || 0)
    const outstanding = parseFloat(c.calculated_remaining_principal || 0)
    const available = Math.max(0, limit - outstanding)
    const usagePercent = limit > 0 ? (outstanding / limit) * 100 : 0
    
    totalLimit += limit
    totalOutstanding += outstanding
    
    return {
      id: c.id,
      name: c.name,
      category: c.category_name,
      limit,
      outstanding,
      available,
      usagePercent: Math.min(100, usagePercent)
    }
  })
  
  const overallUsagePercent = totalLimit > 0 ? (totalOutstanding / totalLimit) * 100 : 0
  
  return {
    cards: items,
    totalLimit,
    totalOutstanding,
    totalAvailable: Math.max(0, totalLimit - totalOutstanding),
    overallUsagePercent: Math.min(100, overallUsagePercent)
  }
})

import SearchableSelect from '@/components/SearchableSelect.vue'

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const selectedPeriod = computed({
  get() {
    return `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}`
  },
  set(val) {
    if (val) {
      const [y, m] = val.split('-')
      selectedYear.value = Number(y)
      selectedMonth.value = Number(m)
    }
  }
})
const currentYear = d.getFullYear()

const debtProgressStart = ref(`${currentYear}-01`)
const debtProgressEnd = ref(`${currentYear}-${String(d.getMonth() + 1).padStart(2, '0')}`)
const origVsRemStart = ref(`${currentYear}-01`)
const origVsRemEnd = ref(`${currentYear}-${String(d.getMonth() + 1).padStart(2, '0')}`)

const trendOptions = ref([])

const generateTrendOptions = (oldestYear, oldestMonth) => {
  const options = []
  const currentY = d.getFullYear()
  const currentM = d.getMonth() + 1
  
  let startYear = oldestYear || (currentY - 2)
  let startMonth = oldestMonth || 1
  
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
  
  trendOptions.value = options
}

const fetchOldestDataDate = async () => {
  try {
    const res = await api.get('/liabilities/snapshots/')
    let oldestY = null
    let oldestM = null
    
    if (res.data && res.data.length > 0) {
      res.data.forEach(item => {
        const itemY = Number(item.year)
        const itemM = Number(item.month)
        if (!oldestY || itemY < oldestY || (itemY === oldestY && itemM < oldestM)) {
          oldestY = itemY
          oldestM = itemM
        }
      })
    }
    
    generateTrendOptions(oldestY, oldestM)
  } catch(e) {
    console.error(e)
    generateTrendOptions()
  }
}

const filterLender = ref('')
const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const rawSnapshots = ref([])

const processLiabilitiesData = (allSnaps, startDateStr, endDateStr) => {
  if (!startDateStr || !endDateStr || !allSnaps) return []
  const [startYear, startMonth] = startDateStr.split('-').map(Number)
  const [endYear, endMonth] = endDateStr.split('-').map(Number)
  
  const list = []
  let currYear = startYear
  let currMonth = startMonth
  const shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  
  while (currYear < endYear || (currYear === endYear && currMonth <= endMonth)) {
    list.push({
      year: currYear,
      month: currMonth,
      monthLabel: `${shortMonths[currMonth - 1]} ${currYear}`,
      remainingPrincipal: 0,
      originalAmount: 0
    })
    currMonth++
    if (currMonth > 12) {
      currMonth = 1
      currYear++
    }
  }
  
  list.forEach(item => {
    const priorSnaps = allSnaps.filter(s => {
      const snapY = Number(s.year)
      const snapM = Number(s.month)
      if (snapY < item.year) return true;
      if (snapY === item.year && snapM <= item.month) return true;
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
    
    item.remainingPrincipal = tRemaining
    item.originalAmount = tOriginal
  })
  
  return list.map(item => ({
    month: item.monthLabel,
    remainingPrincipal: item.remainingPrincipal,
    originalAmount: item.originalAmount
  }))
}

// 1. Debt Reduction Progress computed properties
const debtProgressData = computed(() => processLiabilitiesData(rawSnapshots.value, debtProgressStart.value, debtProgressEnd.value))
const debtProgressLabels = computed(() => debtProgressData.value.map(d => d.month))
const progressDatasets = computed(() => [
  { 
    label: 'Total Remaining Principal', 
    data: debtProgressData.value.map(d => d.remainingPrincipal), 
    fill: true, 
    backgroundColor: 'rgba(239, 68, 68, 0.2)', 
    borderColor: '#EF4444', 
    tension: 0.4 
  }
])

// 2. Original vs Remaining computed properties
const origVsRemData = computed(() => processLiabilitiesData(rawSnapshots.value, origVsRemStart.value, origVsRemEnd.value))
const origVsRemLabels = computed(() => origVsRemData.value.map(d => d.month))
const comparisonDatasets = computed(() => [
  { 
    label: 'Original Loan Amount', 
    data: origVsRemData.value.map(d => d.originalAmount), 
    backgroundColor: '#3B82F6',
    borderRadius: 4
  },
  { 
    label: 'Remaining Principal', 
    data: origVsRemData.value.map(d => d.remainingPrincipal), 
    backgroundColor: '#EF4444',
    borderRadius: 4
  }
])

const dataLoading = ref(true)

const handleFilterChange = async () => {
  dataLoading.value = true
  try {
    await fetchData()
  } finally {
    dataLoading.value = false
  }
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
  dataLoading.value = true
  try {
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
      const lendRes = await api.get(`/liabilities/lenders/?month=${selectedMonth.value}&year=${selectedYear.value}`)
      lenders.value = lendRes.data
    } catch(e) {
      console.error(e)
    }

    try {
      const allRes = await api.get(`/liabilities/snapshots/${filterLender.value ? '?lender_id=' + filterLender.value : ''}`)
      const allSnaps = allRes.data
      rawSnapshots.value = allSnaps

      // Calculate Payoff Plans for selected month (itemized)
      const itemsForPayoff = []
      lenders.value.forEach(lender => {
        if (!lender.is_active) return
        if (filterLender.value && lender.id !== Number(filterLender.value)) return

        if (lender.items && lender.items.length > 0) {
          lender.items.forEach(item => {
            const principal = parseFloat(item.remaining_balance || 0)
            if (principal > 0) {
              itemsForPayoff.push({
                id: item.id,
                name: `${item.name} (${lender.name})`,
                interestRate: parseFloat(item.interest_rate || 0),
                remainingPrincipal: principal,
                originalAmount: parseFloat(item.value || 0),
                monthlyPayment: parseFloat(item.monthly_payment || 0)
              })
            }
          })
        } else {
          const principal = parseFloat(lender.calculated_remaining_principal || 0)
          if (principal > 0) {
            itemsForPayoff.push({
              id: `lender_${lender.id}`,
              name: lender.name,
              interestRate: parseFloat(lender.interest_rate || 0),
              remainingPrincipal: principal,
              originalAmount: parseFloat(lender.original_loan_amount || 0),
              monthlyPayment: parseFloat(lender.calculated_monthly_payment || 0)
            })
          }
        }
      })

      let sumPayments = 0;
      let sumWeightedInterest = 0;
      let sumPrincipalForInterest = 0;
      
      payoffPlans.value = itemsForPayoff.map(item => {
        const interestRate = item.interestRate
        const principal = item.remainingPrincipal
        const payment = item.monthlyPayment
        
        sumPayments += payment;
        sumWeightedInterest += (interestRate * principal);
        sumPrincipalForInterest += principal;
        
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
          id: item.id,
          lenderName: item.name,
          interestRate,
          remainingPrincipal: principal,
          originalAmount: item.originalAmount,
          monthlyPayment: payment,
          monthsRemaining: months > 900 ? '∞' : months
        }
      }).sort((a, b) => b.interestRate - a.interestRate)

      totalMonthlyDebtPayment.value = sumPayments;
      weightedAvgInterest.value = sumPrincipalForInterest > 0 ? (sumWeightedInterest / sumPrincipalForInterest) : 0;

    } catch (e) {
      console.error(e)
    }
    
    try {
      const currentBudgetRes = await api.get(`/budgeting/transactions/summary/?month=${selectedMonth.value}&year=${selectedYear.value}`)
      currentMonthIncome.value = currentBudgetRes.data.total_income || 0
    } catch (e) {
      console.error(e)
    }
  } finally {
    dataLoading.value = false
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
  dataLoading.value = true
  try {
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

        // Set all chart end dates to the latest available data date
        const latestStr = `${latest.year}-${String(latest.month).padStart(2, '0')}`
        debtProgressEnd.value = latestStr
        origVsRemEnd.value = latestStr
      }
    } catch(e) {
      console.error(e)
    }

    await fetchOldestDataDate()
    await fetchOptions()
    await fetchData()
  } finally {
    dataLoading.value = false
  }
})
</script>

<style scoped>
:deep(.trend-select-wrapper .searchable-select) {
  width: 95px !important;
}
:deep(.trend-select-wrapper .select-trigger) {
  height: 28px !important;
  padding: 0.2rem 0.4rem !important;
  background: transparent !important;
  border: none !important;
  font-size: 0.8rem !important;
  color: #fff !important;
  box-shadow: none !important;
}
:deep(.trend-select-wrapper .chevron-arrow) {
  font-size: 0.6rem !important;
  margin-left: 0.15rem !important;
}
:deep(.trend-select-wrapper .dropdown-menu) {
  width: 140px !important;
  font-size: 0.8rem !important;
}
</style>
