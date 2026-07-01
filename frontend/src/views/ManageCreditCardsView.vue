<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem;">
      <router-link to="/liabilities" class="text-muted" style="display: inline-block; margin-bottom: 0.5rem;">&larr; Back to Liabilities</router-link>
      <h1 style="font-weight: 600;">Manage Credit Cards</h1>
      <p class="text-muted">Cards added here automatically sync with your debt overview and budgeting app.</p>
    </header>

    <!-- Add Credit Card Modal -->
    <Modal :show="showAddModal" title="Add New Credit Card" @close="showAddModal = false">
      <form @submit.prevent="addCard">
        <div class="form-group">
          <label class="form-label">Card Name</label>
          <input v-model="newCardName" type="text" class="form-input" placeholder="e.g. Chase Sapphire Reserve" required />
        </div>
        <div class="form-group">
          <label class="form-label">Credit Limit (RM)</label>
          <input v-model="newCardLimit" type="number" step="0.01" class="form-input" placeholder="e.g. 10000" required />
        </div>
        <div class="form-group">
          <label class="form-label">Interest Rate % (Optional)</label>
          <input v-model="newCardInterest" type="number" step="0.01" class="form-input" placeholder="e.g. 15" />
        </div>
        <div class="form-group">
          <label class="form-label">Current Outstanding (RM)</label>
          <input v-model="newCardBalance" type="number" step="0.01" class="form-input" placeholder="e.g. 1500" />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : 'Add Credit Card' }}
        </button>
      </form>
    </Modal>

    <!-- Edit Credit Card Modal -->
    <Modal :show="showEditModal" title="Edit Credit Card" @close="cancelEditCard">
      <form @submit.prevent="saveCard">
        <div class="form-group">
          <label class="form-label">Card Name</label>
          <input v-model="editingCardName" type="text" class="form-input" placeholder="Card Name" required />
        </div>
        <div class="form-group">
          <label class="form-label">Credit Limit (RM)</label>
          <input v-model="editingCardLimit" type="number" step="0.01" class="form-input" placeholder="Limit" required />
        </div>
        <div class="form-group">
          <label class="form-label">Interest Rate % (Optional)</label>
          <input v-model="editingCardInterest" type="number" step="0.01" class="form-input" placeholder="Interest %" />
        </div>
        <div class="form-group">
          <label class="form-label">Current Outstanding (RM)</label>
          <input v-model="editingCardBalance" type="number" step="0.01" class="form-input" placeholder="Outstanding Balance" title="Update Current Balance" />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Changes' }}
        </button>
      </form>
    </Modal>

    <div class="card" style="max-width: 800px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3 style="font-weight: 600; margin: 0;">
          Your Credit Cards
          <Tooltip title="Your Credit Cards" description="List of your active credit cards. Track their limits, statement cycles, and current balances." example="Maybank Visa, CIMB Mastercard" />
        </h3>
        <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddModal = true">+ Add Card</button>
      </div>
      <ul style="list-style: none; padding: 0;">
        <li v-if="cards.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No credit cards added yet.</li>
        <li v-for="card in cards" :key="card.id" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; gap: 1rem;">
          <div style="display: flex; align-items: center; gap: 1rem; flex: 1; min-width: 250px;">
            <div>
              <div :class="{ 'text-muted': !card.is_active }" style="font-weight: 600; font-size: 1.1rem;">{{ card.name }}</div>
              <div class="text-muted" style="font-size: 0.875rem;">
                Limit: RM{{ Number(card.original_loan_amount).toLocaleString(undefined, {minimumFractionDigits:2}) }} 
                <span v-if="card.interest_rate > 0">| Interest: {{ card.interest_rate }}%</span>
                <span v-if="card.currentBalance !== undefined">| Outstanding: RM{{ Number(card.currentBalance).toLocaleString(undefined, {minimumFractionDigits:2}) }}</span>
              </div>
            </div>
            
            <span v-if="!card.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <button @click="openEditCard(card)" class="btn btn-secondary" style="padding: 0.25rem 0.75rem;">Edit</button>
            <button @click="toggleCardStatus(card)" class="btn btn-secondary" style="padding: 0.25rem 0.75rem;" :class="{ 'text-success': !card.is_active, 'text-danger': card.is_active }">
              {{ card.is_active ? 'Archive' : 'Restore' }}
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import Tooltip from '@/components/Tooltip.vue'

const creditCardCategoryId = ref(null)
const cards = ref([])
const newCardName = ref('')
const newCardLimit = ref('')
const newCardInterest = ref('')
const newCardBalance = ref('')
const loading = ref(false)
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingCardId = ref(null)
const editingCardName = ref('')
const editingCardLimit = ref('')
const editingCardInterest = ref('')
const editingCardBalance = ref('')

const setupCreditCardCategory = async () => {
  try {
    const res = await api.get('/liabilities/categories/')
    const categories = res.data
    
    // Look for an existing category named exactly "Credit Cards"
    const existing = categories.find(c => c.name.toLowerCase() === 'credit cards')
    if (existing) {
      creditCardCategoryId.value = existing.id
    } else {
      // Create it if it doesn't exist
      const createRes = await api.post('/liabilities/categories/', { name: 'Credit Cards' })
      creditCardCategoryId.value = createRes.data.id
    }
  } catch (e) {
    console.error("Failed to setup credit card category", e)
  }
}

const fetchCards = async () => {
  if (!creditCardCategoryId.value) return
  try {
    const res = await api.get('/liabilities/lenders/')
    
    const d = new Date()
    const m = d.getMonth() + 1
    const y = d.getFullYear()
    let snaps = []
    try {
      const snapsRes = await api.get(`/liabilities/snapshots/?month=${m}&year=${y}`)
      snaps = snapsRes.data
    } catch(err) {
      console.warn("Failed to fetch snapshots", err)
    }

    cards.value = res.data
      .filter(l => l.category === creditCardCategoryId.value)
      .map(c => {
        const snap = snaps.find(s => s.lender === c.id)
        const currentBalance = snap ? snap.remaining_principal : 0
        return {
          ...c,
          currentBalance: currentBalance
        }
      })
  } catch (e) {
    console.error("Failed to fetch cards", e)
  }
}

const addCard = async () => {
  if (!newCardName.value.trim() || !newCardLimit.value || !creditCardCategoryId.value) return
  loading.value = true
  try {
    const res = await api.post('/liabilities/lenders/', {
      name: newCardName.value,
      category: creditCardCategoryId.value,
      original_loan_amount: newCardLimit.value,
      interest_rate: newCardInterest.value || 0
    })
    
    // Automatically log current outstanding balance if provided
    if (newCardBalance.value) {
      const d = new Date()
      await api.post('/liabilities/snapshots/', {
        month: d.getMonth() + 1,
        year: d.getFullYear(),
        category: creditCardCategoryId.value,
        lender: res.data.id,
        original_loan_amount: newCardLimit.value,
        remaining_principal: newCardBalance.value,
        monthly_payment: 0
      })
    }

    newCardName.value = ''
    newCardLimit.value = ''
    newCardInterest.value = ''
    newCardBalance.value = ''
    showAddModal.value = false
    await fetchCards()
  } catch (e) {
    console.error("Failed to add card", e)
    alert("Failed to add credit card.")
  } finally {
    loading.value = false
  }
}

const openEditCard = (card) => {
  editingCardId.value = card.id
  editingCardName.value = card.name
  editingCardLimit.value = card.original_loan_amount || ''
  editingCardInterest.value = card.interest_rate || ''
  editingCardBalance.value = card.currentBalance || ''
  showEditModal.value = true
}

const cancelEditCard = () => {
  showEditModal.value = false
  editingCardId.value = null
  editingCardName.value = ''
  editingCardLimit.value = ''
  editingCardInterest.value = ''
  editingCardBalance.value = ''
}

const saveCard = async () => {
  if (!editingCardId.value || !editingCardName.value.trim() || !editingCardLimit.value) return
  loading.value = true
  try {
    await api.patch(`/liabilities/lenders/${editingCardId.value}/`, {
      name: editingCardName.value,
      original_loan_amount: editingCardLimit.value,
      interest_rate: editingCardInterest.value || 0
    })
    
    // Update outstanding balance snapshot if provided
    if (editingCardBalance.value !== '') {
      const d = new Date()
      const m = d.getMonth() + 1
      const y = d.getFullYear()
      // try to fetch existing snapshot to update, or create a new one
      try {
        const snapsRes = await api.get(`/liabilities/snapshots/?month=${m}&year=${y}&lender=${editingCardId.value}`)
        if (snapsRes.data.length > 0) {
          await api.patch(`/liabilities/snapshots/${snapsRes.data[0].id}/`, {
            remaining_principal: editingCardBalance.value
          })
        } else {
          await api.post('/liabilities/snapshots/', {
            month: m,
            year: y,
            category: creditCardCategoryId.value,
            lender: editingCardId.value,
            original_loan_amount: editingCardLimit.value,
            remaining_principal: editingCardBalance.value,
            monthly_payment: 0
          })
        }
      } catch(err) {
        console.error("Failed to update snapshot balance", err)
      }
    }

    cancelEditCard()
    await fetchCards()
  } catch (e) {
    console.error("Failed to save card", e)
    alert("Failed to save credit card.")
  } finally {
    loading.value = false
  }
}

const toggleCardStatus = async (card) => {
  try {
    const newStatus = !card.is_active
    await api.patch(`/liabilities/lenders/${card.id}/`, { is_active: newStatus })
    card.is_active = newStatus
  } catch (e) {
    console.error("Failed to toggle status", e)
  }
}

onMounted(async () => {
  await setupCreditCardCategory()
  await fetchCards()
})
</script>
