<script setup>
defineProps({ modelValue: [String, Number], options: Array })
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="seg">
    <button v-for="o in options" :key="o.value" type="button"
            :class="{ active: modelValue === o.value }"
            @click="emit('update:modelValue', o.value)">
      {{ o.label }}
    </button>
  </div>
</template>
