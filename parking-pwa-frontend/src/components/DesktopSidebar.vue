<script setup>
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '../store'

const props = defineProps({
  activeTab: { type: String, default: 'all' }
})
const emit = defineEmits(['close-sheet'])
const store = useAppStore()
const { user, parkingSpots, mySubmissions, filters, filteredSpots } = storeToRefs(store)

const currentView = ref('home')
const searchQuery = ref('') 

// IL FIX DEL MENU: Se l'utente clicca una tab nell'Header/Footer, forziamo la barra a tornare alla vista principale
watch(() => props.activeTab, () => {
  currentView.value = 'home'
})

const openMySubmissions = () => {
  store.fetchMySubmissions()
  currentView.value = 'submissions'
}

const goHome = () => { currentView.value = 'home' }

const focusSpot = (spot) => {
  store.center = [spot.geometry.coordinates[1], spot.geometry.coordinates[0]]
  store.zoom = 17 
  emit('close-sheet')
}
</script>

<template>
  <aside class="desktop-sidebar">
    <div class="mobile-close-bar">
      <!-- SVG Close Moderno -->
      <button class="icon-btn" @click="$emit('close-sheet')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>

    <!-- LE MIE SEGNALAZIONI -->
    <div v-if="currentView === 'submissions'" class="sidebar-view">
      <div class="view-header">
        <div style="display: flex; align-items: center; gap: 10px;">
          <!-- SVG Freccia Indietro -->
          <button class="icon-btn" @click="goHome">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
          </button>
          <h2>Le mie Segnalazioni</h2>
        </div>
      </div>
      <p class="text-sm">Storico delle richieste inviate.</p>

      <p v-if="mySubmissions.length === 0" class="text-sm empty-msg">Non hai ancora inviato segnalazioni.</p>
      
      <div class="spot-list">
        <div v-for="sub in mySubmissions" :key="sub.id" class="spot-list-item cursor-default">
          <div class="status-row">
            <span class="text-xs">{{ new Date(sub.properties.created_at).toLocaleDateString() }}</span>
            <span class="status-badge" :class="sub.properties.status.toLowerCase()">
              {{ sub.properties.status }}
            </span>
          </div>
          <strong class="item-desc">{{ sub.properties.description || 'Nessuna nota inserita' }}</strong>
        </div>
      </div>
    </div>

    <!-- HOMEPAGE -->
    <div v-else class="sidebar-view">
      
      <!-- PROFILO: Visibile ESCLUSIVAMENTE nella tab profilo -->
      <div v-if="user && activeTab === 'profile'" class="profile-card">
        <div class="profile-header">
          <div class="avatar">{{ user.email.charAt(0).toUpperCase() }}</div>
          <p class="profile-email">{{ user.email }}</p>
        </div>
        <a href="#" class="link-styled" @click.prevent="openMySubmissions">
          Gestisci le tue segnalazioni &rarr;
        </a>
      </div>
      
      <div v-else-if="!user && activeTab === 'profile'" class="profile-card">
        <p class="text-sm" style="text-align: center; margin: 0;">Devi accedere per vedere il tuo profilo.</p>
      </div>
      
      <hr class="divider" v-if="activeTab === 'all'">

      <div class="controls-section" v-if="activeTab === 'all' || activeTab === 'list'">
        <div style="display: flex; gap: 8px; margin-bottom: 15px;">
          <input v-model="searchQuery" class="form-input" style="margin-bottom: 0;" placeholder="Cerca via o città..." @keyup.enter="store.searchAddress(searchQuery)">
          <button class="btn-primary" style="width: auto; padding: 0 15px;" @click="store.searchAddress(searchQuery)">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          </button>
        </div>

        <div style="display: flex; gap: 10px; margin-bottom: 15px; align-items: center;">
          <select v-model="filters.status" class="form-input" style="margin-bottom: 0; flex: 1;">
            <option value="all">Tutti gli stati</option>
            <option value="approved">Solo Approvati</option>
            <option value="pending">In Attesa</option>
          </select>
          <label style="font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 5px; color: #4b5563;">
            <input type="checkbox" v-model="filters.radius1km"> Entro 1km
          </label>
        </div>
      </div>
      
      <div class="spots-section" v-if="activeTab === 'all' || activeTab === 'list'">
        <div class="view-header" style="margin-bottom: 10px;">
          <h3 style="margin: 0; color: #1f2937; font-size: 16px;">Posteggi Disponibili</h3>
        </div>
        <p v-if="filteredSpots.length === 0" class="text-sm">Nessun posteggio trovato.</p>
        
        <div class="spot-list">
          <div v-for="spot in filteredSpots" :key="spot.id" class="spot-list-item" @click="focusSpot(spot)">
            <strong class="item-desc">{{ spot.properties.description ? (spot.properties.description.length > 40 ? spot.properties.description.substring(0, 40) + '...' : spot.properties.description) : 'Posteggio segnalato' }}</strong>
            <span class="text-xs" style="display: block; margin-top: 5px;">Aggiunto il: {{ new Date(spot.properties.created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

    </div>
  </aside>
</template>

<style scoped>
.desktop-sidebar { width: 100%; flex-shrink: 0; background: #ffffff; z-index: 10; display: flex; flex-direction: column; height: 100%; }
@media (max-width: 768px) { .desktop-sidebar { display: none; } }
.mobile-close-bar { display: none; }
@media (max-width: 768px) { .mobile-close-bar { display: flex; justify-content: flex-end; padding: 15px 25px 0 25px; } }
.sidebar-view { padding: 15px 25px 25px 25px; display: flex; flex-direction: column; height: 100%; box-sizing: border-box; overflow-y: auto;}
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.view-header h2 { margin: 0; font-size: 18px; color: #1f2937; font-weight: 700;}
.text-sm { font-size: 14px; color: #6b7280; line-height: 1.5; margin-bottom: 15px;}
.text-xs { font-size: 12px; color: #9ca3af; }
.divider { border: 0; border-top: 1px solid #f3f4f6; margin: 20px 0; width: 100%; }
.icon-btn { background: #f3f4f6; border: none; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; color: #4b5563; display: flex; justify-content: center; align-items: center; transition: background 0.2s;}
.icon-btn:hover { background: #e5e7eb; color: #1f2937; }

/* Profilo Modernizzato */
.profile-card { background: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e5e7eb; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
.profile-header { display: flex; align-items: center; gap: 12px; margin-bottom: 15px; }
.avatar { width: 40px; height: 40px; border-radius: 50%; background: #eff6ff; color: #2563eb; font-weight: bold; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.profile-email { margin: 0; font-weight: 600; color: #1f2937; font-size: 15px;}
.link-styled { display: inline-block; font-size: 14px; font-weight: 600; color: #2563eb; text-decoration: none; transition: color 0.2s; }
.link-styled:hover { color: #1d4ed8; text-decoration: underline; }

.spots-section { display: flex; flex-direction: column; height: 100%; }
.spot-list { display: flex; flex-direction: column; gap: 10px; overflow-y: auto; padding-bottom: 20px; }
.spot-list-item { padding: 15px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.spot-list-item:hover { border-color: #93c5fd; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.item-desc { font-size: 14px; color: #1f2937; font-weight: 500; }
.cursor-default { cursor: default; }
.cursor-default:hover { border-color: #e5e7eb; box-shadow: none; }
.status-row { display: flex; justify-content: space-between; margin-bottom: 8px; align-items: center; }
.status-badge { padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.status-badge.pending { background: #fef9c3; color: #854d0e; }
.status-badge.approved { background: #dcfce7; color: #166534; }
.status-badge.rejected { background: #fee2e2; color: #991b1b; }
.empty-msg { text-align: center; margin-top: 20px; }
.form-input { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-family: inherit; font-size: 14px; transition: border-color 0.2s;}
.form-input:focus { outline: none; border-color: #2563eb; }
.btn-primary { border-radius: 8px; font-weight: 600; border: none; cursor: pointer; background: #2563eb; color: white; transition: background 0.2s;}
.btn-primary:hover { background: #1d4ed8; }
</style>