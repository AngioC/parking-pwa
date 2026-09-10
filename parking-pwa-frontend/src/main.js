import { createApp } from 'vue'
import { createPinia } from 'pinia' // Aggiungi questa riga
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia() // Crea l'istanza di Pinia

app.use(pinia) // Collega Pinia all'app
app.mount('#app')