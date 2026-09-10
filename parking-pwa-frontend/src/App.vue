<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { storeToRefs } from 'pinia'
import { useAppStore } from './store'
import { supabase } from './supabase'

// Importiamo i nostri nuovi componenti ordinati
import MapArea from './components/MapArea.vue'
import DesktopSidebar from './components/DesktopSidebar.vue'
import MobileBottomNav from './components/MobileBottomNav.vue'
import SubmissionForm from './components/SubmissionForm.vue'
import AuthModals from './components/AuthModals.vue'

// Configurazione globale Axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('supabase_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const store = useAppStore()
const { user, draftPosition } = storeToRefs(store)

const showAuthModal = ref(false)
const mobileActiveTab = ref('map') // 'map', 'list', o 'profile'

// Autenticazione e Logout
const handleLogout = async () => {
  await supabase.auth.signOut()
  store.setUser(null)
  localStorage.removeItem('supabase_token')
  mobileActiveTab.value = 'map'
}

// Inizializzazione al caricamento
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
    
    <!-- 1. PANNELLO LATERALE (Desktop) / BOTTOM SHEET (Mobile) -->
    <!-- Su mobile, questo pannello si apre solo se inseriamo un pin o cambiamo tab -->
    <div class="side-panel" :class="{ 'mobile-active': mobileActiveTab !== 'map' || draftPosition }">
      
      <!-- Se c'è un pin in corso, mostriamo il form -->
      <SubmissionForm 
        v-if="draftPosition" 
        @close="store.draftPosition = null" 
        @require-login="showAuthModal = true" 
      />
      
      <!-- Altrimenti, mostriamo la lista e il profilo (DesktopSidebar) -->
      <DesktopSidebar v-else :active-tab="mobileActiveTab === 'map' ? 'all' : mobileActiveTab" />

    </div>

    <!-- 2. AREA MAPPA -->
    <main class="main-map">
      <MapArea />

      <!-- Pulsanti in alto a destra -->
      <div class="top-right-nav">
        <button v-if="!user" class="nav-btn" @click="showAuthModal = true">Accedi</button>
        <button v-else class="nav-btn danger" @click="handleLogout">Logout</button>
      </div>
    </main>

    <!-- 3. BARRA INFERIORE (Visibile solo su Mobile tramite CSS) -->
    <MobileBottomNav @change-tab="(tab) => mobileActiveTab = tab" />

    <!-- 4. MODALI DI AUTENTICAZIONE -->
    <AuthModals v-if="showAuthModal" @close="showAuthModal = false" />
    
  </div>
</template>

<style>
/* STILI GLOBALI BASE */
body { margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; background: #f3f4f6;}

.app-container { display: flex; height: 100vh; width: 100vw; flex-direction: row; }

/* LAYOUT DESKTOP */
.side-panel {
  width: 380px;
  flex-shrink: 0;
  background: #ffffff;
  z-index: 10;
  box-shadow: 4px 0 15px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.main-map {
  flex-grow: 1;
  height: 100%;
  position: relative;
  z-index: 1;
}

/* PULSANTI NAVIGAZIONE ALTA */
.top-right-nav { position: absolute; top: 15px; right: 15px; z-index: 1000; }
.nav-btn { background: white; color: #1f2937; border: 1px solid #d1d5db; padding: 10px 18px; border-radius: 20px; font-weight: 600; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.2s; }
.nav-btn:hover { background: #f9fafb; box-shadow: 0 4px 6px rgba(0,0,0,0.15); }
.nav-btn.danger { color: #dc2626; border-color: #fca5a5; }

/* LAYOUT MOBILE (APP NATIVA) */
@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }
  
  /* Il pannello diventa un Bottom Sheet stile app iOS/Android */
  .side-panel {
    position: fixed;
    bottom: 70px; /* Lascia spazio alla Bottom Nav */
    left: 0;
    right: 0;
    width: 100%;
    height: 65vh; /* Occupa il 65% dello schermo quando aperto */
    border-radius: 20px 20px 0 0;
    transform: translateY(120%); /* Nascondilo in basso di default */
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1500;
  }
  
  /* Classe che fa scorrere il pannello in alto */
  .side-panel.mobile-active {
    transform: translateY(0);
  }

  /* Forza la DesktopSidebar a mostrarsi dentro il nostro Bottom Sheet su Mobile */
  .side-panel .desktop-sidebar { 
    display: flex !important; 
    width: 100% !important; 
    box-shadow: none !important; 
  }
}
</style>