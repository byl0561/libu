<script setup>
defineProps({ name: String, size: { type: Number, default: 76 } })

// Line-drawn illustrations for empty states (currentColor stroke + faint fill).
const ART = {
  // 红包
  redpacket:
    '<rect x="16" y="9" width="32" height="46" rx="5" fill="currentColor" fill-opacity="0.07"/>' +
    '<rect x="16" y="9" width="32" height="46" rx="5"/>' +
    '<path d="M16 21c8 6 24 6 32 0"/>' +
    '<circle cx="32" cy="33" r="7"/><path d="M29 33h6M32 30v6"/>',
  // 礼盒
  gift:
    '<rect x="13" y="27" width="38" height="27" rx="3" fill="currentColor" fill-opacity="0.07"/>' +
    '<rect x="13" y="27" width="38" height="27" rx="3"/>' +
    '<path d="M11 27h42v8H11z"/><path d="M32 21v33"/>' +
    '<path d="M32 21c-4-5-12-4-12 1s8 5 12-1c4 6 12 6 12 1s-8-6-12-1z"/>',
  // 两个人
  people:
    '<circle cx="25" cy="25" r="8" fill="currentColor" fill-opacity="0.07"/>' +
    '<circle cx="25" cy="25" r="8"/>' +
    '<path d="M11 53c0-8 6-13 14-13s14 5 14 13"/>' +
    '<circle cx="45" cy="23" r="6.5"/><path d="M41 39c8 1 14 6 14 13"/>',
  // 账本（台账）
  ledger:
    '<path d="M32 17C26 13 18 12 11 13v33c7-1 15 0 21 4" fill="currentColor" fill-opacity="0.06"/>' +
    '<path d="M32 17C38 13 46 12 53 13v33c-7-1-15 0-21 4" fill="currentColor" fill-opacity="0.06"/>' +
    '<path d="M32 17C26 13 18 12 11 13v33c7-1 15 0 21 4"/>' +
    '<path d="M32 17C38 13 46 12 53 13v33c-7-1-15 0-21 4"/>' +
    '<path d="M32 17v37"/>' +
    '<path d="M17 25h9M17 31h9M38 25h9M38 31h9"/>',
  // 柱状图（趋势）
  chart:
    '<path d="M11 50h42"/>' +
    '<rect x="16" y="34" width="8" height="16" rx="1.5" fill="currentColor" fill-opacity="0.07"/>' +
    '<rect x="16" y="34" width="8" height="16" rx="1.5"/>' +
    '<rect x="28" y="24" width="8" height="26" rx="1.5" fill="currentColor" fill-opacity="0.07"/>' +
    '<rect x="28" y="24" width="8" height="26" rx="1.5"/>' +
    '<rect x="40" y="40" width="8" height="10" rx="1.5" fill="currentColor" fill-opacity="0.07"/>' +
    '<rect x="40" y="40" width="8" height="10" rx="1.5"/>',
}
</script>

<template>
  <svg class="illus" :width="size" :height="size" viewBox="0 0 64 64" fill="none"
       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
       v-html="ART[name]" aria-hidden="true" />
</template>
