<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <router-link to="/liabilities" class="text-muted" style="display: inline-block; margin-bottom: 0.5rem;">&larr; Back to Liabilities</router-link>
        <h1 style="font-weight: 600;">Manage Credit Cards</h1>
        <p class="text-muted">Cards added here automatically sync with your debt overview and budgeting app.</p>
      </div>
    </header>

    <div class="card" style="margin-bottom: 2rem; max-width: 800px;">
      <h3 style="margin-bottom: 1rem; font-weight: 600;">Add New Credit Card</h3>
      <form @submit.prevent="addCard" class="form-group" style="display: flex; gap: 1rem; align-items: flex-end;">
        <div style="flex: 2;">
          <label class="form-label">Card Name</label>
          <input v-model="newCardName" type="text" class="form-input" placeholder="e.g. Chase Sapphire Reserve" required />
        </div>
        <div style="flex: 1;">
          <label class="form-label">Credit Limit (RM)</label>
          <input v-model="newCardLimit" type="number" step="0.01" class="form-input" placeholder="e.g. 10000" required />
        </div>
        <div style="flex: 1;">
          <label class="form-label">Interest Rate % (Optional)</label>
          <input v-model="newCardInterest" type="number" step="0.01" class="form-input" placeholder="e.g. 15" />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading" style="padding: 0.75rem 1.5rem;">Add Card</button>
      </form>
    </div>

    <div class="card" style="max-width: 800px;">
      <h3 style="margin-bottom: 1rem; font-weight: 600;">Your Credit Cards</h3>
      <ul style="list-style: none; padding: 0;">
        <li v-if="cards.length === 0" class="text-muted" style="text-align: center; padding: 2rem;">No credit cards added yet.</li>
        <li v-for="card in cards" :key="card.id" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--border-color);">
          <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
            <template v-if="!card.isEditing">
              <div>
                <div :class="{ 'text-muted': !card.is_active }" style="font-weight: 600; font-size: 1.1rem;">{{ card.name }}</div>
                <div class="text-muted" style="font-size: 0.875rem;">Limit: RM{{ Number(card.original_loan_amount).toLocaleString(undefined, {minimumFractionDigits:2}) }} <span v-if="card.interest_rate > 0">| Interest: {{ card.interest_rate }}%</span></div>
              </div>
            </template>
            <template v-else>
              <div style="display: flex; gap: 0.5rem; flex: 1;">
                <input v-model="card.editName" type="text" class="form-input" style="flex: 2;" placeholder="Card Name" />
                <input v-model="card.editLimit" type="number" step="0.01" class="form-input" style="flex: 1;" placeholder="Credit Limit" />
                <input v-model="card.editInterest" type="number" step="0.01" class="form-input" style="flex: 1;" placeholder="Interest %" />
              </div>
            </template>
            
            <span v-if="!card.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
          </div>
          <div style="display: flex; gap: 0.5rem; margin-left: 1rem;">
            <button v-if="!card.isEditing" @click="editCard(card)" class="btn btn-secondary" style="padding: 0.25rem 0.75rem;">Edit</button>
            <button v-else @click="saveCard(card)" class="btn btn-primary" style="padding: 0.25rem 0.75rem;">Save</button>
            
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

const creditCardCategoryId = ref(null)
const cards = ref([])
const newCardName = ref('')
const newCardLimit = ref('')
const newCardInterest = ref('')
const loading = ref(false)

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
    cards.value = res.data
      .filter(l => l.category === creditCardCategoryId.value)
      .map(c => ({
        ...c,
        isEditing: false,
        editName: c.name,
        editLimit: c.original_loan_amount || '',
        editInterest: c.interest_rate || ''
      }))
  } catch (e) {
    console.error("Failed to fetch cards", e)
  }
}

const addCard = async () => {
  if (!newCardName.value.trim() || !newCardLimit.value || !creditCardCategoryId.value) return
  loading.value = true
  try {
    await api.post('/liabilities/lenders/', {
      name: newCardName.value,
      category: creditCardCategoryId.value,
      original_loan_amount: newCardLimit.value,
      interest_rate: newCardInterest.value || 0
    })
    newCardName.value = ''
    newCardLimit.value = ''
    newCardInterest.value = ''
    await fetchCards()
  } catch (e) {
    console.error("Failed to add card", e)
    alert("Failed to add credit card.")
  } finally {
    loading.value = false
  }
}

const editCard = (card) => {
  card.isEditing = true
}

const saveCard = async (card) => {
  try {
    await api.patch(`/liabilities/lenders/${card.id}/`, {
      name: card.editName,
      original_loan_amount: card.editLimit,
      interest_rate: card.editInterest || 0
    })
    card.name = card.editName
    card.original_loan_amount = card.editLimit
    card.interest_rate = card.editInterest || 0
    card.isEditing = false
  } catch (e) {
    console.error("Failed to save card", e)
    alert("Failed to save credit card.")
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
