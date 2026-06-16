<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, toYuan, toCents } from '../api.js'
import { catMeta, catLabel, dirLabel, subLabel } from '../utils.js'
import { store, ensureLookups, askConfirm } from '../store.js'
import Icon from '../components/Icon.vue'
import Sheet from '../components/Sheet.vue'
import EditEventSheet from '../components/EditEventSheet.vue'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)

const event = ref(null)
const records = ref([])
const counterparties = ref([])
const loading = ref(true)

const drafts = ref([])
const cpSheet = ref({ open: false, name: '', relation: '', target: 0 })

const isGift = computed(() => event.value?.category === 'gift')
const showSubtype = computed(() => event.value && event.value.category !== 'gift' && event.value.direction === 'out')
const subtypeOpts = computed(() => (event.value ? store.meta.subtypes[event.value.category] || [] : []))
const members = computed(() => store.members)
// 对象字段的上下文标签
const cpLabel = computed(() => ({ gift: '往来对象', child: '孩子', parents: '父母' }[event.value?.category] || '对象'))
const cpName = (cid) => counterparties.value.find((c) => c.id === cid)?.name || '—'
const memberName = (mid) => members.value.find((m) => m.id === mid)?.name

async function load() {
  const data = await api.event(id)
  event.value = data.event
  records.value = data.records
}
onMounted(async () => {
  await ensureLookups()
  await load()
  // 三类都需要对象：按事件类别拉取候选对象
  counterparties.value = await api.counterparties({ category: event.value.category })
  loading.value = false
  addDraft()
})

function addDraft() {
  drafts.value.push({
    amount: '',
    counterparty_id: counterparties.value[0]?.id || null,
    subtype: showSubtype.value ? subtypeOpts.value[0] || null : null,
    member_id: members.value[0]?.id || null,
    note: '',
  })
}
const removeDraft = (i) => drafts.value.splice(i, 1)

function openAddCp(i) { cpSheet.value = { open: true, name: '', relation: '', target: i } }
async function saveCp() {
  if (!cpSheet.value.name.trim()) return
  const cp = await api.createCounterparty({
    category: event.value.category,
    name: cpSheet.value.name,
    relation: cpSheet.value.relation || null,
  })
  counterparties.value.unshift(cp)
  drafts.value[cpSheet.value.target].counterparty_id = cp.id
  cpSheet.value.open = false
}

const draftTotal = computed(() =>
  drafts.value.reduce((s, d) => s + (toCents(d.amount) || 0), 0)
)

async function submit() {
  const rows = []
  for (const d of drafts.value) {
    const cents = toCents(d.amount)
    if (!cents || cents <= 0) continue
    if (!d.counterparty_id) return window.__libuToast(`请为每笔选择${cpLabel.value}`, 'error')
    rows.push({
      amount_cents: cents,
      counterparty_id: d.counterparty_id,
      subtype: showSubtype.value ? d.subtype : null,
      member_id: d.member_id,
      note: d.note || null,
    })
  }
  if (!rows.length) return window.__libuToast('请至少填一笔金额', 'error')
  await api.addRecords(id, rows)
  drafts.value = []
  await load()
  addDraft()
  window.__libuToast(`已记 ${rows.length} 笔`)
}

async function delRecord(r) {
  const ok = await askConfirm({
    title: '删除流水',
    message: '删除这笔记录？删除后不可恢复。',
    confirmText: '删除',
    danger: true,
  })
  if (!ok) return
  await api.deleteRecord(r.id)
  await load()
}
const editOpen = ref(false)
</script>

<template>
  <div class="row" style="margin-bottom:8px">
    <button class="iconbtn" @click="router.back()" style="margin-left:-8px"><Icon name="back" :size="22" /></button>
    <span class="muted fs-sm">返回</span>
  </div>

  <template v-if="event">
    <!-- header -->
    <div class="card">
      <div class="row" style="gap:12px; align-items:flex-start">
        <div class="avatar" :style="{ background: catMeta(event.category).color }">
          <Icon :name="catMeta(event.category).icon" :size="20" />
        </div>
        <div class="grow">
          <div class="row wrap" style="gap:8px">
            <h2 style="font-size:18px">{{ event.name }}</h2>
            <span class="pill soft" :class="event.category">
              {{ catLabel(event.category) }} · {{ dirLabel(event.direction) }}
            </span>
          </div>
          <div class="muted fs-sm" style="margin-top:4px">{{ event.occurred_at }} · 共 {{ event.record_count }} 笔</div>
        </div>
      </div>
      <div class="row between" style="margin-top:14px; padding-top:14px; border-top:1px solid var(--line-2)">
        <span class="amount tnum" :class="event.direction === 'in' ? 'pos' : 'neg'">
          {{ dirLabel(event.direction) }} ¥{{ toYuan(event.in_cents + event.out_cents) }}
        </span>
        <button class="iconbtn" title="编辑事件" @click="editOpen = true"><Icon name="edit" :size="19" /></button>
      </div>
    </div>

    <!-- batch entry -->
    <div class="shead"><h2>记一笔</h2><span class="muted fs-sm" v-if="draftTotal">本次 ¥{{ toYuan(draftTotal) }}</span></div>
      <div class="card">
        <div v-for="(d, i) in drafts" :key="i" class="draft">
          <div class="draft-main">
            <input class="input lg" type="number" inputmode="decimal" v-model="d.amount" placeholder="0.00" />
            <button v-if="drafts.length > 1" class="iconbtn" @click="removeDraft(i)"><Icon name="close" :size="18" /></button>
          </div>

          <!-- 对象（三类都要、必填） -->
          <div class="field">
            <label>{{ cpLabel }}</label>
            <div class="field-row">
              <select class="select" v-model="d.counterparty_id">
                <option :value="null" disabled>选择…</option>
                <option v-for="c in counterparties" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
              <button class="btn ghost sm" @click="openAddCp(i)"><Icon name="plus" :size="16" /></button>
            </div>
          </div>
          <!-- 子类：仅非人情、且送出（收到不分子类） -->
          <div v-if="showSubtype" class="field">
            <label>子类</label>
            <div class="filters" style="margin-bottom:0">
              <button v-for="s in subtypeOpts" :key="s" class="fchip" :class="{ active: d.subtype === s }" @click="d.subtype = s">{{ subLabel(s) }}</button>
            </div>
          </div>

          <div class="grid2">
            <div class="field" style="margin-top:10px">
              <label>记账人</label>
              <select class="select" v-model="d.member_id">
                <option v-for="m in members" :key="m.id" :value="m.id">{{ m.name }}</option>
              </select>
            </div>
            <div class="field" style="margin-top:10px">
              <label>备注</label>
              <input class="input" v-model="d.note" placeholder="可选" />
            </div>
          </div>
          <div class="draft-sep" v-if="i < drafts.length - 1" />
        </div>

        <div class="row" style="gap:10px; margin-top:16px">
          <button class="btn ghost" style="flex:1" @click="addDraft"><Icon name="plus" :size="16" /> 再加一笔</button>
          <button class="btn" style="flex:1.6" @click="submit"><Icon name="check" :size="16" /> 保存</button>
        </div>
      </div>

    <!-- existing records -->
    <div class="shead"><h2>已记 {{ records.length }} 笔</h2></div>
    <div v-if="!records.length" class="empty" style="padding:32px"><div class="fs-sm">还没有记录，上面记第一笔吧</div></div>
    <div v-else class="card">
      <div v-for="r in records" :key="r.id" class="litem">
        <div class="grow">
          <div class="name">{{ cpName(r.counterparty_id) }}</div>
          <div class="muted fs-sm">
            <span v-if="r.subtype">{{ subLabel(r.subtype) }}</span>
            <span v-if="memberName(r.member_id)"> · {{ memberName(r.member_id) }}记</span>
            <span v-if="r.note"> · {{ r.note }}</span>
            <span v-if="r.occurred_at !== event.occurred_at"> · {{ r.occurred_at }}</span>
          </div>
        </div>
        <span class="amount tnum" :class="r.direction === 'in' ? 'pos' : 'neg'">{{ r.direction === 'in' ? '+' : '−' }}¥{{ toYuan(r.amount_cents) }}</span>
        <button class="iconbtn" @click="delRecord(r)"><Icon name="trash" :size="17" /></button>
      </div>
    </div>
  </template>

  <!-- quick add 对象（继承事件类别） -->
  <Sheet v-model="cpSheet.open" :title="`新建${cpLabel}`">
    <div class="field"><label>名称</label><input class="input" v-model="cpSheet.name"
      :placeholder="isGift ? '张三 或 张三&李四' : event.category === 'child' ? '老大 / 老二' : '男方父母 / 女方父母'" /></div>
    <div class="field" v-if="isGift"><label>关系</label><input class="input" v-model="cpSheet.relation" placeholder="同事/亲戚/同学/朋友" /></div>
    <template #foot>
      <button class="btn ghost" style="flex:1" @click="cpSheet.open = false">取消</button>
      <button class="btn" style="flex:1.6" @click="saveCp">保存并选用</button>
    </template>
  </Sheet>

  <!-- edit event (shared with the events list) -->
  <EditEventSheet v-model="editOpen" :event="event" @saved="load" @deleted="router.replace('/events')" />
</template>

<style scoped>
.draft-main { display: flex; align-items: center; gap: 10px; }
.draft-main .input.lg { flex: 1; }
.draft-sep { height: 1px; background: var(--line-2); margin: 16px 0 12px; }
@media (min-width: 720px) {
  .draft-main { gap: 14px; }
}
</style>
