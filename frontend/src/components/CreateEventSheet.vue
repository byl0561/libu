<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'
import { CATS, dirOptions, today } from '../utils.js'
import Sheet from './Sheet.vue'
import Segmented from './Segmented.vue'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])
const router = useRouter()

const form = ref({ category: 'gift', direction: 'out', name: '', occurred_at: today(), note: '' })
const saving = ref(false)

watch(() => props.modelValue, (v) => {
  if (v) form.value = { category: 'gift', direction: 'out', name: '', occurred_at: today(), note: '' }
})

const nameHints = {
  gift: ['婚礼', '满月酒', '乔迁', '寿宴', '白事', '过年红包'],
  child: ['报暑期班', '买奶粉尿布', '交学费', '收压岁钱'],
  parents: ['春节给爸妈', '给妈买保健品', '老人住院', '爸妈给的钱'],
}

async function submit() {
  if (!form.value.name.trim()) return window.__libuToast('请填写事件名')
  saving.value = true
  try {
    const ev = await api.createEvent({ ...form.value })
    emit('update:modelValue', false)
    router.push(`/events/${ev.id}`)
  } finally { saving.value = false }
}
</script>

<template>
  <Sheet :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)" title="新建事件">
    <div class="field">
      <label>记哪类账</label>
      <Segmented v-model="form.category" :options="CATS.map((c) => ({ value: c.key, label: c.label }))" />
    </div>

    <div class="field">
      <label>方向</label>
      <Segmented v-model="form.direction" :options="dirOptions(form.category)" />
    </div>

    <div class="field">
      <label>事件名 / 事由</label>
      <input class="input" v-model="form.name" placeholder="如 李四婚礼 / 我家满月酒 / 春节给爸妈" />
      <div class="row wrap" style="gap:6px; margin-top:8px">
        <button v-for="h in nameHints[form.category]" :key="h" class="tag" style="cursor:pointer; border:none"
                @click="form.name = h">{{ h }}</button>
      </div>
    </div>

    <div class="grid2">
      <div class="field"><label>日期</label><input class="input" type="date" v-model="form.occurred_at" /></div>
      <div class="field"><label>备注（可选）</label><input class="input" v-model="form.note" /></div>
    </div>

    <template #foot>
      <button class="btn ghost" style="flex:1" @click="emit('update:modelValue', false)">取消</button>
      <button class="btn" style="flex:2" :disabled="saving" @click="submit">建好，去记账 →</button>
    </template>
  </Sheet>
</template>
