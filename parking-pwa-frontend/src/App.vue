<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import "leaflet/dist/leaflet.css"
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet"
import L from 'leaflet'
import { supabase } from './supabase'

// --- SETUP ICONE MAPPA ---
const cdnIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41], iconAnchor: [12, 41], shadowSize: [41, 41], popupAnchor: [1, -34]
})

const draftIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41], iconAnchor: [12, 41], shadowSize: [41, 41], popupAnchor: [1, -34]
})

// --- STATO MAPPA E DATI ---
const zoom = ref(6)
const center = ref([41.90, 12.49]) 
const parkingSpots = ref([])
const markerRefs = ref({})

// STATI DELLA BARRA LATERALE E MODALI
const showForm = ref(false)    
const showMySubmissions = ref(false)
const mySubmissions = ref([])        

const draftPosition = ref(null) 
const showLoginModal = ref(false)
const showSignupModal = ref(false)

const newReport = ref({ description: '', imageFile: null })
const imagePreview = ref(null)

// --- STATO AUTENTICAZIONE ---
const user = ref(null)
const email = ref('')
const password = ref('')

// --- CONFIGURA AXIOS ---
// Usa la variabile d'ambiente per l'URL del backend (fallback a localhost per sicurezza)
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('supabase_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// --- METODI MAPPA E DATI ---
const fetchSpots = async () => {
  try {
    // Rimosso localhost, usa l'URL base configurato sopra
    const response = await axios.get('/api/spots/')
    parkingSpots.value = response.data.features
  } catch (error) { console.error("Errore GET:", error) }
}

const fetchMySubmissions = async () => {
  if (!user.value) return
  try {
    // Rimosso localhost
    const response = await axios.get('/api/submissions/')
    mySubmissions.value = response.data.features
    showMySubmissions.value = true
    showForm.value = false
  } catch (error) {
    console.error("Errore recupero segnalazioni:", error)
  }
}

const onMapClick = (event) => {
  const { lat, lng } = event.latlng
  draftPosition.value = [lat, lng]
  showForm.value = true
  showMySubmissions.value = false
}

const geolocateAndReport = () => {
  if (!navigator.geolocation) return alert("GPS non supportato.")
  navigator.geolocation.getCurrentPosition(
    (position) => {
      draftPosition.value = [position.coords.latitude, position.coords.longitude]
      center.value = draftPosition.value
      zoom.value = 16
      showForm.value = true
      showMySubmissions.value = false
    },
    () => alert("Impossibile ottenere la posizione.")
  )
}

const setMarkerRef = (el, id) => { if (el) markerRefs.value[id] = el }

const focusSpot = (spot) => {
  showForm.value = false
  showMySubmissions.value = false
  draftPosition.value = null
  center.value = [spot.geometry.coordinates[1], spot.geometry.coordinates[0]]
  zoom.value = 17 
  setTimeout(() => {
    const markerComp = markerRefs.value[spot.id]
    if (markerComp && markerComp.leafletObject) markerComp.leafletObject.openPopup()
  }, 200)
}

const getDirections = (spot) => {
  if (!spot) return
  window.open(`https://www.google.com/maps/dir/?api=1&destination=${spot.geometry.coordinates[1]},${spot.geometry.coordinates[0]}`, '_blank')
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    newReport.value.imageFile = file
    imagePreview.value = URL.createObjectURL(file) 
  }
}

const submitReport = async () => {
  if (!draftPosition.value) return
  if (!user.value) return (showForm.value = false, showLoginModal.value = true)

  const formData = new FormData()
  formData.append('location', JSON.stringify({ type: "Point", coordinates: [draftPosition.value[1], draftPosition.value[0]] }))
  formData.append('description', newReport.value.description)
  if (newReport.value.imageFile) formData.append('photo', newReport.value.imageFile)

  try {
    // Rimosso localhost
    await axios.post('/api/submissions/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    alert("Segnalazione inviata con successo!")
    closeForm()
  } catch (error) {
    alert("Errore nell'invio della segnalazione.")
  }
}

const closeForm = () => {
  showForm.value = false
  showMySubmissions.value = false
  draftPosition.value = null
  newReport.value = { description: '', imageFile: null }
  imagePreview.value = null
}

const openSignup = () => { showLoginModal.value = false; showSignupModal.value = true }
const openLogin = () => { showSignupModal.value = false; showLoginModal.value = true }

const handleLogin = async () => {
  const { data, error } = await supabase.auth.signInWithPassword({ email: email.value, password: password.value })
  if (error) return alert("Errore di login: " + error.message)
  user.value = data.user
  localStorage.setItem('supabase_token', data.session.access_token)
  email.value = ''; password.value = ''
  showLoginModal.value = false
}

const handleSignup = async () => {
  const { data, error } = await supabase.auth.signUp({ email: email.value, password: password.value })
  if (error) return alert("Errore: " + error.message)
  alert("Registrato! Ora puoi accedere.")
  openLogin()
}

const handleLogout = async () => {
  await supabase.auth.signOut()
  user.value = null
  localStorage.removeItem('supabase_token')
  showMySubmissions.value = false
}

onMounted(() => {
  supabase.auth.getSession().then(({ data: { session } }) => {
    if (session) { user.value = session.user; localStorage.setItem('supabase_token', session.access_token) }
  })
  fetchSpots()
})
</script>

<template>
  <div class="app-layout">
    
    <!-- BARRA LATERALE -->
    <aside class="sidebar">
      
      <!-- 1. VISTA: FORM NUOVA SEGNALAZIONE -->
      <div v-if="showForm" class="sidebar-view">
        <div class="view-header">
          <h2>Nuova Segnalazione</h2>
          <button class="icon-btn" @click="closeForm">✖</button>
        </div>
        <p class="text-sm">Hai inserito un pin sulla mappa. Compila i dati per inviare.</p>
        
        <label class="upload-area">
          📸 Scatta o Carica Foto
          <input type="file" accept="image/*" capture="environment" @change="handleFileUpload" hidden>
        </label>
        <img v-if="imagePreview" :src="imagePreview" class="preview-img">
        
        <textarea v-model="newReport.description" class="form-input" placeholder="Dettagli (es. piano terra)" rows="3"></textarea>
        
        <div class="spacer"></div>
        <div class="button-group">
          <button class="btn-secondary" @click="closeForm">Annulla</button>
          <button class="btn-primary" @click="submitReport">Invia Dati</button>
        </div>
      </div>

      <!-- 2. VISTA: LE MIE SEGNALAZIONI -->
      <div v-else-if="showMySubmissions" class="sidebar-view">
        <div class="view-header">
          <h2>Le mie Segnalazioni</h2>
          <button class="icon-btn" @click="closeForm">✖</button>
        </div>
        <p class="text-sm">Qui trovi lo stato di tutte le tue richieste.</p>

        <p v-if="mySubmissions.length === 0" class="text-sm" style="text-align: center; margin-top: 20px;">Non hai ancora inviato nessuna segnalazione.</p>
        
        <div class="spot-list">
          <div v-for="sub in mySubmissions" :key="sub.id" class="spot-list-item cursor-default">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; align-items: center;">
              <span class="text-xs">📅 {{ new Date(sub.properties.created_at).toLocaleDateString() }}</span>
              <span class="status-badge" :class="sub.properties.status.toLowerCase()">
                {{ sub.properties.status }}
              </span>
            </div>
            <strong>📝 {{ sub.properties.description || 'Nessuna nota inserita' }}</strong>
          </div>
        </div>
      </div>

      <!-- 3. VISTA: HOMEPAGE (LISTA POSTEGGI E PROFILO) -->
      <div v-else class="sidebar-view">
        <div class="brand">
          <h1>🅿️ ParkDisabili</h1>
          <p class="text-sm">Mappa collaborativa per posteggi accessibili.</p>
        </div>
        
        <!-- PROFILO UTENTE LOGGATO -->
        <div v-if="user" class="profile-card">
          <p style="margin: 0 0 10px 0; font-weight: bold; color: #1e3a8a;">👤 {{ user.email }}</p>
          <button class="btn-secondary full-width" style="padding: 8px; font-size: 13px;" @click="fetchMySubmissions">
            📋 Vedi le mie segnalazioni
          </button>
        </div>
        
        <hr class="divider">
        
        <div class="view-header" style="margin-bottom: 10px;">
          <h3 style="margin: 0; color: #1f2937;">Posteggi Disponibili</h3>
        </div>
        <p v-if="parkingSpots.length === 0" class="text-sm">Nessun posteggio trovato sulla mappa.</p>
        
        <!-- LISTA SCORREVOLE POSTEGGI -->
        <div class="spot-list">
          <div v-for="spot in parkingSpots" :key="spot.id" class="spot-list-item" @click="focusSpot(spot)">
            <strong>📍 {{ spot.properties.description ? (spot.properties.description.length > 30 ? spot.properties.description.substring(0, 30) + '...' : spot.properties.description) : 'Posteggio segnalato' }}</strong>
            <br>
            <span class="text-xs">Aggiunto il: {{ new Date(spot.properties.created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

    </aside>

    <!-- AREA MAPPA E OVERLAYS -->
    <main class="map-container">
      <l-map ref="map" v-model:zoom="zoom" :center="center" :use-global-leaflet="false" @click="onMapClick">
        <l-tile-layer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap" />
        
        <l-marker v-for="spot in parkingSpots" :key="spot.id" :lat-lng="[spot.geometry.coordinates[1], spot.geometry.coordinates[0]]" :icon="cdnIcon" :ref="el => setMarkerRef(el, spot.id)">
          <l-popup :options="{ minWidth: 260, maxWidth: 300 }">
            <div class="popup-content">
              <h4>Dettagli Posteggio</h4>
              <img v-if="spot.properties.photo" :src="spot.properties.photo" alt="Foto Posteggio" class="popup-image">
              <p><strong>📅 Data:</strong> {{ new Date(spot.properties.created_at).toLocaleDateString() }}</p>
              <p><strong>📝 Nota:</strong> {{ spot.properties.description || 'Nessuna descrizione.' }}</p>
              <button class="btn-primary popup-btn full-width" @click="getDirections(spot)">🧭 Ottieni Indicazioni</button>
            </div>
          </l-popup>
        </l-marker>

        <l-marker v-if="draftPosition" :lat-lng="draftPosition" :icon="draftIcon">
          <l-popup>Stai inserendo un nuovo posteggio qui.</l-popup>
        </l-marker>
      </l-map>

      <div class="top-right-nav">
        <button v-if="!user" class="nav-btn" @click="showLoginModal = true">Accedi</button>
        <button v-else class="nav-btn danger" @click="handleLogout">Logout</button>
      </div>

      <button v-if="!showForm && !showMySubmissions" class="fab" @click="geolocateAndReport">📍 Usa Posizione GPS</button>
    </main>
    
    <!-- MODALI -->
    <div v-if="showLoginModal" class="modal-overlay" @click.self="showLoginModal = false">
      <div class="modal-card">
        <div class="view-header">
          <h2>Accedi</h2>
          <button class="icon-btn" @click="showLoginModal = false">✖</button>
        </div>
        <input type="email" v-model="email" class="form-input" placeholder="La tua Email">
        <input type="password" v-model="password" class="form-input" placeholder="La tua Password">
        <button class="btn-primary" style="margin-bottom: 15px;" @click="handleLogin">Entra</button>
        <hr class="divider">
        <button class="btn-secondary full-width" @click="openSignup">Non hai un account? Registrati</button>
      </div>
    </div>

    <div v-if="showSignupModal" class="modal-overlay" @click.self="showSignupModal = false">
      <div class="modal-card">
        <div class="view-header">
          <h2>Registrazione</h2>
          <button class="icon-btn" @click="showSignupModal = false">✖</button>
        </div>
        <input type="email" v-model="email" class="form-input" placeholder="La tua Email">
        <input type="password" v-model="password" class="form-input" placeholder="Scegli una Password">
        <button class="btn-primary" style="margin-bottom: 15px;" @click="handleSignup">Crea Account</button>
        <hr class="divider">
        <button class="btn-secondary full-width" @click="openLogin">Torna al Login</button>
      </div>
    </div>
  </div>
</template>

<style>
body { margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }
.app-layout { display: flex; height: 100vh; width: 100vw; flex-direction: row; }
.sidebar { width: 380px; flex-shrink: 0; background: #ffffff; z-index: 10; box-shadow: 4px 0 15px rgba(0,0,0,0.1); display: flex; flex-direction: column; }
.map-container { flex-grow: 1; height: 100%; position: relative; z-index: 1; }
@media (max-width: 768px) { .app-layout { flex-direction: column-reverse; } .sidebar { width: 100%; height: 50vh; box-shadow: 0 -4px 15px rgba(0,0,0,0.1); } .map-container { height: 50vh; } }
.top-right-nav { position: absolute; top: 15px; right: 15px; z-index: 1000; }
.nav-btn { background: white; color: #1f2937; border: 1px solid #d1d5db; padding: 10px 18px; border-radius: 20px; font-weight: 600; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.2s; }
.nav-btn:hover { background: #f9fafb; box-shadow: 0 4px 6px rgba(0,0,0,0.15); }
.nav-btn.danger { color: #dc2626; border-color: #fca5a5; }
.fab { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); z-index: 1000; background: #2563eb; color: white; border: none; padding: 16px 28px; border-radius: 30px; font-size: 16px; font-weight: 700; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.4); cursor: pointer; transition: transform 0.2s; }
.fab:active { transform: translateX(-50%) scale(0.95); }
.sidebar-view { padding: 25px; display: flex; flex-direction: column; height: 100%; box-sizing: border-box; overflow-y: auto;}
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.view-header h2 { margin: 0; font-size: 20px; color: #1f2937; }
.spacer { flex-grow: 1; min-height: 20px; }
.text-sm { font-size: 14px; color: #6b7280; line-height: 1.5; margin-bottom: 15px;}
.text-xs { font-size: 12px; color: #9ca3af; }
.divider { border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0; width: 100%; }
.brand h1 { margin: 0 0 5px 0; color: #2563eb; font-size: 24px; }
.icon-btn { background: #f3f4f6; border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; color: #4b5563; display: flex; justify-content: center; align-items: center; }
.icon-btn:hover { background: #e5e7eb; }
.profile-card { background: #eff6ff; padding: 15px; border-radius: 12px; border: 1px solid #bfdbfe; }
.spot-list { display: flex; flex-direction: column; gap: 10px; overflow-y: auto; padding-bottom: 20px; }
.spot-list-item { padding: 15px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; cursor: pointer; transition: background 0.2s, border-color 0.2s; }
.spot-list-item:hover { background: #f3f4f6; border-color: #d1d5db; }
.cursor-default { cursor: default; }
.cursor-default:hover { background: #f9fafb; border-color: #e5e7eb; }
.form-input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; font-family: inherit;}
.upload-area { display: block; text-align: center; background: #f9fafb; border: 2px dashed #d1d5db; padding: 20px; border-radius: 12px; cursor: pointer; font-weight: 600; color: #4b5563; margin-bottom: 15px; }
.preview-img { width: 100%; max-height: 180px; object-fit: cover; border-radius: 12px; margin-bottom: 15px; }
.popup-content { text-align: left; }
.popup-content h4 { margin: 0 0 10px 0; font-size: 16px; color: #1f2937; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px;}
.popup-content p { margin: 6px 0; font-size: 14px; color: #4b5563; }
.popup-image { width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; border: 1px solid #e5e7eb; }
.popup-btn { margin-top: 12px; padding: 10px; font-size: 14px; border-radius: 6px; }
.button-group { display: flex; gap: 10px; width: 100%; }
.btn-primary, .btn-secondary { padding: 12px; border-radius: 8px; font-weight: 600; border: none; cursor: pointer; text-align: center; flex: 1; transition: opacity 0.2s; }
.btn-primary { background: #2563eb; color: white; width: 100%;}
.btn-secondary { background: #f3f4f6; color: #374151; }
.full-width { width: 100%; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); backdrop-filter: blur(2px); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; padding: 30px; border-radius: 16px; width: 100%; max-width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
.status-badge { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; }
.status-badge.pending { background: #fef08a; color: #854d0e; }
.status-badge.approved { background: #bbf7d0; color: #166534; }
.status-badge.rejected { background: #fecaca; color: #991b1b; }
</style>