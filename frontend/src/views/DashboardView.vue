<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem; position: relative; z-index: 50;">
      <h1 style="font-weight: 600;">Dashboard</h1>
      <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;">
        <button class="btn btn-secondary" @click="startTour" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
          <svg style="width: 16px; height: 16px; display: inline; vertical-align: middle; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Help
        </button>
        <SearchableSelect v-model="selectedPeriod" :options="trendOptions" @change="fetchData" placeholder="Select Period" style="width: 140px;" />
      </div>
    </header>

    <AIAdvisorCard v-if="enableAI" dashboardType="MAIN" :month="selectedMonth" :year="selectedYear" style="margin-bottom: 2rem;" />

    <!-- Welcome Onboarding Checklist Card -->
    <div v-if="showOnboardingChecklist && (totalLiquidAssets === 0 || totalAssets === 0 || totalLiabilities === 0)" class="card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%); border: 1px solid var(--border-color); margin-bottom: 2rem; position: relative;">
      <button @click="dismissOnboarding" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.25rem;" title="Dismiss Guide">&times;</button>
      <div style="display: flex; align-items: flex-start; gap: 1.25rem; flex-wrap: wrap; padding-right: 1.5rem;">
        <div style="font-size: 2.25rem; line-height: 1;">✨</div>
        <div style="flex: 1; min-width: 250px;">
          <h3 style="margin: 0 0 0.25rem 0; font-weight: 700; color: #fff;">Welcome to Aether Wealth!</h3>
          <p class="text-muted" style="margin: 0 0 1.25rem 0; font-size: 0.9rem;">Follow these quick-start steps to set up your dashboard and start monitoring your net worth progress.</p>
          
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
            <!-- Step 1: Banking -->
            <div style="display: flex; align-items: center; gap: 0.75rem; background: rgba(255, 255, 255, 0.02); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-color);">
              <input type="checkbox" :checked="totalLiquidAssets > 0" disabled style="accent-color: var(--success); width: 18px; height: 18px;" />
              <div style="display: flex; flex-direction: column;">
                <router-link to="/banking" style="color: var(--text-primary); text-decoration: none; font-size: 0.875rem; font-weight: 600; display: flex; align-items: center; gap: 0.25rem;">
                  1. Link Bank Accounts
                  <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                </router-link>
                <span class="text-muted" style="font-size: 0.75rem;">Add liquid savings & cash</span>
              </div>
            </div>

            <!-- Step 2: Assets -->
            <div style="display: flex; align-items: center; gap: 0.75rem; background: rgba(255, 255, 255, 0.02); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-color);">
              <input type="checkbox" :checked="totalAssets > 0" disabled style="accent-color: var(--success); width: 18px; height: 18px;" />
              <div style="display: flex; flex-direction: column;">
                <router-link to="/assets" style="color: var(--text-primary); text-decoration: none; font-size: 0.875rem; font-weight: 600; display: flex; align-items: center; gap: 0.25rem;">
                  2. Add Asset Snapshot
                  <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                </router-link>
                <span class="text-muted" style="font-size: 0.75rem;">Stocks, crypto, property</span>
              </div>
            </div>

            <!-- Step 3: Liabilities -->
            <div style="display: flex; align-items: center; gap: 0.75rem; background: rgba(255, 255, 255, 0.02); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-color);">
              <input type="checkbox" :checked="totalLiabilities > 0" disabled style="accent-color: var(--success); width: 18px; height: 18px;" />
              <div style="display: flex; flex-direction: column;">
                <router-link to="/liabilities" style="color: var(--text-primary); text-decoration: none; font-size: 0.875rem; font-weight: 600; display: flex; align-items: center; gap: 0.25rem;">
                  3. Log Debt/Loans
                  <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                </router-link>
                <span class="text-muted" style="font-size: 0.75rem;">Car loans, card balances</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <!-- Total Assets Card -->
      <div id="tour-liquid" class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Liquid Assets
          <Tooltip title="Liquid Assets" description="Money in bank accounts or cash that you can spend immediately." example="Savings account, physical cash" />
        </div>
        <template v-if="loading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 50%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--accent-primary);">RM{{ formatCurrency(totalLiquidAssets) }}</div>
          <div class="text-muted" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg style="width: 16px; height: 16px; margin-right: 0.25rem; color: var(--accent-primary);" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            Runway: 
            <strong style="margin-left: 0.25rem;">
              {{ emergencyRunway === null ? 'N/A' : (emergencyRunway >= 999 ? '999+' : emergencyRunway.toFixed(1)) }} Months
            </strong>
          </div>
        </template>
      </div>

      <div id="tour-invested" class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Invested Assets
          <Tooltip title="Invested Assets" description="The current value of your investments like stocks, bonds, or real estate." example="Stock portfolio, mutual funds" />
        </div>
        <template v-if="loading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 45%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">RM{{ formatCurrency(totalAssets) }}</div>
          <div class="text-success" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            +{{ profitPercentage }}% Profit
          </div>
        </template>
      </div>

      <!-- Total Liabilities Card -->
      <div id="tour-liabilities" class="card">
        <div class="text-muted" style="margin-bottom: 0.5rem; font-weight: 500;">
          Total Liabilities
          <Tooltip title="Total Liabilities" description="The total amount of debt you currently owe across all loans and credit cards." example="Car loan, mortgage" />
        </div>
        <template v-if="loading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 40%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary);">RM{{ formatCurrency(totalLiabilities) }}</div>
          <div class="text-warning" style="font-size: 0.875rem; margin-top: 0.5rem; display: flex; align-items: center;">
            <svg style="width: 16px; height: 16px; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
            </svg>
            Outstanding Debt
          </div>
        </template>
      </div>

      <!-- Net Worth Card -->
      <div id="tour-net-worth" class="card" style="background: var(--accent-gradient); border: none;">
        <div style="color: rgba(255, 255, 255, 0.8); margin-bottom: 0.5rem; font-weight: 500;">
          Estimated Net Worth
          <Tooltip title="Estimated Net Worth" description="Your total wealth calculated by subtracting your debts from your assets." example="(Liquid + Invested) - Liabilities" />
        </div>
        <template v-if="loading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0; background: rgba(255,255,255,0.15);"></div>
          <div class="skeleton skeleton-text" style="width: 45%; background: rgba(255,255,255,0.15);"></div>
        </template>
        <template v-else>
          <div style="font-size: 2rem; font-weight: 700; color: #fff;">RM{{ formatCurrency(netWorth) }}</div>
          <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.875rem; margin-top: 0.5rem;">
            Assets - Liabilities
          </div>
        </template>
      </div>
    </div>

    <div class="grid-2col" style="margin-bottom: 2rem;">
      <div id="tour-breakdown" class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">
          Net Worth Breakdown
          <Tooltip title="Net Worth Breakdown" description="Visual allocation of your liquid assets, investments, and liabilities to see your overall wealth distribution." example="Checking accounts, Stock portfolio, and Credit card debt" />
        </h3>
        <div style="display: flex; justify-content: center; align-items: center; min-height: 250px;">
          <PieChart 
            :labels="['Liquid Assets', 'Invested Assets', 'Liabilities (Negative)']" 
            :data="[totalLiquidAssets, totalAssets, totalLiabilities]"
            :colors="['#3B82F6', '#10B981', '#EF4444']"
          />
        </div>
      </div>
      <div class="card" style="display: flex; flex-direction: column;">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">
          Monthly Cash Flow ({{ monthsList[selectedMonth - 1] }})
          <Tooltip title="Cash Flow Diagram" description="A visual breakdown of how your income is split into expenses and savings this month." example="" />
        </h3>
        
        <div style="flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 1.5rem; padding: 1rem; background: var(--bg-background); border-radius: 8px;">
          <div style="display: flex; justify-content: space-between; font-weight: 600; color: var(--success); align-items: center;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <svg style="width: 20px; height: 20px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Total Income
            </div>
            <span>RM{{ formatCurrency(currentMonthIncome) }}</span>
          </div>
          
          <div style="display: flex; height: 32px; border-radius: 16px; overflow: hidden; background: var(--border-color);">
            <div :style="{ width: expensePercentage + '%', background: 'var(--danger)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '0.75rem', fontWeight: 600, transition: 'width 0.5s ease' }">
               {{ expensePercentage >= 5 ? expensePercentage.toFixed(1) + '%' : '' }}
            </div>
            <div :style="{ width: cashflowPercentage + '%', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '0.75rem', fontWeight: 600, transition: 'width 0.5s ease' }">
               {{ cashflowPercentage >= 5 ? cashflowPercentage.toFixed(1) + '%' : '' }}
            </div>
          </div>
          
          <div style="display: flex; justify-content: space-between; font-size: 0.875rem;">
            <div style="color: var(--danger);">
               <div style="font-weight: 600; display: flex; align-items: center; gap: 0.25rem;">
                 <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
                 Total Expenses
               </div>
               <div style="font-weight: 500; font-size: 1rem; margin-top: 0.25rem;">RM{{ formatCurrency(currentMonthExpenses) }}</div>
            </div>
            <div style="color: var(--accent-primary); text-align: right;">
               <div style="font-weight: 600; display: flex; align-items: center; justify-content: flex-end; gap: 0.25rem;">
                 Savings (Net Flow)
                 <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
               </div>
               <div style="font-weight: 500; font-size: 1rem; margin-top: 0.25rem;">RM{{ formatCurrency(currentMonthNetCashFlow) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-weight: 600; margin: 0; display: flex; align-items: center; gap: 0.25rem;">
            Income vs Expenses Trend
            <Tooltip title="Income vs Expenses" description="Historical comparison of your monthly earnings against your monthly spending to track savings trends." example="Salary and business income vs rent and grocer expenses" />
          </h3>
          <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
            <SearchableSelect v-model="incomeExpenseStart" :options="trendOptions" @change="fetchData" placeholder="Start Month" />
            <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
            <SearchableSelect v-model="incomeExpenseEnd" :options="trendOptions" @change="fetchData" placeholder="End Month" />
          </div>
        </div>
        <div style="height: 300px;">
          <BarChart v-if="trendLabels.length > 0" :labels="trendLabels" :datasets="trendDatasets" />
        </div>
      </div>
    </div>
      
    <div style="display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-weight: 600; margin: 0; display: flex; align-items: center; gap: 0.25rem;">
            Total Assets Over Time
            <Tooltip title="Asset History" description="Historical trend of your total assets (liquid and invested) to track wealth growth over time." example="Includes cash balances and broker portfolio value" />
          </h3>
          <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
            <SearchableSelect v-model="assetsOverTimeStart" :options="trendOptions" placeholder="Start Month" />
            <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
            <SearchableSelect v-model="assetsOverTimeEnd" :options="trendOptions" placeholder="End Month" />
          </div>
        </div>
        <div style="height: 300px;">
          <GraphLine v-if="assetsOverTimeData.length > 0" :labels="assetsOverTimeLabels" :datasets="assetDatasets" />
        </div>
      </div>

      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-weight: 600; margin: 0; display: flex; align-items: center; gap: 0.25rem;">
            Asset Progress
            <Tooltip title="Asset Progress" description="The proportional growth and target achievements of your portfolio assets." example="Growth of stocks vs savings accounts" />
          </h3>
          <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
            <SearchableSelect v-model="assetProgressStart" :options="trendOptions" placeholder="Start Month" />
            <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
            <SearchableSelect v-model="assetProgressEnd" :options="trendOptions" placeholder="End Month" />
          </div>
        </div>
        <div style="height: 300px;">
          <GraphLine v-if="assetProgressData.length > 0" :labels="assetProgressLabels" :datasets="progressDatasets" />
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
import PieChart from '@/components/PieChart.vue'
import Tooltip from '@/components/Tooltip.vue'
import AIAdvisorCard from '@/components/AIAdvisorCard.vue'
import { driver } from 'driver.js'

const enableAI = import.meta.env.VITE_ENABLE_AI_ADVISOR === 'true'

const showOnboardingChecklist = ref(localStorage.getItem('dismissed_onboarding') !== 'true')
const dismissOnboarding = () => {
  showOnboardingChecklist.value = false
  localStorage.setItem('dismissed_onboarding', 'true')
}

const startTour = () => {
  const driverObj = driver({
    showProgress: true,
    steps: [
      { element: '#tour-liquid', popover: { title: 'Liquid Assets', description: 'This is the total of your cash, checking, and savings accounts. It is money that you can access immediately.' } },
      { element: '#tour-invested', popover: { title: 'Invested Assets', description: 'This represents the current value of your investments like stocks, bonds, or real estate.' } },
      { element: '#tour-liabilities', popover: { title: 'Total Liabilities', description: 'This is the total amount of debt you currently owe across all loans and credit cards.' } },
      { element: '#tour-net-worth', popover: { title: 'Estimated Net Worth', description: 'Your net worth is calculated by adding your liquid and invested assets, then subtracting your liabilities.' } },
      { element: '#tour-breakdown', popover: { title: 'Net Worth Breakdown', description: 'This chart visually breaks down your wealth into liquid cash, investments, and debts.' } }
    ]
  });
  driverObj.drive();
}

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

const incomeExpenseStart = ref(`${currentYear}-01`)
const incomeExpenseEnd = ref(`${currentYear}-${String(d.getMonth() + 1).padStart(2, '0')}`)
const assetsOverTimeStart = ref(`${currentYear}-01`)
const assetsOverTimeEnd = ref(`${currentYear}-${String(d.getMonth() + 1).padStart(2, '0')}`)
const assetProgressStart = ref(`${currentYear}-01`)
const assetProgressEnd = ref(`${currentYear}-${String(d.getMonth() + 1).padStart(2, '0')}`)

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
    const [assetsRes, liabRes] = await Promise.all([
      api.get('/assets/snapshots/'),
      api.get('/liabilities/snapshots/')
    ])
    
    let oldestY = null
    let oldestM = null
    
    const updateOldest = (item) => {
      const itemY = Number(item.year)
      const itemM = Number(item.month)
      if (!oldestY || itemY < oldestY || (itemY === oldestY && itemM < oldestM)) {
        oldestY = itemY
        oldestM = itemM
      }
    }
    
    if (assetsRes.data && assetsRes.data.length > 0) {
      assetsRes.data.forEach(updateOldest)
    }
    if (liabRes.data && liabRes.data.length > 0) {
      liabRes.data.forEach(updateOldest)
    }
    
    generateTrendOptions(oldestY, oldestM)
  } catch(e) {
    console.error(e)
    generateTrendOptions()
  }
}

const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const totalAssets = ref(0)
const totalLiquidAssets = ref(0)
const profitPercentage = ref(0)
const totalLiabilities = ref(0)
const rawSnapshots = ref([])
const trendData = ref([])

const currentMonthIncome = ref(0)
const currentMonthExpenses = ref(0)
const currentMonthNetCashFlow = ref(0)

const netWorth = computed(() => {
  return totalAssets.value + totalLiquidAssets.value - totalLiabilities.value
})

const emergencyRunway = computed(() => {
  if (currentMonthExpenses.value <= 0) return null;
  return totalLiquidAssets.value / currentMonthExpenses.value;
})

const expensePercentage = computed(() => {
  if (currentMonthIncome.value <= 0) return currentMonthExpenses.value > 0 ? 100 : 0;
  return Math.min((currentMonthExpenses.value / currentMonthIncome.value) * 100, 100);
})

const cashflowPercentage = computed(() => {
  if (currentMonthIncome.value <= 0) return 0;
  return Math.max(0, 100 - expensePercentage.value);
})

const formatCurrency = (val) => {
  return Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const processSnapshotData = (snapshots, startDateStr, endDateStr) => {
  if (!startDateStr || !endDateStr) return []
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
      totalInvested: 0,
      totalBalance: 0,
      profit: 0
    })
    currMonth++
    if (currMonth > 12) {
      currMonth = 1
      currYear++
    }
  }
  
  snapshots.forEach(snap => {
    const match = list.find(l => l.year === Number(snap.year) && l.month === Number(snap.month))
    if (match) {
      match.totalInvested += parseFloat(snap.total_invested || 0)
      match.totalBalance += parseFloat(snap.current_balance || 0)
    }
  })
  
  list.forEach(item => {
    if (item.totalInvested > 0 || item.totalBalance > 0) {
      item.profit = item.totalBalance - item.totalInvested
    }
  })
  return list.map(item => ({
    month: item.monthLabel,
    totalInvested: item.totalInvested,
    totalBalance: item.totalBalance,
    profit: item.profit
  }))
}

// 1. Assets Over Time computed properties
const assetsOverTimeData = computed(() => processSnapshotData(rawSnapshots.value, assetsOverTimeStart.value, assetsOverTimeEnd.value))
const assetsOverTimeLabels = computed(() => assetsOverTimeData.value.map(d => d.month))
const assetDatasets = computed(() => [
  { 
    label: 'Total Balance', 
    data: assetsOverTimeData.value.map(d => d.totalBalance), 
    fill: true, 
    backgroundColor: 'rgba(59, 130, 246, 0.2)', 
    borderColor: '#3B82F6', 
    tension: 0.4 
  }
])

// 2. Asset Progress computed properties
const assetProgressData = computed(() => processSnapshotData(rawSnapshots.value, assetProgressStart.value, assetProgressEnd.value))
const assetProgressLabels = computed(() => assetProgressData.value.map(d => d.month))
const progressDatasets = computed(() => [
  { 
    label: 'Total Invested', 
    data: assetProgressData.value.map(d => d.totalInvested), 
    fill: true, 
    stepped: true, 
    backgroundColor: 'rgba(16, 185, 129, 0.2)', 
    borderColor: '#10B981' 
  },
  { 
    label: 'Current Balance', 
    data: assetProgressData.value.map(d => d.totalBalance), 
    fill: false,
    stepped: true, 
    backgroundColor: '#3B82F6', 
    borderColor: '#3B82F6'
  }
])

// 3. Income vs Expense Trend computed properties
const trendLabels = computed(() => trendData.value.map(d => d.label))
const trendDatasets = computed(() => [
  { 
    label: 'Income', 
    data: trendData.value.map(d => d.income), 
    backgroundColor: '#10B981',
    borderRadius: 4
  },
  { 
    label: 'Expense', 
    data: trendData.value.map(d => d.expense), 
    backgroundColor: '#EF4444',
    borderRadius: 4
  }
])

const loading = ref(true)

const fetchData = async () => {
  loading.value = true
  const month = selectedMonth.value
  const year = selectedYear.value

  try {
    const invRes = await api.get(`/assets/snapshots/allocation/?month=${month}&year=${year}`)
    totalAssets.value = invRes.data.total_portfolio_balance || 0
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
    
    totalLiabilities.value = Object.values(latestPerLiability).reduce((sum, s) => sum + parseFloat(s.remaining_principal), 0)
  } catch (e) {
    console.error(e)
  }

  try {
    const cashRes = await api.get(`/banking/accounts/summary/?month=${month}&year=${year}`)
    totalLiquidAssets.value = parseFloat(cashRes.data.total_balance) || 0
  } catch (e) {
    console.error(e)
  }

  try {
    const res = await api.get(`/budgeting/transactions/summary/?month=${month}&year=${year}`)
    currentMonthIncome.value = res.data.total_income || 0
    currentMonthExpenses.value = res.data.total_expenses || 0
    currentMonthNetCashFlow.value = res.data.net_cash_flow || 0
  } catch(e) {
    console.error(e)
  }

  try {
    const [trendRes, snapRes] = await Promise.all([
      api.get(`/budgeting/transactions/trend/?start_date=${incomeExpenseStart.value}&end_date=${incomeExpenseEnd.value}`),
      api.get('/assets/snapshots/')
    ])
    
    trendData.value = trendRes.data
    rawSnapshots.value = snapRes.data
  } catch(e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const [assetsRes, bankingRes, txRes] = await Promise.all([
      api.get('/assets/snapshots/'),
      api.get('/banking/snapshots/'),
      api.get('/budgeting/transactions/')
    ])
    
    let latest = null
    
    if (assetsRes.data && assetsRes.data.length > 0) {
      latest = assetsRes.data.reduce((prev, current) => {
        if (current.year > prev.year) return current;
        if (current.year === prev.year && current.month > prev.month) return current;
        return prev;
      })
    }
    
    if (bankingRes.data && bankingRes.data.length > 0) {
      const latestBanking = bankingRes.data.reduce((prev, current) => {
        if (current.year > prev.year) return current;
        if (current.year === prev.year && current.month > prev.month) return current;
        return prev;
      })
      if (!latest || latestBanking.year > latest.year || (latestBanking.year === latest.year && latestBanking.month > latest.month)) {
        latest = latestBanking
      }
    }
    
    if (latest) {
      selectedMonth.value = latest.month
      selectedYear.value = latest.year

      // Asset and progress charts: end at latest snapshot date
      const latestStr = `${latest.year}-${String(latest.month).padStart(2, '0')}`
      assetsOverTimeEnd.value = latestStr
      assetProgressEnd.value = latestStr
    }
  } catch(e) {
    console.error(e)
  }

  await fetchOldestDataDate()
  await fetchData()
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
