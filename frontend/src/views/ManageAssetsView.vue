<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem;">
      <router-link to="/assets" class="text-muted" style="display: inline-block; margin-bottom: 0.5rem;">&larr; Back to Assets</router-link>
      <h1 style="font-weight: 600;">Manage Platforms & Categories</h1>
    </header>

    <!-- Add Category Modal -->
    <Modal :show="showAddCategoryModal" title="Add Platform Category" @close="showAddCategoryModal = false">
      <form @submit.prevent="addCategory">
        <div class="form-group">
          <label class="form-label">Category Name</label>
          <input v-model="newCategoryName" type="text" class="form-input" placeholder="e.g. Stocks, Crypto" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.cat">
          {{ loading.cat ? 'Saving...' : 'Add Category' }}
        </button>
      </form>
    </Modal>

    <!-- Add Platform Modal -->
    <Modal :show="showAddPlatformModal" title="Add Platform" @close="showAddPlatformModal = false">
      <form @submit.prevent="addPlatform">
        <div class="form-group">
          <label class="form-label">Platform Name</label>
          <input v-model="newPlatformName" type="text" class="form-input" placeholder="e.g. Binance, Luno" required />
        </div>
        <div class="form-group">
          <label class="form-label">Category</label>
          <SearchableSelect v-model="newPlatformCategoryId" :options="activeCategoryOptions" placeholder="Select Category" />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.plat">
          {{ loading.plat ? 'Saving...' : 'Add Platform' }}
        </button>
      </form>
    </Modal>

    <div class="grid-2col">
      <!-- Categories Section -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">Categories</h3>
          <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddCategoryModal = true">+ Add Category</button>
        </div>

        <ul style="list-style: none; padding: 0;">
          <li v-for="cat in categories" :key="cat.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1; flex-wrap: wrap;">
              <span v-if="!cat.isEditing" :class="{ 'text-muted': !cat.is_active }">{{ cat.name }}</span>
              <input v-else v-model="cat.editName" type="text" class="form-input" style="padding: 0.25rem 0.5rem; margin-right: 0.5rem; min-width: 120px;" @keyup.enter="saveCategory(cat)" />
              
              <span v-if="!cat.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
              <span v-if="cat.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <template v-if="!cat.is_default">
                <template v-if="!cat.isEditing">
                  <button @click="editCategory(cat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
                  <button @click="toggleCategoryStatus(cat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !cat.is_active, 'text-danger': cat.is_active }">
                    {{ cat.is_active ? 'Archive' : 'Unarchive' }}
                  </button>
                </template>
                <template v-else>
                  <button @click="saveCategory(cat)" class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Save</button>
                  <button @click="cat.isEditing = false" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Cancel</button>
                </template>
              </template>
            </div>
          </li>
        </ul>
      </div>

      <!-- Platforms Section -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">Platforms</h3>
          <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddPlatformModal = true">+ Add Platform</button>
        </div>

        <ul style="list-style: none; padding: 0;">
          <li v-for="plat in platforms" :key="plat.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; gap: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1; min-width: 200px; flex-wrap: wrap;">
              <template v-if="!plat.isEditing">
                <span :class="{ 'text-muted': !plat.is_active }">{{ plat.name }}</span>
                <span class="text-muted" style="font-size: 0.875rem; margin-left: 0.5rem;">({{ getCategoryName(plat.category) }})</span>
              </template>
              <template v-else>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; width: 100%;">
                  <input v-model="plat.editName" type="text" class="form-input" style="padding: 0.25rem 0.5rem; flex: 1; min-width: 100px;" />
                  <select v-model="plat.editCategoryId" class="form-input" style="padding: 0.25rem 0.5rem; flex: 1; min-width: 100px;">
                    <option value="" disabled>Select Category</option>
                    <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </div>
              </template>
              
              <span v-if="!plat.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
              <span v-if="plat.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <template v-if="!plat.is_default">
                <template v-if="!plat.isEditing">
                  <button @click="editPlatform(plat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
                  <button @click="togglePlatformStatus(plat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !plat.is_active, 'text-danger': plat.is_active }">
                    {{ plat.is_active ? 'Archive' : 'Unarchive' }}
                  </button>
                </template>
                <template v-else>
                  <button @click="savePlatform(plat)" class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Save</button>
                  <button @click="plat.isEditing = false" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Cancel</button>
                </template>
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
import Modal from '@/components/Modal.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'

const categories = ref([])
const platforms = ref([])
const newCategoryName = ref('')
const newPlatformName = ref('')
const newPlatformCategoryId = ref('')
const loading = ref({ cat: false, plat: false })
const showAddCategoryModal = ref(false)
const showAddPlatformModal = ref(false)

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
    const res = await api.get('/assets/categories/')
    categories.value = res.data.map(c => ({ ...c, isEditing: false, editName: c.name }))
  } catch (e) { console.error(e) }
}

const fetchPlatforms = async () => {
  try {
    const res = await api.get('/assets/platforms/')
    platforms.value = res.data.map(p => ({ ...p, isEditing: false, editName: p.name, editCategoryId: p.category || '' }))
  } catch (e) { console.error(e) }
}

const addCategory = async () => {
  if (!newCategoryName.value.trim()) return
  loading.value.cat = true
  try {
    await api.post('/assets/categories/', { name: newCategoryName.value })
    newCategoryName.value = ''
    showAddCategoryModal.value = false
    await fetchCategories()
  } catch (e) { console.error(e) } finally { loading.value.cat = false }
}

const addPlatform = async () => {
  if (!newPlatformName.value.trim() || !newPlatformCategoryId.value) return
  loading.value.plat = true
  try {
    await api.post('/assets/platforms/', { 
      name: newPlatformName.value,
      category: newPlatformCategoryId.value
    })
    newPlatformName.value = ''
    newPlatformCategoryId.value = ''
    showAddPlatformModal.value = false
    await fetchPlatforms()
  } catch (e) { console.error(e) } finally { loading.value.plat = false }
}

const editCategory = (cat) => {
  cat.isEditing = true
}

const saveCategory = async (cat) => {
  try {
    await api.patch(`/assets/categories/${cat.id}/`, { name: cat.editName })
    cat.name = cat.editName
    cat.isEditing = false
  } catch (e) { console.error(e) }
}

const toggleCategoryStatus = async (cat) => {
  try {
    const newStatus = !cat.is_active
    await api.patch(`/assets/categories/${cat.id}/`, { is_active: newStatus })
    cat.is_active = newStatus
  } catch (e) { console.error(e) }
}

const editPlatform = (plat) => {
  plat.editCategoryId = plat.category || ''
  plat.isEditing = true
}

const savePlatform = async (plat) => {
  try {
    await api.patch(`/assets/platforms/${plat.id}/`, { 
      name: plat.editName,
      category: plat.editCategoryId
    })
    plat.name = plat.editName
    plat.category = plat.editCategoryId
    plat.isEditing = false
  } catch (e) { console.error(e) }
}

const togglePlatformStatus = async (plat) => {
  try {
    const newStatus = !plat.is_active
    await api.patch(`/assets/platforms/${plat.id}/`, { is_active: newStatus })
    plat.is_active = newStatus
  } catch (e) { console.error(e) }
}

onMounted(() => {
  fetchCategories()
  fetchPlatforms()
})
</script>
