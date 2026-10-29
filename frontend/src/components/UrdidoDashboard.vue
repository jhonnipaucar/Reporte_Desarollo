<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col space-y-6">
    <!-- Encabezado de la Sección de Urdido -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
      <div>
        <div class="flex items-center gap-3">
          <span class="w-3.5 h-3.5 rounded-full bg-cyan-600 animate-pulse"></span>
          <h3 class="text-base font-bold text-slate-800 uppercase tracking-wider">
            Urdido — Turnos & Carretos por Operario
          </h3>
          <span v-if="datos && datos.disponible" class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-cyan-100 text-cyan-800 border border-cyan-200">
            {{ totalCarretos }} carretos en el mes
          </span>
        </div>
        <p class="text-xs text-slate-500 mt-1">
          Comparativa operativa entre Turno Diurno y Turno Velada con rendimiento de carretos por operario.
        </p>
      </div>

      <!-- Selector Rápido de Turno -->
      <div v-if="datos && datos.disponible" class="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl border border-slate-200">
        <button 
          @click="filtroTurno = 'todos'" 
          type="button"
          class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="filtroTurno === 'todos' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
        >
          Ambos Turnos
        </button>
        <button 
          @click="filtroTurno = 'dia'" 
          type="button"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="filtroTurno === 'dia' ? 'bg-amber-500 text-white shadow-xs' : 'text-amber-800 hover:bg-amber-100/60'"
        >
          <span>☀️</span> Diurno
        </button>
        <button 
          @click="filtroTurno = 'velada'" 
          type="button"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
          :class="filtroTurno === 'velada' ? 'bg-indigo-600 text-white shadow-xs' : 'text-indigo-800 hover:bg-indigo-100/60'"
        >
          <span>🌙</span> Velada
        </button>
      </div>
    </div>

    <!-- Si el archivo NO tiene hoja de urdido -->
    <div v-if="!datos || !datos.disponible" class="p-8 text-center bg-slate-50 border border-dashed border-slate-300 rounded-xl">
      <div class="text-3xl mb-2">🧵</div>
      <h4 class="text-sm font-bold text-slate-700">Módulo de Urdido no disponible en este archivo</h4>
      <p class="text-xs text-slate-500 mt-1 max-w-md mx-auto">
        El registro detallado de urdido fue incorporado a partir de <strong>Septiembre 2026</strong>. Los archivos históricos anteriores (Julio y Agosto) no contienen esta hoja operativa.
      </p>
    </div>

    <!-- Si el archivo SÍ tiene datos de urdido -->
    <div v-else class="space-y-6">
      
      <!-- 1. Tarjetas Superiores: Metros Totales, Carretos Totales, Turno Diurno y Turno Velada -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <!-- Tarjeta 1: Única Tarjeta de Metros Solicitada -->
        <div class="bg-gradient-to-br from-cyan-50 via-white to-cyan-50/50 rounded-2xl border border-cyan-200/90 p-5 shadow-xs flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[11px] font-bold text-cyan-800 uppercase tracking-wider">Metros Urdidos Totales</span>
            <div class="w-8 h-8 rounded-xl bg-cyan-100 text-cyan-700 flex items-center justify-center text-base">
              🧵
            </div>
          </div>
          <div>
            <div class="text-3xl font-extrabold text-cyan-950 tracking-tight">
              {{ formatearNumero(datos.totales?.metros) }} <span class="text-sm font-semibold text-cyan-700">m</span>
            </div>
            <p class="text-[11px] text-cyan-800/80 font-medium mt-1">
              Promedio: {{ formatearNumero(datos.totales?.promedio_metros_dia) }} m / jornada
            </p>
          </div>
        </div>

        <!-- Tarjeta 2: Carretos Totales -->
        <div class="bg-gradient-to-br from-blue-50 via-white to-blue-50/50 rounded-2xl border border-blue-200/90 p-5 shadow-xs flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[11px] font-bold text-blue-800 uppercase tracking-wider">Carretos Totales</span>
            <div class="w-8 h-8 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center text-base">
              🔘
            </div>
          </div>
          <div>
            <div class="text-3xl font-extrabold text-blue-950 tracking-tight">
              {{ totalCarretos }} <span class="text-sm font-semibold text-blue-700">carretos</span>
            </div>
            <p class="text-[11px] text-blue-800/80 font-medium mt-1">
              Promedio: {{ datos.totales?.promedio_carretos_dia || 0 }} carretos / día
            </p>
          </div>
        </div>

        <!-- Tarjeta 3: Turno Diurno (Día) -->
        <div 
          @click="filtroTurno = filtroTurno === 'dia' ? 'todos' : 'dia'"
          class="rounded-2xl border p-5 shadow-xs flex flex-col justify-between cursor-pointer transition-all"
          :class="filtroTurno === 'dia' 
            ? 'bg-amber-100/60 border-amber-400 ring-2 ring-amber-300' 
            : 'bg-gradient-to-br from-amber-50 via-white to-amber-50/40 border-amber-200/90 hover:shadow-sm'"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-[11px] font-bold text-amber-800 uppercase tracking-wider flex items-center gap-1.5">
              <span>☀️ Turno Diurno</span>
            </span>
            <span class="text-xs font-extrabold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
              {{ turnoDia.porcentaje_carretos }}%
            </span>
          </div>
          <div>
            <div class="text-2xl sm:text-3xl font-extrabold text-amber-950 tracking-tight">
              {{ turnoDia.carretos }} <span class="text-xs font-semibold text-amber-700">carretos</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-amber-800 font-medium mt-1.5 pt-1.5 border-t border-amber-100">
              <span>{{ formatearNumero(turnoDia.metros) }} m ({{ turnoDia.porcentaje_metros }}%)</span>
              <span>{{ turnoDia.registros }} lotes</span>
            </div>
          </div>
        </div>

        <!-- Tarjeta 4: Turno Velada (Noche) -->
        <div 
          @click="filtroTurno = filtroTurno === 'velada' ? 'todos' : 'velada'"
          class="rounded-2xl border p-5 shadow-xs flex flex-col justify-between cursor-pointer transition-all"
          :class="filtroTurno === 'velada' 
            ? 'bg-indigo-100/60 border-indigo-400 ring-2 ring-indigo-300' 
            : 'bg-gradient-to-br from-indigo-50 via-white to-indigo-50/40 border-indigo-200/90 hover:shadow-sm'"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-[11px] font-bold text-indigo-800 uppercase tracking-wider flex items-center gap-1.5">
              <span>🌙 Turno Velada</span>
            </span>
            <span class="text-xs font-extrabold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200">
              {{ turnoVelada.porcentaje_carretos }}%
            </span>
          </div>
          <div>
            <div class="text-2xl sm:text-3xl font-extrabold text-indigo-950 tracking-tight">
              {{ turnoVelada.carretos }} <span class="text-xs font-semibold text-indigo-700">carretos</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-indigo-800 font-medium mt-1.5 pt-1.5 border-t border-indigo-100">
              <span>{{ formatearNumero(turnoVelada.metros) }} m ({{ turnoVelada.porcentaje_metros }}%)</span>
              <span>{{ turnoVelada.registros }} lotes</span>
            </div>
          </div>
        </div>

      </div>

      <!-- 2. Sección Principal: Gráfico y Operarios según el Turno Seleccionado -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- Gráfico de Carretos por Operario (7 Columnas en Desktop) -->
        <div class="lg:col-span-7 bg-slate-50/70 border border-slate-200 rounded-2xl p-5 flex flex-col">
          <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
            <div>
              <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <span>Carretos por Operario</span>
                <span class="text-[11px] px-2 py-0.5 rounded-full font-bold" :class="{
                  'bg-slate-200 text-slate-700': filtroTurno === 'todos',
                  'bg-amber-100 text-amber-800': filtroTurno === 'dia',
                  'bg-indigo-100 text-indigo-800': filtroTurno === 'velada'
                }">
                  {{ filtroTurno === 'todos' ? 'Consolidado (Día + Velada)' : filtroTurno === 'dia' ? 'Solo Turno Diurno' : 'Solo Turno Velada' }}
                </span>
              </h4>
              <p class="text-[11px] text-slate-500 mt-0.5">
                {{ filtroTurno === 'todos' ? 'Desglose comparativo de carretos preparados en ambos turnos' : `Producción focalizada en el turno ${filtroTurno === 'dia' ? 'diurno' : 'de velada'}` }}
              </p>
            </div>

            <!-- Leyenda de colores -->
            <div class="flex items-center gap-3 text-[11px] font-semibold">
              <span v-if="filtroTurno === 'todos' || filtroTurno === 'dia'" class="inline-flex items-center gap-1.5 text-amber-700">
                <span class="w-2.5 h-2.5 rounded-sm bg-amber-500"></span> Diurno
              </span>
              <span v-if="filtroTurno === 'todos' || filtroTurno === 'velada'" class="inline-flex items-center gap-1.5 text-indigo-700">
                <span class="w-2.5 h-2.5 rounded-sm bg-indigo-600"></span> Velada
              </span>
            </div>
          </div>

          <div class="h-72 relative">
            <Bar :data="carretosChartData" :options="carretosChartOptions" />
          </div>

          <div class="flex items-center justify-between text-[11px] text-slate-400 mt-3 pt-2 border-t border-slate-200/80 italic">
            <span>* Las etiquetas muestran el total de carretos y su porcentaje de participación.</span>
            <span class="font-medium text-slate-600">Base: {{ carretosBaseFiltro }} carretos</span>
          </div>
        </div>

        <!-- Tarjetas Detalladas por Operario (5 Columnas en Desktop) -->
        <div class="lg:col-span-5 space-y-3">
          <div class="flex items-center justify-between px-1">
            <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Operarios Activos ({{ operariosFiltrados.length }})
            </h4>
            <span class="text-[11px] font-semibold text-slate-500">
              {{ filtroTurno === 'todos' ? 'Ambos Turnos' : filtroTurno === 'dia' ? 'Turno Diurno' : 'Turno Velada' }}
            </span>
          </div>

          <div 
            v-for="op in operariosFiltrados" 
            :key="op.nombre"
            class="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs hover:shadow-sm transition-all"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-xl bg-slate-100 border border-slate-200 text-slate-700 font-extrabold text-xs flex items-center justify-center">
                  {{ op.nombre.charAt(0) }}
                </div>
                <div>
                  <h5 class="text-sm font-bold text-slate-900 leading-tight">{{ op.nombre }}</h5>
                  <span class="text-[10px] text-slate-400">{{ op.registros }} lotes en el mes</span>
                </div>
              </div>
              <div class="text-right">
                <div class="text-lg font-extrabold text-slate-900">
                  {{ op.carretosMostrados }} <span class="text-xs font-semibold text-slate-500">carretos</span>
                </div>
                <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full" :class="{
                  'bg-blue-50 text-blue-700 border border-blue-200': filtroTurno === 'todos',
                  'bg-amber-50 text-amber-800 border border-amber-200': filtroTurno === 'dia',
                  'bg-indigo-50 text-indigo-800 border border-indigo-200': filtroTurno === 'velada'
                }">
                  {{ op.porcentajeMostrado }}% del {{ filtroTurno === 'todos' ? 'total' : filtroTurno === 'dia' ? 'diurno' : 'velada' }}
                </span>
              </div>
            </div>

            <!-- Barra de Progreso Visual de Turnos -->
            <div class="w-full bg-slate-100 rounded-full h-2 mb-2 overflow-hidden flex">
              <div 
                v-if="filtroTurno === 'todos' || filtroTurno === 'dia'"
                class="bg-amber-500 h-2 transition-all duration-500" 
                :style="{ width: `${totalCarretos > 0 ? (op.carretos_dia / totalCarretos) * 100 : 0}%` }"
                :title="`Diurno: ${op.carretos_dia} carretos`"
              ></div>
              <div 
                v-if="filtroTurno === 'todos' || filtroTurno === 'velada'"
                class="bg-indigo-600 h-2 transition-all duration-500" 
                :style="{ width: `${totalCarretos > 0 ? (op.carretos_velada / totalCarretos) * 100 : 0}%` }"
                :title="`Velada: ${op.carretos_velada} carretos`"
              ></div>
            </div>

            <!-- Desglose Específico Diurno vs Velada -->
            <div class="flex items-center justify-between text-xs text-slate-600 pt-1.5 border-t border-slate-100">
              <span class="inline-flex items-center gap-1" :class="op.carretos_dia > 0 ? 'text-amber-900 font-semibold' : 'text-slate-400'">
                <span>☀️ Diurno:</span> <strong>{{ op.carretos_dia }}</strong>
              </span>
              <span class="inline-flex items-center gap-1" :class="op.carretos_velada > 0 ? 'text-indigo-900 font-semibold' : 'text-slate-400'">
                <span>🌙 Velada:</span> <strong>{{ op.carretos_velada }}</strong>
              </span>
            </div>
          </div>

          <div v-if="operariosFiltrados.length === 0" class="p-6 bg-slate-50 border border-dashed border-slate-300 rounded-2xl text-center text-xs text-slate-400 italic">
            No hay operarios registrados en este turno.
          </div>
        </div>
      </div>

      <!-- 3. Sección Top 7 Artículos Urdidos -->
      <div v-if="top7Articulos.length > 0" class="bg-slate-50/70 border border-slate-200 rounded-2xl p-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-200/80">
          <div>
            <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <span>🧵 Top 7 Artículos Urdidos</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full font-bold bg-cyan-100 text-cyan-800 border border-cyan-200">
                Mayor Metraje
              </span>
            </h4>
            <p class="text-[11px] text-slate-500 mt-0.5">
              Artículos y cintas con mayor demanda urdida y carretos preparados en el mes.
            </p>
          </div>
          <div class="text-[11px] font-semibold text-slate-600 bg-white px-3 py-1.5 rounded-xl border border-slate-200">
            Top 7 acumula: <strong class="text-slate-900">{{ formatearNumero(totalMetrosTop7) }} m</strong> ({{ porcentajeTop7 }}% del total)
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          <!-- Gráfico Horizontal Top 7 (7 Cols) -->
          <div class="lg:col-span-7 h-72 relative">
            <Bar :data="articulosChartData" :options="articulosChartOptions" />
          </div>

          <!-- Ranking List de los 7 Artículos (5 Cols) -->
          <div class="lg:col-span-5 space-y-2">
            <div 
              v-for="(art, idx) in top7Articulos" 
              :key="idx"
              class="bg-white border border-slate-200/90 rounded-xl p-2.5 shadow-2xs hover:shadow-xs transition-all flex items-center justify-between gap-3 text-xs"
            >
              <div class="flex items-center gap-2.5 min-w-0">
                <span class="w-6 h-6 rounded-lg flex items-center justify-center font-extrabold text-[11px] shrink-0" :class="{
                  'bg-amber-100 text-amber-800 border border-amber-300': idx === 0,
                  'bg-slate-200 text-slate-700': idx === 1,
                  'bg-amber-50 text-amber-900 border border-amber-200': idx === 2,
                  'bg-slate-100 text-slate-600': idx > 2
                }">
                  {{ idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}` }}
                </span>
                <div class="truncate">
                  <p class="font-bold text-slate-900 truncate" :title="art.articulo">{{ art.articulo }}</p>
                  <p class="text-[10px] text-slate-400">{{ art.registros }} lotes en planta</p>
                </div>
              </div>

              <div class="text-right shrink-0">
                <div class="font-extrabold text-slate-900">
                  {{ formatearNumero(art.metros) }} <span class="text-[10px] font-normal text-slate-500">m</span>
                </div>
                <div class="flex items-center justify-end gap-1.5 text-[10px]">
                  <span class="font-bold text-cyan-700">{{ art.porcentaje_metros }}%</span>
                  <span class="text-slate-300">•</span>
                  <span class="text-slate-600 font-semibold">{{ art.carretos }} carretos</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  datos: {
    type: Object,
    default: () => ({})
  }
})

// Filtro de turno: 'todos' | 'dia' | 'velada'
const filtroTurno = ref('todos')

// Datos de Turno Diurno
const turnoDia = computed(() => {
  const t = props.datos?.por_turno?.find(x => x.turno?.toLowerCase().includes('d'))
  return t || { carretos: 0, metros: 0, registros: 0, porcentaje_carretos: 0, porcentaje_metros: 0 }
})

// Datos de Turno Velada
const turnoVelada = computed(() => {
  const t = props.datos?.por_turno?.find(x => x.turno?.toLowerCase().includes('velada'))
  return t || { carretos: 0, metros: 0, registros: 0, porcentaje_carretos: 0, porcentaje_metros: 0 }
})

// Total carretos
const totalCarretos = computed(() => {
  if (props.datos?.totales?.carretos !== undefined) return props.datos.totales.carretos
  return (turnoDia.value.carretos || 0) + (turnoVelada.value.carretos || 0)
})

// Carretos base según filtro
const carretosBaseFiltro = computed(() => {
  if (filtroTurno.value === 'dia') return turnoDia.value.carretos
  if (filtroTurno.value === 'velada') return turnoVelada.value.carretos
  return totalCarretos.value
})

// Lista de operarios consolidados ordenada según filtro
const operariosFiltrados = computed(() => {
  const ops = props.datos?.operadores_consolidados || []
  
  if (filtroTurno.value === 'dia') {
    return ops
      .filter(o => (o.carretos_dia || 0) > 0)
      .map(o => ({
        ...o,
        carretosMostrados: o.carretos_dia,
        porcentajeMostrado: turnoDia.value.carretos > 0 ? ((o.carretos_dia / turnoDia.value.carretos) * 100).toFixed(1) : '0.0'
      }))
      .sort((a, b) => b.carretosMostrados - a.carretosMostrados)
  }

  if (filtroTurno.value === 'velada') {
    return ops
      .filter(o => (o.carretos_velada || 0) > 0)
      .map(o => ({
        ...o,
        carretosMostrados: o.carretos_velada,
        porcentajeMostrado: turnoVelada.value.carretos > 0 ? ((o.carretos_velada / turnoVelada.value.carretos) * 100).toFixed(1) : '0.0'
      }))
      .sort((a, b) => b.carretosMostrados - a.carretosMostrados)
  }

  return ops.map(o => ({
    ...o,
    carretosMostrados: o.carretos,
    porcentajeMostrado: o.porcentaje_carretos || (totalCarretos.value > 0 ? ((o.carretos / totalCarretos.value) * 100).toFixed(1) : '0.0')
  }))
})

// Formatear números
const formatearNumero = (num) => {
  if (num === null || num === undefined) return '0'
  return Math.round(num).toLocaleString('es-CO')
}

// Configuración del gráfico de carretos por operario adaptado al filtro de turno
const carretosChartData = computed(() => {
  const ops = operariosFiltrados.value
  if (!ops || ops.length === 0) return { labels: [], datasets: [] }

  const labels = ops.map(o => `${o.nombre} (${o.porcentajeMostrado}%)`)

  if (filtroTurno.value === 'dia') {
    return {
      labels,
      datasets: [
        {
          label: 'Turno Diurno',
          data: ops.map(o => o.carretos_dia),
          backgroundColor: '#f59e0b',
          borderRadius: 6
        }
      ]
    }
  }

  if (filtroTurno.value === 'velada') {
    return {
      labels,
      datasets: [
        {
          label: 'Turno Velada',
          data: ops.map(o => o.carretos_velada),
          backgroundColor: '#4f46e5',
          borderRadius: 6
        }
      ]
    }
  }

  // Ambos Turnos (Apilado)
  return {
    labels,
    datasets: [
      {
        label: 'Turno Diurno',
        data: ops.map(o => o.carretos_dia),
        backgroundColor: '#f59e0b',
        borderRadius: 4
      },
      {
        label: 'Turno Velada',
        data: ops.map(o => o.carretos_velada),
        backgroundColor: '#4f46e5',
        borderRadius: 4
      }
    ]
  }
})

const carretosChartOptions = computed(() => {
  const isStacked = filtroTurno.value === 'todos'

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const turno = context.dataset.label
            const val = context.parsed.y
            return `${turno}: ${val} carretos`
          },
          afterBody: function (context) {
            if (context.length > 0 && isStacked) {
              const op = operariosFiltrados.value[context[0].dataIndex]
              return `Total: ${op.carretos} carretos (${op.porcentajeMostrado}% del total)`
            }
            return ''
          }
        }
      }
    },
    scales: {
      x: {
        stacked: isStacked,
        grid: { display: false }
      },
      y: {
        stacked: isStacked,
        beginAtZero: true,
        ticks: {
          stepSize: 10
        }
      }
    }
  }
})

// Top 7 Artículos Urdidos
const top7Articulos = computed(() => {
  return (props.datos?.top_articulos || []).slice(0, 7)
})

const totalMetrosTop7 = computed(() => {
  return top7Articulos.value.reduce((sum, a) => sum + (a.metros || 0), 0)
})

const porcentajeTop7 = computed(() => {
  const total = props.datos?.totales?.metros || 0
  if (total === 0) return '0.0'
  return ((totalMetrosTop7.value / total) * 100).toFixed(1)
})

const articulosChartData = computed(() => {
  const arts = top7Articulos.value
  if (!arts || arts.length === 0) return { labels: [], datasets: [] }

  const colors = ['#0891b2', '#06b6d4', '#0ea5e9', '#38bdf8', '#6366f1', '#8b5cf6', '#a855f7']

  return {
    labels: arts.map(a => a.articulo.length > 25 ? a.articulo.substring(0, 23) + '...' : a.articulo),
    datasets: [
      {
        label: 'Metros Urdidos',
        data: arts.map(a => a.metros),
        backgroundColor: arts.map((_, i) => colors[i % colors.length]),
        borderRadius: 4
      }
    ]
  }
})

const articulosChartOptions = computed(() => {
  return {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const art = top7Articulos.value[context.dataIndex]
            return `Metros: ${formatearNumero(art.metros)} m (${art.porcentaje_metros}% del mes)`
          },
          afterBody: function (context) {
            if (context.length > 0) {
              const art = top7Articulos.value[context[0].dataIndex]
              return `Carretos: ${art.carretos} carretos`
            }
            return ''
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: { display: true },
        ticks: {
          callback: function (val) {
            return val >= 1000 ? (val / 1000) + 'k' : val
          }
        }
      },
      y: {
        grid: { display: false },
        ticks: {
          font: { size: 10 }
        }
      }
    }
  }
})
</script>
