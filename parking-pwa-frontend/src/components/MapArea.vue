<script setup>
import { ref, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '../store'
import "leaflet/dist/leaflet.css"
import "leaflet.markercluster/dist/MarkerCluster.css"
import "leaflet.markercluster/dist/MarkerCluster.Default.css"

// Importiamo Leaflet puro (addio @vue-leaflet/vue-leaflet!)
import L from 'leaflet'
import "leaflet.markercluster"

const store = useAppStore()
const { filteredSpots, draftPosition, center, zoom } = storeToRefs(store)

// Riferimento al <div> vuoto nel template
const mapContainer = ref(null) 

// Variabili locali totalmente invisibili a Vue
let map = null
let clusterGroup = null
let draftMarker = null

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

// Quando il componente è caricato sullo schermo, avviamo Leaflet
onMounted(() => {
  // 1. Inizializzazione pura (ZERO Proxy!)
  map = L.map(mapContainer.value).setView(center.value, zoom.value)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
  }).addTo(map)

  // 2. Evento Click per la bozza
  map.on('click', (event) => {
    const { lat, lng } = event.latlng
    store.setDraftPosition(lat, lng)
  })

  // 3. Creiamo il motore di clustering (ora sicuro al 100%)
  clusterGroup = L.markerClusterGroup({
    maxClusterRadius: 50,
    disableClusteringAtZoom: 18
  })
  map.addLayer(clusterGroup)

  // 4. Disegniamo i pin iniziali
  renderClusters()
})

// --- SINCRONIZZAZIONE MANUALE CON PINIA ---

// Quando cambiano i filtri o si scaricano nuovi posteggi
watch(filteredSpots, () => {
  renderClusters()
}, { deep: true })

// Quando l'utente clicca un posteggio dalla barra laterale, centriamo la mappa
watch(center, (newCenter) => {
  if (map) map.flyTo(newCenter, zoom.value)
})

// Quando l'utente clicca sulla mappa per inserire un posteggio (Marker rosso)
watch(draftPosition, (newPos) => {
  // Se c'era già un pin rosso, lo togliamo
  if (draftMarker) {
    map.removeLayer(draftMarker)
    draftMarker = null
  }
  // Se c'è una nuova posizione, lo disegniamo
  if (newPos) {
    draftMarker = L.marker(newPos, { icon: draftIcon })
      .bindPopup('Stai inserendo un nuovo posteggio qui.')
      .addTo(map)
  }
})

// --- LOGICA DI DISEGNO DEI CLUSTER ---
const renderClusters = () => {
  if (!map || !clusterGroup) return

  clusterGroup.clearLayers() 
  
  const markersArray = []

  filteredSpots.value.forEach(spot => {
    if (!spot.geometry || !spot.geometry.coordinates) return

    const lat = parseFloat(spot.geometry.coordinates[1])
    const lng = parseFloat(spot.geometry.coordinates[0])

    if (isNaN(lat) || isNaN(lng) || lat === 0 || lng === 0) return

    const marker = L.marker([lat, lng], { icon: cdnIcon })

    marker.bindPopup(() => {
      const div = document.createElement('div')
      div.className = 'popup-content'
      
      const photoHtml = spot.properties.photo ? `<img src="${spot.properties.photo}" class="popup-image">` : ''
      const dateStr = new Date(spot.properties.created_at).toLocaleDateString()
      const noteStr = spot.properties.description || 'Nessuna descrizione.'
      
      div.innerHTML = `
        <h4>Dettagli Posteggio</h4>
        ${photoHtml}
        <p><strong>📅 Data:</strong> ${dateStr}</p>
        <p><strong>📝 Nota:</strong> ${noteStr}</p>
        <button class="btn-primary popup-btn full-width">🧭 Ottieni Indicazioni</button>
      `
      
      div.querySelector('button').onclick = () => getDirections(spot)
      return div
    }, { minWidth: 260, maxWidth: 300 })

    markersArray.push(marker)
  })

  if (markersArray.length > 0) {
    clusterGroup.addLayers(markersArray) 
  }
}

const geolocateAndReport = () => {
  if (!navigator.geolocation) return alert("GPS non supportato.")
  navigator.geolocation.getCurrentPosition(
    (position) => {
      store.setDraftPosition(position.coords.latitude, position.coords.longitude)
      store.center = [position.coords.latitude, position.coords.longitude]
      store.zoom = 16
    },
    () => alert("Impossibile ottenere la posizione.")
  )
}

const getDirections = (spot) => {
  window.open(`https://www.google.com/maps/dir/?api=1&destination=${spot.geometry.coordinates[1]},${spot.geometry.coordinates[0]}`, '_blank')
}
</script>

<template>
  <div class="map-wrapper">
    <!-- ADDIO Wrapper di Vue! Creiamo solo un semplice contenitore <div> -->
    <div ref="mapContainer" class="pure-leaflet-map"></div>

    <button class="fab" @click="geolocateAndReport">📍 Usa Posizione GPS</button>
  </div>
</template>

<style scoped>
/* STILI DEL COMPONENTE VUE (Limitati a questo file) */
.map-wrapper { height: 100%; width: 100%; position: relative; z-index: 1; }
.pure-leaflet-map { height: 100%; width: 100%; z-index: 1; }
.fab { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); z-index: 1000; background: #2563eb; color: white; border: none; padding: 16px 28px; border-radius: 30px; font-size: 16px; font-weight: 700; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.4); cursor: pointer; transition: transform 0.2s; }
.fab:active { transform: translateX(-50%) scale(0.95); }
</style>

<style>
/* STILI GLOBALI (Necessari per elementi creati dinamicamente da Leaflet come i popup) */
.popup-content { text-align: left; }
.popup-content h4 { margin: 0 0 10px 0; font-size: 16px; color: #1f2937; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px;}
.popup-content p { margin: 6px 0; font-size: 14px; color: #4b5563; }

/* Adesso l'immagine obbedirà a queste regole! */
.popup-image { width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; border: 1px solid #e5e7eb; }

.popup-btn { margin-top: 12px; padding: 10px; font-size: 14px; border-radius: 6px; background: #2563eb; color: white; border: none; cursor: pointer; }
.full-width { width: 100%; }

/* Fix aggiuntivo per limitare la larghezza del popup in caso di schermi piccoli */
.leaflet-popup-content { width: 260px !important; max-width: 100%; }
</style>