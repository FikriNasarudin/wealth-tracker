<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1 style="font-weight: 600;">Manage Categories & Platforms</h1>
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

      <!-- Platforms Section -->
      <div class="card">
        <h3 style="margin-bottom: 1rem; font-weight: 600;">Platforms</h3>
        <form @submit.prevent="addPlatform" class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem;">
          <div style="display: flex; gap: 0.5rem;">
            <input v-model="newPlatformName" type="text" class="form-input" placeholder="New Platform Name" required style="flex: 1" />
            <select v-model="newPlatformCategoryId" class="form-input" style="flex: 1" required>
              <option value="" disabled>Select Category</option>
              <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
            <button type="submit" class="btn btn-primary" :disabled="loading.plat">Add</button>
          </div>
        </form>
        <ul style="list-style: none; padding: 0;">
          <li v-for="plat in platforms" :key="plat.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1;">
              <template v-if="!plat.isEditing">
                <span :class="{ 'text-muted': !plat.is_active }">{{ plat.name }}</span>
                <span class="text-muted" style="font-size: 0.875rem; margin-left: 0.5rem;">({{ getCategoryName(plat.category) }})</span>
              </template>
              <template v-else>
                <input v-model="plat.editName" type="text" class="form-input" style="padding: 0.25rem 0.5rem; flex: 1;" />
                <select v-model="plat.editCategoryId" class="form-input" style="padding: 0.25rem 0.5rem; flex: 1;">
                  <option value="" disabled>Select Category</option>
                  <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                </select>
              </template>
              
              <span v-if="!plat.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
              <span v-if="plat.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
            </div>
            <div style="display: flex; gap: 0.5rem; margin-left: 1rem;">
              <template v-if="!plat.is_default">
                <button v-if="!plat.isEditing" @click="editPlatform(plat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
                <button v-else @click="savePlatform(plat)" class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Save</button>
                <button @click="togglePlatformStatus(plat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !plat.is_active, 'text-danger': plat.is_active }">
                  {{ plat.is_active ? 'Archive' : 'Unarchive' }}
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
const platforms = ref([])
const newCategoryName = ref('')
const newPlatformName = ref('')
const newPlatformCategoryId = ref('')
const loading = ref({ cat: false, plat: false })

const activeCategories = computed(() => categories.value.filter(c => c.is_active))

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
