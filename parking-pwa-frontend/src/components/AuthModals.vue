<script setup>
import { ref } from 'vue'
import { supabase } from '../supabase'
import { useAppStore } from '../store'

const store = useAppStore()
const emit = defineEmits(['close']) // Avvisa App.vue di chiudere il modale

const email = ref('')
const password = ref('')
// Variabile per passare da Login a Signup nello stesso popup
const isLoginMode = ref(true) 

const handleLogin = async () => {
  const { data, error } = await supabase.auth.signInWithPassword({ 
    email: email.value, 
    password: password.value 
  })
  
  if (error) return alert("Errore di login: " + error.message)
  
  // Salviamo l'utente nello store e il token nel browser
  store.setUser(data.user)
  localStorage.setItem('supabase_token', data.session.access_token)
  emit('close')
}

const handleSignup = async () => {
  const { data, error } = await supabase.auth.signUp({ 
    email: email.value, 
    password: password.value 
  })
  
  if (error) return alert("Errore: " + error.message)
  
  alert("Registrato! Ora puoi accedere.")
  // Torniamo alla vista di Login
  isLoginMode.value = true
}
</script>

<template>
  <!-- Il .self fa in modo che cliccando fuori dal riquadro bianco, il modale si chiuda -->
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="view-header">
        <h2>{{ isLoginMode ? 'Accedi' : 'Registrazione' }}</h2>
        <button class="icon-btn" @click="$emit('close')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      
      <input type="email" v-model="email" class="form-input" placeholder="La tua Email">
      <input type="password" v-model="password" class="form-input" placeholder="La tua Password (min. 6 caratteri)">
      
      <button class="btn-primary" style="margin-bottom: 15px;" @click="isLoginMode ? handleLogin() : handleSignup()">
        {{ isLoginMode ? 'Entra' : 'Crea Account' }}
      </button>
      
      <hr class="divider">
      
      <button class="btn-secondary full-width" @click="isLoginMode = !isLoginMode">
        {{ isLoginMode ? 'Non hai un account? Registrati' : 'Torna al Login' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(3px); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; padding: 30px; border-radius: 16px; width: 100%; max-width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.view-header h2 { margin: 0; font-size: 20px; color: #1f2937; }
.icon-btn { background: #f3f4f6; border: none; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; color: #4b5563; display: flex; justify-content: center; align-items: center; }
.icon-btn:hover { background: #e5e7eb; }
.form-input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; font-family: inherit; font-size: 15px; }
.btn-primary, .btn-secondary { padding: 12px; border-radius: 8px; font-weight: 600; border: none; cursor: pointer; text-align: center; width: 100%; transition: background-color 0.2s; }
.btn-primary { background: #2563eb; color: white; }
.btn-primary:hover { background: #1d4ed8; }
.btn-secondary { background: #f3f4f6; color: #374151; }
.btn-secondary:hover { background: #e5e7eb; }
.divider { border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0; }
</style>