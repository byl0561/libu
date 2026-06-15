import { reactive } from 'vue'
import { api } from './api.js'

// Lightweight global state: the create-event sheet + cached lookups.
export const ui = reactive({ createOpen: false })
export const openCreate = () => { ui.createOpen = true }

export const store = reactive({
  meta: { subtypes: {}, category_labels: {} },
  members: [],
  loaded: false,
})

export async function ensureLookups() {
  if (store.loaded) return
  const [meta, members] = await Promise.all([api.meta(), api.members()])
  store.meta = meta
  store.members = members
  store.loaded = true
}

export async function reloadMembers() {
  store.members = await api.members()
}
