<template>
  <div class="bg-white rounded-xl shadow-sm border p-6 flex flex-col">
    <!-- Encabezado de la Sección -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-100">
      <div>
        <div class="flex items-center gap-3">
          <span class="w-3 h-3 rounded-full bg-indigo-600 animate-pulse"></span>
          <h3 class="text-base font-bold text-slate-800 uppercase tracking-wider">
            Órdenes en Proceso y Pendientes de Facturación
          </h3>
          <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-800">
            {{ totalPendientes }} órdenes activas
          </span>
        </div>
        <p class="text-xs text-slate-500 mt-1">
          Órdenes en planta textil que aún no registran fecha de facturación y se encuentran en su ciclo productivo.
        </p>
      </div>

      <!-- Buscador en tiempo real -->
      <div class="flex items-center gap-3">
        <div class="relative min-w-[240px]">
          <input 
            v-model="filtroTexto" 
            type="text" 
            placeholder="Buscar OP, detalle, cliente, máquina..." 
            class="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg pl-8 pr-3 py-2 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
          />
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400 absolute left-2.5 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <button 
            v-if="filtroTexto" 
            @click="filtroTexto = ''" 
            class="text-slate-400 hover:text-slate-600 absolute right-2.5 top-2.5 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      </div>
    </div>

    <!-- Banner informativo sobre el motivo -->
    <div class="mb-5 p-3.5 bg-indigo-50/70 border border-indigo-200/80 rounded-xl text-xs text-indigo-950 leading-relaxed flex items-start gap-3">
      <div class="text-indigo-600 text-base mt-0.5">📌</div>
      <div>
        <p class="font-semibold text-indigo-900 mb-0.5">¿Por qué estas órdenes no aparecen como eficientes o no eficientes?</p>
        <p class="text-indigo-800">
          En el control de producción textil, la eficiencia de entrega se calcula <strong>únicamente cuando la orden tiene asignada su Fecha de Facturación</strong>. 
          Las órdenes listadas abajo están activas en planta en sus diferentes etapas (Tejeduría, Acabados, Calibración o esperando entrega/facturación).
        </p>
      </div>
    </div>

    <!-- Filtros Rápidos por Proceso -->
    <div class="flex flex-wrap items-center gap-2 mb-4">
      <span class="text-xs font-semibold text-slate-500 mr-1">Filtrar proceso:</span>
      
      <button 
        @click="filtroProceso = 'todos'"
        type="button"
        class="px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer border"
        :class="filtroProceso === 'todos' 
          ? 'bg-slate-900 text-white border-slate-900 shadow-sm' 
          : 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200'"
      >
        Todas ({{ totalPendientes }})
      </button>

      <button 
        v-if="conteoPorProceso['Tejeduría']"
        @click="filtroProceso = 'Tejeduría'"
        type="button"
        class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer border"
        :class="filtroProceso === 'Tejeduría' 
          ? 'bg-blue-600 text-white border-blue-600 shadow-sm' 
          : 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'"
      >
        <span>🧵 Tejeduría</span>
        <span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="filtroProceso === 'Tejeduría' ? 'bg-blue-800 text-white' : 'bg-blue-200/80 text-blue-900'">
          {{ conteoPorProceso['Tejeduría'] }}
        </span>
      </button>

      <button 
        v-if="conteoPorProceso['Acabados']"
        @click="filtroProceso = 'Acabados'"
        type="button"
        class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer border"
        :class="filtroProceso === 'Acabados' 
          ? 'bg-purple-600 text-white border-purple-600 shadow-sm' 
          : 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100'"
      >
        <span>✨ Acabados</span>
        <span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="filtroProceso === 'Acabados' ? 'bg-purple-800 text-white' : 'bg-purple-200/80 text-purple-900'">
          {{ conteoPorProceso['Acabados'] }}
        </span>
      </button>

      <button 
        v-if="conteoPorProceso['Terminado']"
        @click="filtroProceso = 'Terminado'"
        type="button"
        class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer border"
        :class="filtroProceso === 'Terminado' 
          ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm' 
          : 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100'"
      >
        <span>📦 Terminadas (Sin Facturar)</span>
        <span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="filtroProceso === 'Terminado' ? 'bg-emerald-800 text-white' : 'bg-emerald-200/80 text-emerald-900'">
          {{ conteoPorProceso['Terminado'] }}
        </span>
      </button>

      <button 
        v-if="conteoPorProceso['Calibración']"
        @click="filtroProceso = 'Calibración'"
        type="button"
        class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer border"
        :class="filtroProceso === 'Calibración' 
          ? 'bg-amber-600 text-white border-amber-600 shadow-sm' 
          : 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'"
      >
        <span>🔧 Calibración</span>
        <span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="filtroProceso === 'Calibración' ? 'bg-amber-800 text-white' : 'bg-amber-200/80 text-amber-900'">
          {{ conteoPorProceso['Calibración'] }}
        </span>
      </button>

      <button 
        v-if="conteoPorProceso['Montaje']"
        @click="filtroProceso = 'Montaje'"
        type="button"
        class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer border"
        :class="filtroProceso === 'Montaje' 
          ? 'bg-orange-600 text-white border-orange-600 shadow-sm' 
          : 'bg-orange-50 text-orange-800 border-orange-200 hover:bg-orange-100'"
      >
        <span>⚙️ Montaje</span>
        <span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="filtroProceso === 'Montaje' ? 'bg-orange-800 text-white' : 'bg-orange-200/80 text-orange-900'">
          {{ conteoPorProceso['Montaje'] }}
        </span>
      </button>
    </div>

    <!-- Tabla Principal de Órdenes en Proceso -->
    <div class="overflow-x-auto max-h-96 overflow-y-auto border border-slate-200 rounded-xl">
      <table class="w-full text-left text-sm text-slate-600">
        <thead class="text-xs text-slate-700 uppercase bg-slate-100/90 border-b sticky top-0 z-10">
          <tr>
            <th class="px-4 py-3 whitespace-nowrap font-bold">OP / Orden</th>
            <th class="px-4 py-3 font-bold min-w-[240px]">Nombre / Detalle de la Orden</th>
            <th class="px-4 py-3 whitespace-nowrap font-bold">Proceso Actual</th>
            <th class="px-4 py-3 whitespace-nowrap font-bold">Máquina</th>
            <th class="px-4 py-3 whitespace-nowrap font-bold">Cliente</th>
            <th class="px-4 py-3 whitespace-nowrap font-bold text-center">Metraje Pedido</th>
            <th class="px-4 py-3 whitespace-nowrap font-bold text-center">Fechas & Plazo Meta</th>
            <th class="px-4 py-3 whitespace-nowrap font-bold text-center">Estado Facturación</th>
            <th class="px-4 py-3 min-w-[220px] font-bold">Motivo / Estado</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 bg-white">
          <tr v-for="(orden, idx) in listaFiltrada" :key="idx" class="hover:bg-slate-50/80 transition-colors">
            <!-- OP -->
            <td class="px-4 py-3 font-bold text-slate-900 whitespace-nowrap align-middle">
              {{ orden.op }}
            </td>

            <!-- Nombre / Detalle -->
            <td class="px-4 py-3 align-middle text-xs leading-relaxed text-slate-800 font-medium">
              {{ orden.detalle || 'Sin detalle especificado' }}
            </td>

            <!-- Proceso con Badge de Color -->
            <td class="px-4 py-3 align-middle whitespace-nowrap">
              <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold shadow-xs" :class="{
                'bg-blue-50 text-blue-700 border border-blue-200': orden.badge_color === 'blue',
                'bg-purple-50 text-purple-700 border border-purple-200': orden.badge_color === 'purple',
                'bg-emerald-50 text-emerald-700 border border-emerald-200': orden.badge_color === 'emerald',
                'bg-amber-50 text-amber-800 border border-amber-200': orden.badge_color === 'amber',
                'bg-orange-50 text-orange-800 border border-orange-200': orden.badge_color === 'orange',
                'bg-slate-100 text-slate-700 border border-slate-200': !orden.badge_color || orden.badge_color === 'slate'
              }">
                <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="{
                  'bg-blue-500': orden.badge_color === 'blue',
                  'bg-purple-500': orden.badge_color === 'purple',
                  'bg-emerald-500': orden.badge_color === 'emerald',
                  'bg-amber-500': orden.badge_color === 'amber',
                  'bg-orange-500': orden.badge_color === 'orange',
                  'bg-slate-500': !orden.badge_color || orden.badge_color === 'slate'
                }"></span>
                {{ orden.proceso || orden.estado }}
              </span>
            </td>

            <!-- Máquina -->
            <td class="px-4 py-3 align-middle text-xs font-semibold whitespace-nowrap text-slate-700">
              <span v-if="orden.maquina" class="bg-slate-100 px-2 py-0.5 rounded border border-slate-200 text-slate-800">
                {{ orden.maquina }}
              </span>
              <span v-else class="text-slate-400">-</span>
            </td>

            <!-- Cliente -->
            <td class="px-4 py-3 align-middle text-xs whitespace-nowrap text-slate-600">
              {{ orden.cliente || '-' }}
            </td>

            <!-- Metraje Pedido -->
            <td class="px-4 py-3 align-middle whitespace-nowrap text-center">
              <div v-if="orden.mts_pedido" class="text-xs font-bold text-slate-800">
                {{ Math.round(orden.mts_pedido).toLocaleString() }} m
              </div>
              <div v-else class="text-xs text-slate-400">-</div>
            </td>

            <!-- Fechas de Ingreso y Meta Estimada -->
            <td class="px-4 py-3 align-middle whitespace-nowrap text-center">
              <template v-if="orden.fecha_ingreso">
                <div class="text-xs font-semibold text-slate-900 flex items-center justify-center gap-1.5">
                  <span class="text-slate-400 text-[10px] uppercase font-bold">Ingreso:</span>
                  <span class="text-blue-900 font-bold">{{ orden.fecha_ingreso }}</span>
                </div>
                <div v-if="orden.fecha_meta" class="text-xs font-semibold flex items-center justify-center gap-1.5 mt-0.5">
                  <span class="text-slate-400 text-[10px] uppercase font-bold">Meta:</span>
                  <span class="text-emerald-800 font-extrabold">{{ orden.fecha_meta }}</span>
                </div>
              </template>
              <div v-else class="text-xs text-slate-400 italic">
                Sin fecha en Excel
              </div>

              <!-- Badge de plazo estándar -->
              <div class="inline-flex items-center gap-1 text-[10px] font-semibold text-slate-600 mt-1 bg-slate-100 px-2 py-0.5 rounded-md border border-slate-200">
                <span>{{ orden.dias_estandar || 20 }}d hábiles</span>
                <span v-if="orden.dias_extra_metraje > 0" class="text-amber-700 font-bold" :title="`+${orden.dias_extra_metraje} días adicionales por metraje > 6,500m (Día y Velada)`">
                  (+{{ orden.dias_extra_metraje }}d)
                </span>
              </div>
            </td>

            <!-- Estado Facturación -->
            <td class="px-4 py-3 align-middle whitespace-nowrap text-center">
              <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                ⏳ Sin Facturar
              </span>
            </td>

            <!-- Motivo -->
            <td class="px-4 py-3 align-middle text-xs text-indigo-900 font-medium leading-relaxed">
              {{ orden.motivo || 'Pendiente de fecha de facturación' }}
              <p v-if="orden.observacion" class="text-[11px] text-slate-500 italic mt-0.5">
                Obs: {{ orden.observacion }}
              </p>
            </td>
          </tr>

          <!-- Estado vacío -->
          <tr v-if="listaFiltrada.length === 0">
            <td colspan="9" class="text-center py-10 text-slate-400 text-xs italic">
              {{ totalPendientes === 0 
                ? '✅ En este archivo todas las órdenes están facturadas y evaluadas en eficiencia.' 
                : 'No se encontraron órdenes que coincidan con la búsqueda o filtro seleccionado.' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pie de tabla con totales -->
    <div class="flex flex-wrap justify-between items-center text-xs text-slate-500 mt-4 pt-3 border-t border-slate-100 gap-2">
      <span>Mostrando {{ listaFiltrada.length }} de {{ totalPendientes }} órdenes en proceso</span>
      <span class="text-[11px] text-slate-500 italic">
        * Estándar estimado: 20 días base (+1 día por cada 1,000m adicionales a partir de 6,500m, turnos Día + Velada).
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  datos: {
    type: Object,
    default: () => ({})
  }
})

const filtroTexto = ref('')
const filtroProceso = ref('todos')

const listaPendientes = computed(() => {
  return props.datos.lista_pendientes || []
})

const totalPendientes = computed(() => {
  return props.datos.total_pendientes || listaPendientes.value.length || 0
})

const conteoPorProceso = computed(() => {
  const counts = {}
  for (const item of listaPendientes.value) {
    const proc = item.proceso || 'En Proceso'
    counts[proc] = (counts[proc] || 0) + 1
  }
  return counts
})

const listaFiltrada = computed(() => {
  let list = listaPendientes.value

  // Filtro por proceso seleccionado
  if (filtroProceso.value !== 'todos') {
    list = list.filter(item => (item.proceso || 'En Proceso') === filtroProceso.value)
  }

  // Filtro por texto de búsqueda
  const q = filtroTexto.value.trim().toLowerCase()
  if (q) {
    list = list.filter(item => {
      return (
        (item.op && item.op.toLowerCase().includes(q)) ||
        (item.detalle && item.detalle.toLowerCase().includes(q)) ||
        (item.cliente && item.cliente.toLowerCase().includes(q)) ||
        (item.maquina && item.maquina.toLowerCase().includes(q)) ||
        (item.proceso && item.proceso.toLowerCase().includes(q)) ||
        (item.motivo && item.motivo.toLowerCase().includes(q))
      )
    })
  }

  return list
})
</script>
