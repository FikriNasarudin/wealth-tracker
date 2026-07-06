<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem;">
      <div>
        <h1 style="font-weight: 600;">Financial Calculators</h1>
        <p class="text-muted">Simulate investment returns, loan schedules, and planning for early retirement.</p>
      </div>
    </header>

    <div class="tabs-container">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'compound' }" 
        @click="activeTab = 'compound'"
      >
        📈 Compound Interest
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'loan' }" 
        @click="activeTab = 'loan'"
      >
        🏠 Loan & Mortgage
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'fire' }" 
        @click="activeTab = 'fire'"
      >
        🔥 FIRE Planner
      </button>
    </div>

    <!-- Compound Interest Calculator -->
    <div v-if="activeTab === 'compound'" class="calculator-grid">
      <div class="card">
        <h3 style="margin-bottom: 1.5rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
          <span>📈</span> Compound Interest Estimator
        </h3>
        
        <div class="form-group">
          <label class="form-label">Initial Deposit (RM)</label>
          <input v-model.number="compoundForm.initialDeposit" type="number" class="form-input" placeholder="e.g. 10000" />
        </div>
        
        <div class="form-group">
          <label class="form-label">Monthly Contribution (RM)</label>
          <input v-model.number="compoundForm.monthlyContribution" type="number" class="form-input" placeholder="e.g. 500" />
        </div>

        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Annual Interest Rate (%)</label>
            <input v-model.number="compoundForm.interestRate" type="number" step="0.1" class="form-input" placeholder="e.g. 6" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Duration (Years)</label>
            <input v-model.number="compoundForm.years" type="number" class="form-input" placeholder="e.g. 10" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Compound Frequency</label>
          <select v-model="compoundForm.frequency" class="form-input">
            <option value="12">Monthly</option>
            <option value="4">Quarterly</option>
            <option value="2">Semi-Annually</option>
            <option value="1">Annually</option>
          </select>
        </div>
      </div>

      <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <h3 style="margin-bottom: 1.5rem; font-weight: 600;">Results Projection</h3>
          
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            <div class="metric-card">
              <span class="text-muted" style="font-size: 0.8rem;">Total Balance</span>
              <h2 style="color: var(--accent-primary); margin: 0.25rem 0 0 0; font-weight: 700;">RM{{ formatNumber(compoundResult.totalBalance) }}</h2>
            </div>
            <div class="metric-card">
              <span class="text-muted" style="font-size: 0.8rem;">Total Principal</span>
              <h2 style="margin: 0.25rem 0 0 0; font-weight: 700;">RM{{ formatNumber(compoundResult.totalPrincipal) }}</h2>
            </div>
            <div class="metric-card">
              <span class="text-muted" style="font-size: 0.8rem;">Interest Earned</span>
              <h2 style="color: var(--accent-secondary); margin: 0.25rem 0 0 0; font-weight: 700;">RM{{ formatNumber(compoundResult.totalInterest) }}</h2>
            </div>
          </div>

          <!-- Schedule table -->
          <h4 style="margin-bottom: 0.75rem; font-weight: 600;">Year-by-Year Schedule</h4>
          <div style="overflow-x: auto; max-height: 250px;">
            <table class="schedule-table">
              <thead>
                <tr>
                  <th>Year</th>
                  <th style="text-align: right;">Principal</th>
                  <th style="text-align: right;">Total Interest</th>
                  <th style="text-align: right;">Balance</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in compoundResult.schedule" :key="row.year">
                  <td>Year {{ row.year }}</td>
                  <td style="text-align: right;">RM{{ formatNumber(row.principal) }}</td>
                  <td style="text-align: right; color: var(--accent-secondary);">RM{{ formatNumber(row.interest) }}</td>
                  <td style="text-align: right; color: var(--accent-primary); font-weight: 600;">RM{{ formatNumber(row.balance) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Loan / Mortgage Calculator -->
    <div v-if="activeTab === 'loan'" class="calculator-grid">
      <div class="card">
        <h3 style="margin-bottom: 1.5rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
          <span>🏠</span> Mortgage & Loan Repayment
        </h3>
        
        <div class="form-group">
          <label class="form-label">Loan Amount (RM)</label>
          <input v-model.number="loanForm.amount" type="number" class="form-input" placeholder="e.g. 350000" />
        </div>

        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Interest Rate (%)</label>
            <input v-model.number="loanForm.rate" type="number" step="0.05" class="form-input" placeholder="e.g. 4.2" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Term (Years)</label>
            <input v-model.number="loanForm.years" type="number" class="form-input" placeholder="e.g. 30" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Extra Monthly Payment (Optional)</label>
          <input v-model.number="loanForm.extraPayment" type="number" class="form-input" placeholder="e.g. 200" />
        </div>
      </div>

      <div class="card" style="display: flex; flex-direction: column;">
        <h3 style="margin-bottom: 1.5rem; font-weight: 600;">Loan Summary</h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
          <div class="metric-card">
            <span class="text-muted" style="font-size: 0.8rem;">Monthly Payment</span>
            <h2 style="color: var(--accent-primary); margin: 0.25rem 0 0 0; font-weight: 700;">RM{{ formatNumber(loanResult.monthlyRepayment) }}</h2>
          </div>
          <div class="metric-card" v-if="loanForm.extraPayment > 0">
            <span class="text-muted" style="font-size: 0.8rem;">Total Monthly (with Extra)</span>
            <h2 style="color: #60a5fa; margin: 0.25rem 0 0 0; font-weight: 700;">RM{{ formatNumber(loanResult.monthlyRepayment + loanForm.extraPayment) }}</h2>
          </div>
          <div class="metric-card">
            <span class="text-muted" style="font-size: 0.8rem;">Total Interest Paid</span>
            <h2 style="color: var(--danger); margin: 0.25rem 0 0 0; font-weight: 700;">RM{{ formatNumber(loanResult.totalInterest) }}</h2>
          </div>
          <div class="metric-card" v-if="loanForm.extraPayment > 0">
            <span class="text-muted" style="font-size: 0.8rem;">Years Saved</span>
            <h2 style="color: var(--accent-primary); margin: 0.25rem 0 0 0; font-weight: 700;">{{ formatNumber(loanResult.yearsSaved, 1) }} Years</h2>
          </div>
        </div>

        <h4 style="margin-bottom: 0.75rem; font-weight: 600;">Amortization Projection (First 12 Months)</h4>
        <div style="overflow-x: auto; max-height: 250px;">
          <table class="schedule-table">
            <thead>
              <tr>
                <th>Month</th>
                <th style="text-align: right;">Payment</th>
                <th style="text-align: right;">Principal</th>
                <th style="text-align: right;">Interest</th>
                <th style="text-align: right;">Remaining Balance</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in loanResult.schedule.slice(0, 12)" :key="row.month">
                <td>Month {{ row.month }}</td>
                <td style="text-align: right;">RM{{ formatNumber(row.payment) }}</td>
                <td style="text-align: right;">RM{{ formatNumber(row.principalPaid) }}</td>
                <td style="text-align: right; color: var(--danger);">RM{{ formatNumber(row.interestPaid) }}</td>
                <td style="text-align: right; color: var(--accent-primary); font-weight: 600;">RM{{ formatNumber(row.remaining) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- FIRE Calculator -->
    <div v-if="activeTab === 'fire'" class="calculator-grid">
      <div class="card">
        <h3 style="margin-bottom: 1.5rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
          <span>🔥</span> Financial Independence, Retire Early
        </h3>

        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Annual Expenses (RM)</label>
            <input v-model.number="fireForm.annualExpenses" type="number" class="form-input" placeholder="e.g. 48000" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Current Net Worth (RM)</label>
            <input v-model.number="fireForm.currentSavings" type="number" class="form-input" placeholder="e.g. 50000" />
          </div>
        </div>

        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Annual Savings contribution (RM)</label>
            <input v-model.number="fireForm.annualSavings" type="number" class="form-input" placeholder="e.g. 15000" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Expected Net Return (%)</label>
            <input v-model.number="fireForm.investmentReturn" type="number" step="0.5" class="form-input" placeholder="e.g. 7" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Safe Withdrawal Rate (%)</label>
          <input v-model.number="fireForm.swr" type="number" step="0.1" class="form-input" placeholder="e.g. 4" />
        </div>
      </div>

      <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <h3 style="margin-bottom: 1.5rem; font-weight: 600;">Your FIRE Path</h3>
          
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
            <div class="metric-card">
              <span class="text-muted" style="font-size: 0.8rem;">FIRE Number (Target)</span>
              <h2 style="color: var(--accent-primary); margin: 0.25rem 0 0 0; font-weight: 700;">RM{{ formatNumber(fireResult.fireNumber) }}</h2>
            </div>
            <div class="metric-card">
              <span class="text-muted" style="font-size: 0.8rem;">Estimated Years to FIRE</span>
              <h2 style="color: var(--accent-secondary); margin: 0.25rem 0 0 0; font-weight: 700;">{{ fireResult.yearsToFire }} Years</h2>
            </div>
          </div>

          <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: var(--border-radius-md); padding: 1.25rem; margin-bottom: 1.5rem;">
            <h4 style="margin-bottom: 0.5rem; font-weight: 600; color: #a5b4fc;">FIRE Insights</h4>
            <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-secondary);">
              Based on the <strong>{{ fireForm.swr }}% rule of thumb</strong>, once your net worth reaches <strong>RM{{ formatNumber(fireResult.fireNumber) }}</strong>, you will generate enough passive income to cover <strong>RM{{ formatNumber(fireForm.annualExpenses) }}</strong> in annual living expenses indefinitely.
            </p>
          </div>
          
          <div v-if="fireResult.schedule.length > 0" style="overflow-x: auto; max-height: 200px;">
            <table class="schedule-table">
              <thead>
                <tr>
                  <th>Year</th>
                  <th style="text-align: right;">Projected Net Worth</th>
                  <th style="text-align: right;">Progress to FIRE</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in fireResult.schedule" :key="row.year">
                  <td>Year {{ row.year }}</td>
                  <td style="text-align: right; font-weight: 500;">RM{{ formatNumber(row.balance) }}</td>
                  <td style="text-align: right;">
                    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 0.5rem;">
                      <div style="width: 60px; height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow:hidden;">
                        <div :style="{ width: Math.min(row.percent, 100) + '%', background: 'var(--accent-primary)', height: '100%' }"></div>
                      </div>
                      <span style="font-size: 0.8rem; width: 35px; text-align: right;">{{ Math.min(row.percent, 100) }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const activeTab = ref('compound')

// Form structures
const compoundForm = reactive({
  initialDeposit: 10000,
  monthlyContribution: 500,
  interestRate: 6,
  years: 15,
  frequency: '12' // Monthly
})

const loanForm = reactive({
  amount: 350000,
  rate: 4.2,
  years: 30,
  extraPayment: 0
})

const fireForm = reactive({
  annualExpenses: 48000,
  currentSavings: 50000,
  annualSavings: 15000,
  investmentReturn: 7,
  swr: 4
})

// Formatting helper
const formatNumber = (val, decimals = 0) => {
  if (val === null || val === undefined || isNaN(val)) return '0'
  return Number(val).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

// Compound calculations
const compoundResult = computed(() => {
  const p = compoundForm.initialDeposit || 0
  const PMT = compoundForm.monthlyContribution || 0
  const r = (compoundForm.interestRate || 0) / 100
  const t = compoundForm.years || 0
  const n = parseInt(compoundForm.frequency || '12')

  let totalPrincipal = p
  let schedule = []
  let currentBalance = p

  // Run calculation year by year
  for (let year = 1; year <= t; year++) {
    // Basic compound interest calculation per year
    // Over the course of the year:
    for (let month = 1; month <= 12; month++) {
      // Interest added monthly
      const monthlyRate = r / 12
      currentBalance = currentBalance * (1 + monthlyRate) + PMT
      totalPrincipal += PMT
    }
    
    const yearInterest = currentBalance - totalPrincipal
    schedule.push({
      year,
      principal: Math.round(totalPrincipal),
      interest: Math.round(yearInterest),
      balance: Math.round(currentBalance)
    })
  }

  return {
    totalBalance: Math.round(currentBalance),
    totalPrincipal: Math.round(totalPrincipal),
    totalInterest: Math.round(currentBalance - totalPrincipal),
    schedule
  }
})

// Loan / Mortgage calculations
const loanResult = computed(() => {
  const principal = loanForm.amount || 0
  const annualRate = (loanForm.rate || 0) / 100
  const totalMonths = (loanForm.years || 0) * 12
  const extra = loanForm.extraPayment || 0

  const monthlyRate = annualRate / 12
  
  // Calculate standard monthly payment
  let monthlyRepayment = 0
  if (monthlyRate === 0) {
    monthlyRepayment = principal / totalMonths
  } else {
    monthlyRepayment = (principal * monthlyRate * Math.pow(1 + monthlyRate, totalMonths)) / 
                       (Math.pow(1 + monthlyRate, totalMonths) - 1)
  }

  // Generate schedule with and without extra payments
  let balance = principal
  let standardBalance = principal
  let schedule = []
  let totalInterest = 0
  let totalStandardInterest = 0
  
  let month = 0
  let standardMonths = 0
  let actualMonths = 0

  // Run month-by-month projection
  while (balance > 0.01 && month < 600) {
    month++
    const interestPaid = balance * monthlyRate
    let principalPaid = (monthlyRepayment + extra) - interestPaid
    
    if (principalPaid > balance) {
      principalPaid = balance
    }
    
    balance -= principalPaid
    totalInterest += interestPaid

    schedule.push({
      month,
      payment: Math.round(interestPaid + principalPaid),
      interestPaid: Math.round(interestPaid),
      principalPaid: Math.round(principalPaid),
      remaining: Math.round(balance)
    })

    if (balance <= 0) {
      actualMonths = month
    }
  }

  // Calculate standard schedule for comparison (years saved)
  let stdBalance = principal
  let stdMonth = 0
  while (stdBalance > 0.01 && stdMonth < 600) {
    stdMonth++
    const stdInterestPaid = stdBalance * monthlyRate
    let stdPrincipalPaid = monthlyRepayment - stdInterestPaid
    if (stdPrincipalPaid > stdBalance) {
      stdPrincipalPaid = stdBalance
    }
    stdBalance -= stdPrincipalPaid
    totalStandardInterest += stdInterestPaid
    if (stdBalance <= 0) {
      standardMonths = stdMonth
    }
  }

  const monthsSaved = Math.max(0, standardMonths - actualMonths)
  const yearsSaved = monthsSaved / 12

  return {
    monthlyRepayment: Math.round(monthlyRepayment),
    totalInterest: Math.round(totalInterest),
    yearsSaved,
    schedule
  }
})

// FIRE calculations
const fireResult = computed(() => {
  const annualExp = fireForm.annualExpenses || 0
  const curSavings = fireForm.currentSavings || 0
  const annSavings = fireForm.annualSavings || 0
  const ret = (fireForm.investmentReturn || 0) / 100
  const swr = (fireForm.swr || 4) / 100

  // FIRE Number is Annual Expenses / SWR
  const fireNumber = swr > 0 ? annualExp / swr : 0

  let balance = curSavings
  let schedule = []
  let year = 0
  let targetMet = false

  if (fireNumber > 0) {
    while (balance < fireNumber && year < 50) {
      year++
      // Compound existing balance and add new savings
      balance = balance * (1 + ret) + annSavings
      const percent = Math.round((balance / fireNumber) * 100)
      schedule.push({
        year,
        balance: Math.round(balance),
        percent
      })
    }
  }

  return {
    fireNumber: Math.round(fireNumber),
    yearsToFire: balance >= fireNumber ? year : '50+',
    schedule
  }
})
</script>

<style scoped>
.calculator-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 1.5rem;
}

.tabs-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.25rem;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
}

.tabs-container::-webkit-scrollbar {
  display: none; /* Chrome/Safari/Webkit */
}

.tab-btn {
  background: none;
  border: none;
  padding: 0.75rem 1.5rem;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: var(--accent-primary);
  border-bottom-color: var(--accent-primary);
}

@media (max-width: 768px) {
  .tabs-container {
    gap: 0.25rem;
    margin-bottom: 1.5rem;
  }
  .tab-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.85rem;
  }
}

.metric-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: 1rem;
  text-align: left;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.schedule-table th, .schedule-table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.schedule-table th {
  color: var(--text-muted);
  font-weight: 600;
  text-align: left;
}

.schedule-table tr:hover {
  background: rgba(255, 255, 255, 0.01);
}

@media (max-width: 1024px) {
  .calculator-grid {
    grid-template-columns: 1fr;
  }
}
</style>
