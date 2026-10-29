<template>
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
    <!-- 1. Órdenes Totales -->
    <div class="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between">
      <div class="flex items-center justify-between mb-2">
        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Total Órdenes</span>
        <div class="w-8 h-8 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700 text-sm">
          📑
        </div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-slate-900 tracking-tight">
          {{ datos.ordenes_totales || 0 }}
        </div>
        <p class="text-[11px] text-slate-500 mt-1 font-medium">Lotes de producción</p>
      </div>
    </div>

    <!-- 2. Terminadas -->
    <div class="bg-white rounded-2xl p-4 border border-emerald-200/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between">
      <div class="flex items-center justify-between mb-2">
        <span class="text-[11px] font-bold uppercase tracking-wider text-emerald-700">Terminadas</span>
        <div class="w-8 h-8 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 text-sm">
          📦
        </div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-emerald-600 tracking-tight">
          {{ datos.ordenes_terminadas || 0 }}
        </div>
        <p class="text-[11px] text-emerald-700 mt-1 font-semibold">
          {{ pctTerminadas }}% del total
        </p>
      </div>
    </div>

    <!-- 3. En Tejeduría -->
    <div class="bg-white rounded-2xl p-4 border border-blue-200/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between">
      <div class="flex items-center justify-between mb-2">
        <span class="text-[11px] font-bold uppercase tracking-wider text-blue-700">En Tejeduría</span>
        <div class="w-8 h-8 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 text-sm">
          🧵
        </div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-blue-600 tracking-tight">
          {{ datos.ordenes_en_tejeduria || 0 }}
        </div>
        <p class="text-[11px] text-blue-700 mt-1 font-semibold">
          {{ pctTejeduria }}% en telar
        </p>
      </div>
    </div>

    <!-- 4. Acabados -->
    <div class="bg-white rounded-2xl p-4 border border-purple-200/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between">
      <div class="flex items-center justify-between mb-2">
        <span class="text-[11px] font-bold uppercase tracking-wider text-purple-700">Acabados</span>
        <div class="w-8 h-8 rounded-xl bg-purple-50 flex items-center justify-center text-purple-600 text-sm">
          ✨
        </div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-purple-600 tracking-tight">
          {{ datos.acabados || 0 }}
        </div>
        <p class="text-[11px] text-purple-700 mt-1 font-semibold">
          {{ pctAcabados }}% en empaque
        </p>
      </div>
    </div>

    <!-- 5. Eficientes -->
    <div class="bg-white rounded-2xl p-4 border border-indigo-200/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between">
      <div class="flex items-center justify-between mb-2">
        <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-700">Eficientes</span>
        <div class="w-8 h-8 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 text-sm">
          🎯
        </div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-indigo-600 tracking-tight">
          {{ datos.eficientes || 0 }}
        </div>
        <p class="text-[11px] text-indigo-700 mt-1 font-semibold">
          {{ pctEficientes }}% a tiempo
        </p>
      </div>
    </div>

    <!-- 6. No Eficientes -->
    <div class="bg-white rounded-2xl p-4 border border-amber-200/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between">
      <div class="flex items-center justify-between mb-2">
        <span class="text-[11px] font-bold uppercase tracking-wider text-amber-700">No Eficientes</span>
        <div class="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 text-sm">
          ⚠️
        </div>
      </div>
      <div>
        <div class="text-3xl font-extrabold text-amber-600 tracking-tight">
          {{ datos.no_eficientes || 0 }}
        </div>
        <p class="text-[11px] text-amber-700 mt-1 font-semibold">
          {{ pctNoEficientes }}% con retraso
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  datos: {
    type: Object,
    default: () => ({})
  }
})

const total = computed(() => props.datos.ordenes_totales || 0)
const totalEvaluadas = computed(() => (props.datos.eficientes || 0) + (props.datos.no_eficientes || 0))

const pctTerminadas = computed(() => {
  if (!total.value) return '0.0'
  return (((props.datos.ordenes_terminadas || 0) / total.value) * 100).toFixed(1)
})

const pctTejeduria = computed(() => {
  if (!total.value) return '0.0'
  return (((props.datos.ordenes_en_tejeduria || 0) / total.value) * 100).toFixed(1)
})

const pctAcabados = computed(() => {
  if (!total.value) return '0.0'
  return (((props.datos.acabados || 0) / total.value) * 100).toFixed(1)
})

const pctEficientes = computed(() => {
  if (!totalEvaluadas.value) return '100.0'
  return (((props.datos.eficientes || 0) / totalEvaluadas.value) * 100).toFixed(1)
})

const pctNoEficientes = computed(() => {
  if (!totalEvaluadas.value) return '0.0'
  return (((props.datos.no_eficientes || 0) / totalEvaluadas.value) * 100).toFixed(1)
})
</script>
