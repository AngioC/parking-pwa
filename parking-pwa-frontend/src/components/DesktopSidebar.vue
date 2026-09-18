<script setup>
import { ref, watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '../store'

const props = defineProps({
  activeTab: { type: String, default: 'all' }
})
// Aggiungiamo l'evento logout
const emit = defineEmits(['close-sheet', 'logout'])
const store = useAppStore()
const { user, mySubmissions, filteredSpots } = storeToRefs(store)

const currentView = ref('home')

const totalSubs = computed(() => mySubmissions.value.length)
const approvedSubs = computed(() => {
  return mySubmissions.value.filter(s => s.properties.status.toLowerCase() === 'approved').length
})

watch(() => props.activeTab, (newTab) => {
  if (newTab === 'contact') currentView.value = 'contact'
  else if (newTab === 'about') currentView.value = 'about'
  else {
    currentView.value = 'home'
    if (newTab === 'profile' && user.value) store.fetchMySubmissions()
  }
}, { immediate: true })

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

const sendContactMessage = () => {
  alert("Messaggio inviato con successo! Il team ti risponderà al più presto.")
  goHome()
}
</script>

<template>
  <aside class="desktop-sidebar">
    <div class="mobile-close-bar">
      <div class="drag-handle"></div>
      <button class="icon-btn" @click="$emit('close-sheet')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>

    <!-- LE MIE SEGNALAZIONI -->
    <div v-if="currentView === 'submissions'" class="sidebar-view">
      <div class="view-header">
        <div style="display: flex; align-items: center; gap: 10px;">
          <button class="icon-btn" @click="goHome">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
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

    <!-- CHI SIAMO -->
    <div v-else-if="currentView === 'about'" class="sidebar-view">
      <div class="view-header">
        <h2 style="margin: 0;">Chi Siamo</h2>
      </div>
      <div class="about-content">
        <div class="about-icon">🗺️</div>
        <h3>Mappiamo l'accessibilità, insieme.</h3>
        <p><strong>ParkAbile</strong> è un progetto nato con un obiettivo semplice ma ambizioso: rendere le città più accessibili per tutti.</p>
        <p>Sappiamo quanto sia difficile trovare un posteggio dedicato libero o correttamente segnalato. Grazie alla nostra mappa collaborativa, chiunque può segnalare nuovi stalli in tempo reale, aiutando l'intera community a muoversi con maggiore libertà.</p>
        <p>Ogni segnalazione viene verificata per garantire dati affidabili e aggiornati.</p>
      </div>
    </div>

    <!-- CONTATTACI -->
    <div v-else-if="currentView === 'contact'" class="sidebar-view">
      <div class="view-header">
        <h2 style="margin: 0;">Contattaci</h2>
      </div>
      <p class="text-sm">Hai suggerimenti, problemi tecnici o vuoi collaborare? Scrivici.</p>

      <div class="contact-card">
        <div class="contact-item">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
          <a href="mailto:info@parkabile.it" class="contact-link">info@parkabile.it</a>
        </div>
      </div>

      <form @submit.prevent="sendContactMessage" class="contact-form">
        <input type="text" class="form-input" placeholder="Il tuo nome" required>
        <input type="email" class="form-input" placeholder="La tua email" required>
        <textarea class="form-input" placeholder="Come possiamo aiutarti?" rows="4" required></textarea>
        <button type="submit" class="btn-primary full-width">Invia Messaggio</button>
      </form>
    </div>

    <!-- HOMEPAGE -->
    <div v-else class="sidebar-view">
      
      <!-- PROFILO (con Logout integrato) -->
      <div v-if="activeTab === 'profile'" class="profile-container">
        
        <div v-if="user" class="profile-card">
          <div class="profile-header">
            <div class="avatar">{{ user.email.charAt(0).toUpperCase() }}</div>
            <div>
              <p class="profile-email">{{ user.email }}</p>
              <p class="profile-role">Membro Attivo</p>
            </div>
          </div>
          
          <div class="profile-stats">
            <div class="stat-box">
              <span class="stat-num">{{ totalSubs }}</span>
              <span class="stat-label">Segnalate</span>
            </div>
            <div class="stat-box">
              <span class="stat-num">{{ approvedSubs }}</span>
              <span class="stat-label">Approvate</span>
            </div>
          </div>

          <a href="#" class="link-styled" style="display: block; text-align: center; margin-top: 15px;" @click.prevent="openMySubmissions">
            Gestisci le tue segnalazioni &rarr;
          </a>
          
          <hr class="divider">
          <!-- TASTO LOGOUT SPOSTATO QUI -->
          <button class="btn-logout-inline" @click="$emit('logout')">Esci dall'account</button>
        </div>
        
        <div v-else class="profile-card">
          <p class="text-sm" style="text-align: center; margin: 0;">Accedi o registrati per vedere le tue statistiche e segnalazioni.</p>
        </div>

      </div>
      
      <hr class="divider" v-if="activeTab === 'all'">
      
      <!-- LISTA POSTEGGI -->
      <div class="spots-section" v-if="activeTab === 'all' || activeTab === 'list'">
        <div class="view-header" style="margin-bottom: 15px;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <h3 style="margin: 0; color: var(--text-main); font-size: 17px;">Posteggi Disponibili</h3>
            <!-- Contatore moderno -->
            <span class="count-badge">{{ filteredSpots.length }}</span>
          </div>
        </div>
        
        <p v-if="filteredSpots.length === 0" class="text-sm">Nessun posteggio trovato.</p>
        
        <div class="spot-list">
          <div v-for="spot in filteredSpots" :key="spot.id" class="spot-list-item" @click="focusSpot(spot)">
            <strong class="item-desc">{{ spot.properties.description ? (spot.properties.description.length > 40 ? spot.properties.description.substring(0, 40) + '...' : spot.properties.description) : 'Posteggio segnalato' }}</strong>
            <span class="text-xs" style="display: block; margin-top: 6px;">Aggiunto il: {{ new Date(spot.properties.created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

    </div>
  </aside>
</template>

<style scoped>
.desktop-sidebar { width: 100%; flex-shrink: 0; background: var(--surface); z-index: 10; display: flex; flex-direction: column; height: 100%; }
@media (max-width: 768px) { .desktop-sidebar { display: none; } }

.mobile-close-bar { display: none; }
@media (max-width: 768px) { 
  .mobile-close-bar { display: flex; justify-content: flex-end; padding: 12px 20px 0 20px; position: relative; }
  .drag-handle { position: absolute; left: 50%; top: 12px; transform: translateX(-50%); width: 40px; height: 5px; background: var(--border-light); border-radius: 10px; }
}

.sidebar-view { padding: 20px 25px 25px 25px; display: flex; flex-direction: column; height: 100%; box-sizing: border-box; overflow-y: auto;}
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.view-header h2 { margin: 0; font-size: 20px; color: var(--text-main); font-weight: 800; letter-spacing: -0.5px;}

.text-sm { font-size: 14px; color: var(--text-muted); line-height: 1.6; margin-bottom: 15px;}
.text-xs { font-size: 12px; color: #94a3b8; }
.divider { border: 0; border-top: 1px solid var(--border-light); margin: 20px 0; width: 100%; }

.icon-btn { background: var(--bg-color); border: none; width: 36px; height: 36px; border-radius: 10px; cursor: pointer; color: var(--text-muted); display: flex; justify-content: center; align-items: center; transition: all 0.2s;}
.icon-btn:hover { background: #e2e8f0; color: var(--text-main); }

/* Chi Siamo */
.about-content { background: #eff6ff; padding: 25px; border-radius: 16px; border: 1px solid #dbeafe; color: #1e40af;}
.about-icon { font-size: 32px; margin-bottom: 10px; }
.about-content h3 { margin: 0 0 15px 0; font-size: 18px; font-weight: 700;}
.about-content p { font-size: 14px; line-height: 1.7; margin: 0 0 12px 0; color: #1e3a8a;}

/* PROFILO */
.profile-container { display: flex; flex-direction: column; gap: 20px; }
.profile-card { background: var(--surface); padding: 24px; border-radius: 16px; border: 1px solid var(--border-light); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);}
.profile-header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
.avatar { width: 50px; height: 50px; border-radius: 50%; background: #e0e7ff; color: var(--primary); font-weight: 800; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.profile-email { margin: 0; font-weight: 700; color: var(--text-main); font-size: 16px;}
.profile-role { margin: 2px 0 0 0; font-size: 13px; color: var(--text-muted); font-weight: 500;}

.profile-stats { display: flex; gap: 12px; margin-bottom: 5px; }
.stat-box { flex: 1; background: var(--bg-color); border-radius: 12px; padding: 15px 10px; text-align: center; }
.stat-num { display: block; font-size: 24px; font-weight: 800; color: var(--primary); line-height: 1; }
.stat-label { display: block; font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 6px; font-weight: 700;}

.link-styled { display: inline-block; font-size: 14px; font-weight: 600; color: var(--primary); text-decoration: none; transition: color 0.2s; }
.link-styled:hover { color: var(--primary-hover); text-decoration: underline; }

.btn-logout-inline { width: 100%; background: transparent; border: 1px solid #fecaca; color: #ef4444; padding: 10px; border-radius: 10px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s; }
.btn-logout-inline:hover { background: #fef2f2; border-color: #ef4444; }

/* CONTATTI */
.contact-card { background: #f0fdf4; padding: 18px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #bbf7d0; }
.contact-item { display: flex; align-items: center; gap: 12px; }
.contact-link { color: #166534; font-weight: 600; text-decoration: none; }
.contact-form { display: flex; flex-direction: column; gap: 15px; }

/* LISTE E BADGE */
.count-badge { background: #e0e7ff; color: var(--primary); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 800; }
.spots-section { display: flex; flex-direction: column; height: 100%; }
.spot-list { display: flex; flex-direction: column; gap: 12px; overflow-y: auto; padding: 4px 4px 20px 4px; }
.spot-list-item { padding: 18px; background: var(--surface); border: 1px solid var(--border-light); border-radius: 12px; cursor: pointer; transition: all 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.02);}
.spot-list-item:hover { border-color: var(--primary); box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1); transform: translateY(-1px);}
.item-desc { font-size: 15px; color: var(--text-main); font-weight: 600; line-height: 1.4;}

.status-row { display: flex; justify-content: space-between; margin-bottom: 10px; align-items: center; }
.status-badge { padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
.status-badge.pending { background: #fef3c7; color: #d97706; }
.status-badge.approved { background: #dcfce7; color: #15803d; }
.status-badge.rejected { background: #fee2e2; color: #b91c1c; }
.empty-msg { text-align: center; margin-top: 20px; }

/* FORMS BASE */
.form-input { width: 100%; padding: 14px 16px; border: 1px solid var(--border-light); border-radius: 10px; font-family: inherit; font-size: 14px; transition: border-color 0.2s; box-sizing: border-box; background: var(--bg-color);}
.form-input:focus { outline: none; border-color: var(--primary); background: var(--surface); box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);}
.btn-primary { padding: 14px; border-radius: 10px; font-weight: 600; border: none; cursor: pointer; background: var(--primary); color: white; transition: background 0.2s, transform 0.1s;}
.btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px);}
.full-width { width: 100%; }
</style>