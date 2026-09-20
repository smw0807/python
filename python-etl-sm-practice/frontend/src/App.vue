<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { api, type Customer, type MonthlySale, type ProductSale } from './api'

const customers = ref<Customer[]>([]), monthly = ref<MonthlySale[]>([]), products = ref<ProductSale[]>([])
const grade = ref(''), page = ref(1), total = ref(0), loading = ref(true), error = ref('')
const pages = computed(() => Math.max(1, Math.ceil(total.value / 10)))
const won = (v:number) => new Intl.NumberFormat('ko-KR', {style:'currency', currency:'KRW', maximumFractionDigits:0}).format(v)

async function loadCustomers() {
  loading.value = true; error.value = ''
  try { const data = await api.customers(page.value, grade.value); customers.value=data.items; total.value=data.total }
  catch (e) { error.value = e instanceof Error ? e.message : '알 수 없는 오류' }
  finally { loading.value = false }
}
watch([grade, page], loadCustomers)
watch(grade, () => { page.value = 1 })
onMounted(async () => {
  await loadCustomers()
  try { [monthly.value, products.value] = await Promise.all([api.monthly(), api.products()]) }
  catch (e) { error.value = e instanceof Error ? e.message : '집계 조회 실패' }
})
</script>

<template>
  <main>
    <header><p>Customer Operations</p><h1>통합고객 운영 대시보드</h1></header>
    <p v-if="error" class="error">{{ error }}</p>
    <section class="grid">
      <article><h2>월별 매출</h2><table><thead><tr><th>월</th><th>주문</th><th>고객</th><th>매출</th></tr></thead><tbody><tr v-for="m in monthly" :key="m.month"><td>{{m.month}}</td><td>{{m.order_count}}</td><td>{{m.customer_count}}</td><td>{{won(m.total_amount)}}</td></tr></tbody></table></article>
      <article><h2>상위 상품</h2><table><thead><tr><th>상품</th><th>카테고리</th><th>수량</th><th>매출</th></tr></thead><tbody><tr v-for="p in products" :key="p.product_id"><td>{{p.product_name}}</td><td>{{p.category}}</td><td>{{p.total_quantity}}</td><td>{{won(p.total_amount)}}</td></tr></tbody></table></article>
    </section>
    <section><div class="toolbar"><h2>고객 매출</h2><select v-model="grade"><option value="">전체 등급</option><option v-for="g in ['BRONZE','SILVER','GOLD','VIP']" :key="g">{{g}}</option></select></div>
      <p v-if="loading">불러오는 중...</p><p v-else-if="!customers.length">조건에 맞는 고객이 없습니다.</p>
      <table v-else><thead><tr><th>고객</th><th>등급</th><th>지역</th><th>주문</th><th>총매출</th><th>최근 주문</th></tr></thead><tbody><tr v-for="c in customers" :key="c.customer_id"><td>{{c.customer_name}} <small>{{c.customer_id}}</small></td><td>{{c.grade}}</td><td>{{c.city}}</td><td>{{c.order_count}}</td><td>{{won(c.total_amount)}}</td><td>{{c.last_order_at?.slice(0,10) ?? '-'}}</td></tr></tbody></table>
      <nav><button :disabled="page<=1" @click="page--">이전</button><span>{{page}} / {{pages}}</span><button :disabled="page>=pages" @click="page++">다음</button></nav>
    </section>
  </main>
</template>
