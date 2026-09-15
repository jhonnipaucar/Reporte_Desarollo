from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import logging
import shutil

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

current_excel_path = BASE_DIR / 'AGOSTO 2026.xlsx'

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
        
        df_datos = read_sheet_smart(xls, datos_gen_sheet, ['ORDEN', 'DETALLE', 'ESTADO', 'PRODUCTO', 'EFICIENCIA'])
        df_montaje = read_sheet_smart(xls, montaje_sheet, ['ORDEN', 'OP'])
        df_calibracion = pd.read_excel(xls, sheet_name=calibracion_sheet, header=None)
        df_resumen = pd.read_excel(xls, sheet_name=resumen_sheet, header=None) if resumen_sheet else None
    
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
        if op_col and any(m in str(op_col).upper() for m in ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']):
            titulo = f"CONTROL DE PRODUCCIÓN - {str(op_col).strip()}"
        else:
            titulo = f"CONTROL DE PRODUCCIÓN - {file_path.stem}"
                    
    return {
        'resumen': df_resumen,
        'datos_generales': df_datos,
        'montaje': df_montaje,
        'calibracion': df_calibracion,
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
    
    # 1. Archivo base default si existe
    default_file = BASE_DIR / 'AGOSTO 2026.xlsx'
    if default_file.exists():
        archivos.append({
            "filename": default_file.name,
            "es_activo": current_excel_path.resolve() == default_file.resolve(),
            "tamano_kb": round(default_file.stat().st_size / 1024, 1),
            "fecha": pd.to_datetime(default_file.stat().st_mtime, unit='s').strftime("%Y-%m-%d %H:%M")
        })
    
    # 2. Archivos subidos en uploads
    if UPLOADS_DIR.exists():
        for f in sorted(UPLOADS_DIR.glob("*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.name != default_file.name:
                archivos.append({
                    "filename": f.name,
                    "es_activo": current_excel_path.resolve() == f.resolve(),
                    "tamano_kb": round(f.stat().st_size / 1024, 1),
                    "fecha": pd.to_datetime(f.stat().st_mtime, unit='s').strftime("%Y-%m-%d %H:%M")
                })
                
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

# ==================== ENDPOINTS DE MÉTRICAS ====================

def calcular_metricas_resumen(data):
    df_resumen = data.get('resumen')
    df_datos = data['datos_generales']
    
    op_col = get_col_name(df_datos, ['ORDENES DE PRODUCCION', 'ORDEN', 'OP'])
    if not op_col or op_col not in df_datos.columns:
        op_col = df_datos.columns[0] if len(df_datos.columns) > 0 else 'ORDEN'
        
    valid_df = df_datos[df_datos[op_col].notna()].copy() if op_col in df_datos.columns else df_datos.copy()
    
    # Si existe hoja RESUMEN y tiene datos válidos en fila 4 (compatibilidad histórica)
    if df_resumen is not None and len(df_resumen) > 4 and pd.notna(df_resumen.iloc[4, 2]):
        totales = safe_int(df_resumen.iloc[4, 2])
        terminadas = safe_int(df_resumen.iloc[4, 3])
        tejeduria = safe_int(df_resumen.iloc[4, 4])
        acabados = safe_int(df_resumen.iloc[4, 5])
        eficientes = safe_int(df_resumen.iloc[4, 6])
        no_eficientes = safe_int(df_resumen.iloc[4, 7])
        origen = "hoja_resumen_excel"
    else:
        # CÁLCULO AUTOMÁTICO DESDE DATOS GENERALES (Formato moderno de 3 libros)
        totales = len(valid_df)
        estado_col = get_col_name(df_datos, ['ESTADO'])
        if estado_col and estado_col in valid_df.columns:
            estados = valid_df[estado_col].fillna('').astype(str).str.strip().str.upper()
            terminadas = int(estados.str.contains('TERMINAD').sum())
            tejeduria = int(estados.str.contains('TEJEDUR|MAQUIN').sum())
            acabados = int(estados.str.contains('ACABAD').sum())
        else:
            terminadas = 0
            tejeduria = 0
            acabados = 0
        
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
        
        eficientes = metricas["eficientes"]
        no_eficientes = metricas["no_eficientes"]
        total = eficientes + no_eficientes
        
        pct_eficiente = round((eficientes / total) * 100, 1) if total > 0 else 0
        pct_no_eficiente = round((no_eficientes / total) * 100, 1) if total > 0 else 0
        
        df = data.get('datos_generales')
        lista_eficientes = []
        lista_no_eficientes = []
        
        if df is not None and len(df) > 0:
            eficiencia_col = get_col_name(df, ['EFICIENCIA DE ENTREGA', 'EFICIENCIA'])
            op_col = get_col_name(df, ['ORDENES DE PRODUCCION', 'ORDEN', 'OP']) or (df.columns[0] if len(df.columns) > 0 else 'ORDEN')
            detalle_col = get_col_name(df, ['DETALLE', 'PRODUCTO', 'DESCRIPCION']) or 'DETALLE'
            cliente_col = get_col_name(df, ['CLIENTE']) or 'CLIENTE '
            dias_col = get_col_name(df, ['DIAS TOTAL DE ENTREGA', 'DIAS TOTAL', 'DIAS DE ENTREGA']) or 'DIAS TOTAL DE ENTREGA '
            obs_col = get_col_name(df, ['OBSERVACIONES', 'OBSERVACION', 'CAUSA']) or 'OBSERVACIONES'
            
            valid_df = df[df[op_col].notna()].copy() if op_col in df.columns else df.copy()
            
            if eficiencia_col and eficiencia_col in valid_df.columns:
                for _, row in valid_df.iterrows():
                    ef_val = safe_str(row.get(eficiencia_col)).upper()
                    item = {
                        "op": safe_str(row.get(op_col)),
                        "detalle": safe_str(row.get(detalle_col)),
                        "cliente": safe_str(row.get(cliente_col)),
                        "dias_entrega": safe_int(row.get(dias_col)),
                        "observacion": safe_str(row.get(obs_col))
                    }
                    if ef_val == 'EFICIENTE':
                        lista_eficientes.append(item)
                    elif ef_val == 'NO EFICIENTE':
                        lista_no_eficientes.append(item)
        
        return {
            "eficientes": eficientes,
            "no_eficientes": no_eficientes,
            "total_evaluadas": total,
            "porcentaje_eficiente": pct_eficiente,
            "porcentaje_no_eficiente": pct_no_eficiente,
            "origen_calculo": metricas["origen_calculo"],
            "lista_eficientes": lista_eficientes,
            "lista_no_eficientes": lista_no_eficientes,
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
        
        # Filter for NO EFICIENTE
        if eficiencia_col and eficiencia_col in df.columns:
            df_no_eficiente = df[df[eficiencia_col].astype(str).str.strip().str.upper() == 'NO EFICIENTE']
        else:
            df_no_eficiente = pd.DataFrame()
        
        causas_dict = {
            "Falta de materia prima": [],
            "Materia prima dañada": [],
            "Demora en área específica": [],
            "Otra causa": []
        }
        
        for _, row in df_no_eficiente.iterrows():
            obs = safe_str(row.get(obs_col, '')).lower()
            
            orden_data = {
                "op": safe_str(row.get(op_col, '')),
                "detalle": safe_str(row.get(detalle_col, '')),
                "cliente": safe_str(row.get(cliente_col, '')),
                "dias_entrega": safe_int(row.get(dias_col, 0)),
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
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/produccion/montaje")
def get_montaje():
    try:
        df = get_excel_data()['montaje']
        orden_col = get_col_name(df, ['ORDEN', 'OP'])
        if not orden_col or orden_col not in df.columns:
            orden_col = df.columns[0] if len(df.columns) > 0 else 'ORDEN'
        
        # Filter out rows where ORDEN is NaN
        df_clean = df.dropna(subset=[orden_col]) if orden_col in df.columns else df.copy()
        
        # Identify operarios columns (exclude ORDEN and any column starting with UNNAMED or TOTAL)
        operarios_names = [
            c for c in df_clean.columns 
            if c != orden_col and not str(c).strip().upper().startswith(('UNNAMED', 'TOTAL'))
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
            
            row_dict = {"orden": orden_name}
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
        data = get_excel_data()['calibracion']
        calibradores = []
        total_calibraciones = 0
        
        # Find start row (row after headers like 'NOMBRE', 'NUMERO DE VECES')
        start_row = 2
        for r in range(min(5, len(data))):
            row_str = " ".join([str(x).upper() for x in data.iloc[r] if pd.notna(x)])
            if "NOMBRE" in row_str or "NUMERO DE VECES" in row_str:
                start_row = r + 1
                break
                
        for i in range(start_row, len(data)):
            try:
                # If first column contains 'TOTAL'
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
                if nombre:
                    calibradores.append({
                        "nombre": nombre,
                        "veces": veces,
                        "articulos": articulos
                    })
                    total_calibraciones += veces
            except IndexError:
                pass
                
        return {
            "calibradores": calibradores,
            "total": total_calibraciones,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))