<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem;">
      <router-link to="/" class="text-muted" style="display: inline-block; margin-bottom: 0.5rem;">&larr; Back to Dashboard</router-link>
      <h1 style="font-weight: 600;">Manage Categories & Lenders</h1>
    </header>



    <!-- Add Lender Modal -->
    <Modal :show="showAddLenderModal" title="Add Lender / Credit Card" @close="showAddLenderModal = false">
      <form @submit.prevent="addLender" style="min-height: 270px; display: flex; flex-direction: column; gap: 1rem;">
        <div class="form-group">
          <label class="form-label">Lender / Card Name</label>
          <input v-model="newLenderName" type="text" class="form-input" placeholder="e.g. Maybank, CIMB" required />
        </div>
        <div class="form-group">
          <label class="form-label">Category</label>
          <SearchableSelect v-model="newLenderCategoryId" :options="activeCategoryOptions" placeholder="Select Category" />
        </div>
        <div class="form-group" v-if="showLimitField">
          <label class="form-label">Limit (RM)</label>
          <input v-model="newLenderOriginalAmount" type="number" step="0.01" class="form-input" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: auto;" :disabled="loading.len">
          {{ loading.len ? 'Saving...' : 'Add Lender' }}
        </button>
      </form>
    </Modal>

    <!-- Edit Lender Modal -->
    <Modal :show="showEditLenderModal" title="Edit Lender" @close="cancelEditLender">
      <form @submit.prevent="saveLender" v-if="editingLender" style="min-height: 270px; display: flex; flex-direction: column; gap: 1rem;">
        <div class="form-group">
          <label class="form-label">Lender / Card Name</label>
          <input v-model="editingLender.editName" type="text" class="form-input" required />
        </div>
        <div class="form-group">
          <label class="form-label">Category</label>
          <select v-model="editingLender.editCategoryId" class="form-input" style="color: #fff;" required>
            <option value="" disabled>Select Category</option>
            <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <div class="form-group" v-if="showEditLimitField">
          <label class="form-label">Limit (RM)</label>
          <input v-model="editingLender.editOriginalAmount" type="number" step="0.01" class="form-input" required />
        </div>
        <div style="display: flex; gap: 1rem; margin-top: auto;">
          <button type="submit" class="btn btn-primary" style="flex: 1">Save</button>
          <button type="button" class="btn btn-secondary" @click="cancelEditLender" style="flex: 1">Cancel</button>
        </div>
      </form>
    </Modal>

    <div class="grid-2col">
      <!-- Lenders Section -->
      <div class="card" style="height: fit-content;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Lenders / Credit Cards
            <Tooltip title="Creditors & Lenders" description="Configure individual lenders (e.g., banks) or credit card accounts, specifying interest rates to automate payoff calculations." example="Maybank, Public Bank, CIMB" />
          </h3>
          <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddLenderModal = true">+ Add Lender</button>
        </div>

        <ul style="list-style: none; padding: 0;">
          <li v-if="lenders.length === 0" style="padding: 1.5rem; text-align: center;">
            <span style="font-size: 1.5rem;">🏦</span>
            <p class="text-muted" style="margin: 0.5rem 0 0; font-size: 0.875rem;">No lenders yet. Add a bank, credit card, or loan provider (e.g. Maybank, CIMB) to start tracking your debts.</p>
          </li>
          <li v-for="len in lenders" :key="len.id" 
              @click="selectLender(len)"
              style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; border-bottom: 1px solid var(--border-color); cursor: pointer; border-radius: 6px; margin-bottom: 0.25rem; transition: background 0.2s;"
              :style="activeLenderForItems && activeLenderForItems.id === len.id ? 'background: rgba(255,255,255,0.08); border-left: 3px solid var(--accent-primary);' : ''">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1; min-width: 150px; flex-wrap: wrap;">
              <div>
                <div :class="{ 'text-muted': !len.is_active }" style="font-weight: 600;">{{ len.name }}</div>
                <div class="text-muted" style="font-size: 0.75rem;">
                  {{ getCategoryName(len.category) }} | 
                  Limit/Loan: RM{{ Number(len.original_loan_amount).toLocaleString(undefined, {minimumFractionDigits:2}) }}
                </div>
              </div>
              
              <span v-if="!len.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px; scale: 0.85;">Archived</span>
              <span v-if="len.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px; scale: 0.85;">Default</span>
            </div>
            <div style="display: flex; gap: 0.25rem;" @click.stop>
              <button @click="editLender(len)" class="btn btn-secondary" style="padding: 0.2rem 0.4rem; font-size: 0.75rem;">Edit</button>
              <button @click="deleteLender(len)" class="btn btn-secondary text-danger" style="padding: 0.2rem 0.4rem; font-size: 0.75rem;">Delete</button>
              <button @click="toggleLenderStatus(len)" class="btn btn-secondary" style="padding: 0.2rem 0.4rem; font-size: 0.75rem;" :class="{ 'text-success': !len.is_active, 'text-danger': len.is_active }">
                {{ len.is_active ? 'Archive' : 'Restore' }}
              </button>
            </div>
          </li>
        </ul>
      </div>

      <!-- Items Section -->
      <div class="card">
        <div v-if="activeLenderForItems">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
            <h3 style="font-weight: 600; margin: 0; font-size: 1.25rem;">
              Items for {{ activeLenderForItems.name }}
            </h3>
            <div class="text-muted" style="font-size: 0.875rem; font-weight: 500;">
              Owed: RM{{ Number(activeLenderForItems.calculated_remaining_principal).toLocaleString(undefined, {minimumFractionDigits:2}) }} ({{ activeLenderForItems.progress_percentage }}% paid)
            </div>
          </div>

          <!-- Add Item Form -->
          <form @submit.prevent="addItem" style="border-bottom: 1px solid var(--border-color); padding-bottom: 1.5rem; margin-bottom: 1.5rem;">
            <h4 style="margin-top: 0; margin-bottom: 1rem; font-weight: 600; font-size: 0.95rem;">Add New Item</h4>
            <div class="form-group">
              <label class="form-label">Item / Loan Name</label>
              <input v-model="newItemName" type="text" class="form-input" placeholder="e.g. Purchase iPhone 15" required />
            </div>
            <div class="form-group">
              <label class="form-label">Value / Amount (RM)</label>
              <input v-model="newItemValue" type="number" step="0.01" class="form-input" placeholder="e.g. 5000" required />
            </div>
            <div class="form-group">
              <label class="form-label">Interest Rate (%)</label>
              <input v-model="newItemInterestRate" type="number" step="0.01" class="form-input" placeholder="e.g. 3.5 (Optional)" />
            </div>
            <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
              <div class="form-group" style="flex: 1; margin-bottom: 0;">
                <label class="form-label">Start Date</label>
                <input v-model="newItemStartDate" type="date" class="form-input" required />
              </div>
              <div class="form-group" style="flex: 1; margin-bottom: 0;">
                <label class="form-label">End Date</label>
                <input v-model="newItemEndDate" type="date" class="form-input" required />
              </div>
            </div>
            <div class="form-group">
              <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer;">
                <input type="checkbox" v-model="newItemIsFixedInterest" />
                Fixed Interest / Flat Rate
              </label>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="itemLoading">
              {{ itemLoading ? 'Saving...' : 'Add Item' }}
            </button>
          </form>

          <!-- Items List -->
          <h4 style="margin-bottom: 1rem; font-weight: 600; font-size: 0.95rem;">Current Items / Tally</h4>
          <ul style="list-style: none; padding: 0; max-height: 400px; overflow-y: auto;">
            <li v-for="item in activeLenderForItems.items" :key="item.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); gap: 0.5rem; flex-wrap: wrap;">
              <div style="flex: 1; min-width: 180px;">
                <div style="font-weight: 600; font-size: 0.95rem;">
                  {{ item.name }}
                  <span class="text-muted" style="font-size: 0.7rem; border: 1px solid var(--border-color); padding: 0 0.25rem; border-radius: 4px; margin-left: 0.25rem; font-weight: normal;">
                    {{ item.type === 'manual' ? 'Manual' : (item.type === 'recurring' ? 'Recurring' : 'Budget Transaction') }}
                  </span>
                </div>
                <div class="text-muted" style="font-size: 0.78rem;">
                  Amt: RM{{ Number(item.value).toLocaleString(undefined, {minimumFractionDigits:2}) }} | 
                  Remaining: RM{{ Number(item.remaining_balance).toLocaleString(undefined, {minimumFractionDigits:2}) }} | 
                  Contrib/Mo: RM{{ Number(item.monthly_payment).toLocaleString(undefined, {minimumFractionDigits:2}) }}
                  <span v-if="item.interest_rate > 0"> | Rate: {{ item.interest_rate }}%</span>
                </div>
              </div>
              <div style="display: flex; align-items: center; gap: 0.25rem;">
                <button v-if="item.type === 'manual'" @click="deleteItem(item)" class="btn btn-secondary text-danger" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" :disabled="itemLoading">Delete</button>
                
                <div style="display: flex; align-items: center; gap: 0.25rem;">
                  <input v-model="item.interest_rate" type="number" step="0.01" style="width: 55px; padding: 0.2rem; font-size: 0.75rem; color: #fff; height: 28px;" class="form-input" placeholder="0%" />
                  <button @click="updateItemInterest(item)" class="btn btn-primary" style="padding: 0.2rem 0.4rem; font-size: 0.75rem; height: 28px;" :disabled="itemLoading">Set Interest</button>
                </div>
              </div>
            </li>
            <li v-if="!activeLenderForItems.items || activeLenderForItems.items.length === 0" class="text-muted" style="text-align: center; padding: 2rem 0; font-size: 0.875rem;">
              No items added yet. Add a manual item above or tag transactions in the budgeting section.
            </li>
          </ul>
        </div>
        <div v-else style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 350px; text-align: center; color: var(--text-muted);">
          <span style="font-size: 3rem; margin-bottom: 1rem;">🏦</span>
          <h4 style="margin: 0 0 0.5rem; font-weight: 600; font-size: 1.1rem; color: var(--text-primary);">Select a Lender</h4>
          <p style="font-size: 0.875rem; max-width: 260px; margin: 0;">Click on any lender in the list on the left to view and manage its individual items.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'
import Tooltip from '@/components/Tooltip.vue'

const categories = ref([])
const lenders = ref([])
const newCategoryName = ref('')
const newLenderName = ref('')
const newLenderCategoryId = ref('')
const newLenderOriginalAmount = ref('')
const newLenderInterestRate = ref('')
const newLenderStartDate = ref('')
const newLenderEndDate = ref('')
const autoAddSubscription = ref(false)
const newLenderMonthlyPayment = ref('')
const loading = ref({ cat: false, len: false })
const showAddCategoryModal = ref(false)
const showAddLenderModal = ref(false)

const showItemsModal = ref(false)
const activeLenderForItems = ref(null)
const newItemName = ref('')
const newItemValue = ref('')
const newItemInterestRate = ref('')
const newItemStartDate = ref('')
const newItemEndDate = ref('')
const newItemIsFixedInterest = ref(true)
const itemLoading = ref(false)

const showEditLenderModal = ref(false)
const editingLender = ref(null)
const showEditCategoryModal = ref(false)
const editingCategory = ref(null)

const activeCategories = computed(() => categories.value.filter(c => c.is_active))

const activeCategoryOptions = computed(() => {
  return activeCategories.value.map(c => ({ value: c.id, label: c.name }))
})

const showLimitField = computed(() => {
  if (!newLenderCategoryId.value) return false
  const cat = categories.value.find(c => c.id === newLenderCategoryId.value)
  if (!cat) return false
  const name = cat.name.toLowerCase()
  return name.includes('pay later') || name.includes('bnpl')
})

const showEditLimitField = computed(() => {
  if (!editingLender.value || !editingLender.value.editCategoryId) return false
  const cat = categories.value.find(c => c.id === editingLender.value.editCategoryId)
  if (!cat) return false
  const name = cat.name.toLowerCase()
  return name.includes('pay later') || name.includes('bnpl')
})

const getCategoryName = (id) => {
  if (!id) return 'Uncategorized'
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : 'Uncategorized'
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/liabilities/categories/')
    categories.value = res.data.map(c => ({ ...c, isEditing: false, editName: c.name }))
  } catch (e) { console.error(e) }
}

const fetchLenders = async () => {
  try {
    const res = await api.get('/liabilities/lenders/')
    lenders.value = res.data.map(l => ({ 
      ...l, 
      isEditing: false, 
      editName: l.name, 
      editCategoryId: l.category || '', 
      editOriginalAmount: l.original_loan_amount || '', 
      editInterestRate: l.interest_rate || '',
      editStartDate: l.start_date || '',
      editEndDate: l.end_date || ''
    }))
    if (activeLenderForItems.value) {
      activeLenderForItems.value = lenders.value.find(l => l.id === activeLenderForItems.value.id) || null
    }
  } catch (e) { console.error(e) }
}



const addLender = async () => {
  if (!newLenderName.value.trim() || !newLenderCategoryId.value) return
  if (showLimitField.value && !newLenderOriginalAmount.value) return
  
  loading.value.len = true
  try {
    const payload = { 
      name: newLenderName.value,
      category: newLenderCategoryId.value,
      original_loan_amount: showLimitField.value ? newLenderOriginalAmount.value : 0,
      interest_rate: 0
    }
    
    await api.post('/liabilities/lenders/', payload)
    
    newLenderName.value = ''
    newLenderCategoryId.value = ''
    newLenderOriginalAmount.value = ''
    showAddLenderModal.value = false
    
    await fetchLenders()
  } catch (e) { console.error(e) } finally { loading.value.len = false }
}



const editLender = (len) => {
  editingLender.value = {
    ...len,
    editCategoryId: len.category || '',
    editName: len.name,
    editOriginalAmount: len.original_loan_amount || 0
  }
  showEditLenderModal.value = true
}

const cancelEditLender = () => {
  showEditLenderModal.value = false
  editingLender.value = null
}

const saveLender = async () => {
  const len = editingLender.value
  if (!len) return
  if (!confirm(`Are you sure you want to save changes to ${len.name}?`)) return
  
  try {
    const payload = { 
      name: len.editName,
      category: len.editCategoryId,
      original_loan_amount: showEditLimitField.value ? len.editOriginalAmount : 0
    }

    await api.patch(`/liabilities/lenders/${len.id}/`, payload)
    cancelEditLender()
    await fetchLenders()
  } catch (e) {
    console.error(e)
    alert("Failed to save changes.")
  }
}

const deleteLender = async (len) => {
  if (len.items && len.items.length > 0) {
    alert("Cannot delete a lender that has active items. Please delete or reassign its items first.")
    return
  }
  if (!confirm(`Are you sure you want to delete ${len.name}?`)) return
  try {
    await api.delete(`/liabilities/lenders/${len.id}/`)
    if (activeLenderForItems.value && activeLenderForItems.value.id === len.id) {
      activeLenderForItems.value = null
    }
    await fetchLenders()
  } catch (e) {
    console.error("Failed to delete lender", e)
    alert("Failed to delete lender.")
  }
}

const toggleLenderStatus = async (len) => {
  const actionText = len.is_active ? 'archive' : 'restore'
  if (!confirm(`Are you sure you want to ${actionText} ${len.name}?`)) return
  try {
    const newStatus = !len.is_active
    await api.patch(`/liabilities/lenders/${len.id}/`, { is_active: newStatus })
    len.is_active = newStatus
  } catch (e) { console.error(e) }
}

const selectLender = (len) => {
  if (hasItemsSupport(len)) {
    activeLenderForItems.value = len
  } else {
    activeLenderForItems.value = null
  }
}

const addItem = async () => {
  if (!activeLenderForItems.value) return
  itemLoading.value = true
  try {
    const payload = {
      lender: activeLenderForItems.value.id,
      name: newItemName.value,
      value: newItemValue.value,
      interest_rate: newItemInterestRate.value || 0,
      is_fixed_interest: newItemIsFixedInterest.value
    }
    if (newItemStartDate.value) payload.start_date = newItemStartDate.value
    if (newItemEndDate.value) payload.end_date = newItemEndDate.value

    await api.post('/liabilities/items/', payload)
    
    newItemName.value = ''
    newItemValue.value = ''
    newItemInterestRate.value = ''
    newItemStartDate.value = ''
    newItemEndDate.value = ''
    newItemIsFixedInterest.value = true
    
    await fetchLenders()
    activeLenderForItems.value = lenders.value.find(l => l.id === activeLenderForItems.value.id)
  } catch (e) {
    console.error("Failed to add item", e)
    alert("Failed to add item.")
  } finally {
    itemLoading.value = false
  }
}

const deleteItem = async (item) => {
  if (!activeLenderForItems.value || !item.db_id) return
  if (!confirm(`Are you sure you want to delete this item: ${item.name}?`)) return
  itemLoading.value = true
  try {
    await api.delete(`/liabilities/items/${item.db_id}/`)
    await fetchLenders()
    activeLenderForItems.value = lenders.value.find(l => l.id === activeLenderForItems.value.id)
  } catch (e) {
    console.error("Failed to delete item", e)
    alert("Failed to delete item.")
  } finally {
    itemLoading.value = false
  }
}

const updateItemInterest = async (item) => {
  if (!activeLenderForItems.value) return
  if (!confirm(`Are you sure you want to update the interest rate for: ${item.name}?`)) return
  itemLoading.value = true
  try {
    const payload = {
      lender: activeLenderForItems.value.id,
      interest_rate: item.interest_rate || 0
    }
    
    if (!item.db_id) {
      payload.name = item.name
      payload.value = item.value
      payload.start_date = item.start_date
      payload.end_date = item.end_date
      payload.is_fixed_interest = true
      
      if (item.type === 'recurring') {
        payload.subscription_id = parseInt(item.id.replace('sub_', ''))
      } else if (item.type === 'non-recurring') {
        payload.transaction_id = parseInt(item.id.replace('txn_', ''))
      }
      
      await api.post('/liabilities/items/', payload)
    } else {
      await api.patch(`/liabilities/items/${item.db_id}/`, {
        interest_rate: item.interest_rate || 0
      })
    }
    
    await fetchLenders()
    activeLenderForItems.value = lenders.value.find(l => l.id === activeLenderForItems.value.id)
    alert("Interest rate updated successfully!")
  } catch (e) {
    console.error("Failed to update item interest", e)
    alert("Failed to update interest rate.")
  } finally {
    itemLoading.value = false
  }
}

const hasItemsSupport = (len) => {
  const catName = getCategoryName(len.category).toLowerCase()
  return catName.includes('pay later') || catName.includes('loan') || catName.includes('credit card') || catName.includes('bnpl')
}

onMounted(() => {
  fetchCategories()
  fetchLenders()
})
</script>
