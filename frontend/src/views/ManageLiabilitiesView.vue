<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem;">
      <router-link to="/" class="text-muted" style="display: inline-block; margin-bottom: 0.5rem;">&larr; Back to Dashboard</router-link>
      <h1 style="font-weight: 600;">Manage Categories & Lenders</h1>
    </header>

    <!-- Add Category Modal -->
    <Modal :show="showAddCategoryModal" title="Add Liability Category" @close="showAddCategoryModal = false">
      <form @submit.prevent="addCategory">
        <div class="form-group">
          <label class="form-label">Category Name</label>
          <input v-model="newCategoryName" type="text" class="form-input" placeholder="e.g. Mortgages, Auto Loans" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.cat">
          {{ loading.cat ? 'Saving...' : 'Add Category' }}
        </button>
      </form>
    </Modal>

    <!-- Edit Category Modal -->
    <Modal :show="showEditCategoryModal" title="Edit Category" @close="cancelEditCategory">
      <form @submit.prevent="saveCategory" v-if="editingCategory">
        <div class="form-group">
          <label class="form-label">Category Name</label>
          <input v-model="editingCategory.editName" type="text" class="form-input" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.cat">
          {{ loading.cat ? 'Saving...' : 'Save Changes' }}
        </button>
      </form>
    </Modal>

    <!-- Add Lender Modal -->
    <Modal :show="showAddLenderModal" title="Add Lender / Credit Card" @close="showAddLenderModal = false">
      <form @submit.prevent="addLender">
        <div class="form-group">
          <label class="form-label">Lender / Card Name</label>
          <input v-model="newLenderName" type="text" class="form-input" placeholder="e.g. Maybank, CIMB" required />
        </div>
        <div class="form-group">
          <label class="form-label">Category</label>
          <SearchableSelect v-model="newLenderCategoryId" :options="activeCategoryOptions" placeholder="Select Category" />
        </div>
        <div class="form-group">
          <label class="form-label">Loan Amount / Credit Limit</label>
          <input v-model="newLenderOriginalAmount" type="number" step="0.01" class="form-input" required />
        </div>
        <div class="form-group">
          <label class="form-label">Interest Rate (%)</label>
          <input v-model="newLenderInterestRate" type="number" step="0.01" class="form-input" />
        </div>
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1; margin-bottom: 0;">
            <label class="form-label">Start Date (Optional)</label>
            <input v-model="newLenderStartDate" type="date" class="form-input" />
          </div>
          <div class="form-group" style="flex: 1; margin-bottom: 0;">
            <label class="form-label">End Date (Optional)</label>
            <input v-model="newLenderEndDate" type="date" class="form-input" />
          </div>
        </div>
        <div class="form-group">
          <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; cursor: pointer;">
            <input type="checkbox" v-model="autoAddSubscription" />
            Auto-create as a recurring monthly expense in Budgeting
          </label>
          <div v-if="autoAddSubscription" style="margin-top: 0.5rem;">
            <input v-model="newLenderMonthlyPayment" type="number" step="0.01" class="form-input" placeholder="Expected Monthly Payment Amount" required />
          </div>
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.len">
          {{ loading.len ? 'Saving...' : 'Add Lender' }}
        </button>
      </form>
    </Modal>

    <div class="grid-2col">
      <!-- Categories Section -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Categories
            <Tooltip title="Liability Categories" description="Broad categories of debt like Credit Cards, Mortgages, Student Loans, Personal Loans." example="Mortgage, Credit Cards, Car Loan" />
          </h3>
          <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddCategoryModal = true">+ Add Category</button>
        </div>

        <ul style="list-style: none; padding: 0;">
          <li v-for="cat in categories" :key="cat.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; gap: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1;">
              <span :class="{ 'text-muted': !cat.is_active }">{{ cat.name }}</span>
              
              <span v-if="!cat.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
              <span v-if="cat.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <template v-if="!cat.is_default">
                <button @click="openEditCategory(cat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
                <button @click="toggleCategoryStatus(cat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !cat.is_active, 'text-danger': cat.is_active }">
                  {{ cat.is_active ? 'Archive' : 'Unarchive' }}
                </button>
              </template>
            </div>
          </li>
          <li v-if="categories.length === 0" style="padding: 1.5rem; text-align: center;">
            <span style="font-size: 1.5rem;">🏷️</span>
            <p class="text-muted" style="margin: 0.5rem 0 0; font-size: 0.875rem;">No categories yet. Create one (e.g. Mortgages, Auto Loans) before adding lenders.</p>
          </li>
        </ul>
      </div>

      <!-- Lenders Section -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Lenders / Credit Cards
            <Tooltip title="Lenders & Credit Cards" description="Individual entities or banks you owe money to, along with their interest rates." example="Maybank Visa, CIMB Housing Loan" />
          </h3>
          <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddLenderModal = true">+ Add Lender / Card</button>
        </div>

        <ul style="list-style: none; padding: 0;">
          <li v-if="lenders.length === 0" style="padding: 1.5rem; text-align: center;">
            <span style="font-size: 1.5rem;">🏦</span>
            <p class="text-muted" style="margin: 0.5rem 0 0; font-size: 0.875rem;">No lenders yet. Add a bank, credit card, or loan provider (e.g. Maybank, CIMB) to start tracking your debts.</p>
          </li>
          <li v-for="len in lenders" :key="len.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; gap: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1; min-width: 250px; flex-wrap: wrap;">
              <div>
                <span :class="{ 'text-muted': !len.is_active }" style="font-weight: 600;">{{ len.name }}</span>
                <span class="text-muted" style="font-size: 0.875rem; margin-left: 0.5rem;">({{ getCategoryName(len.category) }} - RM{{ Number(len.original_loan_amount).toLocaleString(undefined, {minimumFractionDigits:2}) }} @ {{ len.interest_rate || 0 }}%)</span>
              </div>
              
              <span v-if="!len.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
              <span v-if="len.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <template v-if="!len.is_default">
                <button @click="editLender(len)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
                <button @click="toggleLenderStatus(len)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !len.is_active, 'text-danger': len.is_active }">
                  {{ len.is_active ? 'Archive' : 'Unarchive' }}
                </button>
              </template>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Edit Lender Modal -->
    <Modal :show="showEditLenderModal" title="Edit Lender / Credit Card" @close="cancelEditLender">
      <form @submit.prevent="saveLender" v-if="editingLender">
        <div class="form-group">
          <label class="form-label">Name</label>
          <input v-model="editingLender.editName" type="text" class="form-input" required />
        </div>
        <div class="form-group">
          <label class="form-label">Category</label>
          <select v-model="editingLender.editCategoryId" class="form-input" required>
            <option value="" disabled>Select Category</option>
            <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Amount / Credit Limit (RM)</label>
          <input v-model="editingLender.editOriginalAmount" type="number" step="0.01" class="form-input" required />
        </div>
        <div class="form-group">
          <label class="form-label">Interest Rate (%)</label>
          <input v-model="editingLender.editInterestRate" type="number" step="0.01" class="form-input" />
        </div>
        <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Start Date (Optional)</label>
            <input v-model="editingLender.editStartDate" type="date" class="form-input" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label class="form-label">End Date (Optional)</label>
            <input v-model="editingLender.editEndDate" type="date" class="form-input" />
          </div>
        </div>
        <div style="display: flex; gap: 1rem;">
          <button type="submit" class="btn btn-primary" style="flex: 1">Save</button>
          <button type="button" class="btn btn-secondary" @click="cancelEditLender" style="flex: 1">Cancel</button>
        </div>
      </form>
    </Modal>
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

const showEditLenderModal = ref(false)
const editingLender = ref(null)
const showEditCategoryModal = ref(false)
const editingCategory = ref(null)

const activeCategories = computed(() => categories.value.filter(c => c.is_active))

const activeCategoryOptions = computed(() => {
  return activeCategories.value.map(c => ({ value: c.id, label: c.name }))
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
  } catch (e) { console.error(e) }
}

const addCategory = async () => {
  if (!newCategoryName.value.trim()) return
  loading.value.cat = true
  try {
    await api.post('/liabilities/categories/', { name: newCategoryName.value })
    newCategoryName.value = ''
    showAddCategoryModal.value = false
    await fetchCategories()
  } catch (e) { console.error(e) } finally { loading.value.cat = false }
}

const addLender = async () => {
  if (!newLenderName.value.trim() || !newLenderCategoryId.value || !newLenderOriginalAmount.value) return
  if (autoAddSubscription.value && !newLenderMonthlyPayment.value) {
    alert("Please enter a monthly payment amount for the subscription.")
    return
  }
  loading.value.len = true
  try {
    const payload = { 
      name: newLenderName.value,
      category: newLenderCategoryId.value,
      original_loan_amount: newLenderOriginalAmount.value,
      interest_rate: newLenderInterestRate.value || 0
    }
    if (newLenderStartDate.value) payload.start_date = newLenderStartDate.value;
    if (newLenderEndDate.value) payload.end_date = newLenderEndDate.value;
    
    await api.post('/liabilities/lenders/', payload)
    
    if (autoAddSubscription.value) {
      await api.post('/budgeting/subscriptions/', {
        name: `${newLenderName.value} Payment`,
        type: 'EXPENSE',
        amount: newLenderMonthlyPayment.value,
        billing_cycle: 'MONTHLY',
        status: 'ACTIVE',
        start_date: newLenderStartDate.value || null,
        end_date: newLenderEndDate.value || null
      })
    }
    
    newLenderName.value = ''
    newLenderCategoryId.value = ''
    newLenderOriginalAmount.value = ''
    newLenderInterestRate.value = ''
    newLenderStartDate.value = ''
    newLenderEndDate.value = ''
    autoAddSubscription.value = false
    newLenderMonthlyPayment.value = ''
    showAddLenderModal.value = false
    
    await fetchLenders()
  } catch (e) { console.error(e) } finally { loading.value.len = false }
}

const openEditCategory = (cat) => {
  editingCategory.value = {
    ...cat,
    editName: cat.name
  }
  showEditCategoryModal.value = true
}

const cancelEditCategory = () => {
  showEditCategoryModal.value = false
  editingCategory.value = null
}

const saveCategory = async () => {
  const cat = editingCategory.value
  if (!cat || !cat.editName.trim()) return
  loading.value.cat = true
  try {
    await api.patch(`/liabilities/categories/${cat.id}/`, { name: cat.editName })
    cancelEditCategory()
    await fetchCategories()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value.cat = false
  }
}

const toggleCategoryStatus = async (cat) => {
  try {
    const newStatus = !cat.is_active
    await api.patch(`/liabilities/categories/${cat.id}/`, { is_active: newStatus })
    cat.is_active = newStatus
  } catch (e) { console.error(e) }
}

const editLender = (len) => {
  editingLender.value = {
    ...len,
    editCategoryId: len.category || '',
    editName: len.name,
    editOriginalAmount: len.original_loan_amount || '',
    editInterestRate: len.interest_rate || '',
    editStartDate: len.start_date || '',
    editEndDate: len.end_date || ''
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
  
  try {
    const payload = { 
      name: len.editName,
      category: len.editCategoryId,
      original_loan_amount: len.editOriginalAmount,
      interest_rate: len.editInterestRate || 0
    }
    if (len.editStartDate) payload.start_date = len.editStartDate;
    else payload.start_date = null;
    
    if (len.editEndDate) payload.end_date = len.editEndDate;
    else payload.end_date = null;

    await api.patch(`/liabilities/lenders/${len.id}/`, payload)
    
    // Update local state
    const originalLen = lenders.value.find(l => l.id === len.id)
    if (originalLen) {
      originalLen.name = len.editName
      originalLen.category = len.editCategoryId
      originalLen.original_loan_amount = len.editOriginalAmount
      originalLen.interest_rate = len.editInterestRate || 0
      originalLen.start_date = len.editStartDate
      originalLen.end_date = len.editEndDate
    }
    
    cancelEditLender()
  } catch (e) { console.error(e) }
}

const toggleLenderStatus = async (len) => {
  try {
    const newStatus = !len.is_active
    await api.patch(`/liabilities/lenders/${len.id}/`, { is_active: newStatus })
    len.is_active = newStatus
  } catch (e) { console.error(e) }
}

onMounted(() => {
  fetchCategories()
  fetchLenders()
})
</script>
