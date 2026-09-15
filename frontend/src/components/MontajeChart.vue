<template>
  <div class="bg-white rounded-xl shadow-sm border p-6 flex flex-col h-full">
    <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider mb-6 text-center">Montaje por Operario</h3>
    
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
          <div class="flex justify-between items-center mb-3">
            <h4 class="font-bold text-sm text-slate-800">
              Detalle: {{ selectedOperarioData.nombre }}
            </h4>
            <div class="flex items-center gap-4">
              <span class="text-xs text-slate-500 font-semibold">Órdenes: {{ selectedOperarioData.ordenes_atendidas }}</span>
              <span class="text-xs text-slate-500 font-semibold">Tiras: {{ selectedOperarioData.total_tiras }}</span>
              <button @click="selectedOperario = null" class="text-slate-400 hover:text-slate-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="overflow-x-auto max-h-60 overflow-y-auto">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b sticky top-0">
                <tr>
                  <th class="px-3 py-2">Orden</th>
                  <th class="px-3 py-2 text-right">Tiras montadas</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in ordenesOperario" :key="idx" class="border-b last:border-0 hover:bg-slate-100/50">
                  <td class="px-3 py-2 font-medium text-slate-800">{{ item.orden }}</td>
                  <td class="px-3 py-2 text-right">{{ item.tiras }}</td>
                </tr>
              </tbody>
            </table>
            <div v-if="ordenesOperario.length === 0" class="text-center py-4 text-slate-500 text-sm">
              No hay órdenes con montaje para este operario.
            </div>
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
      tiras: orden[nombre]
    }))
    .sort((a, b) => b.tiras - a.tiras)
})

const chartData = computed(() => {
  if (!props.datos.operarios) return { labels: [], datasets: [] }
  
  // Create a gradient-like palette based on a primary hue (e.g., teal/blue)
  const baseColors = [
    '#0d9488', '#0f766e', '#115e59', '#134e4a',
    '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a'
  ]
  
  return {
    labels: props.datos.operarios.map(o => o.nombre),
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
        selectedOperario.value = selectedOperario.value === index ? null : index
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
            return [
              `Total Tiras: ${op.total_tiras}`,
              `Órdenes: ${op.ordenes_atendidas}`
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
