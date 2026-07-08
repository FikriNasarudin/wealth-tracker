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
       <div class="targets-list" style="display: flex; flex-direction: column; gap: 0.75rem;">
         <div v-if="mergedTargetRows.length === 0" style="text-align: center; padding: 3rem 2rem;">
           <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🎯</div>
           <div style="font-weight: 600; margin-bottom: 0.4rem;">No budget targets yet</div>
           <div class="text-muted" style="font-size: 0.875rem; max-width: 360px; margin: 0 auto;">Set spending limits or income goals for expense categories or names. Targets help you see how well you're sticking to your budget each month.</div>
         </div>
         <div v-else v-for="row in paginatedTargets" :key="row.key" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(255,255,255,0.015); border-radius: var(--border-radius-sm); border: 1px solid var(--border-color); transition: background var(--transition-fast);" :style="row.isDefault ? 'opacity: 0.65;' : ''">
           <div style="display: flex; align-items: center; gap: 0.75rem;">
             <div :style="{
               width: '32px',
               height: '32px',
               borderRadius: '50%',
               display: 'flex',
               alignItems: 'center',
               justifyContent: 'center',
               background: row.type === 'INCOME' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
               color: row.type === 'INCOME' ? 'var(--success)' : 'var(--danger)',
               fontWeight: '600'
             }">
               {{ row.type === 'INCOME' ? '↑' : '↓' }}
             </div>
             <div style="display: flex; flex-direction: column;">
               <span style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary);">
                 <span v-if="row.isNameTarget" class="text-muted" style="font-size: 0.7em; margin-right: 0.4rem; border: 1px solid var(--border-color); padding: 0.1rem 0.3rem; border-radius: 4px;">NAME</span>
                 {{ row.label }}
               </span>
               <span style="font-size: 0.75rem; color: var(--text-muted);">
                 Limit: <strong style="color: var(--text-primary);">RM{{ formatCurrency(row.amount) }}</strong>
                 <template v-if="row.target && (row.target.start_date || row.target.end_date)">
                   • Active: {{ row.target.start_date || 'Forever' }} → {{ row.target.end_date || 'Forever' }}
                 </template>
                 <template v-if="row.target && row.target.status === 'ARCHIVED'"> • (Archived)</template>
                 <template v-if="row.target && row.target.paused_months && row.target.paused_months.includes(currentMonthKey)"> • (Paused)</template>
               </span>
             </div>
           </div>
           
           <div style="display: flex; align-items: center; gap: 1rem;">
             <span v-if="row.isDefault" style="font-size: 0.72rem; padding: 0.15rem 0.55rem; border-radius: 999px; font-weight: 600; background: rgba(255,255,255,0.07); color: var(--text-muted); border: 1px solid var(--border-color);">🔁 Default</span>
             <span v-else style="font-size: 0.72rem; padding: 0.15rem 0.55rem; border-radius: 999px; font-weight: 600; background: rgba(99,102,241,0.15); color: var(--accent-primary); border: 1px solid rgba(99,102,241,0.3);">✏️ Custom</span>
             
             <div style="display: flex; gap: 0.4rem; justify-content: flex-end; flex-wrap: wrap;">
               <template v-if="row.isDefault">
                 <button class="btn btn-primary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="openModalForCategory(row.categoryObj)">Set Custom</button>
               </template>
               <template v-else-if="row.target">
                 <button v-if="row.target.status === 'ACTIVE' && !(row.target.paused_months && row.target.paused_months.includes(currentMonthKey))" class="btn btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="pauseTargetMonth(row.target.id)">Pause</button>
                 <button v-if="row.target.status === 'ACTIVE' && (row.target.paused_months && row.target.paused_months.includes(currentMonthKey))" class="btn btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="resumeTargetMonth(row.target.id)">Resume</button>
                 <button class="btn btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="openModal(row.target)">Edit</button>
                 <button class="btn btn-danger" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="deleteTarget(row.target.id)">Delete</button>
               </template>
               <template v-else>
                 <button class="btn btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="openModal(row.target)">Edit</button>
                 <button class="btn btn-danger" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="deleteTarget(row.target.id)">Delete</button>
               </template>
             </div>
           </div>
         </div>
         <Pagination v-model="currentPageTargets" :totalItems="mergedTargetRows.length" :itemsPerPage="itemsPerPage" />
       </div>
    </div>

    <div v-if="activeTab === 'CATEGORIES'" class="card" style="margin-bottom: 2rem;">
       <div class="categories-list" style="display: flex; flex-direction: column; gap: 0.75rem;">
         <div v-if="categories.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No categories found.</div>
         <div v-else v-for="c in paginatedCategories" :key="c.id" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(255,255,255,0.015); border-radius: var(--border-radius-sm); border: 1px solid var(--border-color); transition: background var(--transition-fast);">
           <div style="display: flex; align-items: center; gap: 0.75rem;">
             <div :style="{
               width: '32px',
               height: '32px',
               borderRadius: '50%',
               display: 'flex',
               alignItems: 'center',
               justifyContent: 'center',
               background: c.type === 'INCOME' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
               color: c.type === 'INCOME' ? 'var(--success)' : 'var(--danger)',
               fontWeight: '600'
             }">
               {{ c.type === 'INCOME' ? '↑' : '↓' }}
             </div>
             <div style="display: flex; flex-direction: column;">
               <span style="font-weight: 600; font-size: 0.95rem; color: var(--text-primary);">{{ c.name }}</span>
               <span style="font-size: 0.75rem; color: var(--text-muted);">{{ c.type === 'INCOME' ? 'Income category' : 'Expense category' }}</span>
             </div>
           </div>
           
           <div style="display: flex; align-items: center; gap: 1rem;">
             <span v-if="c.is_default" class="text-muted" style="font-size: 0.75rem; padding: 0.2rem;">Default</span>
             <template v-else>
               <div style="display: flex; gap: 0.4rem;">
                 <button class="btn btn-secondary" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="openCategoryModal(c)">Edit</button>
                 <button class="btn btn-danger" style="padding: 0.3rem 0.65rem; font-size: 0.75rem;" @click="deleteCategory(c.id)">Delete</button>
               </div>
             </template>
           </div>
         </div>
         <Pagination v-model="currentPageCategories" :totalItems="categories.length" :itemsPerPage="itemsPerPage" />
       </div>
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

          <!-- Recurring info hint when a category is selected -->
          <div v-if="targetMode === 'category' && form.category && recurringInCategory !== null"
            style="margin-top: 0.6rem; padding: 0.6rem 0.75rem; border-radius: 0.5rem; font-size: 0.82rem; display: flex; align-items: center; gap: 0.5rem;"
            :style="recurringInCategory > 0 ? 'background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3);' : 'background: rgba(255,255,255,0.04); border: 1px solid var(--border-color);'"
          >
            <span style="font-size: 1rem;">🔁</span>
            <span v-if="recurringInCategory > 0">
              <strong style="color: var(--accent-primary);">RM{{ formatCurrency(recurringInCategory) }}/mo</strong>
              <span class="text-muted"> already committed via Recurring Items in this category. Default target pre-filled.</span>
            </span>
            <span v-else class="text-muted">No recurring items in this category yet.</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Target Amount (RM)</label>
          <input v-model="form.amount" type="number" step="0.01" class="form-input" required placeholder="e.g. 500.00" />
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
import { ref, computed, watch, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import Pagination from '@/components/Pagination.vue'

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

const subscriptions = ref([])

const form = ref({ id: null, category: null, name: '', type: 'EXPENSE', amount: '', start_date: null, end_date: null })

// Sum of monthly-equivalent recurring items for the currently selected category in the form
const recurringInCategory = computed(() => {
  if (!form.value.category || targetMode.value !== 'category') return null
  const matched = subscriptions.value.filter(
    s => s.category === form.value.category && s.type === form.value.type && s.status === 'ACTIVE'
  )
  if (matched.length === 0) return 0
  return matched.reduce((sum, s) => {
    const monthly = s.billing_cycle === 'MONTHLY' ? parseFloat(s.amount) : parseFloat(s.amount) / 12
    return sum + monthly
  }, 0)
})

// Build a per-category lookup: categoryId → monthly recurring total
const recurringByCategory = computed(() => {
  const map = {}
  subscriptions.value
    .filter(s => s.status === 'ACTIVE')
    .forEach(s => {
      if (!s.category) return
      const monthly = s.billing_cycle === 'MONTHLY' ? parseFloat(s.amount) : parseFloat(s.amount) / 12
      map[s.category] = (map[s.category] || 0) + monthly
    })
  return map
})

// Merged list: explicit custom targets + default rows for categories with recurring but no custom target
const mergedTargetRows = computed(() => {
  const rows = []

  // 1. All explicit targets (Custom)
  targets.value.forEach(t => {
    rows.push({
      key: `custom-${t.id}`,
      label: t.category ? t.category_name : t.name,
      type: t.type,
      amount: parseFloat(t.amount),
      isDefault: false,
      isNameTarget: !t.category,
      target: t,
      categoryObj: null
    })
  })

  // 2. Categories with recurring items but NO explicit category target yet → Default rows
  const categoriesWithCustomTarget = new Set(
    targets.value.filter(t => t.category).map(t => t.category)
  )
  categories.value.forEach(cat => {
    const recurringTotal = recurringByCategory.value[cat.id] || 0
    if (recurringTotal > 0 && !categoriesWithCustomTarget.has(cat.id)) {
      rows.push({
        key: `default-${cat.id}`,
        label: cat.name,
        type: cat.type,
        amount: recurringTotal,
        isDefault: true,
        isNameTarget: false,
        target: null,
        categoryObj: cat
      })
    }
  })

  // Sort: Custom first, then Default; alphabetically within each group
  rows.sort((a, b) => {
    if (a.isDefault !== b.isDefault) return a.isDefault ? 1 : -1
    return a.label.localeCompare(b.label)
  })

  return rows
})

const currentPageTargets = ref(1)
const currentPageCategories = ref(1)
const itemsPerPage = 10

const paginatedTargets = computed(() => {
  const start = (currentPageTargets.value - 1) * itemsPerPage
  return mergedTargetRows.value.slice(start, start + itemsPerPage)
})

const paginatedCategories = computed(() => {
  const start = (currentPageCategories.value - 1) * itemsPerPage
  return categories.value.slice(start, start + itemsPerPage)
})

watch(() => mergedTargetRows.value.length, () => {
  currentPageTargets.value = 1
})

watch(() => categories.value.length, () => {
  currentPageCategories.value = 1
})

watch(activeTab, () => {
  currentPageTargets.value = 1
  currentPageCategories.value = 1
})

// Auto-fill form amount when a category is chosen (prefill with recurring total)
watch(() => form.value.category, (catId) => {
  if (!catId || targetMode.value !== 'category') return
  const total = recurringByCategory.value[catId] || 0
  if (total > 0 && !form.value.id) {
    // Only auto-fill for new targets (not edits)
    form.value.amount = total.toFixed(2)
  }
})

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

const fetchSubscriptions = async () => {
  try {
    const res = await api.get('/budgeting/subscriptions/')
    subscriptions.value = res.data
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

// Opens Add Target modal pre-filled for a specific category (used from Default rows)
const openModalForCategory = (cat) => {
  targetMode.value = 'category'
  const recurringTotal = recurringByCategory.value[cat.id] || 0
  form.value = {
    id: null,
    category: cat.id,
    name: '',
    type: cat.type,
    amount: recurringTotal > 0 ? recurringTotal.toFixed(2) : '',
    start_date: null,
    end_date: null
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
      if (!confirm('Are you sure you want to update this target?')) return
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
      if (!confirm('Are you sure you want to update this category?')) return
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
  fetchSubscriptions()
})
</script>
