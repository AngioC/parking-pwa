<script setup>
import { ref } from 'vue'

// Emettiamo un evento verso App.vue per comunicare quale scheda ha premuto l'utente
const emit = defineEmits(['change-tab'])
const activeTab = ref('map')

const setTab = (tab) => {
  activeTab.value = tab
  emit('change-tab', tab)
}
</script>

<template>
  <nav class="mobile-bottom-nav">
    <button class="nav-item" :class="{ active: activeTab === 'map' }" @click="setTab('map')">
      <span class="icon">🗺️</span>
      <span class="label">Mappa</span>
    </button>
    
    <button class="nav-item" :class="{ active: activeTab === 'list' }" @click="setTab('list')">
      <span class="icon">📋</span>
      <span class="label">Posteggi</span>
    </button>
    
    <button class="nav-item" :class="{ active: activeTab === 'profile' }" @click="setTab('profile')">
      <span class="icon">👤</span>
      <span class="label">Profilo</span>
    </button>
  </nav>
</template>

<style scoped>
/* Di default (su Desktop) la nascondiamo completamente */
.mobile-bottom-nav {
  display: none;
}

/* Mostriamo la barra SOLO su schermi piccoli (Mobile) */
@media (max-width: 768px) {
  .mobile-bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px; /* Altezza fissa e comoda per le dita */
    background: #ffffff;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    z-index: 2000; /* Deve stare sopra la mappa */
    justify-content: space-around;
    align-items: center;
    /* safe-area-inset-bottom evita che la barra finisca sotto l'indicatore di scorrimento degli iPhone moderni */
    padding-bottom: env(safe-area-inset-bottom); 
  }
  
  .nav-item {
    background: none;
    border: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    height: 100%;
    color: #6b7280;
    cursor: pointer;
    transition: color 0.2s;
  }
  
  .nav-item.active {
    color: #2563eb; /* Colore primario acceso quando selezionato */
  }
  
  .icon {
    font-size: 24px;
    margin-bottom: 4px;
    filter: grayscale(100%);
    transition: filter 0.2s;
  }
  
  .nav-item.active .icon {
    filter: grayscale(0%);
  }
  
  .label {
    font-size: 12px;
    font-weight: 600;
  }
}
</style>