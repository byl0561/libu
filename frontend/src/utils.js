export const CATS = [
  { key: 'gift', label: '人情往来', short: '人情', icon: 'gift', color: 'var(--gift)' },
  { key: 'child', label: '子女', short: '子女', icon: 'child', color: 'var(--child)' },
  { key: 'parents', label: '父母', short: '父母', icon: 'heart', color: 'var(--parents)' },
]
export const catMeta = (k) => CATS.find((c) => c.key === k) || CATS[0]
export const catLabel = (k) => catMeta(k).label
export const catIcon = (k) => catMeta(k).icon
// 三类账统一：收(in) / 送(out)
export const dirLabel = (d) => ({ in: '收', out: '送' }[d] || d)
// 建事件时的方向选项（人情往来用"送礼/收礼"，其余用"送出/收到"）
export const dirOptions = (cat) =>
  cat === 'gift'
    ? [{ value: 'out', label: '送礼 / 随份子' }, { value: 'in', label: '收礼 / 办喜事' }]
    : [{ value: 'out', label: '送出 / 支出' }, { value: 'in', label: '收到 / 收入' }]

export const today = () => {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
}

export const initials = (name = '') => {
  const n = name.split('&')[0].trim()
  return n ? n.slice(0, name.includes('&') ? 1 : 2) : '?'
}

// subtype english key -> 中文
export const SUBTYPE_LABEL = {
  supplies: '用品', education: '教育', medical: '医疗', other: '其他',
  cash: '给钱', health: '保健品',
}
export const subLabel = (s) => SUBTYPE_LABEL[s] || s
