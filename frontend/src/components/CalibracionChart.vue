<template>
  <div class="bg-white rounded-xl shadow-sm border p-6 flex flex-col h-full">
    <div class="mb-6 text-center">
      <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider">Calibraciones por Técnico</h3>
      <p v-if="totalCalibraciones > 0" class="text-xs text-slate-500 mt-1">
        Total: <strong class="text-slate-800">{{ totalCalibraciones }} calibraciones</strong>
      </p>
    </div>
    
    <div v-if="datos && datos.calibradores && datos.calibradores.length > 0" class="flex-1 flex flex-col">
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
        <div v-if="selectedCalibradorData" class="mt-4 border rounded-lg bg-slate-50 p-4">
          <div class="flex flex-wrap justify-between items-center gap-3 mb-3">
            <div class="flex items-center gap-2">
              <h4 class="font-bold text-slate-800 text-sm">{{ selectedCalibradorData.nombre }}</h4>
              <span class="text-xs font-bold text-purple-700 bg-purple-100 px-2 py-0.5 rounded-full">
                {{ selectedCalibradorData.veces }} calibraciones ({{ porcentajeCalibradorSeleccionado }}%)
              </span>
            </div>
            
            <div class="flex items-center gap-2">
              <div v-if="ordenesCalibrador.length > 0" class="relative">
                <input 
                  v-model="filtroTexto" 
                  type="text" 
                  placeholder="Buscar orden o artículo..." 
                  class="text-xs bg-white border border-slate-300 rounded-lg pl-7 pr-3 py-1 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-purple-500"
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
          
          <!-- Tabla de órdenes cuando hay detalle_por_orden disponible -->
          <div v-if="ordenesCalibrador.length > 0" class="overflow-x-auto max-h-64 overflow-y-auto border border-slate-200 rounded-lg">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b sticky top-0 z-10">
                <tr>
                  <th class="px-3 py-2 whitespace-nowrap">Orden</th>
                  <th class="px-3 py-2">Producto / Artículo</th>
                  <th class="px-3 py-2 text-right whitespace-nowrap">Calibraciones</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white">
                <tr v-for="(item, idx) in ordenesFiltradas" :key="idx" class="hover:bg-slate-50 transition-colors">
                  <td class="px-3 py-2 font-semibold text-slate-800 whitespace-nowrap">{{ item.orden }}</td>
                  <td class="px-3 py-2 text-xs text-slate-700 leading-relaxed">{{ item.nombre_orden || 'Sin detalle' }}</td>
                  <td class="px-3 py-2 text-right font-bold text-purple-700">{{ item.veces }}</td>
                </tr>
                <tr v-if="ordenesFiltradas.length === 0">
                  <td colspan="3" class="text-center py-4 text-slate-400 text-xs italic">
                    No se encontraron órdenes que coincidan con la búsqueda.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Si no hay detalle individual (archivos históricos), mostrar lista textual de artículos -->
          <div v-else class="mt-2">
            <h5 class="text-xs font-semibold text-slate-500 uppercase mb-1">Artículos Calibrados</h5>
            <p class="text-sm text-slate-700 italic">{{ selectedCalibradorData.articulos || 'Sin información' }}</p>
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

const selectedCalibrador = ref(null)
const filtroTexto = ref('')

const cerrarDetalle = () => {
  selectedCalibrador.value = null
  filtroTexto.value = ''
}

const selectedCalibradorData = computed(() => {
  if (selectedCalibrador.value === null || !props.datos.calibradores) return null
  return props.datos.calibradores[selectedCalibrador.value]
})

const ordenesCalibrador = computed(() => {
  if (!selectedCalibradorData.value || !props.datos.detalle_por_orden) return []
  const nombre = selectedCalibradorData.value.nombre.trim()
  
  return props.datos.detalle_por_orden
    .filter(orden => (orden[nombre] || 0) > 0)
    .map(orden => ({
      orden: orden.orden,
      nombre_orden: orden.nombre_orden || orden.detalle || '',
      veces: orden[nombre]
    }))
    .sort((a, b) => b.veces - a.veces)
})

const ordenesFiltradas = computed(() => {
  if (!filtroTexto.value.trim()) return ordenesCalibrador.value
  const q = filtroTexto.value.toLowerCase().trim()
  return ordenesCalibrador.value.filter(item => 
    item.orden.toLowerCase().includes(q) || 
    (item.nombre_orden && item.nombre_orden.toLowerCase().includes(q))
  )
})

const totalCalibraciones = computed(() => {
  if (props.datos?.total && props.datos.total > 0) return props.datos.total
  return props.datos?.calibradores?.reduce((sum, c) => sum + (c.veces || 0), 0) || 0
})

const porcentajeCalibradorSeleccionado = computed(() => {
  if (!selectedCalibradorData.value || totalCalibraciones.value === 0) return '0.0'
  return ((selectedCalibradorData.value.veces / totalCalibraciones.value) * 100).toFixed(1)
})

const chartData = computed(() => {
  if (!props.datos.calibradores) return { labels: [], datasets: [] }
  
  const coolTones = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e']
  
  return {
    labels: props.datos.calibradores.map(c => {
      const pct = totalCalibraciones.value > 0 ? ((c.veces / totalCalibraciones.value) * 100).toFixed(1) : '0.0'
      return `${c.nombre} (${pct}%)`
    }),
    datasets: [
      {
        label: 'Calibraciones',
        data: props.datos.calibradores.map(c => c.veces),
        backgroundColor: props.datos.calibradores.map((_, i) => coolTones[i % coolTones.length]),
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
        selectedCalibrador.value = selectedCalibrador.value === index ? null : index
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
            const c = props.datos.calibradores[index]
            const pct = totalCalibraciones.value > 0 ? ((c.veces / totalCalibraciones.value) * 100).toFixed(1) : '0.0'
            return `Calibraciones: ${context.parsed.y} (${pct}% del total)`
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      }
    },
    onHover: (event, chartElement) => {
      event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
    }
  }
})
</script>
