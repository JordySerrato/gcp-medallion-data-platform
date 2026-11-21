
import { useEffect, useState } from 'react'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

import {
  obtenerVentasTiendas,
  type VentaTienda,
} from '../services/ventasService'

// ==========================================
// 1. COMPONENTE DE VENTAS POR TIENDA
// ==========================================

function VentasPorTiendaChart() {

  const [tiendas, setTiendas] = useState<VentaTienda[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // ==========================================
  // 2. CONSULTAR DATOS DESDE FASTAPI
  // ==========================================

  useEffect(() => {
    let activo = true

    async function cargarVentas() {
      try {
        setCargando(true)
        setError(null)

        const respuesta = await obtenerVentasTiendas()

        if (activo) {
          setTiendas(respuesta.tiendas)
        }

      } catch (err) {
        if (activo) {
          setError(
            err instanceof Error
              ? err.message
              : 'No se pudieron cargar las ventas'
          )
        }

      } finally {
        if (activo) {
          setCargando(false)
        }
      }
    }

    cargarVentas()

    return () => {
      activo = false
    }
  }, [])

  // ==========================================
  // 3. PREPARAR DATOS PARA RECHARTS
  // ==========================================

  const datosGrafico = tiendas.map((tienda) => ({
    tienda: tienda.tienda,
    ventas: Number(tienda.ventas_totales),
  }))

  // ==========================================
  // 4. ESTADOS DE LA INTERFAZ
  // ==========================================

  if (cargando) {
    return <p>Cargando ventas por tienda...</p>
  }

  if (error) {
    return <p role="alert">Error: {error}</p>
  }

  if (datosGrafico.length === 0) {
    return <p>No hay ventas disponibles.</p>
  }

  // ==========================================
  // 5. GRAFICO DE BARRAS
  // ==========================================

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart
        data={datosGrafico}
        margin={{ top: 10, right: 10, left: 0, bottom: 5 }}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="#334155"
        />

        <XAxis
          dataKey="tienda"
          stroke="#94a3b8"
          tick={{ fontSize: 12 }}
        />

        <YAxis
          stroke="#94a3b8"
          tick={{ fontSize: 12 }}
        />

        <Tooltip
          formatter={(valor) =>
            `S/ ${Number(valor).toFixed(2)}`
          }
        />

        <Bar
          dataKey="ventas"
          name="Ventas"
          fill="#3b82f6"
          radius={[6, 6, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default VentasPorTiendaChart
