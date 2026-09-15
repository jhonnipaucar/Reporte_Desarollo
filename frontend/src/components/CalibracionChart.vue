<template>
  <div class="bg-white rounded-xl shadow-sm border p-6 flex flex-col h-full">
    <div class="mb-6 text-center">
      <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider">Calibraciones por Técnico</h3>
      <p v-if="datos && datos.total" class="text-xs text-slate-500 mt-1">Total: {{ datos.total }}</p>
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
          <div class="flex justify-between items-start mb-2">
            <div>
              <h4 class="font-bold text-slate-800">{{ selectedCalibradorData.nombre }}</h4>
              <p class="text-sm text-slate-600 font-medium mt-1">
                {{ selectedCalibradorData.veces }} calibraciones
              </p>
            </div>
            <button @click="selectedCalibrador = null" class="text-slate-400 hover:text-slate-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          
          <div class="mt-3">
            <h5 class="text-xs font-semibold text-slate-500 uppercase mb-1">Artículos</h5>
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

const selectedCalibradorData = computed(() => {
  if (selectedCalibrador.value === null || !props.datos.calibradores) return null
  return props.datos.calibradores[selectedCalibrador.value]
})

const chartData = computed(() => {
  if (!props.datos.calibradores) return { labels: [], datasets: [] }
  
  const coolTones = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e']
  
  return {
    labels: props.datos.calibradores.map(c => c.nombre),
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
            return `Veces: ${context.parsed.y}`
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
