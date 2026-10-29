<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col space-y-6">
    <!-- Encabezado de la Tarjeta -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
      <div>
        <div class="flex items-center gap-3">
          <span class="w-3.5 h-3.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <h3 class="text-base font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
            <span>📦 Órdenes Acabadas por Día</span>
            <span class="text-xs font-semibold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
              Control Diario
            </span>
          </h3>
          <span v-if="datos && datos.disponible" class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-200">
            {{ datos.totales?.total_ordenes || 0 }} OPs Acabadas
          </span>
        </div>
        <p class="text-xs text-slate-500 mt-1">
          Seguimiento diario de órdenes completadas con discriminación por turno (Día vs Velada) y bitácora de novedades.
        </p>
      </div>

      <!-- Buscador de órdenes / filtro rápido -->
      <div v-if="datos && datos.disponible" class="flex items-center gap-2">
        <div class="relative">
          <input 
            v-model="busqueda"
            type="text" 
            placeholder="Buscar OP o Artículo..." 
            class="bg-slate-50 border border-slate-200 text-xs rounded-xl px-3 py-1.5 pl-8 text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 w-52"
          />
          <span class="absolute left-2.5 top-2 text-slate-400 text-xs">🔍</span>
          <button 
            v-if="busqueda" 
            @click="busqueda = ''" 
            class="absolute right-2.5 top-1.5 text-slate-400 hover:text-slate-600 text-xs font-bold"
          >
            ✕
          </button>
        </div>
      </div>
    </div>

    <!-- Si NO está disponible en este archivo -->
    <div v-if="!datos || !datos.disponible" class="p-8 text-center bg-slate-50 border border-dashed border-slate-300 rounded-xl">
      <div class="text-3xl mb-2">📦</div>
      <h4 class="text-sm font-bold text-slate-700">Control de Órdenes Acabadas no disponible</h4>
      <p class="text-xs text-slate-500 mt-1 max-w-md mx-auto">
        La hoja operativa <strong>ORDENES ACABADAS</strong> se integró a partir de <strong>Octubre 2026</strong>. Los archivos anteriores no contienen este registro diario.
      </p>
    </div>

    <!-- Si SÍ está disponible -->
    <div v-else class="space-y-6">
      
      <!-- 1. Tarjetas de Resumen Ejecutivo de Terminación -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <!-- Total Acabadas -->
        <div class="bg-gradient-to-br from-emerald-50 via-white to-emerald-50/40 rounded-2xl border border-emerald-200/90 p-4 shadow-xs">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-[11px] font-bold text-emerald-800 uppercase tracking-wider">Total Acabadas</span>
            <span class="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs">
              ✅
            </span>
          </div>
          <div class="text-2xl font-extrabold text-emerald-950">
            {{ datos.totales?.total_ordenes || 0 }} <span class="text-xs font-semibold text-emerald-700">OPs</span>
          </div>
          <p class="text-[10px] text-emerald-800/80 mt-1">
            En {{ datos.totales?.dias_registrados || 0 }} jornadas registradas
          </p>
        </div>

        <!-- Ritmo Promedio en Rango -->
        <div class="bg-gradient-to-br from-blue-50 via-white to-blue-50/40 rounded-2xl border border-blue-200/90 p-4 shadow-xs">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-[11px] font-bold text-blue-800 uppercase tracking-wider">Ritmo Promedio</span>
            <span class="w-6 h-6 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center text-xs">
              📊
            </span>
          </div>
          <div class="text-2xl font-extrabold text-blue-950">
            {{ promedioRango }} <span class="text-xs font-semibold text-blue-700">OPs / día</span>
          </div>
          <p class="text-[10px] text-blue-800/80 mt-1" :title="`Media estadística exacta: ${datos.totales?.promedio_dia || 0} OPs/día`">
            {{ datos.totales?.dias_con_produccion || 0 }} días activos (media: {{ datos.totales?.promedio_dia || 0 }})
          </p>
        </div>

        <!-- Turno Diurno -->
        <div class="bg-gradient-to-br from-amber-50 via-white to-amber-50/40 rounded-2xl border border-amber-200/90 p-4 shadow-xs">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-[11px] font-bold text-amber-800 uppercase tracking-wider flex items-center gap-1">
              <span>☀️</span> Turno Diurno
            </span>
            <span class="text-[10px] font-extrabold px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-800">
              {{ datos.totales?.porcentaje_dia || 0 }}%
            </span>
          </div>
          <div class="text-2xl font-extrabold text-amber-950">
            {{ datos.totales?.total_dia || 0 }} <span class="text-xs font-semibold text-amber-700">OPs</span>
          </div>
          <p class="text-[10px] text-amber-800/80 mt-1">
            Finalizadas en turno de día
          </p>
        </div>

        <!-- Turno Velada -->
        <div class="bg-gradient-to-br from-indigo-50 via-white to-indigo-50/40 rounded-2xl border border-indigo-200/90 p-4 shadow-xs">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-[11px] font-bold text-indigo-800 uppercase tracking-wider flex items-center gap-1">
              <span>🌙</span> Turno Velada
            </span>
            <span class="text-[10px] font-extrabold px-1.5 py-0.2 rounded-full bg-indigo-100 text-indigo-800">
              {{ datos.totales?.porcentaje_velada || 0 }}%
            </span>
          </div>
          <div class="text-2xl font-extrabold text-indigo-950">
            {{ datos.totales?.total_velada || 0 }} <span class="text-xs font-semibold text-indigo-700">OPs</span>
          </div>
          <p class="text-[10px] text-indigo-800/80 mt-1">
            Finalizadas en turno de noche
          </p>
        </div>
      </div>

      <!-- 2. Línea de Tiempo / Calendario Diario Interactivo -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider">
              🗓️ Cronograma Diario de Terminación
            </h4>
            <span class="text-[11px] text-slate-500">
              (Haz clic en un día para ver su detalle de órdenes)
            </span>
          </div>
          <button 
            @click="fechaSeleccionada = null" 
            type="button"
            class="text-[11px] font-bold transition-all cursor-pointer px-2.5 py-1 rounded-lg border"
            :class="fechaSeleccionada === null ? 'bg-slate-800 text-white border-slate-800' : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'"
          >
            Ver Todas las Fechas
          </button>
        </div>

        <!-- Selector de Días en formato Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          <div 
            v-for="dia in datos.por_dia" 
            :key="dia.fecha"
            @click="seleccionarFecha(dia.fecha)"
            class="p-3.5 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between"
            :class="{
              'ring-2 ring-emerald-500 bg-emerald-50/70 border-emerald-300 shadow-sm': fechaSeleccionada === dia.fecha,
              'bg-white border-slate-200/90 hover:border-slate-300 hover:shadow-xs': fechaSeleccionada !== dia.fecha && !dia.sin_ordenes,
              'bg-amber-50/40 border-amber-200 hover:border-amber-300': fechaSeleccionada !== dia.fecha && dia.sin_ordenes
            }"
          >
            <!-- Cabecera de la fecha -->
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-extrabold text-slate-800">
                {{ dia.fecha_corta }}
              </span>
              <span class="text-[10px] font-semibold text-slate-500 uppercase">
                {{ dia.dia_semana }}
              </span>
            </div>

            <!-- Cantidad de órdenes -->
            <div class="my-1">
              <div v-if="!dia.sin_ordenes" class="flex items-baseline gap-1.5">
                <span class="text-2xl font-black" :class="fechaSeleccionada === dia.fecha ? 'text-emerald-900' : 'text-slate-900'">
                  {{ dia.total_ordenes }}
                </span>
                <span class="text-xs font-bold text-slate-500">OPs listas</span>
              </div>
              <div v-else class="flex items-center gap-1.5 py-1">
                <span class="text-xs font-extrabold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-md border border-amber-200">
                  ⚠️ 0 Terminadas
                </span>
              </div>
            </div>

            <!-- Desglose de turno del día -->
            <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-500">
              <span v-if="dia.ordenes_dia > 0" class="inline-flex items-center gap-0.5 text-amber-800 font-semibold">
                ☀️ {{ dia.ordenes_dia }}
              </span>
              <span v-else class="text-slate-400">☀️ 0</span>

              <span v-if="dia.ordenes_velada > 0" class="inline-flex items-center gap-0.5 text-indigo-800 font-semibold">
                🌙 {{ dia.ordenes_velada }}
              </span>
              <span v-else class="text-slate-400">🌙 0</span>

              <span v-if="dia.observaciones_dia && dia.observaciones_dia.length > 0" class="text-amber-600" title="Tiene observación técnica">
                📝
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Alerta de Novedad / Observación General del Día (si aplica) -->
      <div 
        v-if="observacionesDelDia.length > 0" 
        class="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-xs shadow-xs"
      >
        <div class="flex items-start gap-2.5">
          <span class="text-base leading-none">⚠️</span>
          <div class="flex-1">
            <h5 class="font-extrabold text-amber-900 uppercase tracking-wider text-[11px] mb-1">
              Observación Operativa de Planta — {{ fechaSeleccionadaNombre }}
            </h5>
            <div class="space-y-1">
              <p 
                v-for="(obs, idx) in observacionesDelDia" 
                :key="idx" 
                class="text-amber-800 leading-relaxed font-medium"
              >
                {{ obs }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. Detalle de Órdenes Acabadas (Tabla o Cards) -->
      <div class="space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <span>📋 Listado de Órdenes Terminadas</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {{ ordenesFiltradas.length }} {{ ordenesFiltradas.length === 1 ? 'orden' : 'órdenes' }}
              </span>
            </h4>
            <p class="text-[11px] text-slate-500 mt-0.5">
              {{ fechaSeleccionada ? `Mostrando órdenes completadas el ${fechaSeleccionadaNombre}` : 'Mostrando consolidado de todas las fechas registradas' }}
            </p>
          </div>

          <div v-if="fechaSeleccionada" class="flex items-center gap-2">
            <span class="text-xs font-semibold text-slate-600">Filtrando por:</span>
            <span class="px-2.5 py-1 rounded-xl text-xs font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-200">
              {{ fechaSeleccionadaNombre }}
            </span>
            <button 
              @click="fechaSeleccionada = null" 
              class="text-xs text-slate-400 hover:text-slate-600 font-bold p-1"
              title="Quitar filtro de fecha"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Si no hay órdenes para el filtro -->
        <div 
          v-if="ordenesFiltradas.length === 0" 
          class="p-8 text-center bg-slate-50 border border-dashed border-slate-200 rounded-2xl"
        >
          <div class="text-2xl mb-1">🔍</div>
          <p class="text-xs font-bold text-slate-700">No hay órdenes terminadas que coincidan con la búsqueda o fecha seleccionada.</p>
          <p v-if="busqueda" class="text-[11px] text-slate-400 mt-1">
            Intenta limpiar el buscador de texto o seleccionar otra fecha.
          </p>
        </div>

        <!-- Tabla interactiva de órdenes -->
        <div v-else class="overflow-x-auto border border-slate-200 rounded-2xl shadow-2xs">
          <table class="w-full text-left text-xs text-slate-700">
            <thead class="bg-slate-50 text-[11px] uppercase tracking-wider font-bold text-slate-600 border-b border-slate-200">
              <tr>
                <th class="py-3 px-4">Fecha</th>
                <th class="py-3 px-4">Turno</th>
                <th class="py-3 px-4">Orden (OP)</th>
                <th class="py-3 px-4">Artículo / Producto</th>
                <th class="py-3 px-4">Observaciones & Novedades</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr 
                v-for="(item, idx) in ordenesFiltradas" 
                :key="idx" 
                class="hover:bg-slate-50/80 transition-colors"
              >
                <!-- Fecha -->
                <td class="py-3 px-4 whitespace-nowrap">
                  <div class="font-bold text-slate-900">{{ item.fecha_corta }}</div>
                  <div class="text-[10px] text-slate-400">{{ item.dia_semana }}</div>
                </td>

                <!-- Turno -->
                <td class="py-3 px-4 whitespace-nowrap">
                  <span 
                    class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-extrabold border"
                    :class="item.turno === 'Día' ? 'bg-amber-50 text-amber-800 border-amber-200' : 'bg-indigo-50 text-indigo-800 border-indigo-200'"
                  >
                    <span>{{ item.turno === 'Día' ? '☀️' : '🌙' }}</span>
                    <span>{{ item.turno }}</span>
                  </span>
                </td>

                <!-- Código Orden -->
                <td class="py-3 px-4 whitespace-nowrap">
                  <span class="inline-block px-2.5 py-1 rounded-lg text-xs font-extrabold bg-blue-50 text-blue-800 border border-blue-200 tracking-wide font-mono">
                    {{ item.orden }}
                  </span>
                </td>

                <!-- Artículo -->
                <td class="py-3 px-4">
                  <div class="font-semibold text-slate-900 max-w-md">
                    {{ item.articulo || 'Sin descripción' }}
                  </div>
                </td>

                <!-- Observaciones -->
                <td class="py-3 px-4">
                  <div v-if="item.observaciones" class="inline-flex items-start gap-1.5 p-2 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-[11px]">
                    <span class="shrink-0 text-amber-700">⚠️</span>
                    <span>{{ item.observaciones }}</span>
                  </div>
                  <span v-else class="text-slate-300 text-[11px] italic">
                    Sin novedades
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 5. Bitácora Plegable de Todas las Novedades Técnicas -->
      <div v-if="datos.novedades_destacadas && datos.novedades_destacadas.length > 0" class="pt-2 border-t border-slate-100">
        <button 
          @click="mostrarNovedades = !mostrarNovedades"
          type="button"
          class="flex items-center justify-between w-full p-3 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs font-bold text-slate-700 transition-all cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <span>📝</span>
            <span>Bitácora de Observaciones Técnicas Registradas ({{ datos.novedades_destacadas.length }})</span>
          </div>
          <span class="text-slate-400 font-extrabold">{{ mostrarNovedades ? '▲ Ocultar' : '▼ Ver Todas' }}</span>
        </button>

        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="transform -translate-y-2 opacity-0"
          enter-to-class="transform translate-y-0 opacity-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="transform translate-y-0 opacity-100"
          leave-to-class="transform -translate-y-2 opacity-0"
        >
          <div v-if="mostrarNovedades" class="mt-3 space-y-2">
            <div 
              v-for="(nov, idx) in datos.novedades_destacadas" 
              :key="idx"
              class="p-3 rounded-xl border flex items-start gap-3 text-xs"
              :class="nov.tipo === 'dia_general' ? 'bg-amber-50/70 border-amber-200 text-amber-900' : 'bg-blue-50/60 border-blue-200 text-blue-900'"
            >
              <div class="shrink-0 text-center">
                <span class="font-extrabold text-[11px] block">{{ nov.fecha_corta }}</span>
                <span class="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded" :class="nov.tipo === 'dia_general' ? 'bg-amber-200/80 text-amber-900' : 'bg-blue-200/80 text-blue-900'">
                  {{ nov.orden ? nov.orden : 'Planta' }}
                </span>
              </div>
              <div class="flex-1">
                <p class="font-medium leading-relaxed">{{ nov.observacion }}</p>
                <p v-if="nov.articulo" class="text-[10px] text-slate-500 mt-0.5">
                  Artículo: {{ nov.articulo }}
                </p>
              </div>
            </div>
          </div>
        </Transition>
      </div>

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

// Estado interactivo
const fechaSeleccionada = ref(null)
const busqueda = ref('')
const mostrarNovedades = ref(false)

// Seleccionar fecha o alternar
const seleccionarFecha = (fecha) => {
  if (fechaSeleccionada.value === fecha) {
    fechaSeleccionada.value = null
  } else {
    fechaSeleccionada.value = fecha
  }
}

// Ritmo promedio en formato de rango entero (ej. "3 - 4")
const promedioRango = computed(() => {
  const prom = Number(props.datos?.totales?.promedio_dia || 0)
  if (!prom || prom <= 0) return '0'
  const bajo = Math.floor(prom)
  const alto = Math.ceil(prom)
  if (bajo === alto) return `${bajo}`
  return `${bajo} - ${alto}`
})

// Nombre legible de la fecha seleccionada
const fechaSeleccionadaNombre = computed(() => {
  if (!fechaSeleccionada.value || !props.datos?.por_dia) return ''
  const d = props.datos.por_dia.find(x => x.fecha === fechaSeleccionada.value)
  if (d) return `${d.dia_semana} ${d.fecha_corta}`
  return fechaSeleccionada.value
})

// Observaciones generales del día seleccionado
const observacionesDelDia = computed(() => {
  if (!props.datos?.por_dia) return []
  if (fechaSeleccionada.value) {
    const d = props.datos.por_dia.find(x => x.fecha === fechaSeleccionada.value)
    return d?.observaciones_dia || []
  }
  // Si no hay fecha seleccionada, retornar observaciones de días con sin_ordenes
  const res = []
  props.datos.por_dia.forEach(d => {
    if (d.observaciones_dia && d.observaciones_dia.length > 0) {
      d.observaciones_dia.forEach(obs => {
        res.push(`${d.fecha_corta} (${d.dia_semana}): ${obs}`)
      })
    }
  })
  return res
})

// Consolidado plano de todas las órdenes con metadata de fecha
const todasLasOrdenes = computed(() => {
  if (!props.datos?.por_dia) return []
  const list = []
  props.datos.por_dia.forEach(dia => {
    if (dia.ordenes && dia.ordenes.length > 0) {
      dia.ordenes.forEach(o => {
        list.push({
          ...o,
          fecha: dia.fecha,
          fecha_corta: dia.fecha_corta,
          dia_semana: dia.dia_semana
        })
      })
    }
  })
  return list
})

// Órdenes filtradas por fecha seleccionada y texto de búsqueda
const ordenesFiltradas = computed(() => {
  let list = todasLasOrdenes.value

  // Filtro por fecha
  if (fechaSeleccionada.value) {
    list = list.filter(o => o.fecha === fechaSeleccionada.value)
  }

  // Filtro por búsqueda
  const q = busqueda.value.trim().toLowerCase()
  if (q) {
    list = list.filter(o => {
      const op = (o.orden || '').toLowerCase()
      const art = (o.articulo || '').toLowerCase()
      const obs = (o.observaciones || '').toLowerCase()
      const t = (o.turno || '').toLowerCase()
      return op.includes(q) || art.includes(q) || obs.includes(q) || t.includes(q)
    })
  }

  return list
})
</script>
