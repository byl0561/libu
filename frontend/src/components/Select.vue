<script setup>
import { ref, computed, nextTick, onBeforeUnmount } from 'vue'
import Icon from './Icon.vue'

// Themed dropdown replacing native <select>. Options: [{ value, label }].
// `searchable` adds a filter box (used for the counterparty picker).
const props = defineProps({
  modelValue: { default: null }, // value of selected option (any type), null = none
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '选择…' },
  searchable: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  plain: { type: Boolean, default: false }, // borderless trigger (e.g. on the hero)
})
const emit = defineEmits(['update:modelValue', 'change'])

const open = ref(false)
const search = ref('')
const root = ref(null)
const triggerBtn = ref(null)
const searchInput = ref(null)
const popStyle = ref({})

const selected = computed(() => props.options.find((o) => o.value === props.modelValue) || null)
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!props.searchable || !q) return props.options
  return props.options.filter((o) => String(o.label).toLowerCase().includes(q))
})

function place() {
  const el = triggerBtn.value
  if (!el) return
  const r = el.getBoundingClientRect()
  const maxH = 300
  const below = window.innerHeight - r.bottom
  const openUp = below < 200 && r.top > below
  const width = Math.min(Math.max(r.width, 180), 320)
  popStyle.value = {
    position: 'fixed',
    left: Math.max(8, Math.min(r.left, window.innerWidth - width - 8)) + 'px',
    minWidth: r.width + 'px',
    maxWidth: Math.max(r.width, 320) + 'px',
    maxHeight: maxH + 'px',
    ...(openUp
      ? { bottom: window.innerHeight - r.top + 6 + 'px' }
      : { top: r.bottom + 6 + 'px' }),
  }
}

function onDocDown(e) {
  if (root.value?.contains(e.target)) return
  if (e.target.closest?.('.dd-pop')) return
  close()
}

async function openMenu() {
  if (props.disabled) return
  open.value = true
  search.value = ''
  await nextTick()
  place()
  window.addEventListener('scroll', place, true)
  window.addEventListener('resize', place)
  document.addEventListener('mousedown', onDocDown, true)
  if (props.searchable) searchInput.value?.focus()
}

function close() {
  if (!open.value) return
  open.value = false
  window.removeEventListener('scroll', place, true)
  window.removeEventListener('resize', place)
  document.removeEventListener('mousedown', onDocDown, true)
}

function toggle() {
  open.value ? close() : openMenu()
}

function pick(o) {
  emit('update:modelValue', o.value)
  emit('change', o.value)
  close()
}

onBeforeUnmount(close)
</script>

<template>
  <div class="dd" ref="root" :class="{ disabled, 'dd-plain': plain }">
    <button ref="triggerBtn" type="button" class="dd-trigger" :class="{ plain }" :disabled="disabled" @click="toggle">
      <span class="dd-val" :class="{ ph: !selected }">{{ selected ? selected.label : placeholder }}</span>
      <Icon name="chevron" :size="16" class="dd-caret" :class="{ up: open }" />
    </button>

    <Teleport to="body">
      <Transition name="dd">
        <div v-if="open" class="dd-pop" :style="popStyle">
          <div v-if="searchable" class="dd-search">
            <Icon name="search" :size="16" />
            <input ref="searchInput" v-model="search" placeholder="搜索…" @keydown.esc="close" />
          </div>
          <div class="dd-list">
            <button
              v-for="o in filtered"
              :key="String(o.value)"
              type="button"
              class="dd-opt"
              :class="{ on: o.value === modelValue }"
              @click="pick(o)"
            >
              <span>{{ o.label }}</span>
              <Icon v-if="o.value === modelValue" name="check" :size="15" />
            </button>
            <div v-if="!filtered.length" class="dd-empty">无匹配</div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
