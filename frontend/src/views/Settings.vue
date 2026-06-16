<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api.js'
import { reloadMembers, askConfirm, askPrompt } from '../store.js'
import Icon from '../components/Icon.vue'

const members = ref([])
const newName = ref('')

async function load() { members.value = await api.members() }
onMounted(load)

async function add() {
  if (!newName.value.trim()) return
  await api.createMember({ name: newName.value, sort: members.value.length })
  newName.value = ''
  await load(); reloadMembers()
}
async function rename(m) {
  const name = await askPrompt({ title: '重命名成员', value: m.name, placeholder: '成员名', confirmText: '保存' })
  if (name) { await api.updateMember(m.id, { name }); await load(); reloadMembers() }
}
async function del(m) {
  const ok = await askConfirm({
    title: '删除成员',
    message: `删除「${m.name}」？有记账引用则不可删，删除后不可恢复。`,
    confirmText: '删除',
    danger: true,
  })
  if (!ok) return
  try { await api.deleteMember(m.id); await load(); reloadMembers() } catch (e) { /* toast */ }
}
</script>

<template>
  <div class="phead"><div><h1>设置</h1><div class="sub">记账人与关于</div></div></div>

  <div class="shead"><h2>记账人（成员）</h2></div>
  <div class="card">
    <p class="muted fs-sm" style="margin:0 0 8px">记账时下拉手选「谁记的」。访问控制由 nginx 用户名密码负责，这里不是登录账号。</p>
    <div v-for="m in members" :key="m.id" class="litem">
      <div class="avatar neutral round" style="width:34px;height:34px;font-size:13px">{{ m.name.slice(0, 2) }}</div>
      <div class="grow"><span class="name">{{ m.name }}</span></div>
      <button class="iconbtn" title="改名" @click="rename(m)"><Icon name="edit" :size="17" /></button>
      <button class="iconbtn" title="删除" @click="del(m)"><Icon name="trash" :size="17" /></button>
    </div>
    <div class="field-row" style="margin-top:12px">
      <input class="input" v-model="newName" placeholder="新成员名，如 爸爸 / 妈妈" @keyup.enter="add" />
      <button class="btn" @click="add"><Icon name="plus" :size="16" /></button>
    </div>
  </div>

  <div class="shead"><h2>关于</h2></div>
  <div class="card">
    <p class="muted fs-sm" style="margin:0">
      <b>礼簿 Libu</b> · 只记三笔账：人情往来、子女、父母。<br />
      数据存于自托管 SQLite；备份请直接复制服务器上的 <code>libu.db</code>。
    </p>
  </div>
</template>
