import { defineStore } from 'pinia'
import axios from 'axios'
import { supabase } from './supabase'
import L from 'leaflet' // <-- AGGIUNTO: Necessario per calcolare le distanze

export const useAppStore = defineStore('app', {
  state: () => ({
    parkingSpots: [],
    mySubmissions: [],
    user: null,
    draftPosition: null, 
    center: [41.90, 12.49],
    zoom: 6,
    filters: {
      status: 'all', 
      radius1km: false
    }
  }),

  getters: {
    filteredSpots: (state) => {
      return state.parkingSpots.filter(spot => {
        // Filtro per Stato
        if (state.filters.status !== 'all' && spot.properties.status.toLowerCase() !== state.filters.status) return false
        
        // Filtro per Distanza (1 km dal centro mappa attuale)
        if (state.filters.radius1km) {
          const mapCenter = L.latLng(state.center[0], state.center[1])
          const spotPos = L.latLng(spot.geometry.coordinates[1], spot.geometry.coordinates[0])
          if (mapCenter.distanceTo(spotPos) > 1000) return false // distanceTo calcola in metri
        }
        return true
      })
    }
  },

  actions: {
    async fetchSpots() {
      try {
        const response = await axios.get('/api/spots/')
        this.parkingSpots = response.data.features
      } catch (error) { 
        console.error("Errore recupero posteggi:", error) 
      }
    },
    
    async fetchMySubmissions() {
      if (!this.user) return
      try {
        const response = await axios.get('/api/submissions/')
        this.mySubmissions = response.data.features
      } catch (error) {
        console.error("Errore recupero segnalazioni:", error)
      }
    },

    setUser(sessionUser) {
      this.user = sessionUser
    },

    setDraftPosition(lat, lng) {
      this.draftPosition = [lat, lng]
    },

    async searchAddress(query) {
      if (!query) return
      try {
        const res = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`)
        if (res.data && res.data.length > 0) {
          this.center = [parseFloat(res.data[0].lat), parseFloat(res.data[0].lon)]
          this.zoom = 16
        } else {
          alert("Indirizzo non trovato.")
        }
      } catch (e) { console.error("Errore Geocoding:", e) }
    }
  }
})