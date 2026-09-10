import { defineStore } from 'pinia'
import axios from 'axios'
import { supabase } from './supabase'

export const useAppStore = defineStore('app', {
  // 1. STATO: I dati condivisi tra tutti i componenti
  state: () => ({
    parkingSpots: [],
    mySubmissions: [],
    user: null,
    draftPosition: null, // Posizione del nuovo pin da inserire
    center: [41.90, 12.49], // Centro della mappa
    zoom: 6
  }),

  // 2. AZIONI: Le funzioni che modificano i dati
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
    }
  }
})