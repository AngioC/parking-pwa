<script setup>
import { storeToRefs } from 'pinia'
import { useAppStore } from '../store'
import "leaflet/dist/leaflet.css"
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet"
import L from 'leaflet'

// Collega lo store
const store = useAppStore()
const { parkingSpots, draftPosition, center, zoom } = storeToRefs(store)

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

// --- METODI ---
const onMapClick = (event) => {
  const { lat, lng } = event.latlng
  store.setDraftPosition(lat, lng)
  // Più avanti diremo allo store di aprire il form
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
    <l-map v-model:zoom="zoom" :center="center" :use-global-leaflet="false" @click="onMapClick">
      <l-tile-layer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap" />
      
      <!-- Marker dei posteggi -->
      <l-marker v-for="spot in parkingSpots" :key="spot.id" :lat-lng="[spot.geometry.coordinates[1], spot.geometry.coordinates[0]]" :icon="cdnIcon">
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

      <!-- Marker della nuova segnalazione in corso -->
      <l-marker v-if="draftPosition" :lat-lng="draftPosition" :icon="draftIcon">
        <l-popup>Stai inserendo un nuovo posteggio qui.</l-popup>
      </l-marker>
    </l-map>

    <button class="fab" @click="geolocateAndReport">📍 Usa Posizione GPS</button>
  </div>
</template>

<style scoped>
/* Stili specifici isolati per questo componente (aggiunto 'scoped') */
.map-wrapper { 
  height: 100%; 
  width: 100%; 
  position: relative; 
  z-index: 1; 
}
.fab { 
  position: absolute; 
  bottom: 30px; /* Su mobile alzeremo questo valore per non coprire la Bottom Nav */
  left: 50%; 
  transform: translateX(-50%); 
  z-index: 1000; 
  background: #2563eb; 
  color: white; 
  border: none; 
  padding: 16px 28px; 
  border-radius: 30px; 
  font-size: 16px; 
  font-weight: 700; 
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.4); 
  cursor: pointer; 
  transition: transform 0.2s; 
}
.fab:active { transform: translateX(-50%) scale(0.95); }
.popup-content { text-align: left; }
.popup-content h4 { margin: 0 0 10px 0; font-size: 16px; color: #1f2937; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px;}
.popup-content p { margin: 6px 0; font-size: 14px; color: #4b5563; }
.popup-image { width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; border: 1px solid #e5e7eb; }
.popup-btn { margin-top: 12px; padding: 10px; font-size: 14px; border-radius: 6px; background: #2563eb; color: white; border: none; cursor: pointer; }
.full-width { width: 100%; }
</style>