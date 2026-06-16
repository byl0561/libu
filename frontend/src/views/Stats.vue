<script setup>
import { computed, onMounted, ref } from 'vue'
import { api, toYuan } from '../api.js'
import Icon from '../components/Icon.vue'
import Illustration from '../components/Illustration.vue'
import Select from '../components/Select.vue'

const year = ref(new Date().getFullYear())
const ov = ref(null)
const trend = ref([])
const byMember = ref([])

async function load() {
  ;[ov.value, trend.value, byMember.value] = await Promise.all([
    api.overview({ year: year.value }),
    api.trend({ year: year.value }),
    api.byMember(),
  ])
}
onMounted(load)

// Current year shows Jan..current month (已经过去的月份); past years show all 12.
// Always descending, missing months filled with 0 — so no dup/out-of-order months.
const trendRows = computed(() => {
  const now = new Date()
  const lastMonth = year.value === now.getFullYear() ? now.getMonth() + 1 : 12
  const byMonth = Object.fromEntries(trend.value.map((t) => [t.month, t]))
  const rows = []
  for (let m = lastMonth; m >= 1; m--) {
    const mm = String(m).padStart(2, '0')
    const r = byMonth[mm] || { month: mm, in_cents: 0, out_cents: 0 }
    rows.push({ ...r, net: r.in_cents - r.out_cents }) // 当月结余 = 收 - 送
  }
  return rows
})
// Bar length is keyed to the largest |结余| of the shown months, so the most
// extreme month fills the track and color (pos/neg) carries the sign.
const maxTrend = computed(() => Math.max(1, ...trendRows.value.map((t) => Math.abs(t.net))))
const barPct = (t) => (Math.abs(t.net) / maxTrend.value) * 100
// Bar = this member's share of the total record count.
const memberTotal = computed(() => byMember.value.reduce((s, m) => s + m.count, 0) || 1)
const mLabel = (m) => m + '月'
</script>

<template>
  <div class="phead">
    <div><h1>统计</h1><div class="sub">三笔账的全貌</div></div>
    <Select style="width:auto" v-model="year" :options="[year, year - 1, year - 2].map((y) => ({ value: y, label: y + ' 年' }))" @change="load" />
  </div>

  <div v-if="ov" class="stats-grid">
    <div class="stat gift"><div class="k"><Icon name="gift" :size="15" /> 人情净额</div><div class="v tnum">{{ ov.gift.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.gift.net_cents) }}</div><div class="x">收 ¥{{ toYuan(ov.gift.in_cents) }} · 送 ¥{{ toYuan(ov.gift.out_cents) }}</div></div>
    <div class="stat child"><div class="k"><Icon name="child" :size="15" /> 子女净额</div><div class="v tnum">{{ ov.child.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.child.net_cents) }}</div><div class="x">收 ¥{{ toYuan(ov.child.in_cents) }} · 送 ¥{{ toYuan(ov.child.out_cents) }}</div></div>
    <div class="stat parents"><div class="k"><Icon name="heart" :size="15" /> 父母净额</div><div class="v tnum">{{ ov.parents.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.parents.net_cents) }}</div><div class="x">收 ¥{{ toYuan(ov.parents.in_cents) }} · 送 ¥{{ toYuan(ov.parents.out_cents) }}</div></div>
  </div>

  <div class="shead"><h2>本年度趋势</h2></div>
  <div class="card">
    <div v-if="!trend.length" class="empty" style="padding:30px 20px">
      <Illustration name="chart" :size="62" />
      <div class="fs-sm">还没有趋势数据</div>
    </div>
    <template v-else>
      <div v-for="t in trendRows" :key="t.month" class="row" style="gap:10px; margin:9px 0">
        <span class="muted fs-xs" style="width:46px">{{ mLabel(t.month) }}</span>
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: barPct(t) + '%', background: t.net >= 0 ? 'var(--pos)' : 'var(--neg)' }" />
        </div>
        <span class="fs-xs tnum" :class="t.net >= 0 ? 'pos' : 'neg'" style="width:90px; text-align:right">{{ t.net >= 0 ? '+' : '' }}¥{{ toYuan(t.net) }}</span>
      </div>
    </template>
  </div>

  <template v-if="byMember.length">
    <div class="shead"><h2>成员记账占比</h2></div>
    <div class="card">
      <div v-for="m in byMember" :key="m.member" class="row" style="gap:10px; margin:9px 0">
        <span class="muted fs-xs" style="width:46px">{{ m.member }}</span>
        <div class="bar-track"><div class="bar-fill" :style="{ width: (m.count / memberTotal * 100) + '%', background: 'var(--parents)' }" /></div>
        <span class="muted fs-xs tnum" style="width:74px; text-align:right">{{ m.count }}笔</span>
      </div>
    </div>
  </template>
</template>
