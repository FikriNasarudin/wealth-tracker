<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Manage Recurring Items</h1>
        <p class="text-muted">Log, pause, or update your fixed income and costs.</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <select v-model="selectedMonth" class="form-input" style="width: 120px;" @change="fetchData">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <select v-model="selectedYear" class="form-input" style="width: 95px;" @change="fetchData">
          <option v-for="y in yearsList" :key="y" :value="y">{{ y }}</option>
        </select>
        <button class="btn btn-primary" @click="openModal()">+ Add New Item</button>
        <router-link to="/budgeting" class="btn btn-secondary">Back to Budgeting</router-link>
      </div>
    </header>

    <div class="card" style="margin-bottom: 2rem;">
       <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
         <button class="btn" :class="statusTab === 'ACTIVE' ? 'btn-primary' : 'btn-secondary'" style="padding: 0.5rem 1rem;" @click="statusTab = 'ACTIVE'">Active Items</button>
         <button class="btn" :class="statusTab === 'ARCHIVED' ? 'btn-primary' : 'btn-secondary'" style="padding: 0.5rem 1rem;" @click="statusTab = 'ARCHIVED'">Archived</button>
       </div>

       <table class="data-table" style="width: 100%; text-align: left; border-collapse: collapse;">
         <thead>
           <tr style="border-bottom: 1px solid var(--border-color);">
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Name</th>
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Category</th>
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Type</th>
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Amount</th>
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Status for {{ currentMonthStr }}</th>
             <th style="padding: 0.75rem 0; text-align: right; color: var(--text-muted); font-weight: 500;">Actions</th>
           </tr>
         </thead>
         <tbody>
           <tr v-if="filteredSubs.length === 0">
             <td colspan="6" class="text-muted" style="text-align: center; padding: 2rem;">No items found.</td>
           </tr>
           <tr v-for="sub in filteredSubs" :key="sub.id" style="border-bottom: 1px solid var(--border-color);">
             <td style="padding: 0.75rem 0; font-weight: 500;">{{ sub.name }}</td>
             <td style="padding: 0.75rem 0; color: var(--text-muted);">{{ sub.category_name || '-' }}</td>
             <td style="padding: 0.75rem 0;">
               <span :class="sub.type === 'INCOME' ? 'text-success' : 'text-danger'">{{ sub.type === 'INCOME' ? 'Income' : 'Expense' }}</span>
             </td>
             <td style="padding: 0.75rem 0;">
               RM{{ formatCurrency(sub.amount) }} <span class="text-muted">/ {{ sub.billing_cycle === 'MONTHLY' ? 'mo' : 'yr' }}</span>
               <div v-if="sub.start_date || sub.end_date" style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                 Active: {{ sub.start_date || 'Forever' }} to {{ sub.end_date || 'Forever' }}
               </div>
             </td>
             <td style="padding: 0.75rem 0;">
               <span v-if="sub.status === 'ARCHIVED'" class="text-muted">Archived</span>
               <span v-else-if="loggedIds.includes(sub.id)" class="text-success" style="font-weight: 500;">✓ Logged</span>
               <span v-else-if="sub.paused_months && sub.paused_months.includes(currentMonthKey)" class="text-warning">⏸ Paused</span>
               <span v-else class="text-muted">Pending</span>
             </td>
             <td style="padding: 0.75rem 0; text-align: right; display: flex; justify-content: flex-end; gap: 0.5rem;">
               <button v-if="sub.status === 'ACTIVE' && !loggedIds.includes(sub.id) && !(sub.paused_months && sub.paused_months.includes(currentMonthKey))" class="btn btn-primary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="logMonth(sub.id)">Log {{ currentMonthStr }}</button>
               <button v-if="sub.status === 'ACTIVE' && !loggedIds.includes(sub.id) && !(sub.paused_months && sub.paused_months.includes(currentMonthKey))" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="pauseMonth(sub.id)">Pause</button>
               <button v-if="sub.status === 'ACTIVE' && !loggedIds.includes(sub.id) && (sub.paused_months && sub.paused_months.includes(currentMonthKey))" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="resumeMonth(sub.id)">Resume</button>
               
               <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="openModal(sub)">Edit</button>
               
               <button v-if="sub.status === 'ACTIVE'" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem; color: var(--warning);" @click="archiveSub(sub.id)">Archive</button>
               <button v-if="sub.status === 'ARCHIVED'" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem; color: var(--success);" @click="unarchiveSub(sub.id)">Unarchive</button>
               
               <button class="btn btn-danger" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="deleteSub(sub.id)">Delete</button>
             </td>
           </tr>
         </tbody>
       </table>
    </div>

    <Modal :show="showModal" :title="form.id ? 'Edit Item' : 'Add Item'" @close="showModal = false">
      <form @submit.prevent="saveItem">
        <div class="form-group">
          <label class="form-label">Type</label>
          <select v-model="form.type" class="form-input" required>
            <option value="INCOME">Income</option>
            <option value="EXPENSE">Expense</option>
          </select>
        </div>
        
        <div class="form-group">
          <label class="form-label">Category</label>
            <SearchableSelect 
              v-model="form.category" 
              :options="categoryOptions" 
              placeholder="Search category..." 
            />
        </div>
        
        <div class="form-group">
          <label class="form-label">Name</label>
          <input v-model="form.name" type="text" class="form-input" required placeholder="e.g. Netflix or Salary" />
        </div>
        
        <div class="form-group">
          <label class="form-label">Amount (RM)</label>
          <input v-model="form.amount" type="number" step="0.01" class="form-input" required />
        </div>
        <div class="form-group">
          <label class="form-label">Billing Cycle</label>
          <select v-model="form.billing_cycle" class="form-input" required>
            <option value="MONTHLY">Monthly</option>
            <option value="YEARLY">Yearly</option>
          </select>
        </div>
        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Start Date (Optional)</label>
            <input v-model="form.start_date" type="date" class="form-input" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label class="form-label">End Date (Optional)</label>
            <input v-model="form.end_date" type="date" class="form-input" />
          </div>
        </div>
        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Auto-Log Day (Optional)</label>
            <input v-model="form.auto_log_day" type="number" min="1" max="31" class="form-input" placeholder="e.g. 15 for 15th" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Debit Account (Optional)</label>
              <SearchableSelect 
              v-model="form.payment_account" 
              :options="debitAccountOptions" 
              placeholder="Search debit account..." 
            />
          </div>
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Item' }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const monthsList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const yearsList = computed(() => {
  const current = new Date().getFullYear()
  const years = []
  for (let y = current - 5; y <= current + 5; y++) {
    years.push(y)
  }
  return years
})

const subscriptions = ref([])
const categories = ref([])
const bankAccounts = ref([])
const creditCardsList = ref([])
const otherLiabilitiesList = ref([])
const loggedIds = ref([])
const statusTab = ref('ACTIVE')
const loading = ref(false)

const showModal = ref(false)
const form = ref({ id: null, category: null, type: 'EXPENSE', name: '', amount: '', billing_cycle: 'MONTHLY', start_date: null, end_date: null, auto_log_day: null, payment_account: null })

const currentMonthStr = computed(() => `${monthsList[selectedMonth.value - 1]} ${selectedYear.value}`)
const currentMonthKey = computed(() => `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}`)

const filteredSubs = computed(() => {
  return subscriptions.value.filter(s => s.status === statusTab.value)
})

const categoryOptions = computed(() => {
  return [
    { value: null, label: 'Uncategorized' },
    ...categories.value
      .filter(c => c.type === form.value.type)
      .map(c => ({ value: c.id, label: c.name }))
  ]
})

const debitAccountOptions = computed(() => {
  const list = [{ value: null, label: 'None (Cash/Other)' }]
  bankAccounts.value.forEach(b => {
    list.push({ value: b.name, label: `${b.name} (Bank Account)` })
  })
  creditCardsList.value.forEach(c => {
    list.push({ value: c.name, label: `${c.name} (Credit Card)` })
  })
  otherLiabilitiesList.value.forEach(l => {
    list.push({ value: l.name, label: `${l.name} (Loan/Other)` })
  })
  return list
})

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchData = async () => {
  try {
    const subRes = await api.get('/budgeting/subscriptions/')
    subscriptions.value = subRes.data
    
    try {
      const bankRes = await api.get('/banking/accounts/')
      bankAccounts.value = bankRes.data
      
      const liabRes = await api.get('/liabilities/lenders/')
      const catRes = await api.get('/liabilities/categories/')
      
      const ccCategory = catRes.data.find(c => c.name.toLowerCase() === 'credit cards')
      const ccCategoryId = ccCategory ? ccCategory.id : null
      
      creditCardsList.value = liabRes.data.filter(l => l.category === ccCategoryId)
      otherLiabilitiesList.value = liabRes.data.filter(l => l.category !== ccCategoryId)
    } catch(e) {
      console.warn("Could not fetch payment accounts", e)
    }
    
    const summaryRes = await api.get(`/budgeting/transactions/summary/?month=${selectedMonth.value}&year=${selectedYear.value}`)
    loggedIds.value = summaryRes.data.logged_subscription_ids || []
  } catch (e) {
    console.error(e)
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/budgeting/categories/')
    categories.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const logMonth = async (id) => {
  try {
    await api.post(`/budgeting/subscriptions/${id}/log_month/`, { month: currentMonthKey.value })
    await fetchData()
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to log')
  }
}

const pauseMonth = async (id) => {
  try {
    await api.post(`/budgeting/subscriptions/${id}/pause_month/`, { month: currentMonthKey.value })
    await fetchData()
  } catch (e) {
    alert('Failed to pause')
  }
}

const resumeMonth = async (id) => {
  try {
    await api.post(`/budgeting/subscriptions/${id}/resume_month/`, { month: currentMonthKey.value })
    await fetchData()
  } catch (e) {
    alert('Failed to resume')
  }
}

const archiveSub = async (id) => {
  try {
    await api.post(`/budgeting/subscriptions/${id}/archive/`)
    await fetchData()
  } catch (e) {
    alert('Failed to archive')
  }
}

const unarchiveSub = async (id) => {
  try {
    await api.patch(`/budgeting/subscriptions/${id}/`, { status: 'ACTIVE' })
    await fetchData()
  } catch (e) {
    alert('Failed to unarchive')
  }
}

const deleteSub = async (id) => {
  if (!confirm('Are you sure you want to delete this permanently? All logged historical transactions will remain safe.')) return
  try {
    await api.delete(`/budgeting/subscriptions/${id}/`)
    await fetchData()
  } catch (e) {
    alert('Failed to delete')
  }
}

const openModal = (sub = null) => {
  if (sub) {
    form.value = { ...sub, category: sub.category }
  } else {
    form.value = { id: null, category: null, type: 'EXPENSE', name: '', amount: '', billing_cycle: 'MONTHLY', start_date: null, end_date: null, auto_log_day: null, payment_account: null }
  }
  showModal.value = true
}

const saveItem = async () => {
  loading.value = true
  try {
    const payload = { ...form.value }
    if (!payload.start_date) payload.start_date = null
    if (!payload.end_date) payload.end_date = null
    
    if (payload.id) {
      await api.patch(`/budgeting/subscriptions/${payload.id}/`, payload)
    } else {
      await api.post('/budgeting/subscriptions/', payload)
    }
    showModal.value = false
    await fetchData()
  } catch (e) {
    alert('Failed to save item')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  fetchCategories()
})
</script>
