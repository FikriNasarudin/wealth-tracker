<template>
  <div class="main-content">
    <header style="margin-bottom: 2rem;">
      <router-link to="/assets" class="text-muted" style="display: inline-block; margin-bottom: 0.5rem;">&larr; Back to Assets</router-link>
      <h1 style="font-weight: 600;">Manage Platforms, Categories & Assets</h1>
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

    <!-- Add Platform Modal -->
    <Modal :show="showAddPlatformModal" title="Add Platform" @close="showAddPlatformModal = false">
      <form @submit.prevent="addPlatform">
        <div class="form-group">
          <label class="form-label">Platform Name</label>
          <input v-model="newPlatformName" type="text" class="form-input" placeholder="e.g. Binance, Luno" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.plat">
          {{ loading.plat ? 'Saving...' : 'Add Platform' }}
        </button>
      </form>
    </Modal>

    <!-- Edit Platform Modal -->
    <Modal :show="showEditPlatformModal" title="Edit Platform" @close="cancelEditPlatform">
      <form @submit.prevent="savePlatform" v-if="editingPlatform">
        <div class="form-group">
          <label class="form-label">Platform Name</label>
          <input v-model="editingPlatform.editName" type="text" class="form-input" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.plat">
          {{ loading.plat ? 'Saving...' : 'Save Changes' }}
        </button>
      </form>
    </Modal>

    <!-- Add Asset Modal -->
    <Modal :show="showAddAssetModal" title="Add Asset" @close="showAddAssetModal = false">
      <form @submit.prevent="addAsset">
        <div class="form-group">
          <label class="form-label">Asset Name</label>
          <input v-model="newAssetName" type="text" class="form-input" placeholder="e.g. Bitcoin, Apple Inc." required />
        </div>
        <div class="form-group">
          <label class="form-label">Category</label>
          <SearchableSelect v-model="newAssetCategoryId" :options="activeCategoryOptions" placeholder="Select Category" />
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.asset">
          {{ loading.asset ? 'Saving...' : 'Add Asset' }}
        </button>
      </form>
    </Modal>

    <!-- Edit Asset Modal -->
    <Modal :show="showEditAssetModal" title="Edit Asset" @close="cancelEditAsset">
      <form @submit.prevent="saveAsset" v-if="editingAsset">
        <div class="form-group">
          <label class="form-label">Asset Name</label>
          <input v-model="editingAsset.editName" type="text" class="form-input" required />
        </div>
        <div class="form-group">
          <label class="form-label">Category</label>
          <select v-model="editingAsset.editCategoryId" class="form-input" required>
            <option value="" disabled>Select Category</option>
            <option v-for="cat in activeCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%" :disabled="loading.asset">
          {{ loading.asset ? 'Saving...' : 'Save Changes' }}
        </button>
      </form>
    </Modal>

    <div class="grid-2col" style="margin-bottom: 2rem;">
      <!-- Categories Section -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Categories
            <Tooltip title="Asset Categories" description="Categorize your investment platforms into classes like Stocks, Crypto, Real Estate, etc." example="Stocks, Cash, Retirement" />
          </h3>
          <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddCategoryModal = true">+ Add Category</button>
        </div>

        <ul style="list-style: none; padding: 0;">
          <li v-for="cat in categories" :key="cat.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1; flex-wrap: wrap;">
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
            <p class="text-muted" style="margin: 0.5rem 0 0; font-size: 0.875rem;">No categories yet. Create one first before adding platforms.</p>
          </li>
        </ul>
      </div>
 
      <!-- Platforms Section -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-weight: 600; margin: 0;">
            Platforms
            <Tooltip title="Investment Platforms" description="Define the platforms, brokers, or apps where your assets are held." example="IBKR, Luno, EPF, etc." />
          </h3>
          <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddPlatformModal = true">+ Add Platform</button>
        </div>
 
        <ul style="list-style: none; padding: 0;">
          <li v-if="platforms.length === 0" style="padding: 1.5rem; text-align: center;">
            <span style="font-size: 1.5rem;">📦</span>
            <p class="text-muted" style="margin: 0.5rem 0 0; font-size: 0.875rem;">No platforms yet. Add a platform to track assets like Binance, ASB, etc.</p>
          </li>
          <li v-for="plat in platforms" :key="plat.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; gap: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1; min-width: 200px; flex-wrap: wrap;">
              <span :class="{ 'text-muted': !plat.is_active }">{{ plat.name }}</span>
              
              <span v-if="!plat.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
              <span v-if="plat.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <template v-if="!plat.is_default">
                <button @click="openEditPlatform(plat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
                <button @click="togglePlatformStatus(plat)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !plat.is_active, 'text-danger': plat.is_active }">
                  {{ plat.is_active ? 'Archive' : 'Unarchive' }}
                </button>
              </template>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Assets Section -->
    <div class="card" style="margin-top: 2rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3 style="font-weight: 600; margin: 0;">
          Assets
          <Tooltip title="Investment Assets" description="Specific assets that are held within your platforms, tied to category types." example="Bitcoin, ETH, Apple Stock, TSLA, S&P 500" />
        </h3>
        <button class="btn btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.875rem;" @click="showAddAssetModal = true">+ Add Asset</button>
      </div>

      <ul style="list-style: none; padding: 0;">
        <li v-if="assets.length === 0" style="padding: 1.5rem; text-align: center;">
          <span style="font-size: 1.5rem;">📈</span>
          <p class="text-muted" style="margin: 0.5rem 0 0; font-size: 0.875rem;">No assets yet. Create assets that you can map to snapshots.</p>
        </li>
        <li v-for="asset in assets" :key="asset.id" style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; gap: 0.5rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1; min-width: 200px; flex-wrap: wrap;">
            <span :class="{ 'text-muted': !asset.is_active }">{{ asset.name }}</span>
            <span class="text-muted" style="font-size: 0.875rem; margin-left: 0.5rem;">({{ getCategoryName(asset.category) }})</span>
            
            <span v-if="!asset.is_active" class="text-danger" style="font-size: 0.75rem; border: 1px solid var(--danger); padding: 0.1rem 0.3rem; border-radius: 4px;">Archived</span>
            <span v-if="asset.is_default" class="text-muted" style="font-size: 0.75rem; border: 1px solid var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px;">Default</span>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <template v-if="!asset.is_default">
              <button @click="openEditAsset(asset)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">Edit</button>
              <button @click="toggleAssetStatus(asset)" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" :class="{ 'text-success': !asset.is_active, 'text-danger': asset.is_active }">
                {{ asset.is_active ? 'Archive' : 'Unarchive' }}
              </button>
            </template>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Modal from '@/components/Modal.vue'
import SearchableSelect from '@/components/SearchableSelect.vue'
import Tooltip from '@/components/Tooltip.vue'

const categories = ref([])
const platforms = ref([])
const assets = ref([])

const newCategoryName = ref('')
const newPlatformName = ref('')
const newPlatformCategoryId = ref('')
const newAssetName = ref('')
const newAssetCategoryId = ref('')

const loading = ref({ cat: false, plat: false, asset: false })

const showAddCategoryModal = ref(false)
const showAddPlatformModal = ref(false)
const showAddAssetModal = ref(false)

const showEditCategoryModal = ref(false)
const editingCategory = ref(null)

const showEditPlatformModal = ref(false)
const editingPlatform = ref(null)

const showEditAssetModal = ref(false)
const editingAsset = ref(null)

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
    platforms.value = res.data.map(p => ({ ...p, isEditing: false, editName: p.name }))
  } catch (e) { console.error(e) }
}

const fetchAssets = async () => {
  try {
    const res = await api.get('/assets/assets/')
    assets.value = res.data.map(a => ({ ...a, isEditing: false, editName: a.name, editCategoryId: a.category || '' }))
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
  if (!newPlatformName.value.trim()) return
  loading.value.plat = true
  try {
    await api.post('/assets/platforms/', { 
      name: newPlatformName.value
    })
    newPlatformName.value = ''
    showAddPlatformModal.value = false
    await fetchPlatforms()
  } catch (e) { console.error(e) } finally { loading.value.plat = false }
}

const addAsset = async () => {
  if (!newAssetName.value.trim() || !newAssetCategoryId.value) return
  loading.value.asset = true
  try {
    await api.post('/assets/assets/', { 
      name: newAssetName.value,
      category: newAssetCategoryId.value
    })
    newAssetName.value = ''
    newAssetCategoryId.value = ''
    showAddAssetModal.value = false
    await fetchAssets()
  } catch (e) { console.error(e) } finally { loading.value.asset = false }
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
    await api.patch(`/assets/categories/${cat.id}/`, { name: cat.editName })
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
    await api.patch(`/assets/categories/${cat.id}/`, { is_active: newStatus })
    cat.is_active = newStatus
  } catch (e) { console.error(e) }
}

const openEditPlatform = (plat) => {
  editingPlatform.value = {
    ...plat,
    editName: plat.name
  }
  showEditPlatformModal.value = true
}

const cancelEditPlatform = () => {
  showEditPlatformModal.value = false
  editingPlatform.value = null
}

const savePlatform = async () => {
  const plat = editingPlatform.value
  if (!plat || !plat.editName.trim()) return
  loading.value.plat = true
  try {
    await api.patch(`/assets/platforms/${plat.id}/`, { 
      name: plat.editName
    })
    cancelEditPlatform()
    await fetchPlatforms()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value.plat = false
  }
}

const togglePlatformStatus = async (plat) => {
  try {
    const newStatus = !plat.is_active
    await api.patch(`/assets/platforms/${plat.id}/`, { is_active: newStatus })
    plat.is_active = newStatus
  } catch (e) { console.error(e) }
}

const openEditAsset = (asset) => {
  editingAsset.value = {
    ...asset,
    editName: asset.name,
    editCategoryId: asset.category || ''
  }
  showEditAssetModal.value = true
}

const cancelEditAsset = () => {
  showEditAssetModal.value = false
  editingAsset.value = null
}

const saveAsset = async () => {
  const asset = editingAsset.value
  if (!asset || !asset.editName.trim() || !asset.editCategoryId) return
  loading.value.asset = true
  try {
    await api.patch(`/assets/assets/${asset.id}/`, { 
      name: asset.editName,
      category: asset.editCategoryId
    })
    cancelEditAsset()
    await fetchAssets()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value.asset = false
  }
}

const toggleAssetStatus = async (asset) => {
  try {
    const newStatus = !asset.is_active
    await api.patch(`/assets/assets/${asset.id}/`, { is_active: newStatus })
    asset.is_active = newStatus
  } catch (e) { console.error(e) }
}

onMounted(() => {
  fetchCategories()
  fetchPlatforms()
  fetchAssets()
})
</script>
