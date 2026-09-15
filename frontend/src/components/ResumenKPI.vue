<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="bg-white rounded-xl shadow-sm border p-6 border-l-4 border-l-slate-900">
      <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Órdenes Totales</h3>
      <p class="text-4xl font-extrabold text-slate-900">{{ datos.ordenes_totales || 0 }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-6 border-l-4 border-l-green-600">
      <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Terminadas</h3>
      <p class="text-4xl font-extrabold text-green-600">{{ datos.ordenes_terminadas || 0 }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-6 border-l-4 border-l-blue-600">
      <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">En Tejeduría</h3>
      <p class="text-4xl font-extrabold text-blue-600">{{ datos.ordenes_en_tejeduria || 0 }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-6 border-l-4 border-l-purple-600">
      <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Acabados</h3>
      <p class="text-4xl font-extrabold text-purple-600">{{ datos.acabados || 0 }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-6 border-l-4 border-l-blue-600">
      <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Eficientes</h3>
      <p class="text-4xl font-extrabold text-blue-600">{{ datos.eficientes || 0 }}</p>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-6 border-l-4 border-l-amber-500">
      <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">No Eficientes</h3>
      <p class="text-4xl font-extrabold text-amber-500">{{ datos.no_eficientes || 0 }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  datos: {
    type: Object,
    default: () => ({})
  }
})
</script>
