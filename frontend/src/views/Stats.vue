<script setup>
import { computed, onMounted, ref } from 'vue'
import { api, toYuan } from '../api.js'
import Icon from '../components/Icon.vue'
import Illustration from '../components/Illustration.vue'

const year = ref(new Date().getFullYear())
const ov = ref(null)
const trend = ref([])
const byMember = ref([])

async function load() {
  ;[ov.value, trend.value, byMember.value] = await Promise.all([
    api.overview({ year: year.value }),
    api.trend({ months: 12 }),
    api.byMember(),
  ])
}
onMounted(load)

const maxTrend = computed(() => Math.max(1, ...trend.value.map((t) => t.in_cents + t.out_cents)))
const memberMax = computed(() => Math.max(1, ...byMember.value.map((m) => m.total_cents)))
const mLabel = (ym) => ym.slice(5) + '月'
</script>

<template>
  <div class="phead">
    <div><h1>统计</h1><div class="sub">三笔账的全貌</div></div>
    <select class="select" style="width:auto" v-model="year" @change="load">
      <option v-for="y in [year, year - 1, year - 2]" :key="y" :value="y">{{ y }} 年</option>
    </select>
  </div>

  <div v-if="ov" class="stats-grid">
    <div class="stat gift"><div class="k"><Icon name="gift" :size="15" /> 人情净额</div><div class="v tnum">{{ ov.gift.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.gift.net_cents) }}</div><div class="x">收 ¥{{ toYuan(ov.gift.in_cents) }} · 送 ¥{{ toYuan(ov.gift.out_cents) }}</div></div>
    <div class="stat child"><div class="k"><Icon name="child" :size="15" /> 子女净额</div><div class="v tnum">{{ ov.child.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.child.net_cents) }}</div><div class="x">收 ¥{{ toYuan(ov.child.in_cents) }} · 送 ¥{{ toYuan(ov.child.out_cents) }}</div></div>
    <div class="stat parents"><div class="k"><Icon name="heart" :size="15" /> 父母净额</div><div class="v tnum">{{ ov.parents.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.parents.net_cents) }}</div><div class="x">收 ¥{{ toYuan(ov.parents.in_cents) }} · 送 ¥{{ toYuan(ov.parents.out_cents) }}</div></div>
  </div>

  <div class="shead"><h2>近 12 个月趋势</h2></div>
  <div class="card">
    <div v-if="!trend.length" class="empty" style="padding:30px 20px">
      <Illustration name="chart" :size="62" />
      <div class="fs-sm">还没有趋势数据</div>
    </div>
    <div v-for="t in trend" :key="t.month" class="row" style="gap:10px; margin:9px 0">
      <span class="muted fs-xs" style="width:46px">{{ mLabel(t.month) }}</span>
      <div class="bar-track">
        <div class="bar-fill" :style="{ width: ((t.in_cents + t.out_cents) / maxTrend * 100) + '%' }" />
      </div>
      <span class="muted fs-xs tnum" style="width:74px; text-align:right">¥{{ toYuan(t.in_cents + t.out_cents) }}</span>
    </div>
  </div>

  <template v-if="byMember.length">
    <div class="shead"><h2>成员记账占比</h2></div>
    <div class="card">
      <div v-for="m in byMember" :key="m.member" class="row" style="gap:10px; margin:9px 0">
        <span class="muted fs-xs" style="width:46px">{{ m.member }}</span>
        <div class="bar-track"><div class="bar-fill" :style="{ width: (m.total_cents / memberMax * 100) + '%', background: 'var(--parents)' }" /></div>
        <span class="muted fs-xs tnum" style="width:74px; text-align:right">{{ m.count }}笔</span>
      </div>
    </div>
  </template>
</template>
