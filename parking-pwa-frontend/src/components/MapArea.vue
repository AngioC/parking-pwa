<script setup>
import { ref, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '../store'
import "leaflet/dist/leaflet.css"
import "leaflet.markercluster/dist/MarkerCluster.css"
import "leaflet.markercluster/dist/MarkerCluster.Default.css"

import L from 'leaflet'
import "leaflet.markercluster"

const store = useAppStore()
const { filteredSpots, draftPosition, center, zoom } = storeToRefs(store)

const mapContainer = ref(null) 
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

onMounted(() => {
  map = L.map(mapContainer.value).setView(center.value, zoom.value)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map)
  map.on('click', (event) => {
    const { lat, lng } = event.latlng
    store.setDraftPosition(lat, lng)
  })
  clusterGroup = L.markerClusterGroup({ maxClusterRadius: 50, disableClusteringAtZoom: 18 })
  map.addLayer(clusterGroup)
  renderClusters()
})

watch(filteredSpots, () => { renderClusters() }, { deep: true })
watch(center, (newCenter) => {
  if (map) map.setView(newCenter, zoom.value)
})
watch(draftPosition, (newPos) => {
  if (draftMarker) { map.removeLayer(draftMarker); draftMarker = null; }
  if (newPos) {
    draftMarker = L.marker(newPos, { icon: draftIcon }).bindPopup('Stai inserendo un nuovo posteggio qui.').addTo(map)
  }
})

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
        <h4 class="popup-title">Dettagli Posteggio</h4>
        ${photoHtml}
        <p class="popup-text"><span class="info-label">Data:</span> ${dateStr}</p>
        <p class="popup-text"><span class="info-label">Nota:</span> ${noteStr}</p>
        <button class="btn-primary popup-btn full-width">Ottieni Indicazioni</button>
      `
      div.querySelector('button').onclick = () => getDirections(spot)
      return div
    }, { minWidth: 260, maxWidth: 300 })
    markersArray.push(marker)
  })
  if (markersArray.length > 0) clusterGroup.addLayers(markersArray) 
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
const getDirections = (spot) => { window.open(`https://www.google.com/maps/dir/?api=1&destination=${spot.geometry.coordinates[1]},${spot.geometry.coordinates[0]}`, '_blank') }
</script>

<template>
  <div class="map-wrapper">
    <div ref="mapContainer" class="pure-leaflet-map"></div>
    <button class="fab" @click="geolocateAndReport">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>
      Usa Posizione GPS
    </button>
  </div>
</template>

<style scoped>
.map-wrapper { height: 100%; width: 100%; position: relative; z-index: 1; }
.pure-leaflet-map { height: 100%; width: 100%; z-index: 1; }
.fab { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); z-index: 1000; background: #1f2937; color: white; border: none; padding: 14px 24px; border-radius: 30px; font-size: 15px; font-weight: 600; box-shadow: 0 4px 15px rgba(0,0,0,0.2); cursor: pointer; transition: transform 0.2s, background 0.2s; display: flex; align-items: center; }
.fab:active { transform: translateX(-50%) scale(0.95); }
.fab:hover { background: #000000; }
</style>

<style>
.popup-content { text-align: left; font-family: inherit;}
.popup-title { margin: 0 0 12px 0; font-size: 16px; color: #1f2937; font-weight: 700; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px;}
.popup-text { margin: 6px 0; font-size: 14px; color: #374151; line-height: 1.4;}
.info-label { font-size: 12px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; margin-right: 4px;}
.popup-image { width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; border: 1px solid #e5e7eb; }
.popup-btn { margin-top: 12px; padding: 10px; font-size: 14px; border-radius: 8px; background: #2563eb; color: white; border: none; cursor: pointer; font-weight: 600; transition: background 0.2s;}
.popup-btn:hover { background: #1d4ed8; }
.full-width { width: 100%; }
.leaflet-popup-content { width: 260px !important; max-width: 100%; }
</style>