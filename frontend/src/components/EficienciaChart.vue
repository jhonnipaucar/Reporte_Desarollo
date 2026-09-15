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
            {{ datos.eficientes || 0 }}
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
            {{ datos.no_eficientes || 0 }}
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
              <span class="w-3 h-3 rounded-full" :class="selectedTipo === 'eficiente' ? 'bg-blue-600' : 'bg-amber-500'"></span>
              <h4 class="font-bold text-sm text-slate-800">
                Órdenes {{ selectedTipo === 'eficiente' ? 'Eficientes' : 'No Eficientes' }} ({{ listaActual.length }})
              </h4>
            </div>

            <div class="flex items-center gap-2">
              <div class="relative">
                <input 
                  v-model="filtroTexto" 
                  type="text" 
                  placeholder="Buscar OP, producto, cliente..." 
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

          <div class="overflow-x-auto max-h-72 overflow-y-auto border border-slate-200 rounded-lg">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b sticky top-0 z-10">
                <tr>
                  <th class="px-3 py-2.5 whitespace-nowrap">OP</th>
                  <th class="px-3 py-2.5">Producto / Detalle</th>
                  <th class="px-3 py-2.5 whitespace-nowrap">Cliente</th>
                  <th class="px-3 py-2.5 text-center whitespace-nowrap">Días</th>
                  <th v-if="selectedTipo === 'no_eficiente'" class="px-3 py-2.5 min-w-[200px]">Causa / Observación</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white">
                <tr v-for="(orden, idx) in listaFiltrada" :key="idx" class="hover:bg-slate-50 transition-colors">
                  <td class="px-3 py-2.5 font-semibold text-slate-800 whitespace-nowrap align-top">{{ orden.op }}</td>
                  <td class="px-3 py-2.5 align-top text-xs leading-relaxed text-slate-700">{{ orden.detalle || 'Sin detalle' }}</td>
                  <td class="px-3 py-2.5 align-top text-xs whitespace-nowrap text-slate-600">{{ orden.cliente || '-' }}</td>
                  <td class="px-3 py-2.5 align-top text-center text-xs font-semibold text-slate-700">{{ orden.dias_entrega }}</td>
                  <td v-if="selectedTipo === 'no_eficiente'" class="px-3 py-2.5 align-top text-xs leading-relaxed text-slate-700 whitespace-normal break-words">
                    {{ orden.observacion || 'Sin observación' }}
                  </td>
                </tr>
                <tr v-if="listaFiltrada.length === 0">
                  <td :colspan="selectedTipo === 'no_eficiente' ? 5 : 4" class="text-center py-6 text-slate-400 text-xs italic">
                    No se encontraron órdenes que coincidan con la búsqueda.
                  </td>
                </tr>
              </tbody>
            </table>
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
              label += `${context.parsed} órdenes (clic para ver lista)`
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
