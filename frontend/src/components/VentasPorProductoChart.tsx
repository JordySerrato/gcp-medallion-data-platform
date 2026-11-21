
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
  obtenerVentasProductos,
  type VentaProducto,
} from '../services/ventasService'

// ==========================================
// 1. COMPONENTE DE VENTAS POR PRODUCTO
// ==========================================

function VentasPorProductoChart() {

  const [productos, setProductos] = useState<VentaProducto[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // ==========================================
  // 2. CONSULTAR DATOS DESDE FASTAPI
  // ==========================================

  useEffect(() => {
    let activo = true

    async function cargarProductos() {
      try {
        setCargando(true)
        setError(null)

        const respuesta = await obtenerVentasProductos()

        if (activo) {
          setProductos(respuesta.productos)
        }

      } catch (err) {
        if (activo) {
          setError(
            err instanceof Error
              ? err.message
              : 'No se pudieron cargar los productos'
          )
        }

      } finally {
        if (activo) {
          setCargando(false)
        }
      }
    }

    cargarProductos()

    return () => {
      activo = false
    }
  }, [])

  // ==========================================
  // 3. PREPARAR DATOS PARA RECHARTS
  // ==========================================

  const datosGrafico = productos.map((producto) => ({
    producto: producto.producto,
    ventas: Number(producto.ventas_totales),
  }))

  // ==========================================
  // 4. ESTADOS DE LA INTERFAZ
  // ==========================================

  if (cargando) {
    return <p>Cargando ventas por producto...</p>
  }

  if (error) {
    return <p role="alert">Error: {error}</p>
  }

  if (datosGrafico.length === 0) {
    return <p>No hay ventas por producto disponibles.</p>
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
          dataKey="producto"
          stroke="#94a3b8"
          tick={{ fontSize: 11 }}
          interval={0}
          angle={-25}
          textAnchor="end"
          height={55}
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
          fill="#10b981"
          radius={[6, 6, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default VentasPorProductoChart
