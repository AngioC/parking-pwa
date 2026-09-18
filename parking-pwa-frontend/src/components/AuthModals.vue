<script setup>
import { ref } from 'vue'
import { supabase } from '../supabase'
import { useAppStore } from '../store'

const store = useAppStore()
const emit = defineEmits(['close']) 

const email = ref('')
const password = ref('')
const isLoginMode = ref(true) 

const handleLogin = async () => {
  const { data, error } = await supabase.auth.signInWithPassword({ email: email.value, password: password.value })
  if (error) return alert("Errore di login: " + error.message)
  store.setUser(data.user)
  localStorage.setItem('supabase_token', data.session.access_token)
  emit('close')
}

const handleSignup = async () => {
  const { data, error } = await supabase.auth.signUp({ email: email.value, password: password.value })
  if (error) return alert("Errore: " + error.message)
  alert("Registrato! Ora puoi accedere.")
  isLoginMode.value = true
}
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="view-header">
        <h2>{{ isLoginMode ? 'Accedi' : 'Registrazione' }}</h2>
        <button class="icon-btn" @click="$emit('close')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      
      <div class="form-group">
        <input type="email" v-model="email" class="form-input" placeholder="La tua Email">
        <input type="password" v-model="password" class="form-input" placeholder="La tua Password (min. 6 caratteri)">
      </div>
      
      <button class="btn-primary full-width" style="margin-bottom: 20px;" @click="isLoginMode ? handleLogin() : handleSignup()">
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
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; padding: 35px; border-radius: 20px; width: 100%; max-width: 400px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); animation: modalIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);}
@keyframes modalIn { from { opacity: 0; transform: translateY(20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }

.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.view-header h2 { margin: 0; font-size: 24px; color: #0f172a; font-weight: 800; letter-spacing: -0.5px;}
.icon-btn { background: #f1f5f9; border: none; width: 36px; height: 36px; border-radius: 10px; cursor: pointer; color: #64748b; display: flex; justify-content: center; align-items: center; transition: background 0.2s;}
.icon-btn:hover { background: #e2e8f0; color: #0f172a;}

.form-group { display: flex; flex-direction: column; gap: 15px; margin-bottom: 25px;}
.form-input { width: 100%; padding: 14px 16px; border: 1px solid #e2e8f0; border-radius: 10px; box-sizing: border-box; font-family: inherit; font-size: 15px; background: #f8fafc; transition: all 0.2s;}
.form-input:focus { outline: none; border-color: #4f46e5; background: white; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);}

.btn-primary { padding: 14px; border-radius: 10px; font-weight: 600; font-size: 15px; border: none; cursor: pointer; text-align: center; background: #4f46e5; color: white; transition: background-color 0.2s, transform 0.1s; }
.btn-primary:hover { background: #4338ca; transform: translateY(-1px);}
.btn-secondary { padding: 14px; border-radius: 10px; font-weight: 600; font-size: 15px; border: none; cursor: pointer; text-align: center; background: #f1f5f9; color: #475569; transition: background-color 0.2s; }
.btn-secondary:hover { background: #e2e8f0; }

.divider { border: 0; border-top: 1px solid #e2e8f0; margin: 0; margin-bottom: 20px;}
.full-width { width: 100%; }
</style>