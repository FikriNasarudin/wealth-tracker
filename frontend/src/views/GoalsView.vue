<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Financial Goals</h1>
        <p class="text-muted">Track your progress towards your financial milestones.</p>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <button class="btn btn-secondary" @click="startTour" style="padding: 0.5rem 1rem; font-size: 0.875rem;">
          <svg style="width: 16px; height: 16px; display: inline; vertical-align: middle; margin-right: 0.25rem;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          Help
        </button>
        <button id="tour-create-goal" class="btn btn-primary" @click="showModal = true">+ Create Goal</button>
      </div>
    </header>

    <div v-if="goals.length === 0" class="card text-muted" style="text-align: center; padding: 4rem;">
      <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
      <h3>No Goals Yet</h3>
      <p>Set a goal to start tracking your savings progress.</p>
    </div>
    
    <div v-else style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem;">
      <div v-for="goal in goals" :key="goal.id" class="card" style="position: relative; overflow: hidden;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="font-size: 2rem;">{{ goal.icon || '🎯' }}</div>
            <div>
              <h3 style="margin: 0; font-weight: 600;">{{ goal.name }}</h3>
              <div class="text-muted" style="font-size: 0.875rem;">
                Target: {{ goal.target_date ? goal.target_date : 'No deadline' }}
                <Tooltip title="Target Date" description="The deadline you have set to achieve this financial goal." example="Dec 31, 2026" />
              </div>
            </div>
          </div>
          <button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;" @click="openEditModal(goal)">✎ Edit</button>
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
          <Tooltip title="Completion Percentage" description="How close you are to reaching your target amount." example="RM5,000 / RM10,000 = 50% Complete" />
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
import { ref, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import Tooltip from '@/components/Tooltip.vue'
import { driver } from 'driver.js'

const startTour = () => {
  const driverObj = driver({
    showProgress: true,
    steps: [
      { element: '#tour-create-goal', popover: { title: 'Create Goal', description: 'Click here to set up a new financial goal with a target amount and deadline.' } },
      { popover: { title: 'Manage Goals', description: 'Once you create a goal, it will appear here. You can click "Edit" to update your current saved amount at any time.' } }
    ]
  });
  driverObj.drive();
}

const goals = ref([])
const showModal = ref(false)
const isEditing = ref(false)
const loading = ref(false)

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
