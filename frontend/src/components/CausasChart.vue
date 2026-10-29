<template>
  <div class="bg-white rounded-xl shadow-sm border p-6 flex flex-col h-full">
    <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider mb-6 text-center">Causas de No Eficiencia</h3>
    
    <div v-if="datos && datos.causas && datos.causas.length > 0" class="flex-1 flex flex-col">
      <div class="min-h-[280px] relative mb-4">
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
        <div v-if="selectedCausaData" class="mt-4 border rounded-lg bg-slate-50 p-4">
          <div class="flex justify-between items-center mb-3">
            <h4 class="font-bold text-sm text-slate-800">
              Detalle: {{ selectedCausaData.nombre }} ({{ selectedCausaData.cantidad }} órdenes — {{ selectedCausaData.porcentaje.toFixed(1) }}%)
            </h4>
            <button @click="selectedCausa = null" class="text-slate-400 hover:text-slate-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          
          <div class="overflow-x-auto max-h-80 overflow-y-auto border border-slate-200 rounded-lg">
            <table class="w-full text-left text-sm text-slate-600">
              <thead class="text-xs text-slate-700 uppercase bg-slate-100 border-b sticky top-0 z-10">
                <tr>
                  <th class="px-3 py-2.5 whitespace-nowrap">OP</th>
                  <th class="px-3 py-2.5">Producto</th>
                  <th class="px-3 py-2.5 whitespace-nowrap">Cliente</th>
                  <th class="px-3 py-2.5 text-center whitespace-nowrap">Días de Retraso</th>
                  <th class="px-3 py-2.5 min-w-[240px]">Observación</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white">
                <tr v-for="(orden, idx) in selectedCausaData.ordenes" :key="idx" class="hover:bg-slate-50 transition-colors">
                  <td class="px-3 py-2.5 font-semibold text-slate-800 whitespace-nowrap align-top">{{ orden.op }}</td>
                  <td class="px-3 py-2.5 align-top text-xs leading-relaxed">{{ orden.detalle }}</td>
                  <td class="px-3 py-2.5 align-top text-xs whitespace-nowrap">{{ orden.cliente }}</td>
                  <td class="px-3 py-2.5 align-top text-center whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
                      +{{ orden.dias_retraso != null ? orden.dias_retraso : Math.max(0, (orden.dias_entrega || 0) - (orden.dias_estandar || 20)) }} días
                    </span>
                    <div class="text-[10px] text-slate-500 font-medium mt-0.5">
                      Entrega: {{ orden.dias_entrega }}d / Meta: {{ orden.dias_estandar || 20 }}d
                      <span v-if="orden.dias_extra_metraje > 0" class="text-amber-700 font-semibold ml-0.5">
                        (+{{ orden.dias_extra_metraje }}d metraje)
                      </span>
                    </div>
                  </td>
                  <td class="px-3 py-2.5 align-top text-xs leading-relaxed text-slate-700 whitespace-normal break-words">
                    {{ orden.observacion || 'Sin observación' }}
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="px-3 py-2 bg-slate-50 border-t border-slate-200 text-[11px] text-slate-500 italic flex flex-wrap items-center justify-between gap-2">
              <span>* Días de retraso evaluados con estándar base de 20 días (+1 día por cada 1,000m excedentes a partir de 6,500m, turnos Día + Velada).</span>
              <span class="font-medium text-slate-600">Base: 20 días (+días metraje &gt;6,500m)</span>
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
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  datos: {
    type: Object,
    default: () => ({})
  }
})

const selectedCausa = ref(null)

const selectedCausaData = computed(() => {
  if (selectedCausa.value === null || !props.datos.causas) return null
  return props.datos.causas[selectedCausa.value]
})

const chartData = computed(() => {
  if (!props.datos.causas) return { labels: [], datasets: [] }
  
  const colors = ['#ef4444', '#f59e0b', '#3b82f6', '#6b7280', '#8b5cf6', '#10b981']
  
  return {
    labels: props.datos.causas.map(c => `${c.nombre} (${c.porcentaje.toFixed(1)}%)`),
    datasets: [
      {
        label: 'Cantidad',
        data: props.datos.causas.map(c => c.cantidad),
        backgroundColor: props.datos.causas.map((_, i) => colors[i % colors.length]),
        borderRadius: 4
      }
    ]
  }
})

const chartOptions = computed(() => {
  return {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    onClick: (event, elements) => {
      if (elements.length > 0) {
        const index = elements[0].index
        selectedCausa.value = selectedCausa.value === index ? null : index
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
            const causa = props.datos.causas[index]
            return `Cantidad: ${causa.cantidad} órdenes (${causa.porcentaje.toFixed(1)}% del total)`
          }
        }
      }
    },
    scales: {
      x: {
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
