from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import logging
import shutil
import re
import math

app = FastAPI(title="API Reporte Gerencial Textil")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / 'uploads'
UPLOADS_DIR.mkdir(exist_ok=True)

def get_initial_excel_path() -> Path:
    oct_act = BASE_DIR / 'OCTUBRE 2026 ACTUALIZADO.xlsx'
    if oct_act.exists():
        return oct_act
    oct_file = BASE_DIR / 'OCTUBRE 2026.xlsx'
    if oct_file.exists():
        return oct_file
    act_file = BASE_DIR / 'SEPTIEMBRE 2026-ACTUALIZADO.xlsx'
    if act_file.exists():
        return act_file
    sep_file = BASE_DIR / 'SEPTIEMBRE 2026.xlsx'
    if sep_file.exists():
        return sep_file
    ago_file = BASE_DIR / 'AGOSTO 2026.xlsx'
    if ago_file.exists():
        return ago_file
    if UPLOADS_DIR.exists():
        upload_files = sorted(list(UPLOADS_DIR.glob('*.xlsx')), key=lambda x: x.stat().st_mtime, reverse=True)
        if upload_files:
            return upload_files[0]
    return sep_file

current_excel_path = get_initial_excel_path()

# Cache variables
cached_data = {}

def find_sheet(excel_file: pd.ExcelFile, sheet_name_target: str) -> str:
    target_norm = sheet_name_target.strip().upper()
    for s in excel_file.sheet_names:
        if s.strip().upper() == target_norm:
            return s
    for s in excel_file.sheet_names:
        if target_norm in s.strip().upper():
            return s
    raise ValueError(f"No se encontró la hoja obligatoria '{sheet_name_target}'. Hojas disponibles en el archivo: {excel_file.sheet_names}")

def find_sheet_optional(excel_file: pd.ExcelFile, sheet_name_target: str):
    target_norm = sheet_name_target.strip().upper()
    for s in excel_file.sheet_names:
        if s.strip().upper() == target_norm:
            return s
    for s in excel_file.sheet_names:
        if target_norm in s.strip().upper():
            return s
    return None

def get_col_name(df, candidates):
    for cand in candidates:
        cand_norm = cand.strip().upper()
        for c in df.columns:
            norm = str(c).strip().upper()
            if cand_norm in norm:
                return c
    return None

def safe_int(val):
    if pd.isna(val):
        return 0
    try:
        return int(val)
    except:
        return 0

def safe_float(val):
    if pd.isna(val):
        return 0.0
    try:
        return round(float(val), 1)
    except:
        return 0.0

def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

def read_sheet_smart(xls: pd.ExcelFile, sheet_name: str, candidate_keywords: list) -> pd.DataFrame:
    df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    if len(df_raw) == 0:
        return pd.DataFrame()
        
    header_row = 0
    # Escanear las primeras 15 filas buscando la fila que contiene las cabeceras reales
    for r in range(min(15, len(df_raw))):
        row_str = " ".join([str(x).upper() for x in df_raw.iloc[r] if pd.notna(x)])
        matches = sum(1 for kw in candidate_keywords if kw.upper() in row_str)
        threshold = 1 if len(candidate_keywords) == 1 else 2
        if matches >= threshold:
            header_row = r
            break
            
    columns = [str(x).strip() if pd.notna(x) else f"Unnamed_{i}" for i, x in enumerate(df_raw.iloc[header_row])]
    df = df_raw.iloc[header_row + 1:].copy()
    df.columns = columns
    df.reset_index(drop=True, inplace=True)
    return df

def load_excel_data(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"El archivo no existe: {file_path}")
        
    with pd.ExcelFile(file_path) as xls:
        # Solo son obligatorios los 3 libros operativos: DATOS GENERALES, MONTAJE, CALIBRACION
        datos_gen_sheet = find_sheet(xls, 'DATOS GENERALES')
        montaje_sheet = find_sheet(xls, 'MONTAJE')
        calibracion_sheet = find_sheet(xls, 'CALIBRACION')
        
        # El libro RESUMEN es totalmente OPCIONAL (el software lo calcula si no existe)
        resumen_sheet = find_sheet_optional(xls, 'RESUMEN')
        
        # El libro URDIDO es OPCIONAL (incorporado en Septiembre 2026 y futuros)
        urdido_sheet = find_sheet_optional(xls, 'URDIDO')
        
        # El libro ORDENES ACABADAS es OPCIONAL (incorporado en Octubre 2026 y futuros)
        acabadas_sheet = find_sheet_optional(xls, 'ORDENES ACABADAS')
        
        df_datos = read_sheet_smart(xls, datos_gen_sheet, ['ORDEN', 'DETALLE', 'ESTADO', 'PRODUCTO', 'EFICIENCIA'])
        df_montaje = read_sheet_smart(xls, montaje_sheet, ['ORDEN', 'OP'])
        df_calibracion = pd.read_excel(xls, sheet_name=calibracion_sheet, header=None)
        df_resumen = pd.read_excel(xls, sheet_name=resumen_sheet, header=None) if resumen_sheet else None
        df_urdido = pd.read_excel(xls, sheet_name=urdido_sheet, header=None) if urdido_sheet else None
        df_acabadas = pd.read_excel(xls, sheet_name=acabadas_sheet, header=None) if acabadas_sheet else None
    
    # Determinar título dinámico
    titulo = "CONTROL DE PRODUCCIÓN"
    if df_resumen is not None:
        for r in range(min(5, len(df_resumen))):
            for c in range(min(6, len(df_resumen.columns))):
                val = str(df_resumen.iloc[r, c]).strip()
                if "CONTROL DE PRODUCCION" in val.upper():
                    titulo = val
                    break
    
    # Si no había RESUMEN o título genérico, intentar deducir mes de DATOS GENERALES o nombre de archivo
    if titulo == "CONTROL DE PRODUCCIÓN":
        op_col = get_col_name(df_datos, ['ORDENES DE PRODUCCION', 'ORDEN'])
        stem_upper = file_path.stem.upper()
        meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
        mes_archivo = next((m for m in meses if m in stem_upper), None)
        
        if mes_archivo:
            titulo = f"CONTROL DE PRODUCCIÓN - {file_path.stem.upper()}"
        elif op_col and any(m in str(op_col).upper() for m in meses):
            titulo = f"CONTROL DE PRODUCCIÓN - {str(op_col).strip()}"
        else:
            titulo = f"CONTROL DE PRODUCCIÓN - {file_path.stem}"
                    
    return {
        'resumen': df_resumen,
        'datos_generales': df_datos,
        'montaje': df_montaje,
        'calibracion': df_calibracion,
        'urdido': df_urdido,
        'ordenes_acabadas': df_acabadas,
        'filename': file_path.name,
        'titulo': titulo
    }

def get_excel_data():
    global cached_data, current_excel_path
    if not cached_data:
        try:
            cached_data = load_excel_data(current_excel_path)
        except Exception as e:
            logging.error(f"Error reading Excel file {current_excel_path}: {e}")
            raise e
    return cached_data

@app.on_event("startup")
def startup_event():
    try:
        get_excel_data()
    except Exception as e:
        print(f"Warning: Could not load excel data on startup: {e}")

@app.get("/")
def health_check():
    data = get_excel_data()
    return {
        "status": "ok",
        "archivo_activo": current_excel_path.name,
        "titulo": data.get("titulo", "CONTROL DE PRODUCCION")
    }

# ==================== GESTIÓN DE ARCHIVOS ====================

@app.get("/api/produccion/archivos")
def list_archivos():
    global current_excel_path, cached_data
    archivos = []
    
    # 1. Archivos en BASE_DIR (ej. SEPTIEMBRE 2026.xlsx, AGOSTO 2026.xlsx)
    nombres_agregados = set()
    for f in sorted(BASE_DIR.glob("*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.name.startswith('~$'):
            continue
        archivos.append({
            "filename": f.name,
            "es_activo": current_excel_path.resolve() == f.resolve(),
            "tamano_kb": round(f.stat().st_size / 1024, 1),
            "fecha": pd.to_datetime(f.stat().st_mtime, unit='s').strftime("%Y-%m-%d %H:%M")
        })
        nombres_agregados.add(f.name)
    
    # 2. Archivos subidos en uploads
    if UPLOADS_DIR.exists():
        for f in sorted(UPLOADS_DIR.glob("*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.name.startswith('~$'):
                continue
            if f.name not in nombres_agregados:
                archivos.append({
                    "filename": f.name,
                    "es_activo": current_excel_path.resolve() == f.resolve(),
                    "tamano_kb": round(f.stat().st_size / 1024, 1),
                    "fecha": pd.to_datetime(f.stat().st_mtime, unit='s').strftime("%Y-%m-%d %H:%M")
                })
                nombres_agregados.add(f.name)
                
    return {
        "archivo_actual": current_excel_path.name,
        "titulo_actual": cached_data.get('titulo', 'CONTROL DE PRODUCCIÓN'),
        "archivos": archivos
    }

@app.post("/api/produccion/upload")
async def upload_excel(file: UploadFile = File(...)):
    global current_excel_path, cached_data
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos Excel (.xlsx, .xls)")
        
    destino = UPLOADS_DIR / file.filename
    try:
        content = await file.read()
        with open(destino, "wb") as f:
            f.write(content)
            
        # Validar intentando cargar la estructura (solo requiere DATOS GENERALES, MONTAJE, CALIBRACION)
        nuevos_datos = load_excel_data(destino)
        # Validar que los cálculos de métricas funcionen sin errores
        calcular_metricas_resumen(nuevos_datos)
        
        # Si fue exitoso, activar el nuevo archivo
        current_excel_path = destino
        cached_data = nuevos_datos
        
        return {
            "status": "success",
            "mensaje": f"Archivo '{file.filename}' cargado y procesado exitosamente.",
            "filename": file.filename,
            "titulo": cached_data.get("titulo")
        }
    except Exception as e:
        if destino.exists():
            try:
                destino.unlink()
            except:
                pass
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo Excel: {str(e)}")

class SeleccionarArchivoReq(BaseModel):
    filename: str

@app.post("/api/produccion/seleccionar")
def seleccionar_archivo(req: SeleccionarArchivoReq):
    global current_excel_path, cached_data
    default_file = BASE_DIR / req.filename
    upload_file = UPLOADS_DIR / req.filename
    
    target = None
    if default_file.exists():
        target = default_file
    elif upload_file.exists():
        target = upload_file
    else:
        raise HTTPException(status_code=404, detail=f"No se encontró el archivo '{req.filename}'")
        
    try:
        nuevos_datos = load_excel_data(target)
        calcular_metricas_resumen(nuevos_datos)
        current_excel_path = target
        cached_data = nuevos_datos
        return {
            "status": "success",
            "mensaje": f"Se activó el archivo '{req.filename}' correctamente.",
            "filename": req.filename,
            "titulo": cached_data.get("titulo")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error cargando archivo: {str(e)}")

# ==================== CÁLCULO DINÁMICO DE DÍAS ESTÁNDAR ====================

def calcular_dias_estandar_entrega(mts_pedido):
    """
    Regla operativa de planta (Opción 2):
    - Plazo estándar base: 20 días de entrega para pedidos de hasta 6,500 metros.
    - A partir de 6,500 metros en MTS PEDIDO: se adiciona 1 día más de entrega
      por cada 1,000 metros adicionales (contando Turno Día y Turno Velada = 24h continuas de telar).
    """
    mts = safe_float(mts_pedido)
    if mts <= 6500:
        return 20, 0
    mts_exceso = mts - 6500
    dias_extra = math.ceil(mts_exceso / 1000.0)
    return 20 + dias_extra, dias_extra

# ==================== ENDPOINTS DE MÉTRICAS ====================

def calcular_metricas_resumen(data):
    df_resumen = data.get('resumen')
    df_datos = data['datos_generales']
    
    op_col = get_col_name(df_datos, ['ORDENES DE PRODUCCION', 'ORDEN', 'OP'])
    if not op_col or op_col not in df_datos.columns:
        op_col = df_datos.columns[0] if len(df_datos.columns) > 0 else 'ORDEN'
        
    valid_df = df_datos[df_datos[op_col].notna()].copy() if op_col in df_datos.columns else df_datos.copy()
    if op_col in valid_df.columns:
        valid_df = valid_df[
            ~valid_df[op_col].astype(str).str.strip().str.upper().isin(['STOCK', 'TOTAL', 'TOTALES']) &
            ~valid_df[op_col].astype(str).str.strip().str.upper().str.startswith('TOTAL')
        ].copy()
    
    fact_col = get_col_name(df_datos, ['FECHA DE FACTURACION', 'FECHA FACTURACION', 'FACTURACION', 'FECHA FACTURA'])
    dias_col = get_col_name(df_datos, ['DIAS TOTAL DE ENTREGA', 'DIAS TOTAL', 'DIAS DE ENTREGA'])
    mts_col = get_col_name(df_datos, ['MTS PEDIDO', 'MTS PEDIDOS', 'METROS PEDIDO', 'MTS_PEDIDO', 'PEDIDO'])
    estado_col = get_col_name(df_datos, ['ESTADO'])

    # Si hay órdenes en DATOS GENERALES con FECHA DE FACTURACION registrada, calculamos dinámicamente con la regla moderna
    tiene_facturacion = False
    if fact_col and fact_col in valid_df.columns:
        series_fact = valid_df[fact_col].dropna().astype(str).str.strip()
        tiene_facturacion = bool(((series_fact != '') & (~series_fact.str.upper().isin(['NAT', 'NAN']))).any())

    if tiene_facturacion:
        totales = len(valid_df)
        if estado_col and estado_col in valid_df.columns:
            estados = valid_df[estado_col].fillna('').astype(str).str.strip().str.upper()
            terminadas = int(estados.str.contains('TERMINAD').sum())
            tejeduria = int(estados.str.contains('TEJEDUR|MAQUIN').sum())
            acabados = int(estados.str.contains('ACABAD').sum())
            montaje = int(estados.str.contains('MONTAJ').sum())
        else:
            terminadas = tejeduria = acabados = montaje = 0
            
        eficientes = 0
        no_eficientes = 0
        for _, r in valid_df.iterrows():
            f_val = r.get(fact_col)
            if pd.notna(f_val):
                f_str = str(f_val).strip()
                if f_str != '' and f_str.upper() not in ['NAT', 'NAN']:
                    dias_tot = safe_int(r.get(dias_col)) if dias_col else 0
                    mts_ped = safe_float(r.get(mts_col)) if mts_col else 0.0
                    dias_std, _ = calcular_dias_estandar_entrega(mts_ped)
                    if dias_tot <= dias_std:
                        eficientes += 1
                    else:
                        no_eficientes += 1
        origen = "calculado_automatico_datos_generales"
    elif df_resumen is not None and len(df_resumen) > 4 and pd.notna(df_resumen.iloc[4, 2]):
        totales = safe_int(df_resumen.iloc[4, 2])
        terminadas = safe_int(df_resumen.iloc[4, 3])
        tejeduria = safe_int(df_resumen.iloc[4, 4])
        acabados = safe_int(df_resumen.iloc[4, 5])
        montaje = 0
        eficientes = safe_int(df_resumen.iloc[4, 6])
        no_eficientes = safe_int(df_resumen.iloc[4, 7])
        origen = "hoja_resumen_excel"
    else:
        # CÁLCULO AUTOMÁTICO DESDE DATOS GENERALES (Formato moderno de 3 libros sin facturas)
        totales = len(valid_df)
        if estado_col and estado_col in valid_df.columns:
            estados = valid_df[estado_col].fillna('').astype(str).str.strip().str.upper()
            terminadas = int(estados.str.contains('TERMINAD').sum())
            tejeduria = int(estados.str.contains('TEJEDUR|MAQUIN').sum())
            acabados = int(estados.str.contains('ACABAD').sum())
            montaje = int(estados.str.contains('MONTAJ').sum())
        else:
            terminadas = tejeduria = acabados = montaje = 0

        efic_col = get_col_name(df_datos, ['EFICIENCIA DE ENTREGA', 'EFICIENCIA'])
        if efic_col and efic_col in valid_df.columns:
            eficiencias = valid_df[efic_col].fillna('').astype(str).str.strip().str.upper()
            eficientes = int((eficiencias == 'EFICIENTE').sum())
            no_eficientes = int((eficiencias == 'NO EFICIENTE').sum())
        else:
            eficientes = 0
            no_eficientes = 0
        origen = "calculado_automatico_datos_generales"
        
    return {
        "ordenes_totales": totales,
        "ordenes_terminadas": terminadas,
        "ordenes_en_tejeduria": tejeduria,
        "acabados": acabados,
        "montaje": montaje,
        "eficientes": eficientes,
        "no_eficientes": no_eficientes,
        "origen_calculo": origen
    }

@app.get("/api/produccion/resumen")
def get_resumen():
    try:
        data = get_excel_data()
        metricas = calcular_metricas_resumen(data)
        return {
            "titulo": data.get("titulo", "CONTROL DE PRODUCCIÓN"),
            "archivo": current_excel_path.name,
            **metricas,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/produccion/eficiencia")
def get_eficiencia():
    try:
        data = get_excel_data()
        metricas = calcular_metricas_resumen(data)
        
        df = data.get('datos_generales')
        lista_eficientes = []
        lista_no_eficientes = []
        lista_pendientes = []
        
        if df is not None and len(df) > 0:
            eficiencia_col = get_col_name(df, ['EFICIENCIA DE ENTREGA', 'EFICIENCIA'])
            op_col = get_col_name(df, ['ORDENES DE PRODUCCION', 'ORDEN', 'OP']) or (df.columns[0] if len(df.columns) > 0 else 'ORDEN')
            detalle_col = get_col_name(df, ['DETALLE', 'PRODUCTO', 'DESCRIPCION']) or 'DETALLE'
            cliente_col = get_col_name(df, ['CLIENTE']) or 'CLIENTE '
            dias_col = get_col_name(df, ['DIAS TOTAL DE ENTREGA', 'DIAS TOTAL', 'DIAS DE ENTREGA']) or 'DIAS TOTAL DE ENTREGA '
            obs_col = get_col_name(df, ['OBSERVACIONES', 'OBSERVACION', 'CAUSA']) or 'OBSERVACIONES'
            estado_col = get_col_name(df, ['ESTADO'])
            fact_col = get_col_name(df, ['FECHA DE FACTURACION', 'FECHA FACTURACION', 'FACTURACION', 'FECHA FACTURA'])
            maquina_col = get_col_name(df, ['MAQUINA'])
            mts_col = get_col_name(df, ['MTS PEDIDO', 'MTS PEDIDOS', 'METROS PEDIDO', 'MTS_PEDIDO', 'PEDIDO'])
            ingreso_col = get_col_name(df, ['INGRESO', 'FECHA DE INGRESO', 'FECHA INGRESO'])
            aprobacion_col = get_col_name(df, ['APROBACION', 'FECHA APROBACION', 'FECHA DE APROBACION'])
            
            valid_df = df[df[op_col].notna()].copy() if op_col in df.columns else df.copy()
            
            tiene_facturacion = False
            if fact_col and fact_col in valid_df.columns:
                series_fact = valid_df[fact_col].dropna().astype(str).str.strip()
                tiene_facturacion = bool(((series_fact != '') & (~series_fact.str.upper().isin(['NAT', 'NAN']))).any())

            for _, row in valid_df.iterrows():
                op_val = safe_str(row.get(op_col))
                if not op_val or op_val.upper().startswith('TOTAL') or op_val.upper() == 'STOCK':
                    continue

                ef_val = safe_str(row.get(eficiencia_col)).upper() if (eficiencia_col and eficiencia_col in valid_df.columns) else ''
                fact_val = safe_str(row.get(fact_col)) if (fact_col and fact_col in valid_df.columns) else ''
                estado_raw = safe_str(row.get(estado_col)) if (estado_col and estado_col in valid_df.columns) else ''
                estado_norm = estado_raw.strip().upper()
                
                dias_tot = safe_int(row.get(dias_col))
                mts_ped = safe_float(row.get(mts_col)) if mts_col else 0.0
                dias_std, dias_extra = calcular_dias_estandar_entrega(mts_ped)
                dias_ret = max(0, dias_tot - dias_std) if dias_tot > 0 else 0

                raw_ingreso = row.get(ingreso_col) if (ingreso_col and ingreso_col in valid_df.columns) else None
                if (pd.isna(raw_ingreso) or str(raw_ingreso).strip() in ['', 'nan', 'NaT', 'None']) and aprobacion_col:
                    raw_ingreso = row.get(aprobacion_col)

                fecha_ingreso_str = ""
                fecha_meta_str = ""
                if pd.notna(raw_ingreso) and str(raw_ingreso).strip() not in ['', 'nan', 'NaT', 'None']:
                    dt_ing = None
                    if isinstance(raw_ingreso, (pd.Timestamp, pd.DatetimeIndex)):
                        dt_ing = raw_ingreso
                    else:
                        s_ing = str(raw_ingreso).strip()
                        # Corregir errores tipográficos de año (ej. '1-10-20260' -> '1-10-2026')
                        s_ing = re.sub(r'(\d{4})0\b', r'\1', s_ing)
                        s_ing = re.sub(r'2026\d\b', '2026', s_ing)
                        try:
                            if re.match(r'^\d{4}[-/]', s_ing):
                                dt_ing = pd.to_datetime(s_ing)
                            else:
                                dt_ing = pd.to_datetime(s_ing, dayfirst=True)
                        except Exception:
                            dt_ing = None

                    if dt_ing is not None:
                        try:
                            fecha_ingreso_str = dt_ing.strftime('%d/%m/%Y')
                            meta_dt = pd.bdate_range(dt_ing, periods=max(dias_std, 1))[-1]
                            fecha_meta_str = meta_dt.strftime('%d/%m/%Y')
                        except Exception:
                            fecha_ingreso_str = str(raw_ingreso).strip()
                            fecha_meta_str = ""
                    else:
                        fecha_ingreso_str = str(raw_ingreso).strip()
                        fecha_meta_str = ""

                base_item = {
                    "op": op_val,
                    "detalle": safe_str(row.get(detalle_col)),
                    "cliente": safe_str(row.get(cliente_col)),
                    "maquina": safe_str(row.get(maquina_col)),
                    "mts_pedido": mts_ped,
                    "fecha_ingreso": fecha_ingreso_str,
                    "fecha_meta": fecha_meta_str,
                    "dias_estandar": dias_std,
                    "dias_extra_metraje": dias_extra,
                    "dias_entrega": dias_tot,
                    "dias_retraso": dias_ret,
                    "observacion": safe_str(row.get(obs_col))
                }

                has_factura = bool(fact_val and fact_val.strip() != '' and fact_val.upper() not in ['NAN', 'NAT'])

                if tiene_facturacion:
                    if has_factura:
                        if dias_tot <= dias_std:
                            lista_eficientes.append(base_item)
                        else:
                            lista_no_eficientes.append(base_item)
                    else:
                        # Orden sin calificar por falta de fecha de facturación (en proceso de planta)
                        if 'TEJEDUR' in estado_norm or 'MAQUIN' in estado_norm:
                            proceso = 'Tejeduría'
                            badge_color = 'blue'
                        elif 'ACABAD' in estado_norm:
                            proceso = 'Acabados'
                            badge_color = 'purple'
                        elif 'CALIBR' in estado_norm:
                            proceso = 'Calibración'
                            badge_color = 'amber'
                        elif 'MONTAJ' in estado_norm:
                            proceso = 'Montaje'
                            badge_color = 'orange'
                        elif 'TERMINAD' in estado_norm:
                            proceso = 'Terminado'
                            badge_color = 'emerald'
                        else:
                            proceso = estado_raw.title() if estado_raw else 'En Proceso'
                            badge_color = 'slate'

                        if 'TERMINAD' in estado_norm:
                            motivo = 'Sin fecha de facturación (Producción lista, pendiente despacho/factura)'
                        else:
                            motivo = 'Sin fecha de facturación (Aún en proceso de planta)'

                        lista_pendientes.append({
                            **base_item,
                            "estado": estado_raw or 'En Proceso',
                            "proceso": proceso,
                            "badge_color": badge_color,
                            "fecha_factura": fact_val,
                            "motivo": motivo
                        })
                else:
                    # Modo retrocompatible para archivos antiguos sin fecha de facturación
                    if ef_val == 'EFICIENTE' or (dias_tot > 0 and dias_tot <= dias_std):
                        lista_eficientes.append(base_item)
                    elif ef_val == 'NO EFICIENTE' or (dias_tot > dias_std):
                        lista_no_eficientes.append(base_item)
                    else:
                        lista_pendientes.append({
                            **base_item,
                            "estado": estado_raw or 'En Proceso',
                            "proceso": 'En Proceso',
                            "badge_color": 'slate',
                            "fecha_factura": '',
                            "motivo": 'Sin calificación'
                        })

        eficientes = len(lista_eficientes)
        no_eficientes = len(lista_no_eficientes)
        total = eficientes + no_eficientes
        
        pct_eficiente = round((eficientes / total) * 100, 1) if total > 0 else 0
        pct_no_eficiente = round((no_eficientes / total) * 100, 1) if total > 0 else 0

        return {
            "eficientes": eficientes,
            "no_eficientes": no_eficientes,
            "total_evaluadas": total,
            "porcentaje_eficiente": pct_eficiente,
            "porcentaje_no_eficiente": pct_no_eficiente,
            "origen_calculo": metricas["origen_calculo"],
            "regla_entrega": "20 días base + 1 día extra por cada 1,000m adicionales a partir de 6,500m (Turnos Día + Velada)",
            "lista_eficientes": lista_eficientes,
            "lista_no_eficientes": lista_no_eficientes,
            "total_pendientes": len(lista_pendientes),
            "lista_pendientes": lista_pendientes,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/produccion/ordenes-en-proceso")
def get_ordenes_en_proceso():
    try:
        ef = get_eficiencia()
        return {
            "total": ef["total_pendientes"],
            "ordenes": ef["lista_pendientes"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/produccion/causas")
def get_causas():
    try:
        df = get_excel_data()['datos_generales']
        
        eficiencia_col = get_col_name(df, ['EFICIENCIA DE ENTREGA', 'EFICIENCIA'])
        op_col = get_col_name(df, ['ORDENES DE PRODUCCION', 'ORDEN', 'OP']) or (df.columns[0] if len(df.columns) > 0 else 'ORDEN')
        detalle_col = get_col_name(df, ['DETALLE', 'PRODUCTO', 'DESCRIPCION']) or 'DETALLE'
        cliente_col = get_col_name(df, ['CLIENTE']) or 'CLIENTE '
        dias_col = get_col_name(df, ['DIAS TOTAL DE ENTREGA', 'DIAS TOTAL', 'DIAS DE ENTREGA']) or 'DIAS TOTAL DE ENTREGA '
        obs_col = get_col_name(df, ['OBSERVACIONES', 'OBSERVACION', 'CAUSA']) or 'OBSERVACIONES'
        fact_col = get_col_name(df, ['FECHA DE FACTURACION', 'FECHA FACTURACION', 'FACTURACION', 'FECHA FACTURA'])
        mts_col = get_col_name(df, ['MTS PEDIDO', 'MTS PEDIDOS', 'METROS PEDIDO', 'MTS_PEDIDO', 'PEDIDO'])
        
        causas_dict = {
            "Falta de materia prima": [],
            "Materia prima dañada": [],
            "Demora en área específica": [],
            "Otra causa": []
        }
        
        valid_df = df[df[op_col].notna()].copy() if op_col in df.columns else df.copy()
        if op_col in valid_df.columns:
            valid_df = valid_df[
                ~valid_df[op_col].astype(str).str.strip().str.upper().isin(['STOCK', 'TOTAL', 'TOTALES']) &
                ~valid_df[op_col].astype(str).str.strip().str.upper().str.startswith('TOTAL')
            ].copy()

        tiene_facturacion = False
        if fact_col and fact_col in valid_df.columns:
            series_fact = valid_df[fact_col].dropna().astype(str).str.strip()
            tiene_facturacion = bool(((series_fact != '') & (~series_fact.str.upper().isin(['NAT', 'NAN']))).any())

        for _, row in valid_df.iterrows():
            op_val = safe_str(row.get(op_col, ''))
            if not op_val:
                continue

            fact_val = safe_str(row.get(fact_col)) if (fact_col and fact_col in valid_df.columns) else ''
            has_factura = bool(fact_val and fact_val.strip() != '' and fact_val.upper() not in ['NAN', 'NAT'])
            
            dias_tot = safe_int(row.get(dias_col, 0))
            mts_ped = safe_float(row.get(mts_col, 0.0)) if mts_col else 0.0
            dias_std, dias_extra = calcular_dias_estandar_entrega(mts_ped)
            
            es_no_eficiente = False
            if tiene_facturacion:
                # Solo evaluamos si está facturada y superó su plazo estándar ajustado
                if has_factura and dias_tot > dias_std:
                    es_no_eficiente = True
            else:
                # Fallback retrocompatible
                ef_val = safe_str(row.get(eficiencia_col)).upper() if (eficiencia_col and eficiencia_col in valid_df.columns) else ''
                if ef_val == 'NO EFICIENTE' or (dias_tot > dias_std and dias_tot > 0):
                    es_no_eficiente = True

            if not es_no_eficiente:
                continue

            dias_ret = max(0, dias_tot - dias_std) if dias_tot > 0 else 0
            obs = safe_str(row.get(obs_col, '')).lower()

            orden_data = {
                "op": op_val,
                "detalle": safe_str(row.get(detalle_col, '')),
                "cliente": safe_str(row.get(cliente_col, '')),
                "mts_pedido": mts_ped,
                "dias_estandar": dias_std,
                "dias_extra_metraje": dias_extra,
                "dias_entrega": dias_tot,
                "dias_retraso": dias_ret,
                "observacion": safe_str(row.get(obs_col, ''))
            }

            if any(k in obs for k in ['no habia material', 'falta de materia', 'no habia trama', 'no había', 'falta materia']):
                causas_dict["Falta de materia prima"].append(orden_data)
            elif any(k in obs for k in ['enred', 'mota', 'filamento', 'rebobinar', 'dañ', 'roto']):
                causas_dict["Materia prima dañada"].append(orden_data)
            elif any(k in obs for k in ['urdidora con carga', 'carga de trabajo', 'demora', 'retraso', 'se para', 'planch', 'calibracion', 'mantenimiento']):
                causas_dict["Demora en área específica"].append(orden_data)
            else:
                causas_dict["Otra causa"].append(orden_data)

        total_no_eficientes = sum(len(lst) for lst in causas_dict.values())
        
        causas_list = []
        for nombre, ordenes in causas_dict.items():
            pct = round((len(ordenes) / total_no_eficientes) * 100, 1) if total_no_eficientes > 0 else 0
            causas_list.append({
                "nombre": nombre,
                "cantidad": len(ordenes),
                "porcentaje": pct,
                "ordenes": ordenes
            })
        
        return {
            "causas": causas_list,
            "total_no_eficientes": total_no_eficientes,
            "regla_entrega": "20 días base + 1 día extra por cada 1,000m adicionales a partir de 6,500m (Turnos Día + Velada)",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/produccion/montaje")
def get_montaje():
    try:
        excel_data = get_excel_data()
        df = excel_data['montaje']
        orden_col = get_col_name(df, ['ORDEN', 'OP'])
        if not orden_col or orden_col not in df.columns:
            orden_col = df.columns[0] if len(df.columns) > 0 else 'ORDEN'
        
        # Filter out rows where ORDEN is NaN
        df_clean = df.dropna(subset=[orden_col]) if orden_col in df.columns else df.copy()
        
        # 1. Buscar columna de detalle/producto/nombre en la hoja MONTAJE
        det_col_montaje = get_col_name(df_clean, ['DETALLE', 'PRODUCTO', 'DESCRIPCION', 'NOMBRE', 'ARTICULO'])
        
        # Si no tiene nombre explícito, verificar si la segunda columna tiene texto descriptivo (ej. archivos nuevos tipo SEPTIEMBRE)
        if not det_col_montaje and len(df_clean.columns) > 1:
            c2 = df_clean.columns[1]
            c2_upper = str(c2).strip().upper()
            if not c2_upper.startswith('TOTAL'):
                vals = df_clean[c2].dropna().astype(str).str.strip()
                # Verificar si contiene cadenas de texto (letras) y no solo valores numéricos
                has_text = any(any(ch.isalpha() for ch in v) for v in vals[:10])
                if has_text:
                    det_col_montaje = c2

        # 2. Diccionario de respaldo desde DATOS GENERALES para compatibilidad con archivos anteriores (como Agosto y Julio)
        dict_datos = {}
        df_datos = excel_data.get('datos_generales')
        if df_datos is not None and len(df_datos) > 0:
            d_op_col = get_col_name(df_datos, ['ORDENES DE PRODUCCION', 'ORDEN', 'OP']) or df_datos.columns[0]
            d_det_col = get_col_name(df_datos, ['DETALLE', 'PRODUCTO', 'DESCRIPCION', 'ARTICULO'])
            if d_det_col and d_op_col in df_datos.columns:
                for _, r in df_datos.iterrows():
                    k = safe_str(r.get(d_op_col)).strip()
                    v = safe_str(r.get(d_det_col)).strip()
                    if k and v:
                        dict_datos[k.upper()] = v
                        dict_datos[' '.join(k.upper().split())] = v
                        ku_clean = re.sub(r'AGOS\b', 'AGO', k.upper())
                        dict_datos[ku_clean] = v
                        dict_datos[' '.join(ku_clean.split())] = v

        # Columnas a excluir al buscar operarios
        exclude_cols = {orden_col}
        if det_col_montaje:
            exclude_cols.add(det_col_montaje)

        # Identify operarios columns (exclude ORDEN, detalle column, UNNAMED, TOTAL and generic text labels)
        operarios_names = [
            c for c in df_clean.columns 
            if c not in exclude_cols 
            and not str(c).strip().upper().startswith(('UNNAMED', 'TOTAL'))
            and str(c).strip().upper() not in ['DETALLE', 'DESCRIPCION', 'NOMBRE', 'ARTICULO', 'PRODUCTO']
        ]
        
        operarios = []
        for op in operarios_names:
            col_data = df_clean[op].apply(pd.to_numeric, errors='coerce')
            total_tiras = safe_float(col_data.sum())
            ordenes_atendidas = int(col_data.notna().sum())
            
            operarios.append({
                "nombre": str(op).strip(),
                "total_tiras": total_tiras,
                "ordenes_atendidas": ordenes_atendidas
            })
        
        detalle_por_orden = []
        for _, row in df_clean.iterrows():
            orden_name = safe_str(row.get(orden_col, ''))
            if not orden_name:
                continue
            
            # Obtener nombre de la orden desde MONTAJE o desde DATOS GENERALES
            nombre_orden = ""
            if det_col_montaje:
                nombre_orden = safe_str(row.get(det_col_montaje, ''))
            if not nombre_orden:
                norm_key = ' '.join(orden_name.upper().split())
                norm_key_clean = re.sub(r'AGOS\b', 'AGO', norm_key)
                nombre_orden = dict_datos.get(norm_key, dict_datos.get(norm_key_clean, ''))
                if not nombre_orden:
                    nums = re.findall(r'\d+', norm_key)
                    mes = 'SEP' if 'SEP' in norm_key else ('AGO' if 'AGO' in norm_key else '')
                    if nums and mes:
                        for k, v in dict_datos.items():
                            if mes in k and any(n in re.findall(r'\d+', k) for n in nums):
                                nombre_orden = v
                                break

            row_dict = {
                "orden": orden_name,
                "nombre_orden": nombre_orden,
                "detalle": nombre_orden
            }
            for op in operarios_names:
                val = row.get(op)
                row_dict[str(op).strip()] = safe_float(val)
            detalle_por_orden.append(row_dict)
            
        return {
            "operarios": operarios,
            "detalle_por_orden": detalle_por_orden,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/produccion/calibracion")
def get_calibracion():
    try:
        excel_data = get_excel_data()
        data = excel_data.get('calibracion')
        if data is None or len(data) == 0:
            return {"calibradores": [], "total": 0, "detalle_por_orden": [], "status": "success"}

        calibradores = []
        total_calibraciones = 0
        detalle_por_orden = []

        # Detectar si es formato lista tradicional (Julio, Agosto, Septiembre) o formato matriz (Octubre en adelante)
        is_list_format = False
        start_row = 2
        for r in range(min(5, len(data))):
            row_str = " ".join([str(x).upper() for x in data.iloc[r] if pd.notna(x)])
            if "NOMBRE" in row_str or "NUMERO DE VECES" in row_str:
                is_list_format = True
                start_row = r + 1
                break

        if is_list_format:
            for i in range(start_row, len(data)):
                try:
                    first_cell = safe_str(data.iloc[i, 0]).upper()
                    second_cell = safe_str(data.iloc[i, 1]).upper()
                    if "TOTAL" in first_cell or "TOTAL" in second_cell:
                        total_val = safe_int(data.iloc[i, 2])
                        if total_val > 0:
                            total_calibraciones = total_val
                        break

                    nombre = safe_str(data.iloc[i, 1])
                    veces = safe_int(data.iloc[i, 2])
                    articulos = safe_str(data.iloc[i, 3])
                    if nombre and nombre.upper() != 'NAN':
                        calibradores.append({
                            "nombre": nombre,
                            "veces": veces,
                            "articulos": articulos
                        })
                        total_calibraciones += veces
                except IndexError:
                    pass
        else:
            # Formato Matriz (como en Montaje, donde las columnas son los calibradores)
            header_row = 0
            for r in range(min(5, len(data))):
                row_vals = [str(x).strip().upper() for x in data.iloc[r] if pd.notna(x)]
                if any('ORDEN' in x for x in row_vals):
                    header_row = r
                    break

            headers = data.iloc[header_row].tolist()
            # Identificar columnas de técnicos (omitir col 0=ORDEN, col 1=DETALLE/ARTICULO, UNNAMED, TOTAL)
            tech_cols = []
            for c in range(2, len(headers)):
                col_name = str(headers[c]).strip()
                if col_name and col_name.upper() != 'NAN' and not col_name.upper().startswith(('UNNAMED', 'TOTAL')):
                    tech_cols.append((c, col_name))

            df_data = data.iloc[header_row + 1:].copy()
            # Diccionario de respaldo de productos desde DATOS GENERALES
            dict_datos = {}
            df_datos = excel_data.get('datos_generales')
            if df_datos is not None and len(df_datos) > 0:
                d_op_col = get_col_name(df_datos, ['ORDENES DE PRODUCCION', 'ORDEN', 'OP']) or df_datos.columns[0]
                d_det_col = get_col_name(df_datos, ['DETALLE', 'PRODUCTO', 'DESCRIPCION', 'ARTICULO'])
                if d_det_col and d_op_col in df_datos.columns:
                    for _, r in df_datos.iterrows():
                        k = safe_str(r.get(d_op_col)).strip()
                        v = safe_str(r.get(d_det_col)).strip()
                        if k and v:
                            dict_datos[k.upper()] = v

            for col_idx, tech_name in tech_cols:
                veces_col = pd.to_numeric(df_data[col_idx], errors='coerce').fillna(0)
                veces = int(veces_col.sum())
                arts = []
                for row_idx, val in veces_col.items():
                    if val > 0:
                        art_val = safe_str(df_data.loc[row_idx, 1]).strip()
                        if not art_val:
                            op_code = safe_str(df_data.loc[row_idx, 0]).strip().upper()
                            art_val = dict_datos.get(op_code, '')
                        if art_val and art_val not in arts:
                            arts.append(art_val)
                art_str = ', '.join(arts) if arts else ''
                calibradores.append({
                    "nombre": tech_name,
                    "veces": veces,
                    "articulos": art_str
                })
                total_calibraciones += veces

            # Detalle por orden para calibración interactiva
            for _, row in df_data.iterrows():
                orden_name = safe_str(row.iloc[0]).strip()
                if not orden_name or orden_name.upper().startswith(('TOTAL', 'NAN', 'STOCK')):
                    continue
                art_name = safe_str(row.iloc[1]).strip() or dict_datos.get(orden_name.upper(), '')
                row_dict = {
                    "orden": orden_name,
                    "nombre_orden": art_name,
                    "detalle": art_name
                }
                has_any_calib = False
                for col_idx, tech_name in tech_cols:
                    v = safe_int(row.iloc[col_idx])
                    row_dict[tech_name] = v
                    if v > 0:
                        has_any_calib = True
                if has_any_calib:
                    detalle_por_orden.append(row_dict)

        return {
            "calibradores": calibradores,
            "total": total_calibraciones,
            "detalle_por_orden": detalle_por_orden,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== URDIDO (NUEVA FASE PRODUCTIVA) ====================

def parse_urdido_sheet(df_raw, df_datos_generales=None):
    if df_raw is None or len(df_raw) < 2:
        return {
            "disponible": False,
            "mensaje": "Este archivo no contiene hoja de URDIDO (disponible a partir de Septiembre 2026)",
            "totales": {
                "carretos": 0,
                "metros": 0.0,
                "registros": 0,
                "dias_activos": 0,
                "promedio_metros_dia": 0.0,
                "promedio_carretos_dia": 0.0
            },
            "por_turno": [],
            "por_operador": [],
            "operadores_consolidados": [],
            "top_articulos": [],
            "produccion_diaria": [],
            "novedades": [],
            "detalle": [],
            "status": "success"
        }

    idx_orden = 0
    idx_carretos = 1
    idx_metros = 2
    idx_color = 3
    idx_responsable = 4
    idx_articulo = 5
    idx_obs = 6

    # Diccionario de respaldo desde datos generales para clientes o detalles
    dict_clientes = {}
    dict_detalles = {}
    if df_datos_generales is not None and len(df_datos_generales) > 0:
        for _, r in df_datos_generales.iterrows():
            c0 = str(r.iloc[0]).strip().upper() if pd.notna(r.iloc[0]) else ""
            if c0 and c0 != 'STOCK' and not c0.startswith('TOTAL'):
                c0_clean = re.sub(r'AGOS\b', 'AGO', c0)
                for c in df_datos_generales.columns:
                    if 'CLIENTE' in str(c).upper() and pd.notna(r[c]):
                        val_cli = str(r[c]).strip()
                        dict_clientes[c0] = val_cli
                        dict_clientes[c0_clean] = val_cli
                    if 'DETALLE' in str(c).upper() and pd.notna(r[c]):
                        val_det = str(r[c]).strip()
                        dict_detalles[c0] = val_det
                        dict_detalles[c0_clean] = val_det

    current_fecha = ""
    registros = []
    novedades = []
    last_op = ""

    for r in range(1, len(df_raw)):
        val0 = df_raw.iloc[r, idx_orden]
        
        is_date = False
        if pd.notna(val0):
            val0_str = str(val0).strip()
            if isinstance(val0, (pd.Timestamp, )):
                current_fecha = val0.strftime("%Y-%m-%d")
                is_date = True
            elif any(char.isdigit() for char in val0_str) and ('/' in val0_str or '-' in val0_str) and not val0_str.upper().startswith('OP'):
                try:
                    dt = pd.to_datetime(val0_str, errors='coerce')
                    if pd.notna(dt):
                        current_fecha = dt.strftime("%Y-%m-%d")
                        is_date = True
                except:
                    pass
        else:
            val0_str = ""

        if is_date:
            continue

        if not val0_str:
            c_check = pd.to_numeric(df_raw.iloc[r, idx_carretos], errors='coerce')
            m_check = pd.to_numeric(df_raw.iloc[r, idx_metros], errors='coerce')
            r_check = str(df_raw.iloc[r, idx_responsable]).strip() if pd.notna(df_raw.iloc[r, idx_responsable]) else ""
            if (pd.notna(c_check) or pd.notna(m_check)) and r_check:
                val0_str = last_op
            else:
                continue
        else:
            val0_upper = val0_str.upper()
            if 'TOTAL' in val0_upper or val0_upper in ['N. ORDEN', 'ORDEN', 'FECHA']:
                continue
            last_op = val0_str

        carretos = pd.to_numeric(df_raw.iloc[r, idx_carretos], errors='coerce')
        metros = pd.to_numeric(df_raw.iloc[r, idx_metros], errors='coerce')
        color = str(df_raw.iloc[r, idx_color]).strip() if pd.notna(df_raw.iloc[r, idx_color]) else ""
        responsable = str(df_raw.iloc[r, idx_responsable]).strip() if pd.notna(df_raw.iloc[r, idx_responsable]) else ""
        articulo = str(df_raw.iloc[r, idx_articulo]).strip() if pd.notna(df_raw.iloc[r, idx_articulo]) else ""
        obs = str(df_raw.iloc[r, idx_obs]).strip() if pd.notna(df_raw.iloc[r, idx_obs]) else ""

        if articulo.upper() == 'ARTICULO' and pd.isna(metros) and pd.isna(carretos):
            continue

        carretos_val = float(carretos) if pd.notna(carretos) else 0.0
        metros_val = float(metros) if pd.notna(metros) else 0.0

        resp_upper = responsable.upper()
        if 'VELADA' in resp_upper or 'NOCHE' in resp_upper:
            turno = 'Velada'
        else:
            turno = 'Día'

        norm_op = val0_str.upper()
        norm_op_clean = re.sub(r'AGOS\b', 'AGO', norm_op)
        cliente = dict_clientes.get(norm_op, dict_clientes.get(norm_op_clean, ""))
        if not cliente:
            for k, v in dict_clientes.items():
                if norm_op in k or k in norm_op or norm_op_clean in k:
                    cliente = v
                    break

        art_clean = articulo if articulo.upper() != 'ARTICULO' else ''
        if not art_clean:
            art_clean = dict_detalles.get(norm_op, dict_detalles.get(norm_op_clean, ""))
            if not art_clean:
                for k, v in dict_detalles.items():
                    if norm_op in k or k in norm_op or norm_op_clean in k:
                        art_clean = v
                        break

        item = {
            "fecha": current_fecha,
            "orden": val0_str,
            "articulo": art_clean,
            "color": color,
            "carretos": carretos_val,
            "metros": metros_val,
            "responsable": responsable,
            "turno": turno,
            "cliente": cliente,
            "observacion": obs if obs.upper() != 'OBSERVACIONES' else ''
        }
        registros.append(item)

        if item["observacion"]:
            novedades.append({
                "fecha": current_fecha,
                "orden": val0_str,
                "responsable": responsable,
                "turno": turno,
                "articulo": item["articulo"],
                "observacion": item["observacion"]
            })

    total_carretos = sum(x["carretos"] for x in registros)
    total_metros = sum(x["metros"] for x in registros)
    total_registros = len(registros)
    fechas_unicas = sorted(list(set(x["fecha"] for x in registros if x["fecha"])))
    dias_activos = len(fechas_unicas)

    # Por Turno
    turnos_dict = {}
    for x in registros:
        t = x["turno"]
        if t not in turnos_dict:
            turnos_dict[t] = {"turno": t, "carretos": 0.0, "metros": 0.0, "registros": 0}
        turnos_dict[t]["carretos"] += x["carretos"]
        turnos_dict[t]["metros"] += x["metros"]
        turnos_dict[t]["registros"] += 1

    por_turno = []
    for t_name in ['Día', 'Velada']:
        if t_name in turnos_dict:
            td = turnos_dict[t_name]
            por_turno.append({
                "turno": t_name,
                "carretos": round(td["carretos"], 1),
                "metros": round(td["metros"], 1),
                "registros": td["registros"],
                "porcentaje_metros": round((td["metros"] / total_metros) * 100, 1) if total_metros > 0 else 0.0,
                "porcentaje_carretos": round((td["carretos"] / total_carretos) * 100, 1) if total_carretos > 0 else 0.0
            })

    # Por Operador / Responsable (exacto)
    resp_dict = {}
    for x in registros:
        r_name = x["responsable"] or "Sin Asignar"
        if r_name not in resp_dict:
            resp_dict[r_name] = {"nombre": r_name, "turno": x["turno"], "carretos": 0.0, "metros": 0.0, "registros": 0}
        resp_dict[r_name]["carretos"] += x["carretos"]
        resp_dict[r_name]["metros"] += x["metros"]
        resp_dict[r_name]["registros"] += 1

    por_operador = sorted(
        [
            {
                **v,
                "carretos": round(v["carretos"], 1),
                "metros": round(v["metros"], 1),
                "porcentaje_metros": round((v["metros"] / total_metros) * 100, 1) if total_metros > 0 else 0.0
            }
            for v in resp_dict.values()
        ],
        key=lambda x: x["metros"],
        reverse=True
    )

    # Operadores Consolidados (por persona: JUAN, ALEXANDER, BRYAN)
    def normalizar_persona(nombre_raw):
        n = nombre_raw.upper()
        if 'JUAN' in n and 'BRYAN' in n:
            return 'JUAN / BRYAN'
        if 'ALEXANDER' in n and 'BRYAN' in n:
            return 'ALEXANDER / BRYAN'
        if 'JUAN' in n:
            return 'JUAN'
        if 'ALEXANDER' in n:
            return 'ALEXANDER'
        if 'BRYAN' in n:
            return 'BRYAN'
        return nombre_raw.strip().title()

    cons_dict = {}
    for x in registros:
        p_name = normalizar_persona(x["responsable"] or "Sin Asignar")
        if p_name not in cons_dict:
            cons_dict[p_name] = {
                "nombre": p_name,
                "carretos": 0.0,
                "metros": 0.0,
                "registros": 0,
                "metros_dia": 0.0,
                "metros_velada": 0.0,
                "carretos_dia": 0.0,
                "carretos_velada": 0.0
            }
        cons_dict[p_name]["carretos"] += x["carretos"]
        cons_dict[p_name]["metros"] += x["metros"]
        cons_dict[p_name]["registros"] += 1
        if x["turno"] == 'Día':
            cons_dict[p_name]["metros_dia"] += x["metros"]
            cons_dict[p_name]["carretos_dia"] += x["carretos"]
        else:
            cons_dict[p_name]["metros_velada"] += x["metros"]
            cons_dict[p_name]["carretos_velada"] += x["carretos"]

    operadores_consolidados = sorted(
        [
            {
                "nombre": k,
                "carretos": round(v["carretos"], 1),
                "metros": round(v["metros"], 1),
                "registros": v["registros"],
                "metros_dia": round(v["metros_dia"], 1),
                "metros_velada": round(v["metros_velada"], 1),
                "carretos_dia": round(v["carretos_dia"], 1),
                "carretos_velada": round(v["carretos_velada"], 1),
                "porcentaje_carretos": round((v["carretos"] / total_carretos) * 100, 1) if total_carretos > 0 else 0.0,
                "porcentaje_metros": round((v["metros"] / total_metros) * 100, 1) if total_metros > 0 else 0.0
            }
            for k, v in cons_dict.items()
        ],
        key=lambda x: x["carretos"],
        reverse=True
    )

    # Top Artículos
    art_dict = {}
    for x in registros:
        art = x["articulo"] or "Sin Especificar"
        if art not in art_dict:
            art_dict[art] = {"articulo": art, "carretos": 0.0, "metros": 0.0, "registros": 0}
        art_dict[art]["carretos"] += x["carretos"]
        art_dict[art]["metros"] += x["metros"]
        art_dict[art]["registros"] += 1

    top_articulos = sorted(
        [
            {
                **v,
                "carretos": round(v["carretos"], 1),
                "metros": round(v["metros"], 1),
                "porcentaje_carretos": round((v["carretos"] / total_carretos) * 100, 1) if total_carretos > 0 else 0.0,
                "porcentaje_metros": round((v["metros"] / total_metros) * 100, 1) if total_metros > 0 else 0.0
            }
            for v in art_dict.values()
        ],
        key=lambda x: x["metros"],
        reverse=True
    )[:10]

    # Producción Diaria
    dias_dict = {}
    for x in registros:
        f = x["fecha"] or "Sin Fecha"
        if f not in dias_dict:
            dias_dict[f] = {
                "fecha": f,
                "carretos": 0.0,
                "metros": 0.0,
                "registros": 0,
                "metros_dia": 0.0,
                "metros_velada": 0.0,
                "carretos_dia": 0.0,
                "carretos_velada": 0.0
            }
        dias_dict[f]["carretos"] += x["carretos"]
        dias_dict[f]["metros"] += x["metros"]
        dias_dict[f]["registros"] += 1
        if x["turno"] == 'Día':
            dias_dict[f]["metros_dia"] += x["metros"]
            dias_dict[f]["carretos_dia"] += x["carretos"]
        else:
            dias_dict[f]["metros_velada"] += x["metros"]
            dias_dict[f]["carretos_velada"] += x["carretos"]

    produccion_diaria = [
        {
            "fecha": k,
            "carretos": round(v["carretos"], 1),
            "metros": round(v["metros"], 1),
            "registros": v["registros"],
            "metros_dia": round(v["metros_dia"], 1),
            "metros_velada": round(v["metros_velada"], 1),
            "carretos_dia": round(v["carretos_dia"], 1),
            "carretos_velada": round(v["carretos_velada"], 1)
        }
        for k, v in sorted(dias_dict.items())
    ]

    return {
        "disponible": True,
        "totales": {
            "carretos": round(total_carretos, 1),
            "metros": round(total_metros, 1),
            "registros": total_registros,
            "dias_activos": dias_activos,
            "promedio_metros_dia": round(total_metros / max(dias_activos, 1), 1),
            "promedio_carretos_dia": round(total_carretos / max(dias_activos, 1), 1)
        },
        "por_turno": por_turno,
        "por_operador": por_operador,
        "operadores_consolidados": operadores_consolidados,
        "top_articulos": top_articulos,
        "produccion_diaria": produccion_diaria,
        "novedades": novedades,
        "detalle": registros,
        "status": "success"
    }

@app.get("/api/produccion/urdido")
def get_urdido():
    try:
        excel_data = get_excel_data()
        df_urdido = excel_data.get('urdido')
        df_datos = excel_data.get('datos_generales')
        resultado = parse_urdido_sheet(df_urdido, df_datos)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ORDENES ACABADAS ====================

def parse_ordenes_acabadas_sheet(df_raw, df_datos=None):
    if df_raw is None or len(df_raw) == 0:
        return {
            'disponible': False,
            'totales': {
                'total_ordenes': 0,
                'dias_registrados': 0,
                'dias_con_produccion': 0,
                'promedio_dia': 0.0,
                'total_dia': 0,
                'total_velada': 0,
                'porcentaje_dia': 0.0,
                'porcentaje_velada': 0.0,
                'dia_record': None
            },
            'por_dia': [],
            'novedades_destacadas': [],
            'status': 'not_available'
        }

    # Detectar fila de cabeceras
    header_idx = None
    for r in range(min(15, len(df_raw))):
        vals = [str(x).upper() for x in df_raw.iloc[r] if pd.notna(x)]
        if 'FECHA' in vals and any(k in vals for k in ['ORDEN', 'TURNO', 'ARTICULO']):
            header_idx = r
            break

    if header_idx is None:
        return {
            'disponible': False,
            'totales': {
                'total_ordenes': 0,
                'dias_registrados': 0,
                'dias_con_produccion': 0,
                'promedio_dia': 0.0,
                'total_dia': 0,
                'total_velada': 0,
                'porcentaje_dia': 0.0,
                'porcentaje_velada': 0.0,
                'dia_record': None
            },
            'por_dia': [],
            'novedades_destacadas': [],
            'status': 'header_not_found'
        }

    cols = [str(c).strip().upper() if pd.notna(c) else f'COL_{i}' for i, c in enumerate(df_raw.iloc[header_idx])]
    col_map = {}
    for i, c in enumerate(cols):
        if 'FECHA' in c: col_map['fecha'] = i
        elif 'TURNO' in c: col_map['turno'] = i
        elif 'ORDEN' in c or 'OP' in c: col_map['orden'] = i
        elif any(k in c for k in ['ARTICULO', 'DETALLE', 'PRODUCTO']): col_map['articulo'] = i
        elif any(k in c for k in ['OBSERV', 'NOTA', 'NOVEDAD']): col_map['observaciones'] = i

    if 'fecha' not in col_map: col_map['fecha'] = 0
    if 'turno' not in col_map and len(cols) > 1: col_map['turno'] = 1
    if 'orden' not in col_map and len(cols) > 2: col_map['orden'] = 2
    if 'articulo' not in col_map and len(cols) > 3: col_map['articulo'] = 3
    if 'observaciones' not in col_map and len(cols) > 4: col_map['observaciones'] = 4

    articulos_catalogo = {}
    if df_datos is not None and not df_datos.empty:
        op_col = None
        art_col = None
        for c in df_datos.columns:
            cn = str(c).upper()
            if 'ORDEN' in cn or 'OP' in cn: op_col = c
            if any(k in cn for k in ['DETALLE', 'PRODUCTO', 'ARTICULO']): art_col = c
        if op_col and art_col:
            for _, row_dg in df_datos.iterrows():
                o_val = str(row_dg[op_col]).strip().upper() if pd.notna(row_dg[op_col]) else ''
                a_val = str(row_dg[art_col]).strip() if pd.notna(row_dg[art_col]) else ''
                if o_val and a_val and o_val not in articulos_catalogo:
                    articulos_catalogo[o_val] = a_val

    dias_esp = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    meses_esp = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}

    dias_dict = {}
    current_date = None
    current_turno = 'Velada'
    novedades_destacadas = []

    for r in range(header_idx + 1, len(df_raw)):
        row = df_raw.iloc[r]
        raw_fecha = row[col_map['fecha']] if 'fecha' in col_map else None

        if pd.notna(raw_fecha) and str(raw_fecha).strip() not in ['', 'nan', 'None']:
            try:
                dt = pd.to_datetime(raw_fecha)
                current_date = dt.strftime('%Y-%m-%d')
                dia_sem = dias_esp.get(dt.weekday(), '')
                m_str = meses_esp.get(dt.month, '')
                fecha_corta = f"{dt.day} {m_str}"
            except:
                current_date = str(raw_fecha).strip()
                dia_sem = ''
                fecha_corta = current_date

            if current_date not in dias_dict:
                dias_dict[current_date] = {
                    'fecha': current_date,
                    'fecha_corta': fecha_corta,
                    'dia_semana': dia_sem,
                    'total_ordenes': 0,
                    'ordenes_dia': 0,
                    'ordenes_velada': 0,
                    'sin_ordenes': False,
                    'observaciones_dia': [],
                    'ordenes': []
                }

        if not current_date:
            continue

        raw_turno = row[col_map['turno']] if 'turno' in col_map else None
        if pd.notna(raw_turno) and str(raw_turno).strip() not in ['', 'nan', 'None']:
            t_str = str(raw_turno).strip().upper()
            if 'NO HAY' in t_str or 'SIN ORDEN' in t_str or 'NINGUNA' in t_str:
                dias_dict[current_date]['sin_ordenes'] = True
                current_turno = 'Sin órdenes'
            elif 'DIA' in t_str:
                current_turno = 'Día'
            elif 'VELADA' in t_str:
                current_turno = 'Velada'
            else:
                current_turno = str(raw_turno).strip()

        raw_orden = row[col_map['orden']] if 'orden' in col_map else None
        raw_art = row[col_map['articulo']] if 'articulo' in col_map else None
        raw_obs = row[col_map['observaciones']] if 'observaciones' in col_map else None

        orden_val = str(raw_orden).strip() if pd.notna(raw_orden) else ''
        art_val = str(raw_art).strip() if pd.notna(raw_art) else ''
        obs_val = str(raw_obs).strip() if pd.notna(raw_obs) else ''

        if obs_val.upper() in ['NAN', 'NONE']: obs_val = ''
        if orden_val.upper() in ['NAN', 'NONE', '-']: orden_val = ''

        if obs_val and not orden_val:
            dias_dict[current_date]['observaciones_dia'].append(obs_val)
            novedades_destacadas.append({
                'fecha': current_date,
                'fecha_corta': dias_dict[current_date]['fecha_corta'],
                'tipo': 'dia_general',
                'orden': None,
                'observacion': obs_val
            })

        if orden_val:
            if not art_val:
                art_val = articulos_catalogo.get(orden_val.upper(), '')

            turno_orden = current_turno if current_turno != 'Sin órdenes' else 'Velada'
            item = {
                'orden': orden_val,
                'articulo': art_val,
                'turno': turno_orden,
                'observaciones': obs_val
            }
            dias_dict[current_date]['ordenes'].append(item)
            dias_dict[current_date]['total_ordenes'] += 1
            if turno_orden == 'Día':
                dias_dict[current_date]['ordenes_dia'] += 1
            else:
                dias_dict[current_date]['ordenes_velada'] += 1

            if obs_val:
                novedades_destacadas.append({
                    'fecha': current_date,
                    'fecha_corta': dias_dict[current_date]['fecha_corta'],
                    'tipo': 'orden_especifica',
                    'orden': orden_val,
                    'articulo': art_val,
                    'observacion': obs_val
                })

    por_dia = sorted(list(dias_dict.values()), key=lambda x: x['fecha'])
    total_ordenes = sum(d['total_ordenes'] for d in por_dia)
    total_dia = sum(d['ordenes_dia'] for d in por_dia)
    total_velada = sum(d['ordenes_velada'] for d in por_dia)
    dias_registrados = len(por_dia)
    dias_con_produccion = sum(1 for d in por_dia if d['total_ordenes'] > 0)
    promedio_dia = round(total_ordenes / max(dias_registrados, 1), 1)
    pct_dia = round((total_dia / total_ordenes) * 100, 1) if total_ordenes > 0 else 0.0
    pct_velada = round((total_velada / total_ordenes) * 100, 1) if total_ordenes > 0 else 0.0

    dia_record = None
    if por_dia:
        mejor_dia = max(por_dia, key=lambda x: x['total_ordenes'])
        if mejor_dia['total_ordenes'] > 0:
            dia_record = {
                'fecha': mejor_dia['fecha'],
                'fecha_corta': mejor_dia['fecha_corta'],
                'dia_semana': mejor_dia['dia_semana'],
                'total_ordenes': mejor_dia['total_ordenes']
            }

    return {
        'disponible': True,
        'totales': {
            'total_ordenes': total_ordenes,
            'dias_registrados': dias_registrados,
            'dias_con_produccion': dias_con_produccion,
            'promedio_dia': promedio_dia,
            'total_dia': total_dia,
            'total_velada': total_velada,
            'porcentaje_dia': pct_dia,
            'porcentaje_velada': pct_velada,
            'dia_record': dia_record
        },
        'por_dia': por_dia,
        'novedades_destacadas': novedades_destacadas,
        'status': 'success'
    }

@app.get("/api/produccion/ordenes-acabadas")
def get_ordenes_acabadas():
    try:
        excel_data = get_excel_data()
        df_acabadas = excel_data.get('ordenes_acabadas')
        df_datos = excel_data.get('datos_generales')
        resultado = parse_ordenes_acabadas_sheet(df_acabadas, df_datos)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))