<template>
  <div class="bg-white rounded-xl shadow-sm border p-6 flex flex-col h-full">
    <div class="mb-2 text-center">
      <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider">Montaje por Operario</h3>
      <p v-if="totalTiras > 0" class="text-xs text-slate-500 mt-0.5">
        Total: <strong class="text-slate-800">{{ totalTiras }} tiras</strong> registradas en el mes
      </p>
    </div>
    <p v-if="datos && datos.operarios && datos.operarios.length > 0" class="text-xs text-slate-400 text-center mb-5">
      Haz clic en una barra para ver las órdenes y productos montados por cada operario
    </p>
    
    <div v-if="datos && datos.operarios && datos.operarios.length > 0" class="flex-1 flex flex-col">
      <div class="min-h-[300px] relative mb-4">
        <Bar :data="chartData" :options="chartOptions" />
      </div>
      
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div v-if="selectedOperarioData" class="mt-4 border rounded-lg bg-slate-50 p-4">
          <div class="flex flex-wrap justify-between items-center gap-3 mb-3">
            <div class="flex items-center gap-3">
              <h4 class="font-bold text-sm text-slate-800">
                Detalle: {{ selectedOperarioData.nombre }}
              </h4>
              <span class="text-xs bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full font-semibold">
                {{ selectedOperarioData.ordenes_atendidas }} órdenes
              </span>
              <span class="text-xs bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full font-semibold">
                {{ selectedOperarioData.total_tiras }} tiras ({{ porcentajeOperarioSeleccionado }}%)
              </span>
            </div>

            <div class="flex items-center gap-2">
              <div class="relative">
                <input 
                  v-model="filtroTexto" 
                  type="text" 
                  placeholder="Buscar orden o producto..." 
                  class="text-xs bg-white border border-slate-300 rounded-lg pl-7 pr-3 py-1 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-teal-500"
                />
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-slate-400 absolute left-2 top-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>

              <button @click="cerrarDetalle" title="Cerrar detalle" class="text-slate-400 hover:text-slate-600 p-1 cursor-pointer">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="overflow-x-auto max-h-72 overflow-y-auto border border-slate-200 rounded-lg">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b sticky top-0 z-10">
                <tr>
                  <th class="px-3 py-2.5 whitespace-nowrap">Orden</th>
                  <th class="px-3 py-2.5">Nombre / Detalle del Producto</th>
                  <th class="px-3 py-2.5 text-right whitespace-nowrap">Tiras montadas</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white">
                <tr v-for="(item, idx) in ordenesFiltradas" :key="idx" class="hover:bg-slate-50 transition-colors">
                  <td class="px-3 py-2.5 font-semibold text-slate-800 whitespace-nowrap align-middle">
                    {{ item.orden }}
                  </td>
                  <td class="px-3 py-2.5 align-middle text-xs text-slate-700 leading-relaxed">
                    {{ item.nombre_orden || 'Sin detalle' }}
                  </td>
                  <td class="px-3 py-2.5 text-right align-middle font-bold text-slate-800 whitespace-nowrap">
                    {{ item.tiras }}
                  </td>
                </tr>
                <tr v-if="ordenesFiltradas.length === 0">
                  <td colspan="3" class="text-center py-6 text-slate-400 text-xs italic">
                    {{ filtroTexto ? 'No se encontraron órdenes que coincidan con la búsqueda.' : 'No hay órdenes con montaje para este operario.' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </Transition>
    </div>
    
    <div v-else class="flex-1 min-h-[300px] flex items-center justify-center">
      <p class="text-slate-400">Cargando datos...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  datos: {
    type: Object,
    default: () => ({})
  }
})

const selectedOperario = ref(null)
const filtroTexto = ref('')

const cerrarDetalle = () => {
  selectedOperario.value = null
  filtroTexto.value = ''
}

const selectedOperarioData = computed(() => {
  if (selectedOperario.value === null || !props.datos.operarios) return null
  return props.datos.operarios[selectedOperario.value]
})

const ordenesOperario = computed(() => {
  if (!selectedOperarioData.value || !props.datos.detalle_por_orden) return []
  const nombre = selectedOperarioData.value.nombre
  
  return props.datos.detalle_por_orden
    .filter(orden => orden[nombre] > 0)
    .map(orden => ({
      orden: orden.orden,
      nombre_orden: orden.nombre_orden || orden.detalle || '',
      tiras: orden[nombre]
    }))
    .sort((a, b) => b.tiras - a.tiras)
})

const ordenesFiltradas = computed(() => {
  if (!filtroTexto.value.trim()) return ordenesOperario.value
  const q = filtroTexto.value.trim().toLowerCase()
  return ordenesOperario.value.filter(item => 
    item.orden.toLowerCase().includes(q) || 
    item.nombre_orden.toLowerCase().includes(q)
  )
})

const totalTiras = computed(() => {
  return props.datos.operarios?.reduce((sum, o) => sum + (o.total_tiras || 0), 0) || 0
})

const porcentajeOperarioSeleccionado = computed(() => {
  if (!selectedOperarioData.value || totalTiras.value === 0) return '0.0'
  return ((selectedOperarioData.value.total_tiras / totalTiras.value) * 100).toFixed(1)
})

const chartData = computed(() => {
  if (!props.datos.operarios) return { labels: [], datasets: [] }
  
  // Create a gradient-like palette based on a primary hue (e.g., teal/blue)
  const baseColors = [
    '#0d9488', '#0f766e', '#115e59', '#134e4a',
    '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a'
  ]
  
  return {
    labels: props.datos.operarios.map(o => {
      const pct = totalTiras.value > 0 ? ((o.total_tiras / totalTiras.value) * 100).toFixed(1) : '0.0'
      return `${o.nombre} (${pct}%)`
    }),
    datasets: [
      {
        label: 'Total Tiras',
        data: props.datos.operarios.map(o => o.total_tiras),
        backgroundColor: props.datos.operarios.map((_, i) => baseColors[i % baseColors.length]),
        borderRadius: 4
      }
    ]
  }
})

const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    onClick: (event, elements) => {
      if (elements.length > 0) {
        const index = elements[0].index
        if (selectedOperario.value === index) {
          cerrarDetalle()
        } else {
          selectedOperario.value = index
          filtroTexto.value = ''
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const index = context.dataIndex
            const op = props.datos.operarios[index]
            const pct = totalTiras.value > 0 ? ((op.total_tiras / totalTiras.value) * 100).toFixed(1) : '0.0'
            return [
              `Total Tiras: ${op.total_tiras} (${pct}% del total)`,
              `Órdenes atendidas: ${op.ordenes_atendidas}`
            ]
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    },
    onHover: (event, chartElement) => {
      event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
    }
  }
})
</script>
