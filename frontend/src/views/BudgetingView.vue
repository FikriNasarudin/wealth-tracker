<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem; position: relative; z-index: 50;">
      <div>
        <h1 style="font-weight: 600;">Budgeting Overview</h1>
        <p class="text-muted">Monitor your cash flow and expenses.</p>
      </div>
      <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; justify-content: flex-end;">
        <button class="btn btn-secondary" @click="startTour" style="padding: 0.5rem 1rem; font-size: 0.875rem; display: flex; align-items: center; gap: 0.25rem;">
          <svg style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Help
        </button>
        <SearchableSelect v-model="selectedPeriod" :options="trendOptions" @change="fetchData" placeholder="Select Period" style="width: 140px;" />
      </div>
    </header>

    <AIAdvisorCard v-if="enableAI" dashboardType="BUDGETING" :month="selectedMonth" :year="selectedYear" style="margin-bottom: 2rem;" />

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <!-- Income Card -->
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.75rem; font-weight: 500; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">Total Income</div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 50%;"></div>
        </template>
        <template v-else>
          <!-- Actual vs Target scorecard -->
          <div style="display: grid; grid-template-columns: 1fr 1px 1fr; gap: 0; margin-bottom: 0.75rem;">
            <div>
              <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Actual</div>
              <div style="font-size: 1.75rem; font-weight: 700; color: var(--success);">RM{{ formatCurrency(income) }}</div>
            </div>
            <div style="background: var(--border-color);"></div>
            <div style="padding-left: 1rem;">
              <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Target</div>
              <div style="font-size: 1.75rem; font-weight: 700;" :class="forecastIncome > 0 ? '' : 'text-muted'">
                {{ forecastIncome > 0 ? 'RM' + formatCurrency(forecastIncome) : '—' }}
              </div>
            </div>
          </div>
          <!-- Progress bar -->
          <div v-if="forecastIncome > 0">
            <div style="width: 100%; height: 6px; background: var(--bg-background); border-radius: 3px; overflow: hidden; margin-bottom: 0.4rem;">
              <div :style="{
                width: Math.min((income / forecastIncome) * 100, 100) + '%',
                height: '100%',
                background: income >= forecastIncome ? 'var(--success)' : 'var(--accent-primary)',
                transition: 'width 0.4s ease'
              }"></div>
            </div>
            <div class="text-muted" style="font-size: 0.78rem;">
              {{ Math.min((income / forecastIncome) * 100, 100).toFixed(0) }}% of target reached
            </div>
          </div>
          <div v-else class="text-muted" style="font-size: 0.8rem;">No income target set. Add a recurring income in <router-link to="/manage-recurring" style="color: var(--accent-primary);">Recurring Items</router-link>.</div>
        </template>
      </div>

      <!-- Expenses Card -->
      <div class="card">
        <div class="text-muted" style="margin-bottom: 0.75rem; font-weight: 500; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">Total Expenses</div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 45%;"></div>
        </template>
        <template v-else>
          <!-- Actual vs Budget scorecard -->
          <div style="display: grid; grid-template-columns: 1fr 1px 1fr; gap: 0; margin-bottom: 0.75rem;">
            <div>
              <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Actual</div>
              <div style="font-size: 1.75rem; font-weight: 700; color: var(--danger);">RM{{ formatCurrency(expenses) }}</div>
            </div>
            <div style="background: var(--border-color);"></div>
            <div style="padding-left: 1rem;">
              <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Budget</div>
              <div style="font-size: 1.75rem; font-weight: 700;" :class="forecastExpenses > 0 ? '' : 'text-muted'">
                {{ forecastExpenses > 0 ? 'RM' + formatCurrency(forecastExpenses) : '—' }}
              </div>
            </div>
          </div>
          <!-- Progress bar + remaining label -->
          <div v-if="forecastExpenses > 0">
            <div style="width: 100%; height: 6px; background: var(--bg-background); border-radius: 3px; overflow: hidden; margin-bottom: 0.4rem;">
              <div :style="{
                width: Math.min((expenses / forecastExpenses) * 100, 100) + '%',
                height: '100%',
                background: expenses > forecastExpenses ? 'var(--danger)' : (expenses > forecastExpenses * 0.8 ? 'var(--warning)' : 'var(--success)'),
                transition: 'width 0.4s ease'
              }"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="text-muted" style="font-size: 0.78rem;">{{ ((expenses / forecastExpenses) * 100).toFixed(0) }}% of budget used</span>
              <span style="font-size: 0.78rem;" :class="expenses > forecastExpenses ? 'text-danger' : 'text-success'">
                {{ expenses > forecastExpenses ? '⚠️ Over by RM' + formatCurrency(expenses - forecastExpenses) : 'RM' + formatCurrency(forecastExpenses - expenses) + ' remaining' }}
              </span>
            </div>
          </div>
          <div v-else>
            <div class="text-muted" style="font-size: 0.78rem; margin-bottom: 0.25rem;">Burn Rate: <strong>RM{{ formatCurrency(dailyBurnRate) }} / day</strong></div>
          </div>
        </template>
      </div>

      <!-- Net Cash Flow Card -->
      <div id="tour-cash-flow" class="card">
        <div class="text-muted" style="margin-bottom: 0.75rem; font-weight: 500; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">
          Net Cash Flow
          <Tooltip title="Net Cash Flow" description="Income minus Expenses for the selected month. A positive value means you earned more than you spent." example="RM5,000 Income − RM500 Expenses = RM4,500 Net Cash Flow" />
        </div>
        <template v-if="dataLoading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 40%;"></div>
        </template>
        <template v-else>
          <div style="display: grid; grid-template-columns: 1fr 1px 1fr; gap: 0; margin-bottom: 0.75rem;">
            <div>
              <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Actual</div>
              <div style="font-size: 1.75rem; font-weight: 700;" :class="netCashFlow >= 0 ? 'text-success' : 'text-danger'">RM{{ formatCurrency(netCashFlow) }}</div>
            </div>
            <div style="background: var(--border-color);"></div>
            <div style="padding-left: 1rem;">
              <!-- Only show Budget Surplus target when forecastIncome > 0 to avoid showing confusing negative numbers -->
              <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">Budget Surplus</div>
              <div style="font-size: 1.75rem; font-weight: 700;" :class="forecastIncome > 0 ? 'text-success' : 'text-muted'">
                {{ forecastIncome > 0 ? 'RM' + formatCurrency(forecastIncome - forecastExpenses) : '—' }}
              </div>
            </div>
          </div>
          <!-- Savings Rate badge -->
          <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 0.4rem;">
              <svg style="width: 14px; height: 14px;" :class="savingsRate >= 20 ? 'text-success' : (savingsRate >= 10 ? 'text-warning' : 'text-danger')" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              <span class="text-muted" style="font-size: 0.78rem;">Savings Rate: </span>
              <strong style="font-size: 0.78rem;" :class="savingsRate >= 20 ? 'text-success' : (savingsRate >= 10 ? 'text-warning' : 'text-danger')">{{ savingsRate.toFixed(1) }}%</strong>
            </div>
            <span style="font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 999px; font-weight: 600;"
              :style="savingsRate >= 20 ? 'background: rgba(16,185,129,0.15); color: var(--success)' : (savingsRate >= 10 ? 'background: rgba(245,158,11,0.15); color: var(--warning)' : 'background: rgba(239,68,68,0.15); color: var(--danger)')">
              {{ savingsRate >= 20 ? '✅ Healthy' : (savingsRate >= 10 ? '⚡ Moderate' : '⚠️ Low') }}
            </span>
          </div>
        </template>
      </div>
    </div>

    <div class="grid-2col" style="margin-bottom: 2rem;">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-weight: 600; margin: 0; display: flex; align-items: center; gap: 0.25rem;">
            Income vs Expense Trend
            <Tooltip title="Income vs Expense Trend" description="Tracks your total income and total expenses over the selected date range to visualize your cash flow history." example="Monthly earnings vs total cash outflows" />
          </h3>
          <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
            <SearchableSelect v-model="trendStart" :options="trendOptions" @change="fetchData" placeholder="Start Month" />
            <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
            <SearchableSelect v-model="trendEnd" :options="trendOptions" @change="fetchData" placeholder="End Month" />
          </div>
        </div>
        <div style="height: 300px;">
          <BarChart v-if="trendData.length > 0" :labels="trendLabels" :datasets="trendDatasets" />
        </div>
      </div>

      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Category Targets
            <Tooltip title="Category Targets" description="Compares your actual spending in each category against the monthly target limits you set." example="Rent target RM1,000 vs spent RM1,000" />
          </h3>
          <router-link to="/budgeting/targets" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Manage Targets</router-link>
        </div>
        
        <div style="margin-bottom: 1rem; display: flex; gap: 0.5rem; background: var(--bg-background); padding: 0.25rem; border-radius: 0.5rem; width: max-content;">
          <button class="btn" :class="activeTab === 'EXPENSE' ? 'btn-primary' : 'btn-secondary'" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="activeTab = 'EXPENSE'">Expenses</button>
          <button class="btn" :class="activeTab === 'INCOME' ? 'btn-primary' : 'btn-secondary'" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="activeTab = 'INCOME'">Income</button>
        </div>

        <div v-if="activeTab === 'EXPENSE'">
          <div v-if="enrichedExpenseBreakdown.length === 0" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💸</div>
            <div class="text-muted" style="font-size: 0.875rem;">No expenses logged yet this month. Use the <strong>Log Transaction</strong> button above to record your spending.</div>
          </div>
          <div v-else style="display: flex; flex-direction: column; gap: 1rem; max-height: 250px; overflow-y: auto; padding-right: 0.5rem;">
            <div v-for="item in enrichedExpenseBreakdown" :key="item.category_id || 'uncat'" style="display: flex; flex-direction: column; gap: 0.35rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500;">{{ item.category }} ({{ item.weight_percentage }}%)</span>
                <span class="text-muted" style="font-size: 0.875rem;">
                  RM{{ formatCurrency(item.amount) }}
                  <span v-if="item.budget_limit"> / RM{{ formatCurrency(item.budget_limit) }}</span>
                </span>
              </div>
              <div style="width: 100%; height: 8px; background: var(--bg-background); border-radius: 4px; overflow: hidden;">
                <div :style="{
                  width: item.budget_limit ? Math.min((item.amount / item.budget_limit) * 100, 100) + '%' : '100%',
                  height: '100%',
                  background: item.budget_limit ? (item.amount > item.budget_limit ? 'var(--danger)' : (item.amount > item.budget_limit * 0.8 ? 'var(--warning)' : 'var(--success)')) : 'var(--accent-primary)'
                }"></div>
              </div>
              <!-- Source badge: Default (from recurring) or no budget -->
              <div v-if="item.budgetSource === 'default'" style="font-size: 0.7rem; color: var(--text-muted);">🔁 Default limit from Recurring Items</div>
            </div>
          </div>
        </div>
        
        <div v-if="activeTab === 'INCOME'">
          <div v-if="incomeBreakdown.length === 0" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💰</div>
            <div class="text-muted" style="font-size: 0.875rem;">No income logged yet this month. Use the <strong>Log Transaction</strong> button above to record your income.</div>
          </div>
          <div v-else style="display: flex; flex-direction: column; gap: 1rem; max-height: 250px; overflow-y: auto; padding-right: 0.5rem;">
            <div v-for="item in incomeBreakdown" :key="item.category_id || 'uncat'" style="display: flex; flex-direction: column; gap: 0.5rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500;">{{ item.category }} ({{ item.weight_percentage }}%)</span>
                <span class="text-muted">RM{{ formatCurrency(item.amount) }} <span v-if="item.budget_limit">/ RM{{ formatCurrency(item.budget_limit) }}</span></span>
              </div>
              <div style="width: 100%; height: 8px; background: var(--bg-background); border-radius: 4px; overflow: hidden;">
                <div :style="{
                  width: item.budget_limit ? Math.min((item.amount / item.budget_limit) * 100, 100) + '%' : '100%',
                  height: '100%',
                  background: 'var(--success)'
                }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid-2col" style="margin-bottom: 2rem;">
      <div id="tour-categories" class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Recent Transactions
            <Tooltip title="Recent Transactions" description="List of your most recent transactions. Click on a transaction to edit or delete it." example="Starbucks coffee purchase, monthly salary deposit" />
          </h3>
          <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; align-items: center;">
            <button class="btn btn-secondary" style="padding: 0.35rem 0.7rem; font-size: 0.8rem;" @click="quickAdd('EXPENSE', 'Food')">🍕 Food</button>
            <button class="btn btn-secondary" style="padding: 0.35rem 0.7rem; font-size: 0.8rem;" @click="quickAdd('EXPENSE', 'Transport')">🚗 Transport</button>
            <button id="tour-add-txn" class="btn btn-primary" style="padding: 0.35rem 0.7rem; font-size: 0.8rem;" @click="showModal = true">+ Add Transaction</button>
          </div>
        </div>
        <div class="transaction-list-container" style="display: flex; flex-direction: column; gap: 0.75rem;">
          <div v-if="recentTransactions.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No recent transactions.</div>
          <div v-else v-for="txn in recentTransactions" :key="txn.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; background: rgba(255,255,255,0.015); border-radius: var(--border-radius-sm); border: 1px solid var(--border-color); transition: background var(--transition-fast);">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <div :style="{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: txn.type === 'INCOME' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                color: txn.type === 'INCOME' ? 'var(--success)' : 'var(--danger)',
                fontWeight: '600'
              }">
                {{ txn.type === 'INCOME' ? '↑' : '↓' }}
              </div>
              <div style="display: flex; flex-direction: column;">
                <span style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary);">{{ txn.name }}</span>
                <span style="font-size: 0.75rem; color: var(--text-muted);">{{ txn.category_name || 'Uncategorized' }} • {{ txn.date }}</span>
              </div>
            </div>
            <div :class="txn.type === 'INCOME' ? 'text-success' : 'text-danger'" style="font-weight: 700; font-size: 1rem;">
              {{ txn.type === 'INCOME' ? '+' : '-' }}RM{{ formatCurrency(txn.amount) }}
            </div>
          </div>
        </div>
      </div>

      <div id="tour-subscriptions" class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Fixed Income & Costs
            <Tooltip title="Recurring Items" description="Fixed income like salary, and fixed costs like Netflix, that happen automatically every month." example="Salary, Gym Membership" />
          </h3>
          <router-link to="/budgeting/recurring" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Manage Items</router-link>
        </div>
        <div v-if="activeUnloggedSubscriptions.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No pending recurring items this month.</div>
        <div v-else>
          <div class="subscription-list-container" style="display: flex; flex-direction: column; gap: 0.75rem;">
          <div v-if="activeUnloggedSubscriptions.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No pending recurring items this month.</div>
          <div v-else v-for="sub in activeUnloggedSubscriptions" :key="sub.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; background: rgba(255,255,255,0.015); border-radius: var(--border-radius-sm); border: 1px solid var(--border-color); transition: background var(--transition-fast);" :style="sub.isInactive ? 'opacity: 0.5;' : ''">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <div :style="{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: sub.type === 'INCOME' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                color: sub.type === 'INCOME' ? 'var(--success)' : 'var(--danger)',
                fontWeight: '600'
              }">
                {{ sub.type === 'INCOME' ? '↑' : '↓' }}
              </div>
              <div style="display: flex; flex-direction: column;">
                <span style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary);">
                  {{ sub.name }}
                  <span v-if="sub.isLogged" style="font-size: 0.7rem; padding: 0.15rem 0.35rem; background: rgba(16,185,129,0.12); color: var(--success); border-radius: 4px; margin-left: 0.5rem; font-weight: 600;">
                    ✓ {{ sub.type === 'INCOME' ? 'Received' : 'Paid' }}
                  </span>
                  <span v-else-if="sub.isInactive" style="font-size: 0.7rem; padding: 0.15rem 0.35rem; background: var(--border-color); color: var(--text-muted); border-radius: 4px; margin-left: 0.5rem; font-weight: 500;">
                    Passed
                  </span>
                </span>
                <span style="font-size: 0.75rem; color: var(--text-muted);">
                  <template v-if="sub.auto_log_day">
                    {{ sub.type === 'INCOME' ? 'Auto credit' : 'Auto debit' }} on {{ getOrdinalSuffix(sub.auto_log_day) }}
                  </template>
                  <template v-else>Manual</template>
                </span>
              </div>
            </div>
            <div :class="sub.type === 'INCOME' ? 'text-success' : 'text-danger'" style="font-weight: 700; font-size: 1.05rem; text-align: right;">
              <div>{{ sub.type === 'INCOME' ? '+' : '-' }}RM{{ formatCurrency(sub.amount) }}</div>
              <div style="font-size: 0.7rem; font-weight: 500; color: var(--text-muted); margin-top: 0.15rem;">/ {{ sub.billing_cycle === 'MONTHLY' ? 'mo' : 'yr' }}</div>
            </div>
          </div>
        </div>
          
          <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color); display: flex; justify-content: space-between; font-weight: 600;">
            <span>Monthly Equivalent:</span>
            <span>
              <span class="text-success" v-if="monthlyFixedIncome > 0">+RM{{ formatCurrency(monthlyFixedIncome) }}</span>
              <span style="margin: 0 0.5rem;" v-if="monthlyFixedIncome > 0 && monthlyFixedCosts > 0">|</span>
              <span class="text-danger" v-if="monthlyFixedCosts > 0">-RM{{ formatCurrency(monthlyFixedCosts) }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem;">
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">
          Debit Account Breakdown (Recurring Expenses)
          <Tooltip title="Debit Account Breakdown" description="Visualizes which bank accounts are used to pay for your active recurring items." example="Shows auto-debits linked to your savings account vs credit cards" />
        </h3>
        <div v-if="debitAccountBreakdown.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">
          No recurring expenses configured with debit accounts.
        </div>
        <div v-else>
        <div class="debit-breakdown-list" style="display: flex; flex-direction: column; gap: 1rem;">
          <div v-if="debitAccountBreakdown.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">
            No recurring expenses configured with debit accounts.
          </div>
          <div v-else v-for="item in debitAccountBreakdown" :key="item.name" style="display: flex; flex-direction: column; gap: 0.5rem; padding: 1rem; background: rgba(255,255,255,0.015); border-radius: var(--border-radius-sm); border: 1px solid var(--border-color);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary);">{{ item.name }}</span>
              <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">-RM{{ formatCurrency(item.amount) }}</span>
                <span style="font-size: 0.85rem; font-weight: 700; color: var(--accent-primary);">{{ item.percentage.toFixed(1) }}%</span>
              </div>
            </div>
            <div style="width: 100%; height: 6px; background: var(--bg-primary); border-radius: 3px; overflow: hidden;">
              <div :style="{
                width: item.percentage + '%',
                height: '100%',
                background: 'var(--accent-primary)'
              }"></div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Modal :show="showModal" title="Add Transaction" @close="showModal = false">
      <form @submit.prevent="submitTransaction">
        <div class="form-group">
          <label class="form-label">Type</label>
          <select v-model="form.type" class="form-input" @change="fetchCategories">
            <option value="INCOME">Income</option>
            <option value="EXPENSE">Expense</option>
          </select>
        </div>
        
        <div class="form-group">
          <label class="form-label">Category</label>
          <div style="display: flex; gap: 0.5rem;">
            <SearchableSelect 
              v-if="!isNewCategory" 
              v-model="form.categoryId" 
              :options="categoryOptions" 
              placeholder="Search category..." 
              style="flex: 1;"
            />
            <input v-else v-model="form.newCategoryName" type="text" class="form-input" placeholder="New Category Name" />
            <button type="button" class="btn btn-secondary" @click="isNewCategory = !isNewCategory">
              {{ isNewCategory ? 'Cancel' : 'New' }}
            </button>
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">Item Name</label>
          <input v-model="form.name" type="text" class="form-input" placeholder="e.g. Groceries or Salary" required />
          
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;" v-if="targets && targets.length > 0">
            <button v-for="t in targets.filter(t => t.type === form.type && t.name)" :key="t.id" 
                    type="button" class="btn" 
                    :class="form.name.toLowerCase() === t.name.toLowerCase() ? 'btn-primary' : 'btn-secondary'"
                    @click="form.name = t.name" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">
              {{ t.name }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Amount</label>
          <input v-model="form.amount" type="number" step="0.01" class="form-input" required />
        </div>

        <div class="form-group">
          <label class="form-label">Date</label>
          <input v-model="form.date" type="date" class="form-input" required />
        </div>

        <div class="form-group" v-if="form.type === 'EXPENSE'">
          <label class="form-label">Payment Method / Account</label>
          <SearchableSelect 
            v-model="form.paymentAccount" 
            :options="paymentAccountOptions" 
            placeholder="Search payment account..."
          />
        </div>

        <div class="form-group">
          <label class="form-label">Description (Optional notes)</label>
          <input v-model="form.description" type="text" class="form-input" />
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Transaction' }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import BarChart from '@/components/BarChart.vue'
import Tooltip from '@/components/Tooltip.vue'
import AIAdvisorCard from '@/components/AIAdvisorCard.vue'
import { driver } from 'driver.js'
import SearchableSelect from '@/components/SearchableSelect.vue'

const enableAI = import.meta.env.VITE_ENABLE_AI_ADVISOR === 'true'

const startTour = () => {
  const driverObj = driver({
    showProgress: true,
    steps: [
      { element: '#tour-cash-flow', popover: { title: 'Net Cash Flow', description: 'This tracks whether you are earning more than you spend. It calculates all your logged transactions as well as your unlogged fixed income and costs.' } },
      { element: '#tour-categories', popover: { title: 'Recent Transactions', description: 'A quick overview of your latest spending. You can manage detailed targets and limits above.' } },
      { element: '#tour-subscriptions', popover: { title: 'Fixed Income & Costs', description: 'Add your recurring fixed income (e.g. salary) and costs (e.g. Netflix) here. They will automatically be factored into your disposable income calculation.' } },
      { element: '#tour-add-txn', popover: { title: 'Add Transaction', description: 'Click here to log a new income or expense. Use the quick add buttons for fast entry!' } }
    ]
  });
  driverObj.drive();
}

const income = ref(0)
const expenses = ref(0)
const forecastIncome = ref(0)
const forecastExpenses = ref(0)
const netCashFlow = ref(0)
const expenseBreakdown = ref([])
const incomeBreakdown = ref([])
const recentTransactions = ref([])
const trendData = ref([])
const activeTab = ref('EXPENSE')

const monthlyFixedCosts = computed(() => {
  return activeUnloggedSubscriptions.value
    .filter(s => s.type === 'EXPENSE')
    .reduce((sum, s) => {
      const amt = parseFloat(s.amount)
      return sum + (s.billing_cycle === 'MONTHLY' ? amt : amt / 12)
    }, 0)
})
const monthlyFixedIncome = computed(() => {
  return activeUnloggedSubscriptions.value
    .filter(s => s.type === 'INCOME')
    .reduce((sum, s) => {
      const amt = parseFloat(s.amount)
      return sum + (s.billing_cycle === 'MONTHLY' ? amt : amt / 12)
    }, 0)
})
const loggedSubscriptionIds = ref([])
const subscriptions = ref([])
const targets = ref([])
const categories = ref([])
const creditCards = ref([])
const isNewCategory = ref(false)

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

const trendStart = ref(`${currentYear}-01`)
const trendEnd = ref(`${currentYear}-${String(d.getMonth() + 1).padStart(2, '0')}`)
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
    const res = await api.get('/budgeting/transactions/')
    let oldestY = null
    let oldestM = null
    
    if (res.data && res.data.length > 0) {
      res.data.forEach(item => {
        if (item.date) {
          const parts = item.date.split('-')
          const itemY = Number(parts[0])
          const itemM = Number(parts[1])
          if (!oldestY || itemY < oldestY || (itemY === oldestY && itemM < oldestM)) {
            oldestY = itemY
            oldestM = itemM
          }
        }
      })
    }
    
    generateTrendOptions(oldestY, oldestM)
  } catch(e) {
    console.error(e)
    generateTrendOptions()
  }
}

const monthsList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const yearsList = computed(() => {
  const current = new Date().getFullYear()
  const years = []
  for (let y = current - 5; y <= current + 5; y++) {
    years.push(y)
  }
  return years
})

const showModal = ref(false)
const loading = ref(false)

const getInitialForm = () => ({
  type: 'EXPENSE',
  categoryId: null,
  newCategoryName: '',
  name: '',
  amount: '',
  date: new Date().toISOString().split('T')[0],
  description: '',
  paymentAccount: ''
})

const form = ref(getInitialForm())

const categoryOptions = computed(() => {
  return [
    { value: null, label: 'Uncategorized' },
    ...categories.value.map(c => ({ value: c.id, label: c.name }))
  ]
})

const paymentAccountOptions = computed(() => {
  return [
    { value: '', label: 'Cash / Default Account' },
    ...creditCards.value.map(cc => ({ value: cc.name, label: `${cc.name} (Credit Card)` }))
  ]
})

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const getOrdinalSuffix = (day) => {
  if (day >= 11 && day <= 13) {
    return `${day}th`;
  }
  switch (day % 10) {
    case 1: return `${day}st`;
    case 2: return `${day}nd`;
    case 3: return `${day}rd`;
    default: return `${day}th`;
  }
}

const activeUnloggedSubscriptions = computed(() => {
  const currentMonthKey = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}`
  
  // Filter active (non-archived, non-paused) subscriptions
  const list = subscriptions.value.filter(s => {
    const isArchived = s.status === 'ARCHIVED'
    const isPaused = s.paused_months && s.paused_months.includes(currentMonthKey)
    return !isArchived && !isPaused
  })
  
  // Map with inactive / logged status
  const mapped = list.map(s => {
    const isLogged = loggedSubscriptionIds.value.includes(s.id)
    let isPassed = false
    
    if (s.auto_log_day) {
      const today = new Date();
      const currentYear = today.getFullYear();
      const currentMonth = today.getMonth() + 1;
      const currentDay = today.getDate();
      
      if (selectedYear.value < currentYear) {
        isPassed = true;
      } else if (selectedYear.value === currentYear) {
        if (selectedMonth.value < currentMonth) {
          isPassed = true;
        } else if (selectedMonth.value === currentMonth) {
          isPassed = s.auto_log_day < currentDay;
        }
      }
    }
    
    return {
      ...s,
      isInactive: isLogged || isPassed,
      isLogged
    }
  })
  
  // Sort: active (upcoming) first, then inactive (passed). Within each group, sort by auto_log_day ascending (nulls at the end)
  mapped.sort((a, b) => {
    if (a.isInactive !== b.isInactive) {
      return a.isInactive ? 1 : -1;
    }
    const dayA = a.auto_log_day === null || a.auto_log_day === undefined ? 999 : a.auto_log_day;
    const dayB = b.auto_log_day === null || b.auto_log_day === undefined ? 999 : b.auto_log_day;
    return dayA - dayB;
  })
  
  return mapped
})

const savingsRate = computed(() => {
  if (income.value <= 0) return 0;
  return (netCashFlow.value / income.value) * 100;
})

// Per-category monthly recurring total (for Default budget fallback)
const recurringByCategoryId = computed(() => {
  const map = {}
  subscriptions.value
    .filter(s => s.status === 'ACTIVE' && s.type === 'EXPENSE')
    .forEach(s => {
      if (!s.category) return
      const monthly = s.billing_cycle === 'MONTHLY' ? parseFloat(s.amount) : parseFloat(s.amount) / 12
      map[s.category] = (map[s.category] || 0) + monthly
    })
  return map
})

// Expense breakdown enriched with Default budget_limit from recurring when no explicit target
const enrichedExpenseBreakdown = computed(() => {
  return expenseBreakdown.value.map(item => ({
    ...item,
    budgetSource: item.budget_source || (item.budget_limit ? 'custom' : null)
  }))
})

const debitAccountBreakdown = computed(() => {
  const activeExpenses = subscriptions.value.filter(s => s.status === 'ACTIVE' && s.type === 'EXPENSE')
  
  const breakdown = {}
  let total = 0
  
  activeExpenses.forEach(s => {
    const amt = parseFloat(s.amount)
    const monthlyEquivalent = s.billing_cycle === 'MONTHLY' ? amt : amt / 12
    const accountName = s.payment_account || 'None (Cash/Other)'
    
    if (!breakdown[accountName]) {
      breakdown[accountName] = 0
    }
    breakdown[accountName] += monthlyEquivalent
    total += monthlyEquivalent
  })
  
  return Object.keys(breakdown).map(name => ({
    name,
    amount: breakdown[name],
    percentage: total > 0 ? (breakdown[name] / total) * 100 : 0
  })).sort((a, b) => b.amount - a.amount)
})

const dailyBurnRate = computed(() => {
  if (expenses.value <= 0) return 0;
  const currentRealMonth = d.getMonth() + 1;
  const currentRealYear = d.getFullYear();
  let days = 1;
  
  if (selectedYear.value === currentRealYear && selectedMonth.value === currentRealMonth) {
    days = Math.max(d.getDate(), 1);
  } else {
    days = new Date(selectedYear.value, selectedMonth.value, 0).getDate();
  }
  return expenses.value / days;
})

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

const dataLoading = ref(true)

const fetchData = async () => {
  dataLoading.value = true
  try {
    const res = await api.get(`/budgeting/transactions/summary/?month=${selectedMonth.value}&year=${selectedYear.value}`)
    income.value = res.data.total_income
    expenses.value = res.data.total_expenses
    forecastIncome.value = res.data.forecast_income || 0
    forecastExpenses.value = res.data.forecast_expenses || 0
    netCashFlow.value = res.data.net_cash_flow
    expenseBreakdown.value = res.data.expense_breakdown
    incomeBreakdown.value = res.data.income_breakdown || []
    recentTransactions.value = res.data.recent_transactions || []
    loggedSubscriptionIds.value = res.data.logged_subscription_ids || []
    targets.value = res.data.targets || []
  } catch (e) {
    console.error(e)
  }
  
  try {
    const trendRes = await api.get(`/budgeting/transactions/trend/?start_date=${trendStart.value}&end_date=${trendEnd.value}`)
    trendData.value = trendRes.data
  } catch(e) {
    console.error(e)
  } finally {
    dataLoading.value = false
  }
}

const fetchSubscriptions = async () => {
  try {
    const res = await api.get('/budgeting/subscriptions/')
    subscriptions.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/budgeting/categories/')
    categories.value = res.data.filter(c => c.type === form.value.type)
  } catch (e) {
    console.error(e)
  }
}

const fetchCreditCards = async () => {
  try {
    const res = await api.get('/liabilities/lenders/')
    const catRes = await api.get('/liabilities/categories/')
    const ccCat = catRes.data.find(c => c.name.toLowerCase() === 'credit cards')
    if (ccCat) {
      creditCards.value = res.data.filter(l => l.category === ccCat.id && l.is_active)
    } else {
      creditCards.value = []
    }
  } catch (e) {
    console.error("Failed to fetch credit cards", e)
  }
}

const quickAdd = (type, categoryName) => {
  form.value = getInitialForm()
  form.value.type = type
  fetchCategories().then(() => {
    const cat = categories.value.find(c => c.name.toLowerCase() === categoryName.toLowerCase())
    if (cat) {
      form.value.categoryId = cat.id
      isNewCategory.value = false
    } else {
      isNewCategory.value = true
      form.value.newCategoryName = categoryName
    }
    showModal.value = true
  })
}

const submitTransaction = async () => {
  loading.value = true
  try {
    let categoryId = form.value.categoryId

    if (isNewCategory.value && form.value.newCategoryName) {
      const catRes = await api.post('/budgeting/categories/', {
        name: form.value.newCategoryName,
        type: form.value.type
      })
      categoryId = catRes.data.id
    }

    const payload = {
      category: categoryId,
      name: form.value.name,
      type: form.value.type,
      amount: form.value.amount,
      date: form.value.date,
      description: form.value.description
    }

    if (form.value.paymentAccount) {
      payload.payment_account = form.value.paymentAccount
    }

    await api.post('/budgeting/transactions/', payload)

    showModal.value = false
    isNewCategory.value = false
    
    // Automatically switch the view to the month/year of the newly added transaction
    const dateParts = form.value.date.split('-')
    if (dateParts.length >= 2) {
      selectedYear.value = parseInt(dateParts[0])
      selectedMonth.value = parseInt(dateParts[1])
    }
    
    form.value = getInitialForm()
    
    await fetchData()
    await fetchCategories()
  } catch (e) {
    console.error(e)
    alert('Failed to save transaction')
  } finally {
    loading.value = false
  }
}

// No pagination required for Overview Dashboard

onMounted(async () => {
  try {
    const res = await api.get('/budgeting/transactions/')
    if (res.data && res.data.length > 0) {
      const latest = res.data.reduce((prev, current) => {
        const prevDate = new Date(prev.date)
        const currDate = new Date(current.date)
        return currDate > prevDate ? current : prev
      })
      const d = new Date(latest.date)
      selectedMonth.value = d.getMonth() + 1
      selectedYear.value = d.getFullYear()
    }
  } catch(e) {
    console.error(e)
  }

  await fetchOldestDataDate()
  await fetchData()
  await fetchCategories()
  await fetchSubscriptions()
  await fetchCreditCards()
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
