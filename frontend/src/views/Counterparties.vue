<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api.js'
import { askConfirm } from '../store.js'
import Select from '../components/Select.vue'

const list = ref([])
const loading = ref(true)
const q = ref('')

const showCreate = ref(false)
const form = ref({ name: '', relation: '', note: '', tags: '' })

const action = ref(null) // { type: 'convert'|'merge', cp }
const convertForm = ref({ household_name: '', spouse: '' })
const mergeForm = ref({ from_id: null, household_name: '' })

async function load() {
  loading.value = true
  list.value = await api.counterparties(q.value ? { q: q.value } : {})
  loading.value = false
}
onMounted(load)

async function create() {
  if (!form.value.name.trim()) return window.__libuToast('请填写名称')
  const tags = form.value.tags.split(/[,，\s]+/).filter(Boolean)
  await api.createCounterparty({
    name: form.value.name,
    relation: form.value.relation || null,
    note: form.value.note || null,
    tags,
  })
  showCreate.value = false
  form.value = { name: '', relation: '', note: '', tags: '' }
  load()
}

function openConvert(cp) {
  action.value = { type: 'convert', cp }
  convertForm.value = { household_name: cp.name + '&', spouse: '' }
}
async function doConvert() {
  const cp = action.value.cp
  await api.convertToHousehold(cp.id, {
    household_name: convertForm.value.household_name || null,
    add_persons: convertForm.value.spouse ? [{ name: convertForm.value.spouse, role: '配偶' }] : [],
  })
  action.value = null
  load()
}

function openMerge(cp) {
  action.value = { type: 'merge', cp }
  mergeForm.value = { from_id: null, household_name: cp.name + '&' }
}
async function doMerge() {
  if (!mergeForm.value.from_id) return window.__libuToast('请选择要并入的对象')
  await api.merge(action.value.cp.id, {
    from_id: mergeForm.value.from_id,
    household_name: mergeForm.value.household_name || null,
  })
  action.value = null
  load()
}

async function del(cp) {
  const ok = await askConfirm({
    title: '删除往来对象',
    message: `删除「${cp.name}」？有往来记录则不可删，删除后不可恢复。`,
    confirmText: '删除',
    danger: true,
  })
  if (!ok) return
  try {
    await api.deleteCounterparty(cp.id)
    load()
  } catch (e) { /* toast via interceptor */ }
}
</script>

<template>
  <div class="row" style="gap:8px; margin-bottom:10px">
    <input v-model="q" placeholder="搜索姓名…" @keyup.enter="load" />
    <button class="sm" @click="load">搜</button>
  </div>

  <div v-if="loading" class="empty">加载中…</div>
  <div v-else-if="!list.length" class="empty">还没有往来对象</div>

  <div v-for="cp in list" :key="cp.id" class="card">
    <div class="row between">
      <div>
        <span class="title">{{ cp.name }}</span>
        <span class="tag" v-if="cp.kind === 'household'">家庭</span>
        <span class="muted" v-if="cp.relation"> · {{ cp.relation }}</span>
      </div>
    </div>
    <div style="margin-top:6px" v-if="cp.tags.length || cp.persons.length">
      <span v-for="t in cp.tags" :key="t.id" class="tag">{{ t.name }}</span>
      <span class="muted" v-if="cp.persons.length">成员：{{ cp.persons.map((p) => p.name).join('、') }}</span>
    </div>
    <div class="muted" v-if="cp.note" style="margin-top:4px">{{ cp.note }}</div>
    <div class="row" style="gap:6px; margin-top:10px; flex-wrap:wrap">
      <button v-if="cp.kind === 'person'" class="ghost sm" @click="openConvert(cp)">结婚→家庭</button>
      <button class="ghost sm" @click="openMerge(cp)">合并</button>
      <button class="danger sm" @click="del(cp)">删除</button>
    </div>
  </div>

  <button class="fab" @click="showCreate = true">＋</button>

  <!-- create -->
  <div v-if="showCreate" class="modal-mask" @click.self="showCreate = false">
    <div class="modal">
      <h3>新建往来对象</h3>
      <label>姓名 / 家庭名</label>
      <input v-model="form.name" placeholder="张三 或 张三&李四" />
      <label>关系</label>
      <input v-model="form.relation" placeholder="同事/亲戚/同学/朋友" />
      <label>标签（逗号分隔）</label>
      <input v-model="form.tags" placeholder="发小, 公司" />
      <label>备注</label>
      <input v-model="form.note" />
      <div class="row" style="gap:10px; margin-top:16px">
        <button class="ghost" style="flex:1" @click="showCreate = false">取消</button>
        <button style="flex:1" @click="create">保存</button>
      </div>
    </div>
  </div>

  <!-- convert / merge -->
  <div v-if="action" class="modal-mask" @click.self="action = null">
    <div class="modal" v-if="action.type === 'convert'">
      <h3>{{ action.cp.name }} 结婚 → 升级为家庭</h3>
      <p class="muted">原有所有往来记录会自动归入这个家庭。</p>
      <label>家庭名</label>
      <input v-model="convertForm.household_name" />
      <label>配偶姓名</label>
      <input v-model="convertForm.spouse" placeholder="李四" />
      <div class="row" style="gap:10px; margin-top:16px">
        <button class="ghost" style="flex:1" @click="action = null">取消</button>
        <button style="flex:1" @click="doConvert">升级</button>
      </div>
    </div>
    <div class="modal" v-else>
      <h3>把另一个对象并入「{{ action.cp.name }}」</h3>
      <p class="muted">被并入方的往来历史会合并过来，被并入方随后会被删除。</p>
      <label>选择要并入的对象</label>
      <Select
        searchable
        v-model="mergeForm.from_id"
        placeholder="选择对象…"
        :options="list.filter((x) => x.id !== action.cp.id).map((c) => ({ value: c.id, label: c.name }))"
      />
      <label>合并后家庭名</label>
      <input v-model="mergeForm.household_name" />
      <div class="row" style="gap:10px; margin-top:16px">
        <button class="ghost" style="flex:1" @click="action = null">取消</button>
        <button style="flex:1" @click="doMerge">合并</button>
      </div>
    </div>
  </div>
</template>
