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
      <!-- Logo modernizzato senza emoji -->
      <div class="logo">
        <!-- Assicurati che l'estensione sia corretta (.png, .svg, .jpg) -->
        <img src="/logo.png" alt="Logo ParkAbile" class="logo-img" />
        ParkAbile
      </div>
      <nav class="header-nav">
        <a href="#" class="nav-link hide-mobile" @click.prevent="mobileActiveTab = 'map'">Esplora</a>
        <a href="#" class="nav-link hide-mobile" v-if="user" @click.prevent="mobileActiveTab = 'profile'">Profilo</a>
        <a href="#" class="nav-link hide-mobile" @click.prevent>Contattaci</a>

        <button v-if="!user" class="btn-login" @click="showAuthModal = true">Accedi</button>
        <button v-else class="btn-logout" @click="handleLogout">Logout</button>
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
        />
      </div>
    </div>

    <MobileBottomNav @change-tab="(tab) => mobileActiveTab = tab" />
    <AuthModals v-if="showAuthModal" @close="showAuthModal = false" />
  </div>
</template>

<style>
body { margin: 0; padding: 0; font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; background: #f3f4f6;}
.app-container { display: flex; height: 100vh; width: 100vw; flex-direction: column; }

.app-header { display: flex; justify-content: space-between; align-items: center; padding: 0 25px; height: 65px; background: #ffffff; border-bottom: 1px solid #e5e7eb; z-index: 2000; flex-shrink: 0; }
.logo { display: flex; align-items: center; font-size: 20px; font-weight: 800; color: #1f2937; letter-spacing: -0.5px;}
.logo-img { 
  height: 55px; /* Regola questo valore per fare il logo più grande o più piccolo */
  width: auto; 
  margin-right: 12px; 
  border-radius: 4px; /* Rimuovilo se il tuo logo ha già la forma che desideri */
}
.header-nav { display: flex; align-items: center; gap: 24px; }
.nav-link { text-decoration: none; color: #4b5563; font-weight: 500; font-size: 15px; transition: color 0.2s; }
.nav-link:hover { color: #2563eb; }
.btn-login { background: #2563eb; color: white; border: none; padding: 9px 18px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; transition: background 0.2s;}
.btn-login:hover { background: #1d4ed8; }
.btn-logout { background: #ffffff; color: #dc2626; border: 1px solid #fca5a5; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s;}
.btn-logout:hover { background: #fef2f2; }

.app-content { display: flex; flex: 1; overflow: hidden; position: relative; flex-direction: row; }
.main-map { flex-grow: 1; height: 100%; position: relative; z-index: 1; }

.side-panel { width: 420px; flex-shrink: 0; background: #ffffff; z-index: 10; box-shadow: -4px 0 15px rgba(0,0,0,0.05); display: flex; flex-direction: column; }

@media (max-width: 768px) {
  .app-header { padding: 0 15px; }
  .hide-mobile { display: none; }
  .app-content { flex-direction: column; }
  
  .side-panel { position: fixed; bottom: 70px; left: 0; right: 0; width: 100%; height: 65vh; border-radius: 20px 20px 0 0; transform: translateY(120%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); z-index: 1500; box-shadow: 0 -4px 20px rgba(0,0,0,0.15); }
  .side-panel.mobile-active { transform: translateY(0); }
  .side-panel .desktop-sidebar { display: flex !important; width: 100% !important; box-shadow: none !important; }
}
</style>