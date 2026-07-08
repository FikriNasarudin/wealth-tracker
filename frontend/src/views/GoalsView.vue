<template>
  <div class="main-content">
    <header class="flex-responsive" style="margin-bottom: 2rem; gap: 1rem;">
      <div>
        <h1 style="font-weight: 600;">Financial Goals</h1>
        <p class="text-muted">Track your progress towards your financial milestones.</p>
      </div>
      <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
        <button id="tour-create-goal" class="btn btn-primary" @click="showModal = true">+ Create Goal</button>
      </div>
    </header>

    <div v-if="activeGoals.length === 0" class="card text-muted" style="text-align: center; padding: 4rem;">
      <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
      <h3>No Goals Yet</h3>
      <p>Set a goal to start tracking your savings progress.</p>
    </div>
    
    <div v-else style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem;">
      <div v-for="goal in activeGoals" :key="goal.id" class="card" style="position: relative; overflow: hidden;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="font-size: 2rem;">{{ goal.icon || '🎯' }}</div>
            <div>
              <h3 style="margin: 0; font-weight: 600;">{{ goal.name }}</h3>
              <div class="text-muted" style="font-size: 0.875rem;">
                Target: {{ goal.target_date ? goal.target_date : 'No deadline' }}
                <Tooltip title="Target Deadline" description="The date you aim to achieve this financial target." example="Dec 31, 2026" />
              </div>
            </div>
          </div>
          <div style="display: flex; gap: 0.25rem; align-items: center;">
            <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="openEditModal(goal)">✎ Edit</button>
            <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem; color: var(--text-secondary); display: inline-flex;" @click="archiveGoal(goal)" title="Archive Goal">
              <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" /></svg>
            </button>
            <button class="btn btn-danger" style="padding: 0.2rem 0.5rem; font-size: 0.75rem; display: inline-flex;" @click="deleteGoal(goal)" title="Delete Goal">
              <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-weight: 500; margin-bottom: 0.5rem; font-size: 1.125rem;">
          <span>RM{{ formatCurrency(goal.current_amount) }}</span>
          <span class="text-muted">RM{{ formatCurrency(goal.target_amount) }}</span>
        </div>
        
        <div style="width: 100%; height: 12px; background: var(--bg-background); border-radius: 6px; overflow: hidden; margin-bottom: 0.5rem;">
          <div :style="{
            width: Math.min((goal.current_amount / goal.target_amount) * 100, 100) + '%',
            height: '100%',
            background: goal.color || 'var(--primary)'
          }"></div>
        </div>
        
        <div style="text-align: right; font-size: 0.875rem; font-weight: 600;" :style="{ color: goal.color || 'var(--primary)' }">
          {{ Math.round((goal.current_amount / goal.target_amount) * 100) }}% Complete
          <Tooltip title="Goal Progress" description="How close you are to reaching the target amount based on your currently saved balance." />
        </div>
      </div>
    </div>

    <!-- Archived Goals Section -->
    <div v-if="archivedGoals.length > 0" class="card" style="margin-top: 2rem; border-color: rgba(255, 255, 255, 0.03); background: rgba(18, 24, 40, 0.4);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h4 style="font-weight: 600; margin: 0; color: var(--text-secondary); display: flex; align-items: center; gap: 0.5rem;">
          <svg style="width: 18px; height: 18px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" /></svg>
          Archived Goals ({{ archivedGoals.length }})
        </h4>
        <button class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;" @click="showArchived = !showArchived">
          {{ showArchived ? 'Hide' : 'Show' }}
        </button>
      </div>
      
      <div v-if="showArchived" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem;">
        <div v-for="goal in archivedGoals" :key="goal.id" class="card" style="position: relative; overflow: hidden; opacity: 0.6; background: rgba(0, 0, 0, 0.2); padding: 1.25rem;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <div style="font-size: 1.5rem;">{{ goal.icon || '🎯' }}</div>
              <div>
                <h4 style="margin: 0; font-weight: 600; text-decoration: line-through;">{{ goal.name }}</h4>
                <div class="text-muted" style="font-size: 0.8rem;">Target: RM{{ formatCurrency(goal.target_amount) }}</div>
              </div>
            </div>
            <div style="display: flex; gap: 0.25rem; align-items: center;">
              <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" @click="restoreGoal(goal)" title="Restore Goal">
                Restore
              </button>
              <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; display: inline-flex;" @click="deleteGoal(goal)" title="Delete Goal">
                <svg style="width: 14px; height: 14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Modal :show="showModal" :title="isEditing ? 'Edit Goal' : 'Create Goal'" @close="closeModal">
      <form @submit.prevent="saveGoal">
        <div class="form-group">
          <label class="form-label">Goal Name</label>
          <input v-model="form.name" type="text" class="form-input" placeholder="e.g. House Downpayment" required />
        </div>
        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1">
            <label class="form-label">Target Amount (RM)</label>
            <input v-model="form.target_amount" type="number" step="0.01" class="form-input" required />
          </div>
          <div class="form-group" style="flex: 1">
            <label class="form-label">Current Amount (RM)</label>
            <input v-model="form.current_amount" type="number" step="0.01" class="form-input" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Target Date (Optional)</label>
          <input v-model="form.target_date" type="date" class="form-input" />
        </div>
        <div style="display: flex; gap: 1rem;">
          <div class="form-group" style="flex: 1">
            <label class="form-label">Color</label>
            <input v-model="form.color" type="color" class="form-input" style="height: 40px; padding: 0.25rem;" />
          </div>
          <div class="form-group" style="flex: 1">
            <label class="form-label">Icon (Emoji)</label>
            <input v-model="form.icon" type="text" class="form-input" placeholder="e.g. 🏡" />
          </div>
        </div>
        
        <div v-if="isEditing" class="form-group" style="margin-top: 1rem;">
          <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
            <input v-model="form.is_completed" type="checkbox" />
            <span style="font-weight: 500;">Mark as Completed</span>
          </label>
        </div>
        
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Goal' }}
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




const goals = ref([])
const showModal = ref(false)
const isEditing = ref(false)
const loading = ref(false)
const showArchived = ref(false)

const activeGoals = computed(() => goals.value.filter(g => g.is_active !== false))
const archivedGoals = computed(() => goals.value.filter(g => g.is_active === false))

const archiveGoal = async (goal) => {
  if (!confirm(`Are you sure you want to archive "${goal.name}"? It will be hidden from the active list.`)) return
  try {
    await api.patch(`/goals/${goal.id}/`, { is_active: false })
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to archive goal')
  }
}

const restoreGoal = async (goal) => {
  if (!confirm(`Are you sure you want to restore "${goal.name}"?`)) return
  try {
    await api.patch(`/goals/${goal.id}/`, { is_active: true })
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to restore goal')
  }
}

const deleteGoal = async (goal) => {
  if (!confirm(`Are you sure you want to permanently delete "${goal.name}"? This action cannot be undone.`)) return
  try {
    await api.delete(`/goals/${goal.id}/`)
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to delete goal')
  }
}

const getInitialForm = () => ({
  id: null,
  name: '',
  target_amount: '',
  current_amount: 0,
  target_date: '',
  color: '#3B82F6',
  icon: '🎯',
  is_completed: false
})

const form = ref(getInitialForm())

const formatCurrency = (val) => Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchData = async () => {
  try {
    const res = await api.get('/goals/')
    goals.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const openEditModal = (goal) => {
  isEditing.value = true
  form.value = { ...goal }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  isEditing.value = false
  form.value = getInitialForm()
}

const saveGoal = async () => {
  loading.value = true
  try {
    const payload = { ...form.value }
    if (!payload.target_date) delete payload.target_date
    if (payload.current_amount === '') payload.current_amount = 0
    
    if (isEditing.value) {
      if (!confirm('Are you sure you want to update this goal?')) return
      await api.patch(`/goals/${payload.id}/`, payload)
    } else {
      await api.post('/goals/', payload)
    }
    closeModal()
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Failed to save goal')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
