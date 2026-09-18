<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { storeToRefs } from 'pinia'
import { useAppStore } from './store'
import { supabase } from './supabase'

import MapArea from './components/MapArea.vue'
import DesktopSidebar from './components/DesktopSidebar.vue'
import MobileBottomNav from './components/MobileBottomNav.vue'
import SubmissionForm from './components/SubmissionForm.vue'
import AuthModals from './components/AuthModals.vue'

axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('supabase_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const store = useAppStore()
const { user, draftPosition } = storeToRefs(store)

const showAuthModal = ref(false)
const mobileActiveTab = ref('map') 

const handleLogout = async () => {
  await supabase.auth.signOut()
  store.setUser(null)
  localStorage.removeItem('supabase_token')
  mobileActiveTab.value = 'map'
}

const resetToExplore = () => {
  mobileActiveTab.value = 'map'       
  store.draftPosition = null          
  store.center = [41.90, 12.49]       
  store.zoom = 6                      
}

const handleMobileTabChange = (tab) => {
  mobileActiveTab.value = tab
  if (tab === 'map') {
    store.draftPosition = null
    store.center = [41.90, 12.49]
    store.zoom = 6
  }
}

onMounted(() => {
  supabase.auth.getSession().then(({ data: { session } }) => {
    if (session) { 
      store.setUser(session.user)
      localStorage.setItem('supabase_token', session.access_token) 
    }
  })
  store.fetchSpots()
})
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo">
        <img src="/logo.png" alt="Logo ParkAbile" class="logo-img" />
        ParkAbile
      </div>
      <nav class="header-nav">
        <a href="#" class="nav-link hide-mobile" :class="{ 'active-link': mobileActiveTab === 'map' }" @click.prevent="resetToExplore">Esplora</a>
        <a href="#" class="nav-link hide-mobile" :class="{ 'active-link': mobileActiveTab === 'about' }" @click.prevent="mobileActiveTab = 'about'">Chi siamo</a>
        <a href="#" class="nav-link hide-mobile" :class="{ 'active-link': mobileActiveTab === 'contact' }" @click.prevent="mobileActiveTab = 'contact'">Contattaci</a>
        <a href="#" class="nav-link hide-mobile" :class="{ 'active-link': mobileActiveTab === 'profile' }" v-if="user" @click.prevent="mobileActiveTab = 'profile'">Profilo</a>

        <!-- Il tasto logout è sparito da qui, rimane solo Accedi -->
        <button v-if="!user" class="btn-login" @click="showAuthModal = true">Accedi</button>
      </nav>
    </header>

    <div class="app-content">
      <main class="main-map">
        <MapArea />
      </main>

      <div class="side-panel" :class="{ 'mobile-active': mobileActiveTab !== 'map' || draftPosition }">
        <SubmissionForm 
          v-if="draftPosition" 
          @close="store.draftPosition = null" 
          @require-login="showAuthModal = true" 
        />
        <DesktopSidebar 
          v-else 
          :active-tab="mobileActiveTab === 'map' ? 'all' : mobileActiveTab" 
          @close-sheet="mobileActiveTab = 'map'"
          @logout="handleLogout"
        />
      </div>
    </div>

    <MobileBottomNav @change-tab="handleMobileTabChange" />
    <AuthModals v-if="showAuthModal" @close="showAuthModal = false" />
  </div>
</template>

<style>
/* PALETTE MODERNA: Indaco e Ardesia */
:root {
  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --bg-color: #f8fafc;
  --surface: #ffffff;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --border-light: #e2e8f0;
}

body { margin: 0; padding: 0; font-family: 'Inter', system-ui, -apple-system, sans-serif; overflow: hidden; background: var(--bg-color); color: var(--text-main);}
.app-container { display: flex; height: 100vh; width: 100vw; flex-direction: column; }

.app-header { display: flex; justify-content: space-between; align-items: center; padding: 0 25px; height: 70px; background: var(--surface); border-bottom: 1px solid var(--border-light); z-index: 2000; flex-shrink: 0; }
.logo { display: flex; align-items: center; font-size: 22px; font-weight: 800; color: var(--text-main); letter-spacing: -0.5px;}
.logo-img { height: 50px; width: auto; margin-right: 12px; border-radius: 4px; }

.header-nav { display: flex; align-items: center; gap: 28px; }
.nav-link { text-decoration: none; color: var(--text-muted); font-weight: 600; font-size: 15px; transition: color 0.2s; padding: 5px 0;}
.nav-link:hover { color: var(--primary); }
.active-link { color: var(--primary); border-bottom: 2px solid var(--primary); }

.btn-login { background: var(--primary); color: white; border: none; padding: 10px 22px; border-radius: 10px; font-weight: 600; font-size: 14px; cursor: pointer; transition: background 0.2s, transform 0.1s;}
.btn-login:hover { background: var(--primary-hover); transform: translateY(-1px);}

.app-content { display: flex; flex: 1; overflow: hidden; position: relative; flex-direction: row; }
.main-map { flex-grow: 1; height: 100%; position: relative; z-index: 1; }

.side-panel { width: 420px; flex-shrink: 0; background: var(--surface); z-index: 10; box-shadow: -4px 0 20px rgba(0,0,0,0.03); display: flex; flex-direction: column; border-left: 1px solid var(--border-light);}

@media (max-width: 768px) {
  .app-header { padding: 0 15px; height: 65px; }
  .hide-mobile { display: none; }
  .app-content { flex-direction: column; }
  
  .side-panel { position: fixed; bottom: 70px; left: 0; right: 0; width: 100%; height: 68vh; border-radius: 24px 24px 0 0; transform: translateY(120%); transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1); z-index: 1500; box-shadow: 0 -10px 25px rgba(0,0,0,0.1); border-left: none;}
  .side-panel.mobile-active { transform: translateY(0); }
  .side-panel .desktop-sidebar { display: flex !important; width: 100% !important; box-shadow: none !important; }
}
</style>