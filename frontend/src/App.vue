<template>
  <div class="min-h-screen bg-slate-100 font-sans antialiased text-slate-800 flex flex-col">
    <!-- Header Principal -->
    <header class="bg-slate-900 text-white shadow-md py-4 px-6 md:px-8 border-b border-slate-800 sticky top-0 z-30">
      <div class="max-w-7xl mx-auto flex flex-wrap justify-between items-center gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-lg shadow-inner">
            🧵
          </div>
          <div>
            <h1 class="text-xl md:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              REPORTE GERENCIAL
              <span class="text-xs font-semibold px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30">
                PRODUCCIÓN
              </span>
            </h1>
            <p class="text-xs text-slate-400">Planta Textil | Sistema de Monitoreo & Control Operativo</p>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <!-- Badge de conexión API -->
          <span class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border" :class="{
            'bg-slate-800 text-slate-300 border-slate-700': cargando,
            'bg-emerald-500/10 text-emerald-400 border-emerald-500/30': !cargando && !error,
            'bg-rose-500/10 text-rose-400 border-rose-500/30': error
          }">
            <span v-if="cargando" class="animate-pulse">● Conectando...</span>
            <span v-else-if="!error">● API en Línea</span>
            <span v-else>● Sin Conexión</span>
          </span>

          <div class="hidden sm:flex items-center gap-2 border-l border-slate-800 pl-4 text-xs text-slate-300">
            <div class="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-slate-200 text-xs">
              J
            </div>
            <span class="font-semibold text-slate-200">Jhonni</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Barra de Control Ejecutivo & Selector de Mes -->
    <div class="bg-white border-b border-slate-200 shadow-xs py-3 px-6 md:px-8">
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        <!-- Archivo Activo y Título -->
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 shrink-0 shadow-xs">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Mes Activo:</span>
              <span class="px-2 py-0.2 rounded text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                {{ archivoActual || 'Cargando...' }}
              </span>
            </div>
            <h2 class="text-sm md:text-base font-extrabold text-slate-900 leading-tight">
              {{ resumenData.titulo || 'CONTROL DE PRODUCCIÓN' }}
            </h2>
          </div>
        </div>

        <!-- Ribbon de Métricas Rápidas en Cabecera -->
        <div class="hidden xl:flex items-center gap-4 bg-slate-50 border border-slate-200/80 rounded-xl px-4 py-1.5 text-xs">
          <div class="flex items-center gap-1.5">
            <span class="text-slate-400 font-medium">Efic. Entrega:</span>
            <span class="font-extrabold px-1.5 py-0.2 rounded" :class="(eficienciaData.porcentaje_eficiente || 0) >= 90 ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'">
              {{ eficienciaData.porcentaje_eficiente !== undefined ? Math.round(eficienciaData.porcentaje_eficiente) : 0 }}%
            </span>
          </div>
          <span class="text-slate-300">|</span>
          <div class="flex items-center gap-1.5">
            <span class="text-slate-400 font-medium">En Planta:</span>
            <span class="font-extrabold text-indigo-700">{{ totalPendientes }} OPs</span>
          </div>
          <span class="text-slate-300">|</span>
          <div class="flex items-center gap-1.5">
            <span class="text-slate-400 font-medium">Urdido:</span>
            <span class="font-extrabold text-cyan-700">
              {{ urdidoData.disponible ? `${urdidoData.totales?.carretos || 0} carretos` : 'N/A' }}
            </span>
          </div>
          <span class="text-slate-300">|</span>
          <div class="flex items-center gap-1.5">
            <span class="text-slate-400 font-medium">Montaje:</span>
            <span class="font-extrabold text-teal-700">{{ totalTirasMontaje }} tiras</span>
          </div>
          <template v-if="ordenesAcabadasData.disponible">
            <span class="text-slate-300">|</span>
            <div class="flex items-center gap-1.5">
              <span class="text-slate-400 font-medium">Acabadas:</span>
              <span class="font-extrabold text-emerald-700">{{ ordenesAcabadasData.totales?.total_ordenes || 0 }} OPs</span>
            </div>
          </template>
        </div>

        <!-- Acciones: Selector de archivo y botón de subir -->
        <div class="flex flex-wrap items-center gap-2.5 justify-end">
          <div v-if="archivosDisponibles.length > 1" class="relative">
            <select 
              :value="archivoActual" 
              @change="cambiarArchivo($event.target.value)"
              :disabled="subiendo || cargando"
              class="bg-white border border-slate-300 text-slate-700 text-xs font-semibold rounded-xl px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer disabled:opacity-50 shadow-2xs hover:border-slate-400 transition-all"
            >
              <option v-for="arch in archivosDisponibles" :key="arch.filename" :value="arch.filename">
                {{ arch.filename }} ({{ arch.tamano_kb }} KB)
              </option>
            </select>
          </div>

          <label 
            class="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 active:scale-95 transition-all shadow-sm cursor-pointer"
            :class="{ 'opacity-50 pointer-events-none': subiendo || cargando }"
          >
            <svg v-if="!subiendo" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <span v-if="subiendo" class="inline-block animate-spin">⟳</span>
            <span>{{ subiendo ? 'Procesando...' : 'Subir Excel' }}</span>
            <input 
              type="file" 
              accept=".xlsx,.xls" 
              @change="handleFileUpload" 
              class="hidden" 
              :disabled="subiendo || cargando"
            />
          </label>
        </div>
      </div>
    </div>

    <!-- Navegación de Pestañas del Dashboard -->
    <div class="bg-white border-b border-slate-200/90 shadow-2xs sticky top-[73px] z-20">
      <div class="max-w-7xl mx-auto px-6 md:px-8 py-2.5">
        <nav class="flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5">
          <!-- Tab 1: Resumen General -->
          <button 
            @click="activeTab = 'overview'" 
            type="button"
            class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap border"
            :class="activeTab === 'overview' 
              ? 'bg-slate-900 text-white border-slate-900 shadow-sm' 
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 hover:text-slate-900'"
          >
            <span>📊</span>
            <span>Resumen Ejecutivo</span>
          </button>

          <!-- Tab 2: Órdenes en Planta -->
          <button 
            @click="activeTab = 'proceso'" 
            type="button"
            class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap border"
            :class="activeTab === 'proceso' 
              ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm' 
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 hover:text-slate-900'"
          >
            <span>📋</span>
            <span>Órdenes en Planta</span>
            <span class="px-2 py-0.2 rounded-full text-[10px] font-extrabold" :class="activeTab === 'proceso' ? 'bg-indigo-800 text-white' : 'bg-indigo-100 text-indigo-800'">
              {{ totalPendientes }}
            </span>
          </button>

          <!-- Tab 3: Urdido -->
          <button 
            @click="activeTab = 'urdido'" 
            type="button"
            class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap border"
            :class="activeTab === 'urdido' 
              ? 'bg-cyan-700 text-white border-cyan-700 shadow-sm' 
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 hover:text-slate-900'"
          >
            <span>🧵</span>
            <span>Urdido</span>
            <span v-if="urdidoData.disponible" class="px-2 py-0.2 rounded-full text-[10px] font-extrabold" :class="activeTab === 'urdido' ? 'bg-cyan-900 text-white' : 'bg-cyan-100 text-cyan-800'">
              {{ urdidoData.totales?.carretos || 0 }} carretos
            </span>
            <span v-else class="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-slate-200 text-slate-500">
              No disp.
            </span>
            <span v-if="ordenesAcabadasData.disponible" class="px-1.5 py-0.2 rounded-full text-[10px] font-extrabold" :class="activeTab === 'urdido' ? 'bg-emerald-800 text-white' : 'bg-emerald-100 text-emerald-800'">
              {{ ordenesAcabadasData.totales?.total_ordenes || 0 }} acabadas
            </span>
          </button>

          <!-- Tab 4: Maquinaria (Montaje & Calibración) -->
          <button 
            @click="activeTab = 'maquinaria'" 
            type="button"
            class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap border"
            :class="activeTab === 'maquinaria' 
              ? 'bg-teal-700 text-white border-teal-700 shadow-sm' 
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 hover:text-slate-900'"
          >
            <span>⚙️</span>
            <span>Montaje & Calibración</span>
            <span class="px-2 py-0.2 rounded-full text-[10px] font-extrabold" :class="activeTab === 'maquinaria' ? 'bg-teal-900 text-white' : 'bg-teal-100 text-teal-800'">
              {{ totalTirasMontaje }} tiras
            </span>
          </button>

          <!-- Tab 5: Vista Completa -->
          <button 
            @click="activeTab = 'todas'" 
            type="button"
            title="Ver todas las secciones juntas"
            class="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap border ml-auto"
            :class="activeTab === 'todas' 
              ? 'bg-slate-800 text-white border-slate-800 shadow-sm' 
              : 'bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200 hover:text-slate-800'"
          >
            <span>📄</span>
            <span>Vista Completa</span>
          </button>
        </nav>
      </div>
    </div>

    <!-- Cuerpo Principal con Vistas del Dashboard -->
    <main class="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full space-y-6">
      
      <!-- Mensajes de Notificación / Alertas -->
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform -translate-y-2 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform -translate-y-2 opacity-0"
      >
        <div v-if="notificacion.mensaje" class="p-4 rounded-2xl text-xs font-semibold flex items-center justify-between shadow-xs transition-all" :class="{
          'bg-emerald-50 text-emerald-800 border border-emerald-200': notificacion.tipo === 'success',
          'bg-rose-50 text-rose-800 border border-rose-200': notificacion.tipo === 'error'
        }">
          <div class="flex items-center gap-2">
            <span>{{ notificacion.tipo === 'success' ? '✅' : '⚠️' }}</span>
            <span>{{ notificacion.mensaje }}</span>
          </div>
          <button @click="notificacion.mensaje = ''" class="text-slate-400 hover:text-slate-600 font-bold p-1">✕</button>
        </div>
      </Transition>

      <!-- ==================== VISTA 1: RESUMEN EJECUTIVO ==================== -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <!-- 1. KPI Cards Renovadas -->
        <ResumenKPI :datos="resumenData" />

        <!-- 2. Gráficos de Eficiencia y Causas lado a lado -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <EficienciaChart :datos="eficienciaData" />
          <CausasChart :datos="causasData" />
        </div>

        <!-- 3. Tarjeta de Balance Operativo & Accesos Directos -->
        <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 pb-4 border-b border-slate-100">
            <div>
              <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <span>🏭 Estado de Planta Textil</span>
                <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                  {{ totalPendientes }} órdenes en curso
                </span>
              </h3>
              <p class="text-xs text-slate-500 mt-0.5">
                Distribución de órdenes en fabricación sin facturar y atajos a módulos detallados.
              </p>
            </div>
            
            <div class="flex items-center gap-3">
              <button 
                @click="activeTab = 'proceso'"
                class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition-all cursor-pointer"
              >
                <span>Ver Órdenes en Planta</span>
                <span>→</span>
              </button>
              <button 
                v-if="urdidoData.disponible"
                @click="activeTab = 'urdido'"
                class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-cyan-50 text-cyan-800 hover:bg-cyan-100 border border-cyan-200 transition-all cursor-pointer"
              >
                <span>Ver Urdido ({{ urdidoData.totales?.carretos || 0 }} carretos)</span>
                <span>→</span>
              </button>
            </div>
          </div>

          <!-- Distribución Rápida de Proceso -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="p-3.5 rounded-xl bg-blue-50/60 border border-blue-100">
              <span class="text-[11px] font-bold text-blue-700 uppercase">Tejeduría</span>
              <p class="text-xl font-extrabold text-blue-900 mt-1">{{ resumenData.ordenes_en_tejeduria || 0 }}</p>
              <p class="text-[10px] text-blue-600 mt-0.5">En telar</p>
            </div>
            <div class="p-3.5 rounded-xl bg-purple-50/60 border border-purple-100">
              <span class="text-[11px] font-bold text-purple-700 uppercase">Acabados</span>
              <p class="text-xl font-extrabold text-purple-900 mt-1">{{ resumenData.acabados || 0 }}</p>
              <p class="text-[10px] text-purple-600 mt-0.5">Envolviendo / Terminado</p>
            </div>
            <div class="p-3.5 rounded-xl bg-teal-50/60 border border-teal-100">
              <span class="text-[11px] font-bold text-teal-700 uppercase">Montaje</span>
              <p class="text-xl font-extrabold text-teal-900 mt-1">{{ totalTirasMontaje }}</p>
              <p class="text-[10px] text-teal-600 mt-0.5">Tiras registradas</p>
            </div>
            <div class="p-3.5 rounded-xl bg-indigo-50/60 border border-indigo-100">
              <span class="text-[11px] font-bold text-indigo-700 uppercase">Calibración</span>
              <p class="text-xl font-extrabold text-indigo-900 mt-1">{{ totalCalibraciones }}</p>
              <p class="text-[10px] text-indigo-600 mt-0.5">Ajustes técnicos</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== VISTA 2: ÓRDENES EN PLANTA ==================== -->
      <div v-else-if="activeTab === 'proceso'" class="space-y-6">
        <OrdenesProceso :datos="eficienciaData" />
      </div>

      <!-- ==================== VISTA 3: URDIDO ==================== -->
      <div v-else-if="activeTab === 'urdido'" class="space-y-6">
        <UrdidoDashboard :datos="urdidoData" />
        <OrdenesAcabadasCard :datos="ordenesAcabadasData" />
      </div>

      <!-- ==================== VISTA 4: MAQUINARIA (MONTAJE & CALIBRACIÓN) ==================== -->
      <div v-else-if="activeTab === 'maquinaria'" class="space-y-6">
        <!-- Sub-selector de vista técnica -->
        <div class="flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
          <div>
            <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider">
              Alistamiento Técnico de Maquinaria
            </h3>
            <p class="text-xs text-slate-500 mt-0.5">
              Control de operarios de montaje en telares y calibraciones por técnicos especialistas.
            </p>
          </div>

          <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
            <button 
              @click="subTabMaquinaria = 'ambos'" 
              type="button"
              class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
              :class="subTabMaquinaria === 'ambos' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
            >
              Vista Dual
            </button>
            <button 
              @click="subTabMaquinaria = 'montaje'" 
              type="button"
              class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
              :class="subTabMaquinaria === 'montaje' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
            >
              Solo Montaje
            </button>
            <button 
              @click="subTabMaquinaria = 'calibracion'" 
              type="button"
              class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
              :class="subTabMaquinaria === 'calibracion' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
            >
              Solo Calibración
            </button>
          </div>
        </div>

        <!-- Vista Dual -->
        <div v-if="subTabMaquinaria === 'ambos'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MontajeChart :datos="montajeData" />
          <CalibracionChart :datos="calibracionData" />
        </div>

        <!-- Solo Montaje (Ancho completo) -->
        <div v-else-if="subTabMaquinaria === 'montaje'">
          <MontajeChart :datos="montajeData" />
        </div>

        <!-- Solo Calibración (Ancho completo) -->
        <div v-else-if="subTabMaquinaria === 'calibracion'">
          <CalibracionChart :datos="calibracionData" />
        </div>
      </div>

      <!-- ==================== VISTA 5: VISTA COMPLETA (TODO) ==================== -->
      <div v-else-if="activeTab === 'todas'" class="space-y-8">
        <div class="p-3 bg-slate-200/70 border border-slate-300 rounded-xl text-xs text-slate-700 font-semibold flex items-center justify-between">
          <span>📄 Modo Vista Completa: Se muestran todos los módulos secuencialmente.</span>
          <button @click="activeTab = 'overview'" class="text-blue-700 hover:underline font-bold">
            Volver a modo Dashboard
          </button>
        </div>

        <ResumenKPI :datos="resumenData" />

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <EficienciaChart :datos="eficienciaData" />
          <CausasChart :datos="causasData" />
        </div>

        <OrdenesProceso :datos="eficienciaData" />

        <UrdidoDashboard :datos="urdidoData" />
        <OrdenesAcabadasCard :datos="ordenesAcabadasData" />

        <MontajeChart :datos="montajeData" />

        <CalibracionChart :datos="calibracionData" />
      </div>

    </main>

    <!-- Footer -->
    <footer class="bg-slate-900 text-slate-500 text-xs text-center py-4 mt-8 border-t border-slate-800">
      Sistema de Reportes Gerenciales — Planta Textil © 2026
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ResumenKPI from './components/ResumenKPI.vue'
import EficienciaChart from './components/EficienciaChart.vue'
import CausasChart from './components/CausasChart.vue'
import OrdenesProceso from './components/OrdenesProceso.vue'
import UrdidoDashboard from './components/UrdidoDashboard.vue'
import OrdenesAcabadasCard from './components/OrdenesAcabadasCard.vue'
import MontajeChart from './components/MontajeChart.vue'
import CalibracionChart from './components/CalibracionChart.vue'

const API = 'http://127.0.0.1:8000'

const activeTab = ref('overview')
const subTabMaquinaria = ref('ambos')

const resumenData = ref({})
const eficienciaData = ref({})
const causasData = ref({})
const urdidoData = ref({})
const ordenesAcabadasData = ref({})
const montajeData = ref({})
const calibracionData = ref({})
const archivosDisponibles = ref([])
const archivoActual = ref('')

const cargando = ref(true)
const subiendo = ref(false)
const error = ref(false)
const notificacion = ref({ tipo: '', mensaje: '' })

// Total de órdenes pendientes
const totalPendientes = computed(() => {
  return eficienciaData.value?.lista_pendientes?.length || eficienciaData.value?.total_pendientes || 0
})

// Total de tiras de montaje
const totalTirasMontaje = computed(() => {
  if (montajeData.value?.total_tiras !== undefined) return montajeData.value.total_tiras
  return montajeData.value?.operarios?.reduce((sum, o) => sum + (o.total_tiras || 0), 0) || 0
})

// Total de calibraciones
const totalCalibraciones = computed(() => {
  if (calibracionData.value?.total !== undefined) return calibracionData.value.total
  return calibracionData.value?.calibradores?.reduce((sum, c) => sum + (c.veces || 0), 0) || 0
})

// Formatear miles
const formatearMiles = (num) => {
  if (num === null || num === undefined) return '0'
  return Math.round(num).toLocaleString('es-CO')
}

// Mostrar notificación temporal
const mostrarNotificacion = (tipo, mensaje) => {
  notificacion.value = { tipo, mensaje }
  setTimeout(() => {
    if (notificacion.value.mensaje === mensaje) {
      notificacion.value.mensaje = ''
    }
  }, 6000)
}

// Cargar lista de archivos disponibles
const cargarArchivos = async () => {
  try {
    const res = await fetch(`${API}/api/produccion/archivos`)
    if (res.ok) {
      const data = await res.json()
      archivosDisponibles.value = data.archivos || []
      archivoActual.value = data.archivo_actual || ''
    }
  } catch (e) {
    console.error('Error cargando archivos:', e)
  }
}

// Cargar todos los datos del dashboard
const cargarDatos = async () => {
  cargando.value = true
  error.value = false
  try {
    const fetchJson = async (url) => {
      const r = await fetch(url)
      if (!r.ok) {
        const errData = await r.json().catch(() => ({}))
        throw new Error(errData.detail || `Error al consultar ${url}`)
      }
      return r.json()
    }

    const [r1, r2, r3, r4, r5, r6, r7] = await Promise.all([
      fetchJson(`${API}/api/produccion/resumen`),
      fetchJson(`${API}/api/produccion/eficiencia`),
      fetchJson(`${API}/api/produccion/causas`),
      fetchJson(`${API}/api/produccion/montaje`),
      fetchJson(`${API}/api/produccion/calibracion`),
      fetchJson(`${API}/api/produccion/urdido`),
      fetchJson(`${API}/api/produccion/ordenes-acabadas`),
    ])
    resumenData.value = r1
    eficienciaData.value = r2
    causasData.value = r3
    montajeData.value = r4
    calibracionData.value = r5
    urdidoData.value = r6
    ordenesAcabadasData.value = r7
    archivoActual.value = r1.archivo || archivoActual.value
    await cargarArchivos()
  } catch (e) {
    console.error('Error fetching data:', e)
    error.value = true
    mostrarNotificacion('error', e.message || 'Error al conectar con la API')
  } finally {
    cargando.value = false
  }
}

// Cambiar de archivo activo
const cambiarArchivo = async (filename) => {
  if (!filename || filename === archivoActual.value) return
  cargando.value = true
  try {
    const res = await fetch(`${API}/api/produccion/seleccionar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    })
    const data = await res.json()
    if (res.ok) {
      mostrarNotificacion('success', data.mensaje || `Se activó ${filename}`)
      await cargarDatos()
    } else {
      mostrarNotificacion('error', data.detail || 'Error al cambiar archivo')
      cargando.value = false
    }
  } catch (e) {
    mostrarNotificacion('error', 'Error al conectar con el servidor')
    cargando.value = false
  }
}

// Manejar subida de nuevo archivo Excel
const handleFileUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  subiendo.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await fetch(`${API}/api/produccion/upload`, {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    if (res.ok) {
      mostrarNotificacion('success', data.mensaje || `Archivo ${file.name} cargado con éxito.`)
      await cargarDatos()
    } else {
      mostrarNotificacion('error', data.detail || 'Error al procesar el archivo Excel')
    }
  } catch (e) {
    mostrarNotificacion('error', 'Error de conexión al subir el archivo')
  } finally {
    subiendo.value = false
    event.target.value = ''
  }
}

onMounted(() => {
  cargarDatos()
})
</script>