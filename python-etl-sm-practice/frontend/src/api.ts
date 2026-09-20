export type Customer = { customer_id:string; customer_name:string; grade:string; city:string; order_count:number; total_amount:number; avg_order_amount:number; last_order_at:string|null }
export type Page<T> = { items:T[]; page:number; page_size:number; total:number }
export type MonthlySale = { month:string; order_count:number; customer_count:number; total_amount:number }
export type ProductSale = { product_id:string; product_name:string; category:string; total_quantity:number; total_amount:number; gross_profit:number }

const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
async function get<T>(path:string):Promise<T> {
  const response = await fetch(`${base}${path}`)
  if (!response.ok) throw new Error(`API ${response.status}`)
  return response.json()
}
export const api = {
      customers: (page=1, grade='') => {
        const params = new URLSearchParams({page:String(page), page_size:'10', sort:'-total_amount'})
        if (grade) params.set('grade', grade)
        return get<Page<Customer>>(`/api/customers?${params}`)
      },
  monthly: () => get<MonthlySale[]>('/api/sales/monthly?from_month=2026-01&to_month=2026-09'),
  products: () => get<ProductSale[]>('/api/sales/products?limit=8'),
}
