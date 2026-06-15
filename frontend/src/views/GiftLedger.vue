<script setup>
import { computed, onMounted, ref } from 'vue'
import { api, toYuan } from '../api.js'
import { CATS, catLabel, initials } from '../utils.js'
import Icon from '../components/Icon.vue'
import Sheet from '../components/Sheet.vue'
import Illustration from '../components/Illustration.vue'

const rows = ref([])
const loading = ref(true)
const q = ref('')
const filter = ref('')
const detail = ref({ open: false, data: null })

async function load() {
  loading.value = true
  const params = {}
  if (filter.value) params.category = filter.value
  if (q.value) params.q = q.value
  rows.value = await api.ledger(params)
  loading.value = false
}
onMounted(load)
function setFilter(k) { filter.value = k; load() }

async function open(r) {
  detail.value = { open: true, data: await api.ledgerDetail(r.counterparty_id) }
}

// width ratios for the net bar
const ratio = (r) => {
  const tot = r.in_cents + r.out_cents || 1
  return { out: (r.out_cents / tot) * 100, in: (r.in_cents / tot) * 100 }
}
</script>

<template>
  <div class="phead">
    <div><h1>台账</h1><div class="sub">每个对象的 送出 · 收到 · 净额累计</div></div>
  </div>

  <div class="filters">
    <button class="fchip" :class="{ active: filter === '' }" @click="setFilter('')">全部</button>
    <button v-for="c in CATS" :key="c.key" class="fchip" :class="{ active: filter === c.key }" @click="setFilter(c.key)">{{ c.label }}</button>
  </div>

  <div class="field" style="margin-top:0; position:relative; margin-bottom:14px">
    <Icon name="search" :size="18" style="position:absolute; left:12px; top:11px; color:var(--muted)" />
    <input class="input" style="padding-left:38px" v-model="q" placeholder="搜索对象…" @keyup.enter="load" @input="q || load()" />
  </div>

  <div v-if="loading" class="card"><div class="litem" v-for="i in 4" :key="i"><div class="skel" style="width:38px;height:38px;border-radius:12px" /><div class="grow"><div class="skel" style="height:14px;width:45%" /></div></div></div>

  <div v-else-if="!rows.length" class="empty">
    <Illustration name="ledger" /><div class="et">还没有往来记录</div>
    <div class="fs-sm">建事件并记账后，这里按对象汇总送/收/净</div>
  </div>

  <div v-else class="stack">
    <div v-for="r in rows" :key="r.counterparty_id" class="card tap" @click="open(r)">
      <div class="row" style="gap:12px">
        <div class="avatar" :class="[r.category, { round: r.kind === 'household' }]">{{ initials(r.name) }}</div>
        <div class="grow">
          <div class="row between">
            <span class="title">{{ r.name }}<span class="muted fs-sm" v-if="r.relation"> · {{ r.relation }}</span><span class="pill soft" :class="r.category" style="margin-left:6px">{{ catLabel(r.category) }}</span></span>
            <span class="amount tnum" :class="r.net_cents >= 0 ? 'pos' : 'neg'">
              净 {{ r.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(r.net_cents) }}
            </span>
          </div>
          <div class="netbar">
            <div class="out" :style="{ width: ratio(r).out + '%' }" />
            <div class="in" :style="{ width: ratio(r).in + '%' }" />
          </div>
          <div class="row between fs-sm muted" style="margin-top:6px">
            <span><span class="neg">送 ¥{{ toYuan(r.out_cents) }}</span> · <span class="pos">收 ¥{{ toYuan(r.in_cents) }}</span></span>
            <span>{{ r.count }} 笔 · 最近 {{ r.last_at || '—' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <Sheet v-model="detail.open" :title="detail.data ? detail.data.name + ' · 往来明细' : ''">
    <div v-if="detail.data">
      <div v-for="rec in detail.data.records" :key="rec.id" class="litem">
        <div class="grow">
          <div class="name">{{ rec.event_name }}</div>
          <div class="muted fs-sm">
            {{ rec.direction === 'in' ? '收礼' : '送礼' }} · {{ rec.occurred_at }}<span v-if="rec.note"> · {{ rec.note }}</span>
          </div>
        </div>
        <span class="amount tnum" :class="rec.direction === 'in' ? 'pos' : 'neg'">{{ rec.direction === 'in' ? '+' : '−' }}¥{{ toYuan(rec.amount_cents) }}</span>
      </div>
    </div>
  </Sheet>
</template>
