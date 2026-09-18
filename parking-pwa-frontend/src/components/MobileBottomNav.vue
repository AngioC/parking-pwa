<script setup>
import { ref } from 'vue'
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
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon><line x1="8" y1="2" x2="8" y2="18"></line><line x1="16" y1="6" x2="16" y2="22"></line></svg>
      <span class="label">Esplora</span>
    </button>
    
    <button class="nav-item" :class="{ active: activeTab === 'list' }" @click="setTab('list')">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
      <span class="label">Lista</span>
    </button>
    
    <!-- Nuova Tab Chi Siamo -->
    <button class="nav-item" :class="{ active: activeTab === 'about' }" @click="setTab('about')">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
      <span class="label">Info</span>
    </button>
    
    <button class="nav-item" :class="{ active: activeTab === 'profile' }" @click="setTab('profile')">
      <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
      <span class="label">Profilo</span>
    </button>
  </nav>
</template>

<style scoped>
.mobile-bottom-nav { display: none; }
@media (max-width: 768px) {
  .mobile-bottom-nav { display: flex; position: fixed; bottom: 0; left: 0; right: 0; height: 70px; background: #ffffff; box-shadow: 0 -2px 15px rgba(0,0,0,0.06); border-top: 1px solid #e2e8f0; z-index: 2000; justify-content: space-around; align-items: center; padding-bottom: env(safe-area-inset-bottom); }
  .nav-item { background: none; border: none; display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; height: 100%; color: #94a3b8; cursor: pointer; transition: all 0.2s; }
  .nav-item.active { color: #4f46e5; }
  .icon { width: 22px; height: 22px; margin-bottom: 5px; transition: transform 0.2s; }
  .nav-item.active .icon { transform: scale(1.1); stroke-width: 2.5;}
  .label { font-size: 11px; font-weight: 700; letter-spacing: 0.3px;}
}
</style>