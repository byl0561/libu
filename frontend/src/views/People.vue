<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api.js'
import { CATS, catLabel, catMeta, initials } from '../utils.js'
import Icon from '../components/Icon.vue'
import Sheet from '../components/Sheet.vue'
import Segmented from '../components/Segmented.vue'
import Illustration from '../components/Illustration.vue'

const list = ref([])
const loading = ref(true)
const q = ref('')
const filter = ref('')

const create = ref({ open: false, category: 'gift', name: '', relation: '', tags: '', note: '' })
const edit = ref({ open: false, id: null, name: '', kind: 'person', relation: '', tags: '', note: '', persons: [] })
const merge = ref({ open: false, cp: null, from_id: null, household_name: '' })

async function load() {
  loading.value = true
  const params = {}
  if (filter.value) params.category = filter.value
  if (q.value) params.q = q.value
  list.value = await api.counterparties(params)
  loading.value = false
}
onMounted(load)
function setFilter(k) { filter.value = k; load() }

function openCreate() {
  create.value = { open: true, category: filter.value || 'gift', name: '', relation: '', tags: '', note: '' }
}
async function doCreate() {
  if (!create.value.name.trim()) return window.__libuToast('请填写名称', 'error')
  await api.createCounterparty({
    category: create.value.category,
    name: create.value.name,
    relation: create.value.relation || null,
    note: create.value.note || null,
    tags: create.value.tags.split(/[,，\s]+/).filter(Boolean),
  })
  create.value.open = false
  load()
}

function openEdit(cp) {
  edit.value = {
    open: true, id: cp.id, name: cp.name, kind: cp.kind,
    relation: cp.relation || '', note: cp.note || '',
    tags: cp.tags.map((t) => t.name).join(', '),
    persons: cp.persons.map((p) => ({ name: p.name, role: p.role || '' })),
  }
}
const addPerson = () => edit.value.persons.push({ name: '', role: '' })
const rmPerson = (i) => edit.value.persons.splice(i, 1)
async function doEdit() {
  if (!edit.value.name.trim()) return window.__libuToast('请填写名称', 'error')
  await api.updateCounterparty(edit.value.id, {
    name: edit.value.name,
    kind: edit.value.kind,
    relation: edit.value.relation || null,
    note: edit.value.note || null,
    tags: edit.value.tags.split(/[,，\s]+/).filter(Boolean),
    persons: edit.value.persons.filter((p) => p.name.trim()).map((p) => ({ name: p.name.trim(), role: p.role || null })),
  })
  edit.value.open = false
  window.__libuToast('已保存')
  load()
}

function openMerge(cp) { merge.value = { open: true, cp, from_id: null, household_name: cp.name + '&' } }
async function doMerge() {
  if (!merge.value.from_id) return window.__libuToast('请选择要并入的对象', 'error')
  await api.merge(merge.value.cp.id, { from_id: merge.value.from_id, household_name: merge.value.household_name || null })
  merge.value.open = false
  window.__libuToast('已合并往来历史')
  load()
}

async function doDelete() {
  if (!confirm(`删除「${edit.value.name}」？有往来记录则不可删，删除后不可恢复`)) return
  try {
    await api.deleteCounterparty(edit.value.id)
    edit.value.open = false
    load()
  } catch (e) { /* toast via interceptor */ }
}
</script>

<template>
  <div class="phead">
    <div><h1>关系</h1><div class="sub">往来对象 · 人情 / 子女 / 父母</div></div>
    <button class="btn" @click="openCreate"><Icon name="plus" :size="18" /> 新建</button>
  </div>

  <div class="filters">
    <button class="fchip" :class="{ active: filter === '' }" @click="setFilter('')">全部</button>
    <button v-for="c in CATS" :key="c.key" class="fchip" :class="{ active: filter === c.key }" @click="setFilter(c.key)">{{ c.label }}</button>
  </div>

  <div class="field" style="margin-top:0; position:relative; margin-bottom:14px">
    <Icon name="search" :size="18" style="position:absolute; left:12px; top:11px; color:var(--muted)" />
    <input class="input" style="padding-left:38px" v-model="q" placeholder="搜索姓名…" @keyup.enter="load" @input="q || load()" />
  </div>

  <div v-if="loading" class="card"><div class="litem" v-for="i in 4" :key="i"><div class="skel" style="width:38px;height:38px;border-radius:12px" /><div class="grow"><div class="skel" style="height:14px;width:40%" /></div></div></div>

  <div v-else-if="!list.length" class="empty">
    <Illustration name="people" /><div class="et">还没有往来对象</div>
    <div class="fs-sm">记人情时也可以即输即建</div>
  </div>

  <div v-else class="stack">
    <div v-for="cp in list" :key="cp.id" class="card">
      <div class="row" style="gap:12px; align-items:flex-start">
        <div class="avatar" :class="[cp.category, { round: cp.kind === 'household' }]">{{ initials(cp.name) }}</div>
        <div class="grow">
          <div class="row wrap" style="gap:6px">
            <span class="title">{{ cp.name }}</span>
            <span class="pill soft" :class="cp.category">{{ catLabel(cp.category) }}</span>
            <span v-if="cp.kind === 'household'" class="chip">家庭</span>
            <span v-if="cp.relation" class="muted fs-sm">· {{ cp.relation }}</span>
          </div>
          <div style="margin-top:6px" v-if="cp.tags.length">
            <span v-for="t in cp.tags" :key="t.id" class="tag">{{ t.name }}</span>
          </div>
          <div class="muted fs-sm" v-if="cp.persons.length">成员：{{ cp.persons.map((p) => p.name).join(' & ') }}</div>
          <div class="muted fs-sm" v-if="cp.note">{{ cp.note }}</div>
        </div>
        <div class="row" style="gap:2px">
          <button class="iconbtn" title="合并" @click="openMerge(cp)"><Icon name="link" :size="19" /></button>
          <button class="iconbtn" title="编辑" @click="openEdit(cp)"><Icon name="edit" :size="19" /></button>
        </div>
      </div>
    </div>
  </div>

  <!-- create -->
  <Sheet v-model="create.open" title="新建往来对象">
    <div class="field">
      <label>属于哪类</label>
      <Segmented v-model="create.category" :options="CATS.map((c) => ({ value: c.key, label: c.label }))" />
    </div>
    <div class="field">
      <label>{{ create.category === 'gift' ? '姓名 / 家庭名' : create.category === 'child' ? '孩子' : '父母（哪边）' }}</label>
      <input class="input" v-model="create.name"
             :placeholder="create.category === 'gift' ? '张三 或 张三&李四' : create.category === 'child' ? '老大 / 老二' : '男方父母 / 女方父母'" />
    </div>
    <div class="field" v-if="create.category === 'gift'"><label>关系</label><input class="input" v-model="create.relation" placeholder="同事/亲戚/同学/朋友" /></div>
    <div class="field"><label>标签（逗号分隔，可选）</label><input class="input" v-model="create.tags" placeholder="发小, 公司" /></div>
    <div class="field"><label>备注</label><input class="input" v-model="create.note" /></div>
    <template #foot>
      <button class="btn ghost" style="flex:1" @click="create.open = false">取消</button>
      <button class="btn" style="flex:1.6" @click="doCreate">保存</button>
    </template>
  </Sheet>

  <!-- edit -->
  <Sheet v-model="edit.open" title="编辑往来对象">
    <div class="field"><label>姓名 / 家庭名</label><input class="input" v-model="edit.name" placeholder="张三 或 张三&李四" /></div>
    <div class="field">
      <label>类型</label>
      <Segmented v-model="edit.kind" :options="[{ value: 'person', label: '个人' }, { value: 'household', label: '家庭' }]" />
      <div class="muted fs-xs" style="margin-top:6px">结婚 → 改为「家庭」并加成员；离婚 → 改回「个人」。往来历史始终保留。</div>
    </div>
    <div class="field" v-if="edit.kind === 'household'">
      <label>家庭成员</label>
      <div class="stack">
        <div v-for="(p, i) in edit.persons" :key="i" class="field-row">
          <input class="input" v-model="p.name" placeholder="姓名，如 张三" />
          <input class="input" v-model="p.role" placeholder="称谓" style="max-width:104px" />
          <button class="iconbtn" @click="rmPerson(i)"><Icon name="close" :size="18" /></button>
        </div>
      </div>
      <button class="btn ghost sm" style="margin-top:8px" @click="addPerson"><Icon name="plus" :size="15" /> 添加成员</button>
    </div>
    <div class="field"><label>关系</label><input class="input" v-model="edit.relation" placeholder="同事/亲戚/同学/朋友" /></div>
    <div class="field"><label>标签（逗号分隔）</label><input class="input" v-model="edit.tags" placeholder="发小, 公司" /></div>
    <div class="field"><label>备注</label><input class="input" v-model="edit.note" /></div>

    <button class="btn block" style="background:transparent; color:var(--neg); border:1px solid var(--line); margin-top:16px" @click="doDelete">
      <Icon name="trash" :size="16" /> 删除往来对象
    </button>

    <template #foot>
      <button class="btn ghost" style="flex:1" @click="edit.open = false">取消</button>
      <button class="btn" style="flex:1.6" @click="doEdit">保存</button>
    </template>
  </Sheet>

  <!-- merge -->
  <Sheet v-model="merge.open" title="合并往来对象">
    <p class="muted fs-sm" style="margin-top:0">把另一个对象并入「{{ merge.cp?.name }}」，往来历史合并过来，被并入方随后会被删除。</p>
    <div class="field">
      <label>选择要并入的对象</label>
      <select class="select" v-model="merge.from_id">
        <option :value="null">—</option>
        <option v-for="c in list.filter((x) => x.id !== merge.cp?.id && x.category === merge.cp?.category)" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
    </div>
    <div class="field"><label>合并后家庭名</label><input class="input" v-model="merge.household_name" /></div>
    <template #foot>
      <button class="btn ghost" style="flex:1" @click="merge.open = false">取消</button>
      <button class="btn" style="flex:1.6" @click="doMerge">合并</button>
    </template>
  </Sheet>
</template>
