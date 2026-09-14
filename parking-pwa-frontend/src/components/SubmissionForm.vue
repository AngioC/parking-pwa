<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { storeToRefs } from 'pinia'
import { useAppStore } from '../store'

const store = useAppStore()
// Recuperiamo l'utente e la posizione del nuovo pin dallo store
const { user, draftPosition } = storeToRefs(store)

// Emettiamo eventi per comunicare con App.vue (es. chiudere il form o chiedere il login)
const emit = defineEmits(['close', 'require-login'])

const newReport = ref({ description: '', imageFile: null })
const imagePreview = ref(null)

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    newReport.value.imageFile = file
    imagePreview.value = URL.createObjectURL(file) 
  }
}

const closeForm = () => {
  // Puliamo i dati locali
  newReport.value = { description: '', imageFile: null }
  imagePreview.value = null
  // Resettiamo il pin sullo store
  store.draftPosition = null
  // Avvisiamo il componente padre di chiudere la vista
  emit('close')
}

const submitReport = async () => {
  if (!draftPosition.value) return
  
  // Se l'utente non è loggato, blocchiamo tutto e chiediamo ad App.vue di aprire il login
  if (!user.value) {
    emit('require-login')
    return
  }

  const formData = new FormData()
  formData.append('location', JSON.stringify({ 
    type: "Point", 
    coordinates: [draftPosition.value[1], draftPosition.value[0]] 
  }))
  formData.append('description', newReport.value.description)
  if (newReport.value.imageFile) formData.append('photo', newReport.value.imageFile)

  try {
    await axios.post('/api/submissions/', formData, { 
      headers: { 'Content-Type': 'multipart/form-data' } 
    })
    alert("Segnalazione inviata con successo!")
    // Aggiorniamo la lista delle segnalazioni dell'utente per mostrare quella nuova
    store.fetchMySubmissions()
    closeForm()
  } catch (error) {
    console.error(error)
    alert("Errore nell'invio della segnalazione.")
  }
}
</script>

<template>
  <div class="submission-form">
    <div class="view-header">
      <h2>Nuova Segnalazione</h2>
      <button class="icon-btn" @click="closeForm">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
    <p class="text-sm">Hai inserito un pin sulla mappa. Compila i dati per inviare.</p>
    
    <label class="upload-area">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
      <br>Scatta o Carica Foto
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
</template>

<style scoped>
.submission-form {
  padding: 25px;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
  background: white;
  overflow-y: auto;
}
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.view-header h2 { margin: 0; font-size: 20px; color: #1f2937; }
.spacer { flex-grow: 1; min-height: 20px; }
.text-sm { font-size: 14px; color: #6b7280; line-height: 1.5; margin-bottom: 15px;}
.icon-btn { background: #f3f4f6; border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; color: #4b5563; display: flex; justify-content: center; align-items: center; }
.icon-btn:hover { background: #e5e7eb; }
.form-input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; font-family: inherit;}
.upload-area { display: block; text-align: center; background: #f9fafb; border: 2px dashed #d1d5db; padding: 20px; border-radius: 12px; cursor: pointer; font-weight: 600; color: #4b5563; margin-bottom: 15px; }
.preview-img { width: 100%; max-height: 180px; object-fit: cover; border-radius: 12px; margin-bottom: 15px; }
.button-group { display: flex; gap: 10px; width: 100%; }
.btn-primary, .btn-secondary { padding: 12px; border-radius: 8px; font-weight: 600; border: none; cursor: pointer; text-align: center; flex: 1; transition: opacity 0.2s; }
.btn-primary { background: #2563eb; color: white; width: 100%;}
.btn-secondary { background: #f3f4f6; color: #374151; }
</style>