
import { useEffect, useState } from 'react'

import {
  obtenerEjecucionesPipeline,
  type EjecucionPipeline,
} from '../services/pipelineService'

// ==========================================
// 1. ETAPAS DEL PIPELINE
// ==========================================

const ETAPAS = [
  { clave: 'external_to_landing', nombre: 'External → Landing' },
  { clave: 'landing_to_bronze', nombre: 'Landing → Bronze' },
  { clave: 'bronze_to_silver', nombre: 'Bronze → Silver' },
  { clave: 'silver_to_gold', nombre: 'Silver → Gold' },
]

// ==========================================
// 2. FORMATEAR FECHAS
// ==========================================

function formatearFecha(fecha: string | null): string {
  if (!fecha) {
    return 'Sin registrar'
  }

  return new Date(fecha).toLocaleString('es-PE', {
    timeZone: 'America/Lima',
    dateStyle: 'short',
    timeStyle: 'medium',
  })
}

// ==========================================
// 3. COMPONENTE DE MONITOREO
// ==========================================

function PipelineMonitor() {

  const [ejecucion, setEjecucion] = useState<EjecucionPipeline | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // ==========================================
  // 4. CONSULTAR FIRESTORE MEDIANTE FASTAPI
  // ==========================================

  useEffect(() => {
    let activo = true

    async function cargarPipeline() {
      try {
        setCargando(true)
        setError(null)

        const respuesta = await obtenerEjecucionesPipeline()

        if (activo) {
          setEjecucion(respuesta.ejecuciones[0] ?? null)
        }

      } catch (err) {
        if (activo) {
          setError(
            err instanceof Error
              ? err.message
              : 'No se pudo consultar el pipeline'
          )
        }

      } finally {
        if (activo) {
          setCargando(false)
        }
      }
    }

    cargarPipeline()

    return () => {
      activo = false
    }
  }, [])

  // ==========================================
  // 5. ESTADOS DE LA INTERFAZ
  // ==========================================

  if (cargando) {
    return <p>Cargando información del pipeline...</p>
  }

  if (error) {
    return <p role="alert">Error: {error}</p>
  }

  if (!ejecucion) {
    return <p>No hay ejecuciones registradas en Firestore.</p>
  }

  // ==========================================
  // 6. MOSTRAR EJECUCIÓN
  // ==========================================

  return (
    <div className="pipeline-monitor">

      <div className="pipeline-header">
        <div>
          <h3>{ejecucion.pipeline}</h3>
          <p>Última ejecución registrada</p>
        </div>

        <span className={`pipeline-status ${ejecucion.estado.toLowerCase()}`}>
          {ejecucion.estado}
        </span>
      </div>

      <div className="pipeline-info">
        <p>
          <strong>ID:</strong> {ejecucion.id}
        </p>

        <p>
          <strong>Inicio:</strong> {formatearFecha(ejecucion.fecha_inicio)}
        </p>

        <p>
          <strong>Fin:</strong> {formatearFecha(ejecucion.fecha_fin)}
        </p>
      </div>

      <h4>Estado de las etapas</h4>

      <div className="pipeline-stages">

        {ETAPAS.map((etapa) => {
          const datos = ejecucion.etapas?.[etapa.clave]

          return (
            <div className="pipeline-stage" key={etapa.clave}>

              <span className="stage-name">
                {etapa.nombre}
              </span>

              <span className={`stage-status ${(datos?.estado ?? 'pending').toLowerCase()}`}>
                {datos?.estado ?? 'PENDING'}
              </span>

            </div>
          )
        })}

      </div>

      {ejecucion.error && (
        <p role="alert" className="pipeline-error">
          <strong>Error:</strong> {ejecucion.error}
        </p>
      )}

    </div>
  )
}

export default PipelineMonitor
