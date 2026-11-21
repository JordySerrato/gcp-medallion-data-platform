
/* ==========================================
   SERVICIO DE MONITOREO DEL PIPELINE
========================================== */

// Información de cada etapa del pipeline
export interface EtapaPipeline {
  estado: string
  fecha_inicio: string | null
  fecha_fin: string | null
}

// Información de una ejecución completa
export interface EjecucionPipeline {
  id: string
  pipeline: string
  estado: string
  etapa_actual: string | null
  error: string | null
  fecha_inicio: string
  fecha_fin: string | null
  etapas: Record<string, EtapaPipeline>
}

// Respuesta de FastAPI
export interface RespuestaEjecuciones {
  total_ejecuciones: number
  ejecuciones: EjecucionPipeline[]
}

// Consultar historial del pipeline
export async function obtenerEjecucionesPipeline(): Promise<RespuestaEjecuciones> {

  const respuesta = await fetch('/api/pipeline/ejecuciones')

  if (!respuesta.ok) {
    throw new Error(
      `Error al consultar ejecuciones: ${respuesta.status}`
    )
  }

  const datos: RespuestaEjecuciones = await respuesta.json()

  return datos
}
