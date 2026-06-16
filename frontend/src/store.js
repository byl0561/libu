import { reactive } from 'vue'
import { api } from './api.js'

// Lightweight global state: the create-event sheet + cached lookups.
export const ui = reactive({ createOpen: false })
export const openCreate = () => { ui.createOpen = true }

// Global confirm dialog (replaces native window.confirm). ConfirmDialog.vue is
// rendered once in App.vue and bound to this state; askConfirm() resolves to a
// boolean when the user picks an action.
export const confirmState = reactive({
  open: false,
  title: '确认',
  message: '',
  confirmText: '确定',
  cancelText: '取消',
  danger: false,
  prompt: false, // when true, show a text input and resolve its value (or null)
  value: '',
  placeholder: '',
  _resolve: null,
})

export function askConfirm(opts = {}) {
  return new Promise((resolve) => {
    confirmState.title = opts.title || '确认'
    confirmState.message = opts.message || ''
    confirmState.confirmText = opts.confirmText || '确定'
    confirmState.cancelText = opts.cancelText || '取消'
    confirmState.danger = opts.danger ?? false
    confirmState.prompt = false
    confirmState._resolve = resolve
    confirmState.open = true
  })
}

// Themed replacement for window.prompt(): resolves the entered string, or null on cancel.
export function askPrompt(opts = {}) {
  return new Promise((resolve) => {
    confirmState.title = opts.title || '输入'
    confirmState.message = opts.message || ''
    confirmState.confirmText = opts.confirmText || '确定'
    confirmState.cancelText = opts.cancelText || '取消'
    confirmState.danger = false
    confirmState.prompt = true
    confirmState.value = opts.value || ''
    confirmState.placeholder = opts.placeholder || ''
    confirmState._resolve = resolve
    confirmState.open = true
  })
}

export function resolveConfirm(value) {
  if (!confirmState.open) return
  confirmState.open = false
  const done = confirmState._resolve
  confirmState._resolve = null
  if (done) done(value)
}

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
