<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '../store'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'all' 
  }
})

// Dichiariamo l'evento per dire ad App.vue di chiudere il pannello
const emit = defineEmits(['close-sheet'])

const store = useAppStore()
const { user, parkingSpots, mySubmissions } = storeToRefs(store)

const currentView = ref('home')

const openMySubmissions = () => {
  store.fetchMySubmissions()
  currentView.value = 'submissions'
}

const goHome = () => {
  currentView.value = 'home'
}

const focusSpot = (spot) => {
  store.center = [spot.geometry.coordinates[1], spot.geometry.coordinates[0]]
  store.zoom = 17 
  // CHIUSURA AUTOMATICA: Lanciamo l'evento quando si clicca un posteggio
  emit('close-sheet')
}
</script>

<template>
  <aside class="desktop-sidebar">
    
    <!-- PULSANTE CHIUSURA (Visibile SOLO su Mobile) -->
    <div class="mobile-close-bar">
      <button class="icon-btn" @click="$emit('close-sheet')">✖</button>
    </div>

    <!-- VISTA: LE MIE SEGNALAZIONI -->
    <div v-if="currentView === 'submissions'" class="sidebar-view">
      <div class="view-header">
        <h2>Le mie Segnalazioni</h2>
        <button class="icon-btn" @click="goHome">🔙</button>
      </div>
      <p class="text-sm">Qui trovi lo stato di tutte le tue richieste.</p>

      <p v-if="mySubmissions.length === 0" class="text-sm empty-msg">Non hai ancora inviato nessuna segnalazione.</p>
      
      <div class="spot-list">
        <div v-for="sub in mySubmissions" :key="sub.id" class="spot-list-item cursor-default">
          <div class="status-row">
            <span class="text-xs">📅 {{ new Date(sub.properties.created_at).toLocaleDateString() }}</span>
            <span class="status-badge" :class="sub.properties.status.toLowerCase()">
              {{ sub.properties.status }}
            </span>
          </div>
          <strong>📝 {{ sub.properties.description || 'Nessuna nota inserita' }}</strong>
        </div>
      </div>
    </div>

    <!-- VISTA: HOMEPAGE (Divisa dinamicamente) -->
    <div v-else class="sidebar-view">
      
      <!-- TITOLO -->
      <div class="brand" v-if="activeTab === 'all' || activeTab === 'list'">
        <h1>🅿️ ParkDisabili</h1>
        <p class="text-sm">Mappa collaborativa per posteggi accessibili.</p>
      </div>
      
      <!-- PROFILO UTENTE LOGGATO -->
      <div v-if="user && (activeTab === 'all' || activeTab === 'profile')" class="profile-card">
        <p class="profile-email">👤 {{ user.email }}</p>
        <button class="btn-secondary full-width" @click="openMySubmissions">
          📋 Vedi le mie segnalazioni
        </button>
      </div>
      
      <!-- Avviso Utente NON Loggato -->
      <div v-else-if="!user && activeTab === 'profile'" class="profile-card">
        <p class="text-sm" style="text-align: center; margin: 0;">Devi accedere per vedere il tuo profilo.</p>
      </div>
      
      <hr class="divider" v-if="activeTab === 'all'">
      
      <!-- LISTA POSTEGGI -->
      <div class="spots-section" v-if="activeTab === 'all' || activeTab === 'list'">
        <div class="view-header" style="margin-bottom: 10px;">
          <h3 style="margin: 0; color: #1f2937;">Posteggi Disponibili</h3>
        </div>
        <p v-if="parkingSpots.length === 0" class="text-sm">Nessun posteggio trovato sulla mappa.</p>
        
        <div class="spot-list">
          <div v-for="spot in parkingSpots" :key="spot.id" class="spot-list-item" @click="focusSpot(spot)">
            <strong>📍 {{ spot.properties.description ? (spot.properties.description.length > 30 ? spot.properties.description.substring(0, 30) + '...' : spot.properties.description) : 'Posteggio segnalato' }}</strong>
            <br>
            <span class="text-xs">Aggiunto il: {{ new Date(spot.properties.created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

    </div>
  </aside>
</template>

<style scoped>
.desktop-sidebar { width: 380px; flex-shrink: 0; background: #ffffff; z-index: 10; display: flex; flex-direction: column; }
@media (max-width: 768px) { .desktop-sidebar { display: none; } }

/* Nuovo stile per la barra di chiusura su mobile */
.mobile-close-bar { display: none; }
@media (max-width: 768px) {
  .mobile-close-bar {
    display: flex;
    justify-content: flex-end;
    padding: 15px 25px 0 25px; /* Spazio per la X in alto a destra */
  }
}

.sidebar-view { padding: 15px 25px 25px 25px; display: flex; flex-direction: column; height: 100%; box-sizing: border-box; overflow-y: auto;}
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.view-header h2 { margin: 0; font-size: 20px; color: #1f2937; }
.text-sm { font-size: 14px; color: #6b7280; line-height: 1.5; margin-bottom: 15px;}
.text-xs { font-size: 12px; color: #9ca3af; }
.divider { border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0; width: 100%; }
.brand h1 { margin: 0 0 5px 0; color: #2563eb; font-size: 24px; }
.icon-btn { background: #f3f4f6; border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; color: #4b5563; display: flex; justify-content: center; align-items: center; }
.icon-btn:hover { background: #e5e7eb; }
.profile-card { background: #eff6ff; padding: 15px; border-radius: 12px; border: 1px solid #bfdbfe; }
.profile-email { margin: 0 0 10px 0; font-weight: bold; color: #1e3a8a; }
.spots-section { display: flex; flex-direction: column; height: 100%; }
.spot-list { display: flex; flex-direction: column; gap: 10px; overflow-y: auto; padding-bottom: 20px; }
.spot-list-item { padding: 15px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; cursor: pointer; transition: background 0.2s, border-color 0.2s; }
.spot-list-item:hover { background: #f3f4f6; border-color: #d1d5db; }
.cursor-default { cursor: default; }
.cursor-default:hover { background: #f9fafb; border-color: #e5e7eb; }
.status-row { display: flex; justify-content: space-between; margin-bottom: 8px; align-items: center; }
.status-badge { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; }
.status-badge.pending { background: #fef08a; color: #854d0e; }
.status-badge.approved { background: #bbf7d0; color: #166534; }
.status-badge.rejected { background: #fecaca; color: #991b1b; }
.btn-secondary { background: #f3f4f6; color: #374151; padding: 8px; font-size: 13px; border-radius: 8px; font-weight: 600; border: none; cursor: pointer; text-align: center; transition: opacity 0.2s; }
.full-width { width: 100%; }
.empty-msg { text-align: center; margin-top: 20px; }
</style>