import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import Home from './views/Home.vue'
import Events from './views/Events.vue'
import EventDetail from './views/EventDetail.vue'
import People from './views/People.vue'
import GiftLedger from './views/GiftLedger.vue'
import Stats from './views/Stats.vue'
import Settings from './views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', name: 'home', component: Home, meta: { title: '首页' } },
    { path: '/events', name: 'events', component: Events, meta: { title: '事件' } },
    { path: '/events/:id', name: 'event-detail', component: EventDetail, meta: { title: '事件详情' } },
    { path: '/ledger', name: 'ledger', component: GiftLedger, meta: { title: '人情台账' } },
    { path: '/people', name: 'people', component: People, meta: { title: '关系' } },
    { path: '/stats', name: 'stats', component: Stats, meta: { title: '统计' } },
    { path: '/settings', name: 'settings', component: Settings, meta: { title: '设置' } },
  ],
})

createApp(App).use(router).mount('#app')
