<script setup>
import { watch } from 'vue'
import { confirmState, resolveConfirm } from '../store.js'

// lock body scroll while open
watch(() => confirmState.open, (v) => {
  document.body.style.overflow = v ? 'hidden' : ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="confirm">
      <div v-if="confirmState.open" class="confirm-mask" @click.self="resolveConfirm(false)">
        <div class="confirm-box" role="alertdialog" aria-modal="true">
          <h3 class="confirm-title">{{ confirmState.title }}</h3>
          <p class="confirm-msg">{{ confirmState.message }}</p>
          <div class="confirm-actions">
            <button class="btn ghost" @click="resolveConfirm(false)">{{ confirmState.cancelText }}</button>
            <button class="btn" :class="{ danger: confirmState.danger }" @click="resolveConfirm(true)">
              {{ confirmState.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
