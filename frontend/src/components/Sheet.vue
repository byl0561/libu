<script setup>
import { watch } from 'vue'
import Icon from './Icon.vue'

const props = defineProps({ modelValue: Boolean, title: String })
const emit = defineEmits(['update:modelValue'])

function close() { emit('update:modelValue', false) }

// lock body scroll while open
watch(() => props.modelValue, (v) => {
  document.body.style.overflow = v ? 'hidden' : ''
})
</script>

<template>
  <Teleport to="body">
    <Transition>
      <div v-if="modelValue" class="sheet-mask" @click.self="close">
        <div class="sheet" role="dialog">
          <div class="sheet-head">
            <h3>{{ title }}</h3>
            <button class="iconbtn" @click="close"><Icon name="close" :size="20" /></button>
          </div>
          <div class="sheet-body"><slot /></div>
          <div v-if="$slots.foot" class="sheet-foot"><slot name="foot" /></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
