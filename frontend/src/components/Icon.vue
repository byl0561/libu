<script setup>
import { computed } from 'vue'

const props = defineProps({ name: String, size: { type: [Number, String], default: 22 } })

// Stroke-based 24x24 line icons (currentColor).
const ICONS = {
  home: '<path d="M4 11.5 12 4l8 7.5"/><path d="M6 10.2V20h12v-9.8"/>',
  calendar: '<rect x="4" y="5" width="16" height="15" rx="2.5"/><path d="M4 9.5h16M8.5 3v4M15.5 3v4"/>',
  ledger: '<path d="M7 8h11M7 8l3-3M7 8l3 3"/><path d="M17 16H6M17 16l-3-3M17 16l-3 3"/>',
  people: '<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 20c0-3.3 2.5-5.6 5.5-5.6S14.5 16.7 14.5 20"/><path d="M16 6a3 3 0 0 1 0 5.6M20.5 20c0-2.5-1.5-4.5-3.7-5.3"/>',
  chart: '<path d="M5 20V11M12 20V5M19 20v-6"/>',
  settings: '<path d="M4 7h9M19 7h1M4 17h1M11 17h9"/><circle cx="16" cy="7" r="2.4"/><circle cx="8" cy="17" r="2.4"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M21 21l-3.6-3.6"/>',
  close: '<path d="M6 6l12 12M18 6 6 18"/>',
  back: '<path d="M15 5l-7 7 7 7"/>',
  right: '<path d="M9 6l6 6-6 6"/>',
  check: '<path d="M5 12.5l4.5 4.5L19 7"/>',
  trash: '<path d="M4 7h16M9.5 7V5h5v2M6.5 7l1 13h9l1-13"/>',
  archive: '<rect x="3.5" y="4.5" width="17" height="4.5" rx="1.4"/><path d="M5.5 9v10.5h13V9M10 13h4"/>',
  edit: '<path d="M4 20.5h4L19.5 9l-4-4L4 16.5z"/><path d="M14 6.5l3.5 3.5"/>',
  gift: '<rect x="4" y="9.5" width="16" height="10.5" rx="1.6"/><path d="M3 9.5h18v3H3zM12 9.5V20"/><path d="M12 9.5C10.5 9.5 8 9 8 7s3-1 4 2.5C13 6 16 5 16 7s-2.5 2.5-4 2.5z"/>',
  heart: '<path d="M12 20s-6.5-4-8.2-8.2C2.6 9 4 6 7 6c1.8 0 3 1 5 3 2-2 3.2-3 5-3 3 0 4.4 3 3.2 5.8C18.5 16 12 20 12 20z"/>',
  child: '<circle cx="12" cy="6" r="2.6"/><path d="M12 9v6M8.5 11.5 12 10l3.5 1.5M9 20l3-5 3 5"/>',
  swap: '<path d="M7 8h11M7 8l3-3M7 8l3 3"/><path d="M17 16H6M17 16l-3-3M17 16l-3 3"/>',
  merge: '<path d="M7 4v4.5a4 4 0 0 0 4 4h6"/><path d="M14 9.5l3.5 3-3.5 3"/>',
  link: '<path d="M9.5 17H7.5a5 5 0 0 1 0-10h2"/><path d="M14.5 7h2a5 5 0 0 1 0 10h-2"/><path d="M8.5 12h7"/>',
  upgrade: '<path d="M12 19V6M12 6l-5 5M12 6l5 5"/>',
  hide: '<path d="M4 12s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z"/><circle cx="12" cy="12" r="2.4"/><path d="M4 4l16 16"/>',
  wallet: '<rect x="3.5" y="6" width="17" height="13" rx="2.5"/><path d="M16 12h2.5"/><path d="M3.5 9h13a1.5 1.5 0 0 1 0 3"/>',
  tag: '<path d="M4 12.5V5.5A1.5 1.5 0 0 1 5.5 4h7l7.5 7.5a1.5 1.5 0 0 1 0 2.1l-5.4 5.4a1.5 1.5 0 0 1-2.1 0z"/><circle cx="8.5" cy="8.5" r="1.2"/>',
}

const inner = computed(() => ICONS[props.name] || '')
</script>

<template>
  <svg class="ico" :width="size" :height="size" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
       v-html="inner" aria-hidden="true" />
</template>
