<template>
  <div class="main-content">
    <!-- Header -->
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem; position: relative; z-index: 50;">
      <div>
        <h1 style="font-weight: 800; letter-spacing: -1px; font-size: 2.25rem; background: linear-gradient(135deg, #fff 0%, #a3b3cc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Financial Command Center</h1>
        <p class="text-muted">High-fidelity wealth analytics, asset allocation, liabilities, and liquid reserves snapshot.</p>
      </div>
      <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;">
        <SearchableSelect v-model="selectedPeriod" :options="trendOptions" @change="fetchData" placeholder="Select Period" style="width: 150px;" />
      </div>
    </header>

    <!-- AI Advisor -->
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

    <!-- Core Wealth & Net Worth Cards Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem;">
      
      <!-- Net Worth Card -->
      <div id="tour-net-worth" class="card" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(168, 85, 247, 0.15) 100%); border-color: rgba(99, 102, 241, 0.35); position: relative; z-index: 10;">
        <div style="position: absolute; inset: 0; overflow: hidden; border-radius: inherit; pointer-events: none; z-index: 0;">
          <div style="position: absolute; top: -20px; right: -20px; width: 100px; height: 100px; background: rgba(99, 102, 241, 0.2); filter: blur(40px); border-radius: 50%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; position: relative; z-index: 1;">
          <span style="color: rgba(255, 255, 255, 0.85); font-weight: 600; display: flex; align-items: center; gap: 0.25rem;">
            Estimated Net Worth
            <Tooltip title="Net Worth Status" description="Your total assets minus your liabilities. The core metric of your long-term wealth." example="Liquid + Invested Assets - Debts" />
          </span>
          <span v-if="!loading && assetsDelta" style="background: rgba(255, 255, 255, 0.15); color: #fff; padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.25);">
            {{ assetsDelta.isPositive ? '▲' : '▼' }} {{ assetsDelta.pct }}% MoM
          </span>
        </div>
        <template v-if="loading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0; background: rgba(255,255,255,0.15); position: relative; z-index: 1;"></div>
          <div class="skeleton skeleton-text" style="width: 45%; background: rgba(255,255,255,0.15); position: relative; z-index: 1;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2.25rem; font-weight: 800; color: #fff; letter-spacing: -1px; margin: 0.25rem 0; position: relative; z-index: 1;">{{ formatRM(netWorth) }}</div>
          <div style="color: rgba(255, 255, 255, 0.65); font-size: 0.8rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.35rem; position: relative; z-index: 1;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #a855f7; display: inline-block;"></span>
            Assets - Liabilities
          </div>
        </template>
      </div>

      <!-- Liquid Assets Card -->
      <div id="tour-liquid" class="card" style="border-color: rgba(16, 185, 129, 0.2); position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <span class="text-muted" style="font-weight: 500; display: flex; align-items: center; gap: 0.25rem;">
            Liquid Assets
            <Tooltip title="Liquid Capital" description="Immediately spendable cash and deposits in your checking/savings accounts." example="Checking account, physical cash" />
          </span>
          <span v-if="!loading" style="background: rgba(16, 185, 129, 0.12); color: var(--success); padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; border: 1px solid rgba(16, 185, 129, 0.2);">
            Runway: {{ emergencyRunway === null ? 'N/A' : (emergencyRunway >= 999 ? '999+' : emergencyRunway.toFixed(1)) }} Mos
          </span>
        </div>
        <template v-if="loading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 50%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2.25rem; font-weight: 800; color: var(--success); letter-spacing: -1px; margin: 0.25rem 0;">{{ formatRM(totalLiquidAssets) }}</div>
          <div class="text-muted" style="font-size: 0.8rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.35rem;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--success); display: inline-block;"></span>
            Checking, Savings & Cash
          </div>
        </template>
      </div>

      <!-- Invested Assets Card -->
      <div id="tour-invested" class="card" style="border-color: rgba(99, 102, 241, 0.2); position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <span class="text-muted" style="font-weight: 500; display: flex; align-items: center; gap: 0.25rem;">
            Invested Assets
            <Tooltip title="Invested Capital" description="Current market value of assets in growth platforms like stocks, bonds, properties, or crypto." example="Brokerage portfolio value" />
          </span>
          <span v-if="!loading" style="background: rgba(99, 102, 241, 0.12); color: #818cf8; padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; border: 1px solid rgba(99, 102, 241, 0.2);">
            {{ profitPercentage >= 0 ? '+' : '' }}{{ profitPercentage }}% ROI
          </span>
        </div>
        <template v-if="loading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 45%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2.25rem; font-weight: 800; color: #818cf8; letter-spacing: -1px; margin: 0.25rem 0;">{{ formatRM(totalAssets) }}</div>
          <div class="text-muted" style="font-size: 0.8rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.35rem;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #818cf8; display: inline-block;"></span>
            Stocks, Crypto & Holdings
          </div>
        </template>
      </div>

      <!-- Liabilities Card -->
      <div id="tour-liabilities" class="card" style="border-color: rgba(239, 68, 68, 0.2); position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <span class="text-muted" style="font-weight: 500; display: flex; align-items: center; gap: 0.25rem;">
            Total Liabilities
            <Tooltip title="Total Liabilities" description="All your outstanding financial obligations including home loans, car loans, and credit card balances." example="Mortgage + Credit Card debt" />
          </span>
          <span v-if="!loading && liabilitiesChange" :style="{
            background: liabilitiesChange.isPositive ? 'rgba(239, 68, 68, 0.12)' : 'rgba(16, 185, 129, 0.12)',
            color: liabilitiesChange.isPositive ? 'var(--danger)' : 'var(--success)',
            border: liabilitiesChange.isPositive ? '1px solid rgba(239, 68, 68, 0.2)' : '1px solid rgba(16, 185, 129, 0.2)'
          }" style="padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem;">
            {{ liabilitiesChange.isPositive ? '▲' : '▼' }} {{ liabilitiesChange.pct }}% MoM
          </span>
        </div>
        <template v-if="loading">
          <div class="skeleton skeleton-metric" style="margin: 0.5rem 0;"></div>
          <div class="skeleton skeleton-text" style="width: 40%;"></div>
        </template>
        <template v-else>
          <div style="font-size: 2.25rem; font-weight: 800; color: var(--danger); letter-spacing: -1px; margin: 0.25rem 0;">{{ formatRM(totalLiabilities) }}</div>
          <div class="text-muted" style="font-size: 0.8rem; margin-top: 0.5rem; display: flex; align-items: center; gap: 0.35rem;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--danger); display: inline-block;"></span>
            Loans, Cards & BNPL
          </div>
        </template>
      </div>

    </div>

    <!-- Health Indicators & Interactive Insights Section -->
    <div class="grid-2col" style="margin-bottom: 2rem; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
      
      <!-- Financial Health Diagnostics -->
      <div class="card" style="display: flex; flex-direction: column;">
        <h3 style="font-weight: 700; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
          <svg style="width: 20px; height: 20px; color: var(--accent-primary);" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
          Financial Health Diagnostics
        </h3>
        
        <div style="display: flex; flex-direction: column; gap: 1.25rem; flex: 1; justify-content: center;">
          
          <!-- Metric 1: Emergency Fund Runway -->
          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.9rem;">
              <span style="font-weight: 600; color: var(--text-primary);">Emergency Cash Runway</span>
              <span :class="emergencyRunway >= 6 ? 'text-success' : (emergencyRunway >= 3 ? 'text-warning' : 'text-danger')" style="font-weight: 700;">
                {{ emergencyRunway === null ? 'N/A' : emergencyRunway.toFixed(1) }} Months
              </span>
            </div>
            <div style="height: 8px; border-radius: 4px; background: rgba(255,255,255,0.05); overflow: hidden;">
              <div :style="{ 
                width: emergencyRunway === null ? '0%' : `${Math.min((emergencyRunway / 6) * 100, 100)}%`, 
                background: emergencyRunway >= 6 ? 'var(--success)' : (emergencyRunway >= 3 ? 'var(--warning)' : 'var(--danger)')
              }" style="height: 100%; transition: width 0.5s ease;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">
              <span>Target: 3-6 Mos</span>
              <span>{{ emergencyRunway >= 6 ? 'Optimal' : (emergencyRunway >= 3 ? 'Caution' : 'Underfunded') }}</span>
            </div>
          </div>

          <!-- Metric 2: Debt-to-Asset Ratio -->
          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.9rem;">
              <span style="font-weight: 600; color: var(--text-primary);">Debt-to-Asset Ratio</span>
              <span :class="debtToAssetRatio > 50 ? 'text-danger' : (debtToAssetRatio > 25 ? 'text-warning' : 'text-success')" style="font-weight: 700;">
                {{ debtToAssetRatio.toFixed(1) }}%
              </span>
            </div>
            <div style="height: 8px; border-radius: 4px; background: rgba(255,255,255,0.05); overflow: hidden;">
              <div :style="{ 
                width: `${Math.min(debtToAssetRatio, 100)}%`, 
                background: debtToAssetRatio > 50 ? 'var(--danger)' : (debtToAssetRatio > 25 ? 'var(--warning)' : 'var(--success)')
              }" style="height: 100%; transition: width 0.5s ease;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">
              <span>Lower is better</span>
              <span>Target: &lt; 40%</span>
            </div>
          </div>

          <!-- Metric 3: Savings Rate -->
          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.9rem;">
              <span style="font-weight: 600; color: var(--text-primary);">Monthly Savings Rate</span>
              <span :class="cashflowPercentage >= 20 ? 'text-success' : (cashflowPercentage >= 10 ? 'text-warning' : 'text-danger')" style="font-weight: 700;">
                {{ cashflowPercentage.toFixed(0) }}%
              </span>
            </div>
            <div style="height: 8px; border-radius: 4px; background: rgba(255,255,255,0.05); overflow: hidden;">
              <div :style="{ 
                width: `${cashflowPercentage}%`, 
                background: cashflowPercentage >= 20 ? 'var(--success)' : (cashflowPercentage >= 10 ? 'var(--warning)' : 'var(--danger)')
              }" style="height: 100%; transition: width 0.5s ease;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">
              <span>Target: &gt; 20%</span>
              <span>{{ cashflowPercentage.toFixed(0) }}% Savings</span>
            </div>
          </div>

        </div>
      </div>

      <!-- Personalized Wealth Insights Panel -->
      <div class="card" style="display: flex; flex-direction: column;">
        <h3 style="font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
          <svg style="width: 20px; height: 20px; color: var(--accent-primary);" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          Smart Wealth Insights
        </h3>
        
        <div style="flex: 1; overflow-y: auto; max-height: 250px; display: flex; flex-direction: column; gap: 0.75rem; padding-right: 0.5rem;">
          <div v-for="(insight, idx) in financialInsights" :key="idx" 
               style="padding: 0.85rem; border-radius: 8px; display: flex; gap: 0.75rem; border: 1px solid rgba(255,255,255,0.04);"
               :style="{
                 background: insight.type === 'success' ? 'rgba(0, 240, 153, 0.04)' : (insight.type === 'danger' ? 'rgba(255, 74, 107, 0.04)' : (insight.type === 'warning' ? 'rgba(255, 184, 0, 0.04)' : 'rgba(99, 102, 241, 0.04)')),
                 borderColor: insight.type === 'success' ? 'rgba(0, 240, 153, 0.15)' : (insight.type === 'danger' ? 'rgba(255, 74, 107, 0.15)' : (insight.type === 'warning' ? 'rgba(255, 184, 0, 0.15)' : 'rgba(99, 102, 241, 0.15)'))
               }">
            <div style="font-size: 1.1rem; line-height: 1;">
              <span v-if="insight.type === 'success'">✅</span>
              <span v-else-if="insight.type === 'danger'">🚨</span>
              <span v-else-if="insight.type === 'warning'">⚠️</span>
              <span v-else>💡</span>
            </div>
            <div>
              <div style="font-weight: 700; font-size: 0.875rem; color: #fff; margin-bottom: 0.15rem;">{{ insight.title }}</div>
              <div class="text-muted" style="font-size: 0.8rem; line-height: 1.4;">{{ insight.desc }}</div>
            </div>
          </div>
          <div v-if="financialInsights.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">
            No specific insights available for this period. Add assets, bank balances, and liabilities to see personalized advice.
          </div>
        </div>
      </div>

    </div>

    <!-- Detailed Snapshot Tabbed Panel -->
    <div class="card" style="margin-bottom: 2rem; padding: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem;">
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn" :class="activeDetailTab === 'assets' ? 'btn-primary' : 'btn-secondary'" @click="activeDetailTab = 'assets'" style="padding: 0.4rem 1rem; font-size: 0.875rem; border-radius: 6px;">
            Asset Allocations
          </button>
          <button class="btn" :class="activeDetailTab === 'liabilities' ? 'btn-primary' : 'btn-secondary'" @click="activeDetailTab = 'liabilities'" style="padding: 0.4rem 1rem; font-size: 0.875rem; border-radius: 6px;">
            Active Liabilities & Debts
          </button>
        </div>
        <div class="text-muted" style="font-size: 0.8rem;">Detailed snapshot for {{ monthsList[selectedMonth - 1] }} {{ selectedYear }}</div>
      </div>

      <!-- Assets Allocation Details -->
      <div v-if="activeDetailTab === 'assets'">
        <div class="grid-2col" style="grid-template-columns: 1.2fr 0.8fr; gap: 2rem; align-items: start;">
          <div>
            <h4 style="font-weight: 700; margin-bottom: 1rem; color: #fff;">Assets Breakdown</h4>
            <div v-if="byCategory.length === 0" class="text-muted" style="padding: 2rem 0; text-align: center;">No assets tracked. Link bank accounts or log asset snapshots.</div>
            <div v-else style="display: flex; flex-direction: column; gap: 1rem;">
              <div v-for="cat in byCategory" :key="cat.category" style="background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.03); border-radius: 8px; padding: 0.75rem 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; font-size: 0.875rem;">
                  <span style="font-weight: 600;">{{ cat.category }}</span>
                  <span style="font-weight: 700; color: var(--accent-primary);">{{ formatRM(cat.balance) }} ({{ ((cat.balance / (totalAssets + totalLiquidAssets)) * 100).toFixed(1) }}%)</span>
                </div>
                <div style="height: 6px; border-radius: 3px; background: rgba(255,255,255,0.04); overflow: hidden;">
                  <div :style="{ width: `${((cat.balance / (totalAssets + totalLiquidAssets)) * 100)}%` }" style="height: 100%; background: var(--accent-primary);"></div>
                </div>
              </div>
            </div>

            <!-- List Liquid Bank Accounts -->
            <h4 style="font-weight: 700; margin-top: 2rem; margin-bottom: 1rem; color: #fff;">Liquid Accounts</h4>
            <div v-if="liquidAccountsList.length === 0" class="text-muted" style="padding: 1rem 0; text-align: center;">No bank accounts logged.</div>
            <div v-else style="display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 0.75rem;">
              <div v-for="acc in liquidAccountsList" :key="acc.id" style="background: rgba(255,255,255,0.015); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem 1rem;">
                <div style="font-weight: 700; font-size: 0.85rem; color: #fff;">{{ acc.name }}</div>
                <div class="text-muted" style="font-size: 0.75rem; margin-bottom: 0.25rem;">{{ acc.institution || 'Cash' }} &bull; {{ acc.account_type_name }}</div>
                <div style="font-weight: 700; color: var(--success); font-size: 0.95rem;">{{ formatRM(acc.balance) }}</div>
              </div>
            </div>
          </div>
          <div>
            <h4 style="font-weight: 700; margin-bottom: 1rem; color: #fff; text-align: center;">Allocation Breakdown</h4>
            <div v-if="byCategory.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No chart data</div>
            <div v-else style="display: flex; justify-content: center; align-items: center; min-height: 220px;">
              <PieChart 
                :labels="byCategory.map(c => c.category)" 
                :data="byCategory.map(c => c.balance)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Liabilities / Debts Details -->
      <div v-else-if="activeDetailTab === 'liabilities'">
        <div style="display: flex; flex-direction: column; gap: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h4 style="font-weight: 700; margin: 0; color: #fff;">Outstanding Debts & Loans</h4>
            <span class="text-muted" style="font-size: 0.8rem;">Estimated Total: {{ formatRM(totalLiabilities) }}</span>
          </div>

          <div v-if="liabilitiesList.length === 0" class="text-muted" style="text-align: center; padding: 3rem 0;">
            No outstanding liabilities logged.
          </div>
          <div v-else class="table-container">
            <table class="data-table" style="width: 100%; border-collapse: collapse; text-align: left;">
              <thead>
                <tr style="border-bottom: 1px solid var(--border-color); color: var(--text-secondary); font-size: 0.85rem;">
                  <th style="padding: 0.75rem 1rem; font-weight: 600;">Lender / Description</th>
                  <th style="padding: 0.75rem 1rem; font-weight: 600;">Category</th>
                  <th style="padding: 0.75rem 1rem; font-weight: 600; text-align: right;">Interest Rate</th>
                  <th style="padding: 0.75rem 1rem; font-weight: 600; text-align: right;">Monthly Payment</th>
                  <th style="padding: 0.75rem 1rem; font-weight: 600; text-align: right;">Remaining Principal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="liab in liabilitiesList" :key="liab.id" style="border-bottom: 1px solid rgba(255,255,255,0.02); font-size: 0.85rem; color: var(--text-primary);">
                  <td style="padding: 0.75rem 1rem; font-weight: 700;">{{ liab.lender }}</td>
                  <td style="padding: 0.75rem 1rem;"><span style="background: rgba(239, 68, 68, 0.08); color: var(--danger); padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; border: 1px solid rgba(239, 68, 68, 0.15);">{{ liab.category_name }}</span></td>
                  <td style="padding: 0.75rem 1rem; text-align: right; font-weight: 600;">{{ liab.interest_rate.toFixed(2) }}%</td>
                  <td style="padding: 0.75rem 1rem; text-align: right; font-weight: 600; color: #fff;">{{ formatRM(liab.monthly_payment) }}</td>
                  <td style="padding: 0.75rem 1rem; text-align: right; font-weight: 700; color: var(--danger);">{{ formatRM(liab.remaining_principal) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Monthly Cash Flow summary -->
    <div class="card" style="margin-bottom: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <h3 style="font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
          <svg style="width: 20px; height: 20px; color: var(--accent-primary);" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Cash Flow Snapshot ({{ monthsList[selectedMonth - 1] }} {{ selectedYear }})
        </h3>
        <span v-if="!loading" :style="{
          background: cashflowPercentage >= 20 ? 'rgba(16, 185, 129, 0.12)' : 'rgba(245, 158, 11, 0.12)',
          color: cashflowPercentage >= 20 ? 'var(--success)' : 'var(--warning)',
          border: cashflowPercentage >= 20 ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid rgba(245, 158, 11, 0.2)'
        }" style="padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem;">
          Savings Rate: {{ cashflowPercentage.toFixed(0) }}%
        </span>
      </div>
      
      <div style="display: flex; flex-direction: column; gap: 1.25rem; padding: 1.25rem; background: rgba(255, 255, 255, 0.01); border: 1px solid var(--border-color); border-radius: 8px;">
        <div style="display: flex; justify-content: space-between; font-weight: 700; color: var(--success); align-items: center;">
          <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.95rem;">
            Total Income
            <Tooltip title="Total Income" description="The sum of all logged income transactions plus any recurring fixed income for the month." example="Salary + Freelance earnings" />
          </div>
          <span style="font-size: 1.2rem;">{{ formatRM(currentMonthIncome) }}</span>
        </div>
        
        <div style="display: flex; height: 12px; border-radius: 6px; overflow: hidden; background: rgba(255, 255, 255, 0.05);">
          <div :style="{ width: expensePercentage + '%', background: 'var(--danger)', transition: 'width 0.5s ease' }" title="Expenses"></div>
          <div :style="{ width: cashflowPercentage + '%', background: 'var(--accent-primary)', transition: 'width 0.5s ease' }" title="Savings"></div>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 0.875rem;">
          <div style="color: var(--danger);">
             <div style="font-weight: 600; display: flex; align-items: center; gap: 0.25rem;">
               Total Expenses
               <Tooltip title="Total Expenses" description="The sum of all logged expense transactions plus any recurring fixed costs for the month." example="Rent + Groceries + Subscriptions" />
             </div>
             <div style="font-weight: 700; font-size: 1.15rem; margin-top: 0.25rem; color: #fff;">{{ formatRM(currentMonthExpenses) }}</div>
          </div>
          <div style="color: var(--accent-primary); text-align: right;">
             <div style="font-weight: 600; display: flex; align-items: center; justify-content: flex-end; gap: 0.25rem;">
               Savings (Net Flow)
             </div>
             <div style="font-weight: 700; font-size: 1.15rem; margin-top: 0.25rem; color: #fff;">{{ formatRM(currentMonthNetCashFlow) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Trends Tabbed Interface -->
    <div class="card" style="margin-bottom: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn" :class="activeTrendTab === 'networth' ? 'btn-primary' : 'btn-secondary'" @click="activeTrendTab = 'networth'" style="padding: 0.4rem 1rem; font-size: 0.875rem; border-radius: 6px;">
            Net Worth Growth
          </button>
          <button class="btn" :class="activeTrendTab === 'cashflow' ? 'btn-primary' : 'btn-secondary'" @click="activeTrendTab = 'cashflow'" style="padding: 0.4rem 1rem; font-size: 0.875rem; border-radius: 6px;">
            Income vs Expenses
          </button>
          <button class="btn" :class="activeTrendTab === 'compound' ? 'btn-primary' : 'btn-secondary'" @click="activeTrendTab = 'compound'" style="padding: 0.4rem 1rem; font-size: 0.875rem; border-radius: 6px;">
            Asset Progress
          </button>
        </div>
        
        <!-- Period Selectors depending on active tab -->
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <template v-if="activeTrendTab === 'networth'">
            <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
              <SearchableSelect v-model="assetsOverTimeStart" :options="trendOptions" placeholder="Start Month" />
              <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
              <SearchableSelect v-model="assetsOverTimeEnd" :options="trendOptions" placeholder="End Month" />
            </div>
          </template>
          <template v-else-if="activeTrendTab === 'cashflow'">
            <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
              <SearchableSelect v-model="incomeExpenseStart" :options="trendOptions" @change="fetchData" placeholder="Start Month" />
              <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
              <SearchableSelect v-model="incomeExpenseEnd" :options="trendOptions" @change="fetchData" placeholder="End Month" />
            </div>
          </template>
          <template v-else-if="activeTrendTab === 'compound'">
            <div class="trend-select-wrapper" style="display: flex; align-items: center; gap: 0.25rem; background: rgba(255,255,255,0.05); padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
              <SearchableSelect v-model="assetProgressStart" :options="trendOptions" placeholder="Start Month" />
              <span style="color: #94A3B8; font-size: 0.8rem; margin: 0 0.1rem;">to</span>
              <SearchableSelect v-model="assetProgressEnd" :options="trendOptions" placeholder="End Month" />
            </div>
          </template>
        </div>
      </div>

      <!-- Tab Content Area -->
      <div style="height: 320px; position: relative;">
        <!-- Tab 1: Net Worth & Assets -->
        <div v-if="activeTrendTab === 'networth'" style="height: 100%;">
          <GraphLine v-if="assetsOverTimeData.length > 0" :labels="assetsOverTimeLabels" :datasets="assetDatasets" />
          <div v-else class="text-muted" style="text-align: center; padding: 4rem;">No historical asset data. Add monthly asset snapshots.</div>
        </div>

        <!-- Tab 2: Income vs Expenses -->
        <div v-else-if="activeTrendTab === 'cashflow'" style="height: 100%;">
          <BarChart v-if="trendLabels.length > 0" :labels="trendLabels" :datasets="trendDatasets" />
          <div v-else class="text-muted" style="text-align: center; padding: 4rem;">No income/expense records for this timeframe.</div>
        </div>

        <!-- Tab 3: Investment Progress -->
        <div v-else-if="activeTrendTab === 'compound'" style="height: 100%;">
          <GraphLine v-if="assetProgressData.length > 0" :labels="assetProgressLabels" :datasets="progressDatasets" />
          <div v-else class="text-muted" style="text-align: center; padding: 4rem;">No investment progress tracking available.</div>
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
import SearchableSelect from '@/components/SearchableSelect.vue'

const enableAI = import.meta.env.VITE_ENABLE_AI_ADVISOR === 'true'

const showOnboardingChecklist = ref(localStorage.getItem('dismissed_onboarding') !== 'true')
const dismissOnboarding = () => {
  showOnboardingChecklist.value = false
  localStorage.setItem('dismissed_onboarding', 'true')
}

// Tab States
const activeDetailTab = ref('assets')
const activeTrendTab = ref('networth')

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
const totalLoans = ref(0)
const totalCreditCards = ref(0)
const totalPayLater = ref(0)
const rawSnapshots = ref([])
const trendData = ref([])

const byCategory = ref([])
const byPlatform = ref([])
const liquidAccountsList = ref([])
const liabilitiesList = ref([])

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

const debtToAssetRatio = computed(() => {
  const totalAssetsVal = totalAssets.value + totalLiquidAssets.value
  if (totalAssetsVal <= 0) return 0
  return (totalLiabilities.value / totalAssetsVal) * 100
})

const expensePercentage = computed(() => {
  if (currentMonthIncome.value <= 0) return currentMonthExpenses.value > 0 ? 100 : 0;
  return Math.min((currentMonthExpenses.value / currentMonthIncome.value) * 100, 100);
})

const cashflowPercentage = computed(() => {
  if (currentMonthIncome.value <= 0) return 0;
  return Math.max(0, 100 - expensePercentage.value);
})

const assetsDelta = computed(() => {
  if (assetsOverTimeData.value.length < 2) return null;
  const data = assetsOverTimeData.value;
  const current = data[data.length - 1].totalBalance;
  const previous = data[data.length - 2].totalBalance;
  if (previous <= 0) return null;
  const pct = ((current - previous) / previous) * 100;
  return {
    pct: pct.toFixed(1),
    isPositive: pct >= 0,
    amount: current - previous
  };
})

const prevTotalLiabilities = ref(0)
const liabilitiesChange = computed(() => {
  if (!prevTotalLiabilities.value) return null;
  const current = totalLiabilities.value;
  const previous = prevTotalLiabilities.value;
  const pct = ((current - previous) / previous) * 100;
  const diff = current - previous;
  return {
    pct: pct.toFixed(1),
    isPositive: pct >= 0,
    diff: diff
  };
})

// Wealth insights engine based on metrics
const financialInsights = computed(() => {
  const insights = []
  
  if (netWorth.value > 100000) {
    insights.push({
      type: 'success',
      title: 'Wealth Milestone Achieved',
      desc: 'Congratulations! Your net worth is over RM100,000. You are in a strong wealth building phase.'
    })
  } else if (netWorth.value > 0) {
    insights.push({
      type: 'info',
      title: 'Positive Net Worth',
      desc: 'Great job keeping your net worth positive. Keep growing assets and paying down liabilities.'
    })
  } else if (netWorth.value < 0) {
    insights.push({
      type: 'danger',
      title: 'Negative Net Worth Warning',
      desc: 'Your liabilities currently exceed your assets. Focus on paying off high-interest credit cards and building a small liquid reserve.'
    })
  }

  const runway = emergencyRunway.value
  if (runway !== null) {
    if (runway >= 6) {
      insights.push({
        type: 'success',
        title: 'Excellent Cash Runway',
        desc: `Your liquid cash covers ${runway.toFixed(1)} months of expenses. You are well-protected against financial emergencies.`
      })
    } else if (runway >= 3) {
      insights.push({
        type: 'info',
        title: 'Solid Cash Runway',
        desc: `Your cash runway is ${runway.toFixed(1)} months. This is within the recommended 3-6 months range.`
      })
    } else {
      insights.push({
        type: 'warning',
        title: 'Low Emergency Fund',
        desc: `Your cash runway is only ${runway.toFixed(1)} months. Consider building up checking/savings accounts to cover at least 3 months of expenses.`
      })
    }
  }

  const ratio = debtToAssetRatio.value
  if (totalLiabilities.value > 0) {
    if (ratio > 50) {
      insights.push({
        type: 'danger',
        title: 'High Debt-to-Asset Ratio',
        desc: `Your debt represents ${ratio.toFixed(1)}% of your total assets. Avoid taking on new debt and focus on aggressive repayment.`
      })
    } else if (ratio > 25) {
      insights.push({
        type: 'warning',
        title: 'Moderate Debt Exposure',
        desc: `Your debt-to-asset ratio is ${ratio.toFixed(1)}%. Keep monitoring your liabilities to ensure they do not outgrow your assets.`
      })
    } else {
      insights.push({
        type: 'success',
        title: 'Healthy Debt Levels',
        desc: `Your debt is only ${ratio.toFixed(1)}% of your total assets, which is considered low risk and very healthy.`
      })
    }
  }

  const rate = cashflowPercentage.value
  if (currentMonthIncome.value > 0) {
    if (rate >= 30) {
      insights.push({
        type: 'success',
        title: 'Super Saver Status',
        desc: `You saved ${rate.toFixed(0)}% of your income this month. Excellent saving discipline!`
      })
    } else if (rate >= 15) {
      insights.push({
        type: 'info',
        title: 'Good Savings Rate',
        desc: `You saved ${rate.toFixed(0)}% of your income. Keep tracking targets to grow your surplus.`
      })
    } else {
      insights.push({
        type: 'warning',
        title: 'Low Savings Rate',
        desc: `Your savings rate is ${rate.toFixed(0)}% this month. Try auditing variable expenses or cancel unused subscriptions.`
      })
    }
  }

  return insights
})

const formatCurrency = (val) => {
  return Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatRM = (val) => {
  return (val < 0 ? '-' : '') + 'RM' + formatCurrency(Math.abs(val))
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
    byCategory.value = invRes.data.allocation_by_category || []
    byPlatform.value = invRes.data.allocation_by_platform || []
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

    let loansSum = 0
    let ccSum = 0
    let plSum = 0
    
    Object.values(latestPerLiability).forEach(s => {
      const categoryName = (s.category_name || '').toLowerCase()
      const principal = parseFloat(s.remaining_principal) || 0
      if (categoryName.includes('credit card')) {
        ccSum += principal
      } else if (categoryName.includes('pay later') || categoryName.includes('bnpl')) {
        plSum += principal
      } else {
        loansSum += principal
      }
    })
    
    totalLoans.value = loansSum
    totalCreditCards.value = ccSum
    totalPayLater.value = plSum
    totalLiabilities.value = loansSum + ccSum + plSum

    liabilitiesList.value = Object.values(latestPerLiability).map(s => ({
      id: s.id,
      category_name: s.category_name,
      lender: s.lender,
      remaining_principal: parseFloat(s.remaining_principal) || 0,
      interest_rate: parseFloat(s.interest_rate) || 0,
      monthly_payment: parseFloat(s.monthly_payment) || 0
    }))

    // Previous month total liabilities calculation
    let prevM = currentM - 1
    let prevY = currentY
    if (prevM === 0) {
      prevM = 12
      prevY -= 1
    }
    
    const prevPriorSnaps = liabRes.data.filter(s => {
       const snapY = Number(s.year)
       const snapM = Number(s.month)
       if (snapY < prevY) return true;
       if (snapY === prevY && snapM <= prevM) return true;
       return false;
    })
    
    const prevLatestPerLiability = {}
    prevPriorSnaps.forEach(s => {
      const key = `${s.category}_${s.lender}`
      if (!prevLatestPerLiability[key]) {
        prevLatestPerLiability[key] = s
      } else {
        const existing = prevLatestPerLiability[key]
        if (s.year > existing.year || (s.year === existing.year && s.month > existing.month)) {
          prevLatestPerLiability[key] = s
        }
      }
    })
    
    let prevLiabilitiesSum = 0
    Object.values(prevLatestPerLiability).forEach(s => {
      prevLiabilitiesSum += parseFloat(s.remaining_principal) || 0
    })
    prevTotalLiabilities.value = prevLiabilitiesSum
  } catch (e) {
    console.error(e)
  }

  try {
    const cashRes = await api.get(`/banking/accounts/summary/?month=${month}&year=${year}`)
    totalLiquidAssets.value = parseFloat(cashRes.data.total_balance) || 0
  } catch (e) {
    console.error(e)
  }

  // Fetch liquid accounts breakdown details
  try {
    const [accRes, snapRes] = await Promise.all([
      api.get('/banking/accounts/'),
      api.get('/banking/snapshots/')
    ])
    const activeAccs = accRes.data.filter(a => a.is_active)
    liquidAccountsList.value = activeAccs.map(acc => {
      const priorSnaps = snapRes.data.filter(s => {
        if (s.account !== acc.id) return false
        const sY = Number(s.year)
        const sM = Number(s.month)
        if (sY < year) return true
        if (sY === year && sM <= month) return true
        return false
      })
      
      let balance = 0
      if (priorSnaps.length > 0) {
        priorSnaps.sort((a, b) => {
          if (a.year !== b.year) return b.year - a.year
          return b.month - a.month
        })
        balance = parseFloat(priorSnaps[0].balance) || 0
      }
      return {
        id: acc.id,
        name: acc.name,
        institution: acc.institution,
        account_type_name: acc.account_type_name,
        balance
      }
    })
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
  width: 100px !important;
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
