<script setup>
import { ref, watch } from 'vue'
import { api } from '../api.js'
import { askConfirm } from '../store.js'
import { CATS, catMeta, dirLabel, dirOptions } from '../utils.js'
import Sheet from './Sheet.vue'
import Segmented from './Segmented.vue'
import Icon from './Icon.vue'
import DatePicker from './DatePicker.vue'

const props = defineProps({ modelValue: Boolean, event: Object })
const emit = defineEmits(['update:modelValue', 'saved', 'deleted'])

const f = ref({})
watch(() => props.modelValue, (v) => {
  if (v && props.event) {
    const e = props.event
    f.value = {
      name: e.name, occurred_at: e.occurred_at, note: e.note || '',
      category: e.category, direction: e.direction,
      record_count: e.record_count ?? 0, sync_dates: false,
    }
  }
})

const close = () => emit('update:modelValue', false)

async function save() {
  if (!f.value.name.trim()) return window.__libuToast('请填写事件名', 'error')
  const p = { name: f.value.name, occurred_at: f.value.occurred_at, note: f.value.note || null }
  if (f.value.record_count === 0) { p.category = f.value.category; p.direction = f.value.direction }
  if (f.value.sync_dates) p.sync_record_dates = true
  await api.updateEvent(props.event.id, p)
  close()
  window.__libuToast('已保存')
  emit('saved')
}

async function remove() {
  const ok = await askConfirm({
    title: '删除事件',
    message: '仅当事件下没有流水时可删，删除后不可恢复。',
    confirmText: '删除',
    danger: true,
  })
  if (!ok) return
  try { await api.deleteEvent(props.event.id); close(); emit('deleted') } catch (e) { /* toast */ }
}
</script>

<template>
  <Sheet :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)" title="编辑事件">
    <div class="field"><label>事件名 / 事由</label><input class="input" v-model="f.name" /></div>

    <div class="field">
      <label>日期</label>
      <DatePicker v-model="f.occurred_at" />
      <label style="display:flex; align-items:center; gap:8px; margin-top:10px; color:var(--ink-2); cursor:pointer">
        <input type="checkbox" class="check" v-model="f.sync_dates" />
        同时把沿用原日期的流水一起改到新日期
      </label>
    </div>

    <div class="field" v-if="f.record_count === 0">
      <label>类型</label>
      <Segmented v-model="f.category" :options="CATS.map((c) => ({ value: c.key, label: c.label }))" />
      <div style="margin-top:8px">
        <Segmented v-model="f.direction" :options="dirOptions(f.category)" />
      </div>
    </div>
    <div class="field" v-else>
      <label>类型</label>
      <div class="muted fs-sm">{{ catMeta(f.category).label }}<span v-if="f.category === 'gift'"> · {{ dirLabel(f.direction) }}</span> · 已有流水，类型/方向不可改</div>
    </div>

    <div class="field"><label>备注</label><input class="input" v-model="f.note" placeholder="可选" /></div>

    <button class="btn block" style="background:transparent; color:var(--neg); border:1px solid var(--line); margin-top:12px" @click="remove">
      <Icon name="trash" :size="16" /> 删除事件
    </button>

    <template #foot>
      <button class="btn ghost" style="flex:1" @click="close">取消</button>
      <button class="btn" style="flex:1.6" @click="save">保存</button>
    </template>
  </Sheet>
</template>
