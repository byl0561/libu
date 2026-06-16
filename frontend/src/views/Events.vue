<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, toYuan } from '../api.js'
import { CATS, catMeta, dirLabel } from '../utils.js'
import { openCreate } from '../store.js'
import Icon from '../components/Icon.vue'
import EditEventSheet from '../components/EditEventSheet.vue'
import Illustration from '../components/Illustration.vue'

const router = useRouter()
const events = ref([])
const filter = ref('')
const loading = ref(true)

async function load() {
  loading.value = true
  events.value = await api.events(filter.value ? { category: filter.value } : {})
  loading.value = false
}
onMounted(load)
function setFilter(k) { filter.value = k; load() }

// group by year-month
const groups = computed(() => {
  const map = {}
  for (const e of events.value) {
    const ym = (e.occurred_at || '').slice(0, 7)
    ;(map[ym] = map[ym] || []).push(e)
  }
  return Object.entries(map).sort((a, b) => (a[0] < b[0] ? 1 : -1))
})
const evAmount = (e) => `${dirLabel(e.direction)} ¥${toYuan(e.in_cents + e.out_cents)}`

// ----- edit event (right ✎) -----
const ed = ref({ open: false, event: null })
function openEdit(e) { ed.value = { open: true, event: e } }
</script>

<template>
  <div class="phead">
    <div><h1>事件</h1><div class="sub">先建一场事，再批量记账</div></div>
    <button class="btn" @click="openCreate"><Icon name="plus" :size="18" /> 新建</button>
  </div>

  <div class="filters">
    <button class="fchip" :class="{ active: filter === '' }" @click="setFilter('')">全部</button>
    <button v-for="c in CATS" :key="c.key" class="fchip" :class="{ active: filter === c.key }" @click="setFilter(c.key)">
      {{ c.label }}
    </button>
  </div>

  <div v-if="loading" class="card">
    <div class="litem" v-for="i in 4" :key="i">
      <div class="skel" style="width:38px;height:38px;border-radius:12px" />
      <div class="grow"><div class="skel" style="height:14px;width:50%" /><div class="skel" style="height:11px;width:30%;margin-top:8px" /></div>
    </div>
  </div>

  <div v-else-if="!events.length" class="empty">
    <Illustration name="redpacket" />
    <div class="et">这里还没有事件</div>
    <div class="fs-sm">办喜事、随份子、给娃报班、孝敬爸妈，都从「新建事件」开始</div>
    <button class="btn" style="margin-top:16px" @click="openCreate"><Icon name="plus" :size="18" /> 新建事件</button>
  </div>

  <template v-else>
    <div v-for="[ym, list] in groups" :key="ym">
      <div class="shead"><h2>{{ ym.replace('-', ' 年 ') }} 月</h2></div>
      <div class="card">
        <div v-for="e in list" :key="e.id" class="litem" style="cursor:pointer" @click="router.push(`/events/${e.id}`)">
          <div class="avatar" :style="{ background: catMeta(e.category).color }"><Icon :name="catMeta(e.category).icon" :size="19" /></div>
          <div class="grow">
            <div class="name">{{ e.name }}</div>
            <div class="muted fs-sm">{{ e.occurred_at }} · {{ e.record_count }} 笔</div>
          </div>
          <div class="row" style="gap:4px">
            <span class="amount tnum" :class="e.direction === 'in' ? 'pos' : 'neg'">{{ evAmount(e) }}</span>
            <button class="iconbtn" title="编辑事件" @click.stop="openEdit(e)"><Icon name="edit" :size="18" /></button>
          </div>
        </div>
      </div>
    </div>
  </template>

  <EditEventSheet v-model="ed.open" :event="ed.event" @saved="load" @deleted="load" />
</template>
