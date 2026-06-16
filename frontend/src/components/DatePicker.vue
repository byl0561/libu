<script setup>
import { ref, computed, nextTick, onBeforeUnmount } from 'vue'
import Icon from './Icon.vue'

// Themed calendar replacing <input type="date">. v-model is a 'YYYY-MM-DD' string.
const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '选择日期' },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const root = ref(null)
const triggerBtn = ref(null)
const popStyle = ref({})

const pad = (n) => String(n).padStart(2, '0')
const fmt = (y, mo, d) => `${y}-${pad(mo + 1)}-${pad(d)}` // mo is 0-based

function parse(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || '')
  return m ? { y: +m[1], mo: +m[2] - 1, d: +m[3] } : null
}

const view = ref({ y: 2000, mo: 0 })
function syncView() {
  const p = parse(props.modelValue)
  const now = new Date()
  view.value = p ? { y: p.y, mo: p.mo } : { y: now.getFullYear(), mo: now.getMonth() }
}

const WEEK = ['一', '二', '三', '四', '五', '六', '日']

const cells = computed(() => {
  const { y, mo } = view.value
  const lead = (new Date(y, mo, 1).getDay() + 6) % 7 // Monday-first
  const days = new Date(y, mo + 1, 0).getDate()
  const arr = []
  for (let i = 0; i < lead; i++) arr.push(null)
  for (let d = 1; d <= days; d++) arr.push(d)
  return arr
})

const todayStr = (() => {
  const n = new Date()
  return fmt(n.getFullYear(), n.getMonth(), n.getDate())
})()

function shift(delta) {
  let { y, mo } = view.value
  mo += delta
  if (mo < 0) { mo = 11; y-- } else if (mo > 11) { mo = 0; y++ }
  view.value = { y, mo }
}

function place() {
  const el = triggerBtn.value
  if (!el) return
  const r = el.getBoundingClientRect()
  const below = window.innerHeight - r.bottom
  const openUp = below < 320 && r.top > below
  popStyle.value = {
    position: 'fixed',
    left: Math.min(r.left, window.innerWidth - 280) + 'px',
    width: '264px',
    ...(openUp ? { bottom: window.innerHeight - r.top + 6 + 'px' } : { top: r.bottom + 6 + 'px' }),
  }
}

function onDocDown(e) {
  if (root.value?.contains(e.target)) return
  if (e.target.closest?.('.dd-pop')) return
  close()
}

async function openCal() {
  syncView()
  open.value = true
  await nextTick()
  place()
  window.addEventListener('scroll', place, true)
  window.addEventListener('resize', place)
  document.addEventListener('mousedown', onDocDown, true)
}

function close() {
  if (!open.value) return
  open.value = false
  window.removeEventListener('scroll', place, true)
  window.removeEventListener('resize', place)
  document.removeEventListener('mousedown', onDocDown, true)
}

function toggle() { open.value ? close() : openCal() }

function pick(d) {
  if (!d) return
  emit('update:modelValue', fmt(view.value.y, view.value.mo, d))
  close()
}

onBeforeUnmount(close)
</script>

<template>
  <div class="dd" ref="root">
    <button ref="triggerBtn" type="button" class="dd-trigger" @click="toggle">
      <span class="dd-val" :class="{ ph: !modelValue }">{{ modelValue || placeholder }}</span>
      <Icon name="calendar" :size="16" class="dd-caret" />
    </button>

    <Teleport to="body">
      <Transition name="dd">
        <div v-if="open" class="dd-pop cal" :style="popStyle">
          <div class="cal-head">
            <button type="button" class="iconbtn" @click="shift(-1)"><Icon name="back" :size="18" /></button>
            <span class="cal-title">{{ view.y }} 年 {{ view.mo + 1 }} 月</span>
            <button type="button" class="iconbtn" @click="shift(1)"><Icon name="right" :size="18" /></button>
          </div>
          <div class="cal-grid">
            <span v-for="w in WEEK" :key="w" class="cal-wd">{{ w }}</span>
          </div>
          <div class="cal-grid">
            <template v-for="(d, i) in cells" :key="i">
              <span v-if="d === null" class="cal-cell empty" />
              <button
                v-else
                type="button"
                class="cal-cell"
                :class="{ sel: fmt(view.y, view.mo, d) === modelValue, today: fmt(view.y, view.mo, d) === todayStr }"
                @click="pick(d)"
              >{{ d }}</button>
            </template>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
