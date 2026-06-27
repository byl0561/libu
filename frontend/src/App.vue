<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './components/Icon.vue'
import CreateEventSheet from './components/CreateEventSheet.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import AppLogo from './components/AppLogo.vue'
import { ui, openCreate } from './store.js'

const route = useRoute()

const NAV = [
  { to: '/', name: 'events', icon: 'home', label: '首页' },
  { to: '/events', icon: 'calendar', label: '事件' },
  { to: '/ledger', icon: 'ledger', label: '台账' },
  { to: '/people', icon: 'people', label: '关系' },
  { to: '/stats', icon: 'chart', label: '统计' },
  { to: '/settings', icon: 'settings', label: '设置' },
]
// mobile bottom bar shows the 5 most-used
const TABS = NAV.filter((n) => n.label !== '统计')

const title = computed(() => route.meta?.title || '礼簿')

// toast host
const toasts = ref([])
let seq = 0
onMounted(() => {
  window.__libuToast = (msg, type = 'info') => {
    const id = ++seq
    toasts.value.push({ id, msg, type })
    setTimeout(() => { toasts.value = toasts.value.filter((t) => t.id !== id) }, 2800)
  }
})

const isActive = (to) => (to === '/' ? route.path === '/' : route.path.startsWith(to))
</script>

<template>
  <div class="layout">
    <!-- Desktop sidebar -->
    <aside class="sidebar">
      <div class="sb-brand">
        <div class="logo"><AppLogo /></div>
        <div>
          <div class="name">礼簿</div>
          <div class="tag">只记三笔账</div>
        </div>
      </div>
      <router-link v-for="n in NAV" :key="n.to" :to="n.to" class="sb-link" :class="{ active: isActive(n.to) }">
        <Icon :name="n.icon" :size="20" /> {{ n.label }}
      </router-link>
    </aside>

    <div class="main">
      <!-- Mobile top bar -->
      <header class="appbar">
        <span class="ab-brand">礼簿</span>
        <span class="ab-title" v-if="title !== '礼簿'">· {{ title }}</span>
        <span class="ab-spacer" />
        <button class="iconbtn" @click="openCreate"><Icon name="plus" :size="22" /></button>
      </header>

      <main class="page">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </main>
    </div>

    <!-- Mobile bottom tab bar -->
    <nav class="tabbar">
      <router-link v-for="t in TABS" :key="t.to" :to="t.to" :class="{ active: isActive(t.to) }">
        <Icon class="ico" :name="t.icon" :size="22" />
        <span>{{ t.label }}</span>
      </router-link>
    </nav>

    <!-- Mobile FAB -->
    <button class="fab" @click="openCreate"><Icon name="plus" :size="26" /></button>

    <CreateEventSheet v-model="ui.createOpen" />

    <!-- Global confirm dialog -->
    <ConfirmDialog />

    <!-- Toasts -->
    <div class="toast-wrap">
      <TransitionGroup name="toast">
        <div v-for="t in toasts" :key="t.id" class="toast" :class="{ err: t.type === 'error' }">
          <Icon :name="t.type === 'error' ? 'close' : 'check'" :size="16" /> {{ t.msg }}
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>
