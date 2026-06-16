<script setup>
import { ref, watch, nextTick } from 'vue'
import { confirmState, resolveConfirm } from '../store.js'

const inputVal = ref('')
const inputEl = ref(null)
let prevOverflow = ''

// lock body scroll while open; seed/focus the input in prompt mode.
// Save/restore the previous value so opening over an already-open Sheet
// (which also locks scroll) doesn't unlock it on close.
watch(() => confirmState.open, async (v) => {
  if (v) {
    prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = prevOverflow
  }
  if (v && confirmState.prompt) {
    inputVal.value = confirmState.value
    await nextTick()
    inputEl.value?.focus()
    inputEl.value?.select()
  }
})

function onConfirm() {
  if (confirmState.prompt) resolveConfirm(inputVal.value.trim())
  else resolveConfirm(true)
}
function onCancel() {
  resolveConfirm(confirmState.prompt ? null : false)
}
</script>

<template>
  <Teleport to="body">
    <Transition name="confirm">
      <div v-if="confirmState.open" class="confirm-mask" @click.self="onCancel">
        <div class="confirm-box" role="alertdialog" aria-modal="true">
          <h3 class="confirm-title">{{ confirmState.title }}</h3>
          <p v-if="confirmState.message" class="confirm-msg">{{ confirmState.message }}</p>
          <input
            v-if="confirmState.prompt"
            ref="inputEl"
            class="input"
            style="margin-bottom:18px"
            v-model="inputVal"
            :placeholder="confirmState.placeholder"
            @keyup.enter="onConfirm"
          />
          <div class="confirm-actions">
            <button class="btn ghost" @click="onCancel">{{ confirmState.cancelText }}</button>
            <button class="btn" :class="{ danger: confirmState.danger }" @click="onConfirm">
              {{ confirmState.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
