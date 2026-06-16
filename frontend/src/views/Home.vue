<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, toYuan } from '../api.js'
import { catMeta, catLabel, dirLabel } from '../utils.js'
import Icon from '../components/Icon.vue'
import Illustration from '../components/Illustration.vue'
import Select from '../components/Select.vue'

const router = useRouter()
const year = ref(new Date().getFullYear())
const yearOptions = computed(() => [year.value, year.value - 1, year.value - 2].map((y) => ({ value: y, label: y + ' 年' })))
const ov = ref(null)
const recent = ref([])
const loading = ref(true)

async function load() {
  loading.value = true
  const [o, evs] = await Promise.all([api.overview({ year: year.value }), api.events()])
  ov.value = o
  recent.value = evs.slice(0, 5)
  loading.value = false
}
onMounted(load)

const evAmount = (e) => `${dirLabel(e.direction)} ¥${toYuan(e.in_cents + e.out_cents)}`
</script>

<template>
  <div class="hero">
    <div class="seal">礼</div>
    <div class="hero-content">
      <div class="hero-title">礼簿</div>
      <div class="hero-sub">中国家庭只记三笔账 · 人情往来 · 子女 · 父母</div>
      <span class="yearsel">
        <Select plain v-model="year" :options="yearOptions" @change="load" />
      </span>
    </div>
  </div>

  <template v-if="loading">
    <div class="stats-grid">
      <div class="skel" style="height:108px; border-radius:20px" v-for="i in 3" :key="i" />
    </div>
  </template>

  <template v-else-if="ov">
    <div class="stats-grid">
      <div class="stat gift">
        <div class="k"><Icon name="gift" :size="15" /> 人情往来 · 净额</div>
        <div class="v tnum">{{ ov.gift.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.gift.net_cents) }}</div>
        <div class="x">收 ¥{{ toYuan(ov.gift.in_cents) }} · 送 ¥{{ toYuan(ov.gift.out_cents) }}</div>
      </div>
      <div class="stat child">
        <div class="k"><Icon name="child" :size="15" /> 子女 · 净额</div>
        <div class="v tnum">{{ ov.child.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.child.net_cents) }}</div>
        <div class="x">收 ¥{{ toYuan(ov.child.in_cents) }} · 送 ¥{{ toYuan(ov.child.out_cents) }}</div>
      </div>
      <div class="stat parents">
        <div class="k"><Icon name="heart" :size="15" /> 父母 · 净额</div>
        <div class="v tnum">{{ ov.parents.net_cents >= 0 ? '+' : '' }}¥{{ toYuan(ov.parents.net_cents) }}</div>
        <div class="x">收 ¥{{ toYuan(ov.parents.in_cents) }} · 送 ¥{{ toYuan(ov.parents.out_cents) }}</div>
      </div>
    </div>

    <div class="shead" style="margin-top:22px">
      <h2>最近事件</h2>
      <span class="link" @click="router.push('/events')">全部 ›</span>
    </div>

    <div v-if="!recent.length" class="empty">
      <Illustration name="redpacket" />
      <div class="et">还没有事件</div>
      <div class="fs-sm">点「新建事件」记下第一笔人情或开销</div>
    </div>
    <div v-else class="card">
      <div v-for="e in recent" :key="e.id" class="litem" style="cursor:pointer" @click="router.push(`/events/${e.id}`)">
        <div class="avatar" :style="{ background: catMeta(e.category).color }"><Icon :name="catMeta(e.category).icon" :size="19" /></div>
        <div class="grow">
          <div class="name">{{ e.name }}</div>
          <div class="muted fs-sm">{{ e.occurred_at }} · {{ e.record_count }} 笔</div>
        </div>
        <div class="amount tnum">{{ evAmount(e) }}</div>
      </div>
    </div>
  </template>
</template>
