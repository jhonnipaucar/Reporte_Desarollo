<template>
  <div class="bg-white rounded-xl shadow-sm border p-6 flex flex-col h-full">
    <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 text-center">Eficiencia de Entrega</h3>
    
    <div v-if="datos && (datos.eficientes !== undefined)" class="flex-1 flex flex-col">
      <!-- Gráfico Doughnut -->
      <div class="min-h-[260px] relative">
        <Doughnut :data="chartData" :options="chartOptions" :plugins="plugins" />
      </div>

      <!-- Botones de Selección Rápida -->
      <div class="flex flex-wrap items-center justify-center gap-3 mt-4 pt-3 border-t border-slate-100">
        <button 
          @click="toggleTipo('eficiente')"
          type="button"
          class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border cursor-pointer"
          :class="selectedTipo === 'eficiente' 
            ? 'bg-blue-600 text-white border-blue-600 shadow-sm ring-2 ring-blue-300' 
            : 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'"
        >
          <span class="w-2 h-2 rounded-full bg-blue-400"></span>
          <span>Ver Eficientes</span>
          <span class="px-1.5 py-0.2 rounded-full text-[10px] font-extrabold" :class="selectedTipo === 'eficiente' ? 'bg-blue-800 text-white' : 'bg-blue-200/60 text-blue-800'">
            {{ datos.eficientes || 0 }} ({{ datos.porcentaje_eficiente !== undefined ? Math.round(datos.porcentaje_eficiente) : 0 }}%)
          </span>
        </button>

        <button 
          @click="toggleTipo('no_eficiente')"
          type="button"
          class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border cursor-pointer"
          :class="selectedTipo === 'no_eficiente' 
            ? 'bg-amber-500 text-white border-amber-500 shadow-sm ring-2 ring-amber-300' 
            : 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'"
        >
          <span class="w-2 h-2 rounded-full bg-amber-300"></span>
          <span>Ver No Eficientes</span>
          <span class="px-1.5 py-0.2 rounded-full text-[10px] font-extrabold" :class="selectedTipo === 'no_eficiente' ? 'bg-amber-700 text-white' : 'bg-amber-200/70 text-amber-900'">
            {{ datos.no_eficientes || 0 }} ({{ datos.porcentaje_no_eficiente !== undefined ? Math.round(datos.porcentaje_no_eficiente) : 0 }}%)
          </span>
        </button>

        <button 
          v-if="datos.total_pendientes"
          @click="toggleTipo('pendiente')"
          type="button"
          class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border cursor-pointer"
          :class="selectedTipo === 'pendiente' 
            ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm ring-2 ring-indigo-300' 
            : 'bg-indigo-50 text-indigo-800 border-indigo-200 hover:bg-indigo-100'"
        >
          <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
          <span>En Proceso / Sin Facturar</span>
          <span class="px-1.5 py-0.2 rounded-full text-[10px] font-extrabold" :class="selectedTipo === 'pendiente' ? 'bg-indigo-800 text-white' : 'bg-indigo-200/70 text-indigo-900'">
            {{ datos.total_pendientes || 0 }}
          </span>
        </button>
      </div>

      <!-- Detalle Interactivo de Órdenes -->
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div v-if="selectedTipo" class="mt-4 border rounded-lg bg-slate-50 p-4">
          <div class="flex flex-wrap justify-between items-center gap-3 mb-3">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full" :class="{
                'bg-blue-600': selectedTipo === 'eficiente',
                'bg-amber-500': selectedTipo === 'no_eficiente',
                'bg-indigo-600': selectedTipo === 'pendiente'
              }"></span>
              <h4 class="font-bold text-sm text-slate-800">
                {{ selectedTipo === 'eficiente' ? 'Órdenes Eficientes' : selectedTipo === 'no_eficiente' ? 'Órdenes No Eficientes' : 'Órdenes en Proceso / Pendientes de Facturación' }} ({{ listaActual.length }})
              </h4>
            </div>

            <div class="flex items-center gap-2">
              <div class="relative">
                <input 
                  v-model="filtroTexto" 
                  type="text" 
                  placeholder="Buscar OP, detalle, cliente..." 
                  class="text-xs bg-white border border-slate-300 rounded-lg pl-7 pr-3 py-1 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-slate-400 absolute left-2 top-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>

              <button @click="selectedTipo = null" title="Cerrar detalle" class="text-slate-400 hover:text-slate-600 p-1 cursor-pointer">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Mensaje explicativo para órdenes en proceso -->
          <div v-if="selectedTipo === 'pendiente'" class="mb-3 p-2.5 bg-indigo-50/80 border border-indigo-200 rounded-lg text-xs text-indigo-900 leading-relaxed flex items-start gap-2">
            <span class="text-indigo-600 text-sm">ℹ️</span>
            <div>
              <strong>Motivo de estado pendiente:</strong> Estas órdenes no están calificadas aún como eficientes o no eficientes porque <strong>aún no tienen Fecha de Facturación registrada</strong>. Se encuentran en proceso en planta textil (Tejeduría, Acabados, Calibración o esperando despacho).
            </div>
          </div>

          <div class="overflow-x-auto max-h-72 overflow-y-auto border border-slate-200 rounded-lg">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b sticky top-0 z-10">
                <tr>
                  <th class="px-3 py-2.5 whitespace-nowrap">OP</th>
                  <th class="px-3 py-2.5">Producto / Detalle</th>
                  <th v-if="selectedTipo === 'pendiente'" class="px-3 py-2.5 whitespace-nowrap">Proceso</th>
                  <th v-if="selectedTipo === 'pendiente'" class="px-3 py-2.5 whitespace-nowrap">Máquina</th>
                  <th class="px-3 py-2.5 whitespace-nowrap">Cliente</th>
                  <th v-if="selectedTipo !== 'pendiente'" class="px-3 py-2.5 text-center whitespace-nowrap">{{ selectedTipo === 'no_eficiente' ? 'Retraso vs Meta' : 'Días Entrega' }}</th>
                  <th v-if="selectedTipo === 'no_eficiente'" class="px-3 py-2.5 min-w-[200px]">Causa / Observación</th>
                  <th v-if="selectedTipo === 'pendiente'" class="px-3 py-2.5 min-w-[180px]">Motivo</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white">
                <tr v-for="(orden, idx) in listaFiltrada" :key="idx" class="hover:bg-slate-50 transition-colors">
                  <td class="px-3 py-2.5 font-semibold text-slate-800 whitespace-nowrap align-top">{{ orden.op }}</td>
                  <td class="px-3 py-2.5 align-top text-xs leading-relaxed text-slate-700">{{ orden.detalle || 'Sin detalle' }}</td>
                  <td v-if="selectedTipo === 'pendiente'" class="px-3 py-2.5 align-top whitespace-nowrap">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold" :class="{
                      'bg-blue-100 text-blue-800': orden.badge_color === 'blue',
                      'bg-purple-100 text-purple-800': orden.badge_color === 'purple',
                      'bg-emerald-100 text-emerald-800': orden.badge_color === 'emerald',
                      'bg-amber-100 text-amber-800': orden.badge_color === 'amber',
                      'bg-slate-100 text-slate-800': !orden.badge_color || orden.badge_color === 'slate'
                    }">
                      {{ orden.proceso || orden.estado }}
                    </span>
                  </td>
                  <td v-if="selectedTipo === 'pendiente'" class="px-3 py-2.5 align-top text-xs whitespace-nowrap text-slate-600">{{ orden.maquina || '-' }}</td>
                  <td class="px-3 py-2.5 align-top text-xs whitespace-nowrap text-slate-600">{{ orden.cliente || '-' }}</td>
                  <td v-if="selectedTipo !== 'pendiente'" class="px-3 py-2.5 align-top text-center whitespace-nowrap">
                    <div v-if="selectedTipo === 'no_eficiente'">
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
                        +{{ orden.dias_retraso != null ? orden.dias_retraso : Math.max(0, (orden.dias_entrega || 0) - (orden.dias_estandar || 20)) }} días
                      </span>
                      <div class="text-[10px] text-slate-500 font-medium mt-0.5">
                        Entrega: {{ orden.dias_entrega }}d / Meta: {{ orden.dias_estandar || 20 }}d
                        <span v-if="orden.dias_extra_metraje > 0" class="text-amber-700 font-semibold ml-0.5" :title="`+${orden.dias_extra_metraje}d por metraje (${orden.mts_pedido ? orden.mts_pedido.toLocaleString() : ''}m > 6,500m)`">
                          (+{{ orden.dias_extra_metraje }}d metraje)
                        </span>
                      </div>
                    </div>
                    <div v-else>
                      <span class="text-xs font-semibold text-slate-700">{{ orden.dias_entrega }} días</span>
                      <div class="text-[10px] text-slate-400 font-medium mt-0.5">
                        Meta: {{ orden.dias_estandar || 20 }}d
                        <span v-if="orden.dias_extra_metraje > 0" class="text-emerald-700 font-semibold ml-0.5">
                          (+{{ orden.dias_extra_metraje }}d metraje)
                        </span>
                      </div>
                    </div>
                  </td>
                  <td v-if="selectedTipo === 'no_eficiente'" class="px-3 py-2.5 align-top text-xs leading-relaxed text-slate-700 whitespace-normal break-words">
                    {{ orden.observacion || 'Sin observación' }}
                  </td>
                  <td v-if="selectedTipo === 'pendiente'" class="px-3 py-2.5 align-top text-xs text-indigo-700 font-medium whitespace-normal">
                    {{ orden.motivo || 'Sin fecha de facturación' }}
                  </td>
                </tr>
                <tr v-if="listaFiltrada.length === 0">
                  <td :colspan="selectedTipo === 'pendiente' ? 6 : (selectedTipo === 'no_eficiente' ? 5 : 4)" class="text-center py-6 text-slate-400 text-xs italic">
                    No se encontraron órdenes que coincidan con la búsqueda.
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="selectedTipo !== 'pendiente'" class="px-3 py-2 bg-slate-50 border-t border-slate-200 text-[11px] text-slate-500 flex flex-wrap items-center justify-between gap-2">
              <span>* Estándar de entrega: <strong>20 días base</strong> (+1 día adicional por cada 1,000m a partir de 6,500m en turnos Día y Velada).</span>
              <span class="font-semibold text-slate-600">Regla continua &gt; 6,500m</span>
            </div>
          </div>
        </div>
      </Transition>
    </div>
    <div v-else class="flex-1 min-h-[280px] flex items-center justify-center">
      <p class="text-slate-400">Cargando datos...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  datos: {
    type: Object,
    default: () => ({})
  }
})

const selectedTipo = ref(null) // 'eficiente' | 'no_eficiente' | null
const filtroTexto = ref('')

const toggleTipo = (tipo) => {
  if (selectedTipo.value === tipo) {
    selectedTipo.value = null
  } else {
    selectedTipo.value = tipo
    filtroTexto.value = ''
  }
}

const listaActual = computed(() => {
  if (selectedTipo.value === 'eficiente') {
    return props.datos.lista_eficientes || []
  }
  if (selectedTipo.value === 'no_eficiente') {
    return props.datos.lista_no_eficientes || []
  }
  if (selectedTipo.value === 'pendiente') {
    return props.datos.lista_pendientes || []
  }
  return []
})

const listaFiltrada = computed(() => {
  const query = filtroTexto.value.trim().toLowerCase()
  if (!query) return listaActual.value
  return listaActual.value.filter(item => {
    return (
      (item.op && item.op.toLowerCase().includes(query)) ||
      (item.detalle && item.detalle.toLowerCase().includes(query)) ||
      (item.cliente && item.cliente.toLowerCase().includes(query)) ||
      (item.maquina && item.maquina.toLowerCase().includes(query)) ||
      (item.proceso && item.proceso.toLowerCase().includes(query)) ||
      (item.motivo && item.motivo.toLowerCase().includes(query)) ||
      (item.observacion && item.observacion.toLowerCase().includes(query))
    )
  })
})

const chartData = computed(() => {
  return {
    labels: ['Eficiente', 'No Eficiente'],
    datasets: [
      {
        data: [props.datos.eficientes || 0, props.datos.no_eficientes || 0],
        backgroundColor: ['#2563eb', '#f59e0b'],
        borderWidth: 0,
        hoverOffset: 6
      }
    ]
  }
})

const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '75%',
    onClick: (event, elements) => {
      if (elements.length > 0) {
        const index = elements[0].index
        toggleTipo(index === 0 ? 'eficiente' : 'no_eficiente')
      }
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          generateLabels: (chart) => {
            const data = chart.data
            if (data.labels.length && data.datasets.length) {
              const ds = data.datasets[0]
              const total = ds.data.reduce((a, b) => a + b, 0)
              return data.labels.map((label, i) => {
                const value = ds.data[i]
                const percentage = total > 0 ? Math.round((value / total) * 100) : 0
                return {
                  text: `${label} (${percentage}%)`,
                  fillStyle: ds.backgroundColor[i],
                  strokeStyle: ds.backgroundColor[i],
                  lineWidth: 0,
                  hidden: chart.getDatasetMeta(0).data[i]?.hidden || false,
                  index: i
                }
              })
            }
            return []
          }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.label || ''
            if (label) {
              label += ': '
            }
            if (context.parsed !== null) {
              const val = context.parsed
              const total = (props.datos.eficientes || 0) + (props.datos.no_eficientes || 0)
              const pct = total > 0 ? ((val / total) * 100).toFixed(1) : '0.0'
              label += `${val} órdenes (${pct}%) — Clic para ver detalle`
            }
            return label
          }
        }
      }
    },
    onHover: (event, chartElement) => {
      event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
    }
  }
})

const plugins = computed(() => {
  return [{
    id: 'centerText',
    beforeDraw: function(chart) {
      if (props.datos && props.datos.porcentaje_eficiente !== undefined) {
        var width = chart.width,
            height = chart.height,
            ctx = chart.ctx

        ctx.restore()
        var fontSize = (height / 114).toFixed(2)
        ctx.font = "bold " + fontSize + "em sans-serif"
        ctx.textBaseline = "middle"
        ctx.fillStyle = "#1e293b" // slate-800

        var text = Math.round(props.datos.porcentaje_eficiente) + "%",
            textX = Math.round((width - ctx.measureText(text).width) / 2),
            textY = height / 2 - (chart.legend?.height || 0) / 2

        ctx.fillText(text, textX, textY)
        ctx.save()
      }
    }
  }]
})
</script>
