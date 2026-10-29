# Memoria del Proyecto — Sistema de Reporte Gerencial Textil

## 1. Arquitectura y Componentes
- **Backend (`backend/main.py`)**: FastAPI con Python 3.12, Pandas y OpenPyXL. Sirve en el puerto 8000.
- **Frontend (`frontend/`)**: Vue 3 (Vite, Tailwind CSS, Chart.js, vue-chartjs). Sirve en el puerto 5173.
- **Lanzador (`iniciar_sistema.bat`)**: Inicia tanto backend como frontend en ventanas cmd independientes y abre el navegador.

---

## 2. Reglas de Negocio y Estructura de Datos Excel

### Libros y Hojas Requeridas
- Solo son obligatorias 3 hojas operativas: `DATOS GENERALES`, `MONTAJE`, y `CALIBRACION`.
- La hoja `RESUMEN` es opcional (el sistema calcula las métricas dinámicamente si no existe).
- Siempre utilizar `read_sheet_smart()`, `find_sheet()` y `get_col_name()` para tolerancia a variaciones en nombres de columnas y espacios en blanco.

### Criterio de Eficiencia de Entrega
- **Regla clave de planta**: Una orden solo es evaluada como `EFICIENTE` o `NO EFICIENTE` **cuando cuenta con su Fecha de Facturación**.
- **Estándar Dinámico de Días de Entrega (Opción 2)**:
  - Base: **20 días** de entrega para órdenes con hasta 6,500 metros (`MTS PEDIDO` $\le 6,500$).
  - A partir de **6,500 metros**: se agrega **+1 día extra de plazo por cada 1,000 metros adicionales**, considerando producción continua en dos turnos (**Día y Velada**):
    $$\text{Días Estándar} = 20 + \lceil(\text{MTS PEDIDO} - 6,500) / 1,000\rceil$$
  - Si los `DIAS TOTAL DE ENTREGA` son $\le \text{Días Estándar}$, la orden se califica como **EFICIENTE**.
  - Si superan dicho plazo, se califica como **NO EFICIENTE** y se registra en Causas con `Días Retraso = Días Entrega - Días Estándar`.
- **Prevalencia de Cálculo Dinámico sobre Fórmulas de Excel**:
  - Las columnas de Excel como `EFICIENCIA DE ENTREGA` suelen tener fórmulas estáticas congeladas en 20 días (`=IF(<=20...)`).
  - El backend **debe ignorar esa columna estática** cuando existe `FECHA DE FACTURACION` y `MTS PEDIDO`, calculando siempre el estándar en tiempo real para evitar falsos negativos en órdenes de gran metraje.
- **Órdenes en Proceso / Pendientes de Facturación**: Las órdenes que no tienen fecha de facturación continúan en planta textil en sus respectivos procesos:
  - `Tejeduría` (órdenes en telar/máquina).
  - `Acabados` (planchado, envoltura, etc.).
  - `Calibración` (ajuste técnico de maquinaria).
  - `Terminado` (fabricación completada, a la espera de entrega/facturación).
- Estas órdenes se visualizan en:
  1. El componente dedicado `frontend/src/components/OrdenesProceso.vue` (Pestaña 'Órdenes en Planta' y vista completa), con columnas diferenciadas para `Metraje Pedido` y `Fechas & Plazo Meta` (mostrando la fecha real de `INGRESO`, la fecha estimada/meta calculada según días hábiles y el badge del estándar aplicable).
  2. Dentro de `frontend/src/components/EficienciaChart.vue` a través del botón interactivo `En Proceso / Sin Facturar`.

### Montaje por Operario
- La hoja `MONTAJE` puede incluir el nombre o descripción del producto/orden justo al lado del código de orden (a veces con cabecera en blanco `Unnamed_1` o rotulada como `DETALLE`/`PRODUCTO`).
- **Cruce automático**: Si en la hoja `MONTAJE` no viene la columna del producto, el backend hace un fallback automático buscando el código de orden en `DATOS GENERALES` para extraer el `DETALLE`.
- `frontend/src/components/MontajeChart.vue` muestra en la tabla de detalle por operario:
  - **Orden** (Código OP).
  - **Nombre / Detalle del Producto**.
  - **Tiras montadas**.
  - Buscador rápido en tiempo real.

### Calibración por Técnico
- Soporta formato dual automático:
  1. **Formato Lista tradicional** (Julio a Septiembre): Columnas `NOMBRE`, `NUMERO DE VECES`, `ARTICULO`.
  2. **Formato Matriz** (Octubre en adelante): Columnas de técnicos (`CARLOS`, `CLAUDIO`, `JAVIER`, `JESSICA`, `OSCAR`, `JOSE`) y filas con códigos de órdenes y artículos.
- En ambos formatos se extrae el total de calibraciones, artículos intervenidos y desglose interactivo de órdenes (`detalle_por_orden`) con buscador en tiempo real.

### Urdido (Enfoque Simplificado)
- **Regla de visualización**: El módulo de Urdido está enfocado en:
  1. **Cuántos carretos hace cada operario**: Gráfico comparativo de carretos por operario con desglose por turno (Día vs Velada) y tarjetas individuales con total de carretos y porcentaje del mes.
  2. **Una sola tarjeta para metros**: Tarjeta ejecutiva con el total de metros urdidos (`Metros Urdidos Totales`) con sutil discriminación de Día y Velada.
  3. **Top 7 Artículos Urdidos**: Gráfico horizontal y lista ranking con los 7 artículos de mayor demanda urdida, sus metros, porcentaje acumulado y carretos preparados.
- Se eliminaron las tablas pesadas y bitácoras para mantener la vista limpia, ágil y ejecutiva.
- **Prohibición de saturación**: No reintroducir tablas crudas, bitácoras extensas o métricas redundantes en la vista de Urdido.

### Órdenes Acabadas por Día (Hoja Opcional `ORDENES ACABADAS`)
- **Incorporación**: Añadida a partir de **Octubre 2026**.
- **Estructura**:
  - `FECHA`: Fecha de la jornada (aplica forward fill a los registros de ese día).
  - `TURNO`: Turno operativo (`DIA` o `VELADA`, o indicador de `NO HAY ORDENES TERMINADAS`).
  - `ORDEN`: Código de orden OP completada.
  - `ARTICULO`: Nombre / descripción de producto (con fallback automático a `DATOS GENERALES`).
  - `OBSERVACIONES`: Novedades técnicas tanto de la jornada (ej. motivos de 0 terminadas por cambios de máquina o hilos) como notas específicas de la OP (ej. máquinas compartidas con otra orden).
- **Componente Frontend (`frontend/src/components/OrdenesAcabadasCard.vue`)**:
  - Ubicado en la pestaña **🧵 Urdido** y en **📄 Vista Completa**.
  - Tarjetas resumen: Total acabadas, Ritmo promedio diario en rango entero (ej. 3 - 4 OPs/día), OPs Día (%) y OPs Velada (%).
  - Cronograma diario interactivo en cards con conteo por día y badges de turnos.
  - Alerta destacada para observaciones generales de planta por fecha.
  - Tabla de órdenes terminadas con badges de turno, código OP, artículo y observaciones.
  - Bitácora plegable con todas las novedades técnicas registradas.
  - Buscador en tiempo real por código de orden o artículo.
  - Insignia en el ribbon superior permanente y en el botón de la pestaña Urdido.

### Arquitectura de Navegación Dashboard (Anti-Saturación Visual)
- `frontend/src/App.vue` implementa navegación por pestañas ejecutivas para evitar la acumulación vertical de secciones:
  1. **📊 Resumen Ejecutivo**: KPIs de cabecera renovados, gráficos de Eficiencia y Causas, y balance operativo de planta con accesos directos.
  2. **📋 Órdenes en Planta**: Seguimiento focalizado de órdenes sin facturar con filtros por proceso (Tejeduría, Acabados, Calibración, Montaje, Terminadas) y buscador.
  3. **🧵 Urdido**: Módulo enfocado en carretos por operario, tarjeta única de metros y control de Órdenes Acabadas por Día.
  4. **⚙️ Montaje & Calibración**: Alistamiento de maquinaria con selector de vista (Dual, Solo Montaje con ancho completo, o Solo Calibración con ancho completo).
  5. **📄 Vista Completa**: Vista panorámica secuencial para reportes continuos o impresión.
- Cinta métrica superior (Quick Ribbon) permanente: Eficiencia %, Órdenes en planta, Carretos urdidos, Tiras montadas y Órdenes acabadas visibles en todo momento.

---

## 3. Endpoints del Backend
- `GET /`: Health check y archivo activo.
- `GET /api/produccion/archivos`: Lista de archivos Excel disponibles y activo.
- `POST /api/produccion/upload`: Carga y validación de nuevo archivo Excel.
- `POST /api/produccion/seleccionar`: Cambio de mes/archivo activo en memoria.
- `GET /api/produccion/resumen`: Totales de producción, terminadas, tejeduría, acabados, eficientes y no eficientes.
- `GET /api/produccion/eficiencia`: Detalle de eficientes, no eficientes, y lista completa de órdenes en proceso (`lista_pendientes`).
- `GET /api/produccion/ordenes-en-proceso`: Detalle directo de órdenes activas sin fecha de facturación.
- `GET /api/produccion/causas`: Clasificación de causas de no eficiencia.
- `GET /api/produccion/montaje`: Operarios, tiras montadas y detalle por orden (incluyendo código y nombre).
- `GET /api/produccion/calibracion`: Métricas por técnico calibrador y detalle por orden.
- `GET /api/produccion/urdido`: Métricas completas de urdido (carretos, metros, turnos Día/Velada, top artículos, producción diaria, bitácora técnica y detalle por orden).
- `GET /api/produccion/ordenes-acabadas`: Métricas diarias de órdenes completadas, desglose por turnos (Día vs Velada), selección por fecha y bitácora de novedades.

---

## 4. Lineamientos de Desarrollo
- Mantener siempre retrocompatibilidad con meses anteriores (Julio 2026, Agosto 2026, Septiembre 2026, Octubre 2026 y futuros).
- Verificar que la compilación del frontend (`npm run build`) se ejecute sin errores tras cualquier modificación.
- No alterar claves de respuestas existentes en los endpoints para no romper componentes cliente.
- Mantener en todo nuevo gráfico el estándar de visualización dual: valor cuantitativo + porcentaje de participación.
- En verificaciones booleanas de Series de Pandas con `.any()`, agrupar estrictamente entre paréntesis: `bool(((s != '') & (~s.isin(...))).any())`.
- **Tolerancia y Sanitización de Fechas en Excel**:
  - Al parsear fechas en texto, corregir errores tipográficos comunes en el año (ej. 5 dígitos como `20260 -> 2026`).
  - Si la fecha no inicia con 4 dígitos de año (`YYYY`), aplicar `dayfirst=True` para preservar el estándar de planta Día/Mes/Año (ej. `1-10-2026` es 01 de Octubre, no 10 de Enero).
  - Si la celda `INGRESO` viene vacía, realizar fallback automático a `APROBACION`.
- **Exclusión de Archivos Temporales de Bloqueo de Excel (`~$*`)**:
  - Al listar o buscar archivos Excel (`glob("*.xlsx")`), omitir estrictamente cualquier archivo cuyo nombre inicie con `~$` para evitar errores `Permission denied [Errno 13]` cuando el usuario tiene el archivo abierto en Excel.
- **Presentación Operativa de Metas y Ritmos**:
  - En órdenes en proceso, mostrar siempre las fechas reales (`INGRESO` y `META ESTIMADA` calculada con `bdate_range` según días hábiles estándar).
  - En órdenes terminadas, expresar el ritmo promedio diario en rango de enteros (ej. `3 - 4 OPs/día`) acompañado del valor estadístico exacto en tooltip/subtítulo.
