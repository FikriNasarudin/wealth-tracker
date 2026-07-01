<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem;">
      <div>
        <h1 style="font-weight: 600;">Banking & Liquid Assets</h1>
        <p class="text-muted">Manage your cash, checking, and savings accounts.</p>
      </div>
      <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
        <button class="btn btn-secondary" @click="startTour" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
          <svg style="width: 16px; height: 16px; display: inline; vertical-align: middle; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Help
        </button>
      </div>
    </header>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div id="tour-liquid-total" class="card" style="background: linear-gradient(135deg, var(--primary) 0%, #1e40af 100%); color: white;">
        <div style="margin-bottom: 0.5rem; font-weight: 500; opacity: 0.9;">
          Total Liquid Assets
          <Tooltip title="Total Liquid Assets" description="The total available balance across all your cash, savings, and checking accounts." example="Checking + Savings = RM15,000" />
        </div>
        <div style="font-size: 2.5rem; font-weight: 700;">RM{{ formatCurrency(totalLiquidity) }}</div>
      </div>
    </div>

    <div id="tour-accounts-list" class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
        <h3 style="font-weight: 600; margin: 0;">
          Your Accounts
          <Tooltip title="Your Accounts" description="Keep track of individual balances. Click 'Update Balance' at the end of every month to log a new snapshot." example="Maybank Savings: RM10,000" />
        </h3>
        <button id="tour-add-account" class="btn btn-primary" @click="showAddAccountModal = true" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;">+ Add Account</button>
      </div>
      <div v-if="activeAccounts.length === 0" style="text-align: center; padding: 3rem 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🏦</div>
        <h4 style="font-weight: 600; margin-bottom: 0.5rem;">No bank accounts yet</h4>
        <p class="text-muted" style="font-size: 0.9rem; margin-bottom: 1.25rem; max-width: 380px; margin-left: auto; margin-right: auto;">Add your cash, savings, or checking accounts to track your total liquid assets and emergency fund runway.</p>
        <button class="btn btn-primary" @click="showAddAccountModal = true" style="padding: 0.6rem 1.5rem;">+ Add Your First Account</button>
      </div>
      <div v-else style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
        <div v-for="acc in activeAccounts" :key="acc.id" style="border: 1px solid var(--border-color); border-radius: 0.5rem; padding: 1.5rem; position: relative;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div>
              <div style="font-weight: 600; font-size: 1.125rem;">{{ acc.name }}</div>
              <div class="text-muted" style="font-size: 0.875rem;">{{ acc.institution || 'Cash' }} &bull; {{ acc.type }}</div>
            </div>
            <div style="display: flex; gap: 0.25rem; align-items: center;">
              <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" @click="openUpdateModal(acc)" title="Update Balance">Update Balance</button>
              <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; color: var(--text-secondary); display: inline-flex;" @click="archiveAccount(acc)" title="Archive Account">
                <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" /></svg>
              </button>
              <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; display: inline-flex;" @click="deleteAccount(acc)" title="Delete Account">
                <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
            </div>
          </div>
          
          <div style="font-size: 1.5rem; font-weight: 700;" :class="getLatestBalance(acc.id) >= 0 ? 'text-success' : 'text-danger'">
            RM{{ formatCurrency(getLatestBalance(acc.id)) }}
          </div>
          <div class="text-muted" style="font-size: 0.75rem; margin-top: 0.25rem;">
            Last updated: {{ getLastUpdatedText(acc.id) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Archived Accounts Section -->
    <div v-if="archivedAccounts.length > 0" class="card" style="margin-top: 2rem; border-color: rgba(255, 255, 255, 0.03); background: rgba(18, 24, 40, 0.4);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h4 style="font-weight: 600; margin: 0; color: var(--text-secondary); display: flex; align-items: center; gap: 0.5rem;">
          <svg style="width: 18px; height: 18px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" /></svg>
          Archived Accounts ({{ archivedAccounts.length }})
        </h4>
        <button class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="showArchived = !showArchived">
          {{ showArchived ? 'Hide' : 'Show' }}
        </button>
      </div>
      
      <div v-if="showArchived" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
        <div v-for="acc in archivedAccounts" :key="acc.id" style="border: 1px solid var(--border-color); border-radius: 0.5rem; padding: 1.25rem; opacity: 0.6; background: rgba(0, 0, 0, 0.2);">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
            <div>
              <div style="font-weight: 600; font-size: 1rem; text-decoration: line-through;">{{ acc.name }}</div>
              <div class="text-muted" style="font-size: 0.8rem;">{{ acc.institution || 'Cash' }} &bull; {{ acc.type }}</div>
            </div>
            <div style="display: flex; gap: 0.25rem; align-items: center;">
              <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" @click="restoreAccount(acc)" title="Restore Account">
                Restore
              </button>
              <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; display: inline-flex;" @click="deleteAccount(acc)" title="Delete Account">
                <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
            </div>
          </div>
          <div style="font-size: 1.25rem; font-weight: 700;" class="text-muted">
            RM{{ formatCurrency(getLatestBalance(acc.id)) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Add Account Modal -->
    <Modal :show="showAddAccountModal" title="Add Bank Account" @close="showAddAccountModal = false">
      <form @submit.prevent="saveAccount">
        <div class="form-group">
          <label class="form-label">Account Name</label>
          <input v-model="accountForm.name" type="text" class="form-input" placeholder="e.g. Main Checking" required />
        </div>
        <div class="form-group">
          <label class="form-label">Institution (Bank Name)</label>
          <input v-model="accountForm.institution" type="text" class="form-input" placeholder="e.g. Maybank" />
        </div>
        <div class="form-group">
          <label class="form-label">Account Type</label>
          <select v-model="accountForm.type" class="form-input" required>
            <option value="CHECKING">Checking</option>
            <option value="SAVINGS">Savings</option>
            <option value="CASH">Physical Cash</option>
            <option value="OTHER">Other</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Initial Balance (RM)</label>
          <input v-model="accountForm.initialBalance" type="number" step="0.01" class="form-input" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : 'Add Account' }}
        </button>
      </form>
    </Modal>

    <!-- Update Balance Modal -->
    <Modal :show="showUpdateModal" title="Update Balance" @close="showUpdateModal = false">
      <form @submit.prevent="saveBalance">
        <div class="form-group">
          <label class="form-label">Month</label>
          <input v-model="updateForm.month" type="number" min="1" max="12" class="form-input" required />
        </div>
        <div class="form-group">
          <label class="form-label">Year</label>
          <input v-model="updateForm.year" type="number" min="2000" max="2100" class="form-input" required />
        </div>
        <div class="form-group">
          <label class="form-label">New Balance (RM)</label>
          <input v-model="updateForm.balance" type="number" step="0.01" class="form-input" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : 'Update Balance' }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import Tooltip from '@/components/Tooltip.vue'
import { driver } from 'driver.js'

const startTour = () => {
  const driverObj = driver({
    showProgress: true,
    steps: [
      { element: '#tour-liquid-total', popover: { title: 'Total Liquidity', description: 'This highlights your immediately accessible funds across all tracked accounts.' } },
      { element: '#tour-accounts-list', popover: { title: 'Tracked Accounts', description: 'This section displays your individual accounts. You can click "Update Balance" to add a new balance snapshot for the current month.' } },
      { element: '#tour-add-account', popover: { title: 'Add a New Account', description: 'Click here to add a new bank account or physical cash source to track.' } }
    ]
  });
  driverObj.drive();
}

const accounts = ref([])
const snapshots = ref([])
const loading = ref(false)

const showAddAccountModal = ref(false)
const showUpdateModal = ref(false)

const accountForm = ref({ name: '', institution: '', type: 'CHECKING', initialBalance: 0 })
const updateForm = ref({ accountId: null, month: 1, year: 2023, balance: 0 })

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const getLatestSnapshot = (accountId) => {
  const accountSnaps = snapshots.value.filter(s => s.account === accountId)
  if (accountSnaps.length === 0) return null
  return accountSnaps.reduce((latest, current) => {
    if (current.year > latest.year) return current
    if (current.year === latest.year && current.month > latest.month) return current
    return latest
  })
}

const getLatestBalance = (accountId) => {
  const snap = getLatestSnapshot(accountId)
  return snap ? parseFloat(snap.balance) : 0
}

const getLastUpdatedText = (accountId) => {
  const snap = getLatestSnapshot(accountId)
  if (!snap) return 'Never'
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${months[snap.month - 1]} ${snap.year}`
}

const showArchived = ref(false)

const activeAccounts = computed(() => accounts.value.filter(a => a.is_active))
const archivedAccounts = computed(() => accounts.value.filter(a => !a.is_active))

const totalLiquidity = computed(() => {
  return activeAccounts.value.reduce((total, acc) => total + getLatestBalance(acc.id), 0)
})

const archiveAccount = async (acc) => {
  if (!confirm(`Are you sure you want to archive "${acc.name}"? It will be hidden from the active list and excluded from total assets.`)) return
  try {
    await api.patch(`/banking/accounts/${acc.id}/`, { is_active: false })
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to archive account')
  }
}

const restoreAccount = async (acc) => {
  try {
    await api.patch(`/banking/accounts/${acc.id}/`, { is_active: true })
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to restore account')
  }
}

const deleteAccount = async (acc) => {
  if (!confirm(`Are you sure you want to permanently delete "${acc.name}"? This will delete all balance history and cannot be undone.`)) return
  try {
    await api.delete(`/banking/accounts/${acc.id}/`)
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to delete account')
  }
}

const fetchData = async () => {
  try {
    const [accRes, snapRes] = await Promise.all([
      api.get('/banking/accounts/'),
      api.get('/banking/snapshots/')
    ])
    accounts.value = accRes.data
    snapshots.value = snapRes.data
  } catch (e) {
    console.error(e)
  }
}

const saveAccount = async () => {
  loading.value = true
  try {
    const res = await api.post('/banking/accounts/', {
      name: accountForm.value.name,
      institution: accountForm.value.institution,
      type: accountForm.value.type
    })
    
    const d = new Date()
    await api.post('/banking/snapshots/', {
      account: res.data.id,
      month: d.getMonth() + 1,
      year: d.getFullYear(),
      balance: accountForm.value.initialBalance
    })
    
    showAddAccountModal.value = false
    accountForm.value = { name: '', institution: '', type: 'CHECKING', initialBalance: 0 }
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to add account')
  } finally {
    loading.value = false
  }
}

const openUpdateModal = (acc) => {
  const d = new Date()
  updateForm.value.accountId = acc.id
  updateForm.value.month = d.getMonth() + 1
  updateForm.value.year = d.getFullYear()
  updateForm.value.balance = getLatestBalance(acc.id)
  showUpdateModal.value = true
}

const saveBalance = async () => {
  loading.value = true
  try {
    // Check if snapshot for this month/year already exists
    const existing = snapshots.value.find(s => s.account === updateForm.value.accountId && s.month === updateForm.value.month && s.year === updateForm.value.year)
    
    if (existing) {
      await api.patch(`/banking/snapshots/${existing.id}/`, { balance: updateForm.value.balance })
    } else {
      await api.post('/banking/snapshots/', {
        account: updateForm.value.accountId,
        month: updateForm.value.month,
        year: updateForm.value.year,
        balance: updateForm.value.balance
      })
    }
    
    showUpdateModal.value = false
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to update balance')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
