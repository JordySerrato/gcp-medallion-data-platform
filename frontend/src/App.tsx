import { useEffect, useState } from 'react'

import {
  obtenerResumenVentas,
  type ResumenVentas,
} from './services/ventasService'

import VentasPorTiendaChart from './components/VentasPorTiendaChart'
import VentasPorProductoChart from './components/VentasPorProductoChart'
import VentasPorCategoriaChart from './components/VentasPorCategoriaChart'
import PipelineMonitor from './components/PipelineMonitor'
import './App.css'

function App() {
  // Aquí continúa tu código existente
  // ==========================================
  // 1. ESTADOS
  // ==========================================

  const [resumen, setResumen] = useState<ResumenVentas | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // ==========================================
  // 2. CONSULTAR DATOS DESDE FASTAPI
  // ==========================================

  useEffect(() => {
    let activo = true

    async function cargarResumen() {
      try {
        setCargando(true)
        setError(null)

        const datos = await obtenerResumenVentas()

        if (activo) {
          setResumen(datos)
        }

      } catch (err) {
        if (activo) {
          setError(
            err instanceof Error
              ? err.message
              : 'No se pudo cargar el resumen de ventas'
          )
        }

      } finally {
        if (activo) {
          setCargando(false)
        }
      }
    }

    cargarResumen()

    return () => {
      activo = false
    }
  }, [])

  // ==========================================
  // 3. INTERFAZ DEL DASHBOARD
  // ==========================================

  return (
    <main className="dashboard">

      {/* ENCABEZADO */}
      <header className="dashboard-header">
        <div>
          <h1>GCP Medallion Data Platform</h1>
          <p>Dashboard de analítica y monitoreo de datos</p>
        </div>
      </header>

      {/* INDICADORES GENERALES */}
      <section className="dashboard-section">
        <h2>Indicadores generales</h2>

        {error && (
          <p role="alert">
            Error al cargar los indicadores: {error}
          </p>
        )}

        <div className="metrics-grid">

          <article className="metric-card">
            <h3>Ventas totales</h3>
            <p>
              {cargando
                ? 'Cargando...'
                : resumen
                  ? `S/ ${Number(resumen.ventas_totales).toFixed(2)}`
                  : '—'}
            </p>
          </article>

          <article className="metric-card">
            <h3>Transacciones</h3>
            <p>
              {cargando
                ? 'Cargando...'
                : resumen?.total_transacciones ?? '—'}
            </p>
          </article>

          <article className="metric-card">
            <h3>Tiendas</h3>
            <p>
              {cargando
                ? 'Cargando...'
                : resumen?.total_tiendas ?? '—'}
            </p>
          </article>

          <article className="metric-card">
            <h3>Productos</h3>
            <p>
              {cargando
                ? 'Cargando...'
                : resumen?.total_productos ?? '—'}
            </p>
          </article>

        </div>
      </section>

      {/* ANALITICA GOLD */}
      <section className="dashboard-section">
        <h2>Análisis de ventas — Gold</h2>

        <div className="charts-grid">


          <article className="chart-card">
            <h3>Ventas por tienda</h3>
            <VentasPorTiendaChart />
          </article>



          <article className="chart-card">
            <h3>Ventas por producto</h3>
            <VentasPorProductoChart />
          </article>



          <article className="chart-card">
            <h3>Ventas por categoría</h3>
            <VentasPorCategoriaChart />
          </article>


        </div>
      </section>

      {/* MONITOREO DEL PIPELINE */}
      <section className="dashboard-section">
        <h2>Monitoreo del pipeline Medallion</h2>

        <article className="pipeline-card">
          <PipelineMonitor />
        </article>
      </section>

    </main>
  )
}

export default App
