<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Manage Categories & Targets</h1>
        <p class="text-muted">Manage your raw categories or set budget limits on them.</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <select v-if="activeTab === 'TARGETS'" v-model="selectedMonth" class="form-input" style="width: 120px;" @change="fetchData">
          <option v-for="(m, i) in monthsList" :key="i" :value="i + 1">{{ m }}</option>
        </select>
        <input v-if="activeTab === 'TARGETS'" v-model="selectedYear" type="number" min="2000" max="2100" class="form-input" style="width: 100px;" @change="fetchData" />
        
        <button v-if="activeTab === 'TARGETS'" class="btn btn-primary" @click="openModal()">+ Add Target</button>
        <button v-if="activeTab === 'CATEGORIES'" class="btn btn-primary" @click="openCategoryModal()">+ Add Category</button>
        
        <router-link to="/budgeting" class="btn btn-secondary">Back to Budgeting</router-link>
      </div>
    </header>

    <div style="margin-bottom: 1rem; display: flex; gap: 0.5rem; background: var(--bg-background); padding: 0.25rem; border-radius: 0.5rem; width: max-content;">
      <button class="btn" :class="activeTab === 'TARGETS' ? 'btn-primary' : 'btn-secondary'" style="padding: 0.5rem 1rem;" @click="activeTab = 'TARGETS'">Targets</button>
      <button class="btn" :class="activeTab === 'CATEGORIES' ? 'btn-primary' : 'btn-secondary'" style="padding: 0.5rem 1rem;" @click="activeTab = 'CATEGORIES'">Categories</button>
    </div>

    <div v-if="activeTab === 'TARGETS'" class="card" style="margin-bottom: 2rem;">
       <table class="data-table" style="width: 100%; text-align: left; border-collapse: collapse;">
         <thead>
           <tr style="border-bottom: 1px solid var(--border-color);">
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Target On</th>
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Type</th>
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Limit ({{ currentMonthStr }})</th>
             <th style="padding: 0.75rem 0; text-align: right; color: var(--text-muted); font-weight: 500;">Actions</th>
           </tr>
         </thead>
         <tbody>
           <tr v-if="targets.length === 0">
             <td colspan="4" class="text-muted" style="text-align: center; padding: 2rem;">No targets found.</td>
           </tr>
           <tr v-for="t in targets" :key="t.id" style="border-bottom: 1px solid var(--border-color);">
             <td style="padding: 0.75rem 0; font-weight: 500;">
               <span v-if="t.category" class="text-muted" style="font-size: 0.8em; margin-right: 0.5rem; border: 1px solid var(--border-color); padding: 0.1rem 0.3rem; border-radius: 4px;">CATEGORY</span>
               <span v-else class="text-muted" style="font-size: 0.8em; margin-right: 0.5rem; border: 1px solid var(--border-color); padding: 0.1rem 0.3rem; border-radius: 4px;">NAME</span>
               {{ t.category ? t.category_name : t.name }}
             </td>
             <td style="padding: 0.75rem 0;">
               <span :class="t.type === 'INCOME' ? 'text-success' : 'text-danger'">{{ t.type === 'INCOME' ? 'Income' : 'Expense' }}</span>
             </td>
             <td style="padding: 0.75rem 0;">
                 RM{{ formatCurrency(t.amount) }}
                 <div v-if="t.start_date || t.end_date" style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                   Active: {{ t.start_date || 'Forever' }} to {{ t.end_date || 'Forever' }}
                 </div>
                 <div v-if="t.status === 'ARCHIVED'" style="font-size: 0.75rem; color: var(--warning); margin-top: 0.25rem;">(Target Archived)</div>
                 <div v-if="t.paused_months && t.paused_months.includes(currentMonthKey)" style="font-size: 0.75rem; color: var(--warning); margin-top: 0.25rem;">(Target Paused this month)</div>
             </td>
             <td style="padding: 0.75rem 0; text-align: right; display: flex; justify-content: flex-end; gap: 0.5rem;">
               <button v-if="t.status === 'ACTIVE' && !(t.paused_months && t.paused_months.includes(currentMonthKey))" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="pauseTargetMonth(t.id)">Pause Limit</button>
               <button v-if="t.status === 'ACTIVE' && (t.paused_months && t.paused_months.includes(currentMonthKey))" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="resumeTargetMonth(t.id)">Resume Limit</button>
               
               <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="openModal(t)">Edit</button>
               <button class="btn btn-danger" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="deleteTarget(t.id)">Delete</button>
             </td>
           </tr>
         </tbody>
       </table>
    </div>

    <div v-if="activeTab === 'CATEGORIES'" class="card" style="margin-bottom: 2rem;">
       <table class="data-table" style="width: 100%; text-align: left; border-collapse: collapse;">
         <thead>
           <tr style="border-bottom: 1px solid var(--border-color);">
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Name</th>
             <th style="padding: 0.75rem 0; color: var(--text-muted); font-weight: 500;">Type</th>
             <th style="padding: 0.75rem 0; text-align: right; color: var(--text-muted); font-weight: 500;">Actions</th>
           </tr>
         </thead>
         <tbody>
           <tr v-if="categories.length === 0">
             <td colspan="3" class="text-muted" style="text-align: center; padding: 2rem;">No categories found.</td>
           </tr>
           <tr v-for="c in categories" :key="c.id" style="border-bottom: 1px solid var(--border-color);">
             <td style="padding: 0.75rem 0; font-weight: 500;">{{ c.name }}</td>
             <td style="padding: 0.75rem 0;">
               <span :class="c.type === 'INCOME' ? 'text-success' : 'text-danger'">{{ c.type === 'INCOME' ? 'Income' : 'Expense' }}</span>
             </td>
             <td style="padding: 0.75rem 0; text-align: right; display: flex; justify-content: flex-end; gap: 0.5rem;">
               <span v-if="c.is_default" class="text-muted" style="font-size: 0.75rem; padding: 0.2rem;">Default</span>
               <template v-else>
                 <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="openCategoryModal(c)">Edit</button>
                 <button class="btn btn-danger" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="deleteCategory(c.id)">Delete</button>
               </template>
             </td>
           </tr>
         </tbody>
       </table>
    </div>

    <Modal :show="showModal" :title="form.id ? 'Edit Target' : 'Add Target'" @close="showModal = false">
      <form @submit.prevent="saveTarget">
        <div class="form-group">
          <label class="form-label">Type</label>
          <select v-model="form.type" class="form-input" required @change="fetchCategories">
            <option value="EXPENSE">Expense</option>
            <option value="INCOME">Income</option>
          </select>
        </div>
        
        <div class="form-group">
          <label class="form-label">Target On</label>
          <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
            <label style="display: flex; align-items: center; gap: 0.25rem;"><input type="radio" v-model="targetMode" value="category" /> Category</label>
            <label style="display: flex; align-items: center; gap: 0.25rem;"><input type="radio" v-model="targetMode" value="name" /> Specific Name</label>
          </div>
          
          <select v-if="targetMode === 'category'" v-model="form.category" class="form-input" required>
            <option v-for="c in categories.filter(c => c.type === form.type)" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <input v-else v-model="form.name" type="text" class="form-input" required placeholder="e.g. Starbucks" />
        </div>

        <div class="form-group">
          <label class="form-label">Target Amount (RM)</label>
          <input v-model="form.amount" type="number" step="0.01" class="form-input" required />
        </div>
        
        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Active From (Optional)</label>
            <input v-model="form.start_date" type="date" class="form-input" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label class="form-label">Active Until (Optional)</label>
            <input v-model="form.end_date" type="date" class="form-input" />
          </div>
        </div>
        
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Target' }}
        </button>
      </form>
    </Modal>
    
    <Modal :show="showCatModal" :title="catForm.id ? 'Edit Category' : 'Add Category'" @close="showCatModal = false">
      <form @submit.prevent="saveCategory">
        <div class="form-group">
          <label class="form-label">Type</label>
          <select v-model="catForm.type" class="form-input" required>
            <option value="EXPENSE">Expense</option>
            <option value="INCOME">Income</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Category Name</label>
          <input v-model="catForm.name" type="text" class="form-input" required placeholder="e.g. Groceries" />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Category' }}
        </button>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'

const d = new Date()
const selectedMonth = ref(d.getMonth() + 1)
const selectedYear = ref(d.getFullYear())
const monthsList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const targets = ref([])
const categories = ref([])
const loading = ref(false)
const targetMode = ref('category')
const activeTab = ref('TARGETS')

const showModal = ref(false)
const showCatModal = ref(false)

const form = ref({ id: null, category: null, name: '', type: 'EXPENSE', amount: '', start_date: null, end_date: null })
const catForm = ref({ id: null, type: 'EXPENSE', name: '' })

const currentMonthStr = computed(() => `${monthsList[selectedMonth.value - 1]} ${selectedYear.value}`)
const currentMonthKey = computed(() => `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}`)

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })


const fetchData = async () => {
  try {
    const targetRes = await api.get('/budgeting/targets/')
    targets.value = targetRes.data
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

const pauseTargetMonth = async (id) => {
  try {
    await api.post(`/budgeting/targets/${id}/pause_month/`, { month: currentMonthKey.value })
    await fetchData()
  } catch (e) {
    alert('Failed to pause')
  }
}

const resumeTargetMonth = async (id) => {
  try {
    await api.post(`/budgeting/targets/${id}/resume_month/`, { month: currentMonthKey.value })
    await fetchData()
  } catch (e) {
    alert('Failed to resume')
  }
}

const deleteTarget = async (id) => {
  if (!confirm('Are you sure you want to delete this target?')) return
  try {
    await api.delete(`/budgeting/targets/${id}/`)
    await fetchData()
  } catch (e) {
    alert('Failed to delete target')
  }
}

const openModal = (t = null) => {
  if (t) {
    targetMode.value = t.category ? 'category' : 'name'
    form.value = { 
      id: t.id, 
      category: t.category,
      name: t.name, 
      type: t.type, 
      amount: t.amount, 
      start_date: t.start_date, 
      end_date: t.end_date 
    }
  } else {
    targetMode.value = 'category'
    form.value = { id: null, category: categories.value.filter(c => c.type === 'EXPENSE')[0]?.id || null, name: '', type: 'EXPENSE', amount: '', start_date: null, end_date: null }
  }
  showModal.value = true
}

const saveTarget = async () => {
  loading.value = true
  try {
    const targetPayload = {
      type: form.value.type,
      amount: form.value.amount,
      start_date: form.value.start_date || null,
      end_date: form.value.end_date || null,
      status: 'ACTIVE'
    }
    
    if (targetMode.value === 'category') {
      targetPayload.category = form.value.category
      targetPayload.name = null
    } else {
      targetPayload.category = null
      targetPayload.name = form.value.name
    }
    
    if (form.value.id) {
      await api.patch(`/budgeting/targets/${form.value.id}/`, targetPayload)
    } else {
      await api.post('/budgeting/targets/', targetPayload)
    }
    
    showModal.value = false
    await fetchData()
  } catch (e) {
    alert(e.response?.data?.[0] || 'Failed to save')
  } finally {
    loading.value = false
  }
}

const openCategoryModal = (c = null) => {
  if (c) {
    catForm.value = { id: c.id, type: c.type, name: c.name }
  } else {
    catForm.value = { id: null, type: 'EXPENSE', name: '' }
  }
  showCatModal.value = true
}

const saveCategory = async () => {
  loading.value = true
  try {
    if (catForm.value.id) {
      await api.patch(`/budgeting/categories/${catForm.value.id}/`, catForm.value)
    } else {
      await api.post('/budgeting/categories/', catForm.value)
    }
    showCatModal.value = false
    await fetchCategories()
  } catch (e) {
    alert('Failed to save category')
  } finally {
    loading.value = false
  }
}

const deleteCategory = async (id) => {
  if (!confirm('Are you sure you want to delete this category? Targets linked to it will also be deleted.')) return
  try {
    await api.delete(`/budgeting/categories/${id}/`)
    await fetchCategories()
    await fetchData()
  } catch (e) {
    alert('Failed to delete category')
  }
}

onMounted(() => {
  fetchData()
  fetchCategories()
})
</script>
