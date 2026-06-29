<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <router-link to="/" class="text-muted" style="display: inline-block; margin-bottom: 0.5rem;">&larr; Back to Dashboard</router-link>
        <h1 style="font-weight: 600;">Manage Categories & Lenders</h1>
      </div>
    </header>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem;">
      <!-- Categories Section -->
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Categories</h3>
        <form @submit.prevent="addCategory" class="form-group" style="display: flex; gap: 0.5rem;">
          <input v-model="newCategoryName" type="text" class="form-input" placeholder="New Category Name" required />
          <button type="submit" class="btn btn-primary" :disabled="loading.cat">Add</button>
        </form>
        <ul style="list-style: none; padding: 0;">
          <li v-for="cat in categories" :key="cat.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1;">
              <span v-if="!cat.isEditing" :class="{ 'text-muted': !cat.is_active }">{{ cat.name }}</span>
              <input v-else v-model="cat.editName" type="text" class="form-input" style="padding: 0.25rem 0.5rem; margin-right: 0.5rem;" @keyup.enter="saveCategory(cat)" />
              
              <span v-if="!cat.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
              <span v-if="cat.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <template v-if="!cat.is_default">
                <button v-if="!cat.isEditing" @click="editCategory(cat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
                <button v-else @click="saveCategory(cat)" class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Save</button>
                <button @click="toggleCategoryStatus(cat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !cat.is_active, 'text-danger': cat.is_active }">
                  {{ cat.is_active ? 'Archive' : 'Unarchive' }}
                </button>
              </template>
            </div>
          </li>
        </ul>
      </div>

      <!-- Lenders Section -->
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Lenders</h3>
        <form @submit.prevent="addLender" class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem;">
          <div style="display: flex; gap: 0.5rem;">
            <input v-model="newLenderName" type="text" class="form-input" placeholder="New Lender Name" required style="flex: 1" />
            <select v-model="newLenderCategoryId" class="form-input" style="flex: 1" required>
              <option value="" disabled>Select Category</option>
              <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
            <input v-model="newLenderOriginalAmount" type="number" step="0.01" class="form-input" placeholder="Original Amount" required style="flex: 1" />
            <input v-model="newLenderInterestRate" type="number" step="0.01" class="form-input" placeholder="Interest Rate (%)" style="flex: 1" />
            <button type="submit" class="btn btn-primary" :disabled="loading.len">Add</button>
          </div>
        </form>
        <ul style="list-style: none; padding: 0;">
          <li v-for="len in lenders" :key="len.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1;">
              <template v-if="!len.isEditing">
                <span :class="{ 'text-muted': !len.is_active }">{{ len.name }}</span>
                <span class="text-muted" style="font-size: 0.875rem; margin-left: 0.5rem;">({{ getCategoryName(len.category) }} - RM{{ Number(len.original_loan_amount).toLocaleString(undefined, {minimumFractionDigits:2}) }} @ {{ len.interest_rate || 0 }}%)</span>
              </template>
              <template v-else>
                <input v-model="len.editName" type="text" class="form-input" style="padding: 0.25rem 0.5rem; flex: 1;" />
                <select v-model="len.editCategoryId" class="form-input" style="padding: 0.25rem 0.5rem; flex: 1;">
                  <option value="" disabled>Select Category</option>
                  <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                </select>
                <input v-model="len.editOriginalAmount" type="number" step="0.01" class="form-input" style="padding: 0.25rem 0.5rem; flex: 1;" placeholder="Amount" />
                <input v-model="len.editInterestRate" type="number" step="0.01" class="form-input" style="padding: 0.25rem 0.5rem; flex: 1;" placeholder="Interest %" />
              </template>
              
              <span v-if="!len.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
              <span v-if="len.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
            </div>
            <div style="display: flex; gap: 0.5rem; margin-left: 1rem;">
              <template v-if="!len.is_default">
                <button v-if="!len.isEditing" @click="editLender(len)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
                <button v-else @click="saveLender(len)" class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Save</button>
                <button @click="toggleLenderStatus(len)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !len.is_active, 'text-danger': len.is_active }">
                  {{ len.is_active ? 'Archive' : 'Unarchive' }}
                </button>
              </template>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const categories = ref([])
const lenders = ref([])
const newCategoryName = ref('')
const newLenderName = ref('')
const newLenderCategoryId = ref('')
const newLenderOriginalAmount = ref('')
const newLenderInterestRate = ref('')
const loading = ref({ cat: false, len: false })

const activeCategories = computed(() => categories.value.filter(c => c.is_active))

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
    lenders.value = res.data.map(l => ({ ...l, isEditing: false, editName: l.name, editCategoryId: l.category || '', editOriginalAmount: l.original_loan_amount || '', editInterestRate: l.interest_rate || '' }))
  } catch (e) { console.error(e) }
}

const addCategory = async () => {
  if (!newCategoryName.value.trim()) return
  loading.value.cat = true
  try {
    await api.post('/liabilities/categories/', { name: newCategoryName.value })
    newCategoryName.value = ''
    await fetchCategories()
  } catch (e) { console.error(e) } finally { loading.value.cat = false }
}

const addLender = async () => {
  if (!newLenderName.value.trim() || !newLenderCategoryId.value || !newLenderOriginalAmount.value) return
  loading.value.len = true
  try {
    await api.post('/liabilities/lenders/', { 
      name: newLenderName.value,
      category: newLenderCategoryId.value,
      original_loan_amount: newLenderOriginalAmount.value,
      interest_rate: newLenderInterestRate.value || 0
    })
    newLenderName.value = ''
    newLenderCategoryId.value = ''
    newLenderOriginalAmount.value = ''
    newLenderInterestRate.value = ''
    await fetchLenders()
  } catch (e) { console.error(e) } finally { loading.value.len = false }
}

const editCategory = (cat) => {
  cat.isEditing = true
}

const saveCategory = async (cat) => {
  try {
    await api.patch(`/liabilities/categories/${cat.id}/`, { name: cat.editName })
    cat.name = cat.editName
    cat.isEditing = false
  } catch (e) { console.error(e) }
}

const toggleCategoryStatus = async (cat) => {
  try {
    const newStatus = !cat.is_active
    await api.patch(`/liabilities/categories/${cat.id}/`, { is_active: newStatus })
    cat.is_active = newStatus
  } catch (e) { console.error(e) }
}

const editLender = (len) => {
  len.editCategoryId = len.category || ''
  len.isEditing = true
}

const saveLender = async (len) => {
  try {
    await api.patch(`/liabilities/lenders/${len.id}/`, { 
      name: len.editName,
      category: len.editCategoryId,
      original_loan_amount: len.editOriginalAmount,
      interest_rate: len.editInterestRate || 0
    })
    len.name = len.editName
    len.category = len.editCategoryId
    len.original_loan_amount = len.editOriginalAmount
    len.interest_rate = len.editInterestRate || 0
    len.isEditing = false
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
