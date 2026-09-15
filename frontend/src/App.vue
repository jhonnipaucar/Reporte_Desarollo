<template>
  <div class="min-h-screen bg-slate-50 font-sans antialiased text-slate-800 flex flex-col">
    <!-- Header Principal -->
    <header class="bg-slate-900 text-white shadow-md py-4 px-8 flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-wide">REPORTE GERENCIAL — PRODUCCIÓN</h1>
        <p class="text-xs text-slate-400">Planta Textil | Sistema de Monitoreo Operativo</p>
      </div>
      <div class="flex items-center gap-3">
        <!-- Badge de conexión -->
        <span class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border" :class="{
          'bg-slate-700/50 text-slate-300 border-slate-600': cargando,
          'bg-emerald-500/20 text-emerald-400 border-emerald-500/30': !cargando && !error,
          'bg-amber-500/20 text-amber-400 border-amber-500/30': error
        }">
          <span v-if="cargando" class="animate-pulse">● Conectando...</span>
          <span v-else-if="!error">● API en Línea</span>
          <span v-else>● Error de Conexión</span>
        </span>
        <span class="text-sm font-semibold border-l border-slate-700 pl-3 text-slate-200">Jhonni</span>
      </div>
    </header>

    <main class="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full space-y-6">
      
      <!-- Barra de Gestión de Archivo Excel -->
      <section class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 flex flex-col md:flex-row items-center justify-between gap-4">
        <!-- Archivo Activo -->
        <div class="flex items-center gap-3 w-full md:w-auto">
          <div class="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Archivo Activo:</span>
              <span class="px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                {{ archivoActual || 'Cargando...' }}
              </span>
            </div>
            <h2 class="text-base font-bold text-slate-800 mt-0.5">
              {{ resumenData.titulo || 'CONTROL DE PRODUCCIÓN' }}
            </h2>
          </div>
        </div>

        <!-- Acciones: Selector de archivos y botón de subir -->
        <div class="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
          <!-- Selector si hay múltiples archivos -->
          <div v-if="archivosDisponibles.length > 1" class="relative">
            <select 
              :value="archivoActual" 
              @change="cambiarArchivo($event.target.value)"
              :disabled="subiendo || cargando"
              class="bg-slate-50 border border-slate-300 text-slate-700 text-xs font-medium rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer disabled:opacity-50"
            >
              <option v-for="arch in archivosDisponibles" :key="arch.filename" :value="arch.filename">
                {{ arch.filename }} ({{ arch.tamano_kb }} KB)
              </option>
            </select>
          </div>

          <!-- Botón Subir Archivo Excel -->
          <label 
            class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 active:scale-95 transition-all shadow-sm cursor-pointer"
            :class="{ 'opacity-50 pointer-events-none': subiendo || cargando }"
          >
            <svg v-if="!subiendo" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <span v-if="subiendo" class="inline-block animate-spin">⟳</span>
            <span>{{ subiendo ? 'Procesando Excel...' : 'Subir otro Excel' }}</span>
            <input 
              type="file" 
              accept=".xlsx,.xls" 
              @change="handleFileUpload" 
              class="hidden" 
              :disabled="subiendo || cargando"
            />
          </label>
        </div>
      </section>

      <!-- Mensajes de Notificación / Alertas -->
      <div v-if="notificacion.mensaje" class="p-4 rounded-xl text-xs font-semibold flex items-center justify-between transition-all" :class="{
        'bg-emerald-50 text-emerald-800 border border-emerald-200': notificacion.tipo === 'success',
        'bg-red-50 text-red-800 border border-red-200': notificacion.tipo === 'error'
      }">
        <div class="flex items-center gap-2">
          <span>{{ notificacion.tipo === 'success' ? '✅' : '⚠️' }}</span>
          <span>{{ notificacion.mensaje }}</span>
        </div>
        <button @click="notificacion.mensaje = ''" class="text-slate-400 hover:text-slate-600">✕</button>
      </div>

      <!-- Section 2: KPI Cards -->
      <ResumenKPI :datos="resumenData" />

      <!-- Section 3: Two-column layout for charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <EficienciaChart :datos="eficienciaData" />
        <CausasChart :datos="causasData" />
      </div>

      <!-- Section 4: Montaje -->
      <MontajeChart :datos="montajeData" />

      <!-- Section 5: Calibracion -->
      <CalibracionChart :datos="calibracionData" />
    </main>

    <!-- Footer -->
    <footer class="bg-slate-900 text-slate-500 text-xs text-center py-4 mt-8 border-t border-slate-800">
      Sistema de Reportes Gerenciales — Planta Textil © 2026
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ResumenKPI from './components/ResumenKPI.vue'
import EficienciaChart from './components/EficienciaChart.vue'
import CausasChart from './components/CausasChart.vue'
import MontajeChart from './components/MontajeChart.vue'
import CalibracionChart from './components/CalibracionChart.vue'

const API = 'http://127.0.0.1:8000'

const resumenData = ref({})
const eficienciaData = ref({})
const causasData = ref({})
const montajeData = ref({})
const calibracionData = ref({})
const archivosDisponibles = ref([])
const archivoActual = ref('')

const cargando = ref(true)
const subiendo = ref(false)
const error = ref(false)
const notificacion = ref({ tipo: '', mensaje: '' })

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

    const [r1, r2, r3, r4, r5] = await Promise.all([
      fetchJson(`${API}/api/produccion/resumen`),
      fetchJson(`${API}/api/produccion/eficiencia`),
      fetchJson(`${API}/api/produccion/causas`),
      fetchJson(`${API}/api/produccion/montaje`),
      fetchJson(`${API}/api/produccion/calibracion`),
    ])
    resumenData.value = r1
    eficienciaData.value = r2
    causasData.value = r3
    montajeData.value = r4
    calibracionData.value = r5
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
    // Reset input
    event.target.value = ''
  }
}

onMounted(() => {
  cargarDatos()
})
</script>