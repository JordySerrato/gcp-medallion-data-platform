
import { useEffect, useState } from 'react'

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

import {
  obtenerVentasCategorias,
  type VentaCategoria,
} from '../services/ventasService'

// ==========================================
// 1. COLORES DEL GRÁFICO
// ==========================================

const COLORES = ['#8b5cf6', '#f59e0b', '#10b981', '#3b82f6']

// ==========================================
// 2. COMPONENTE DE VENTAS POR CATEGORÍA
// ==========================================

function VentasPorCategoriaChart() {

  const [categorias, setCategorias] = useState<VentaCategoria[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // ==========================================
  // 3. CONSULTAR DATOS DESDE FASTAPI
  // ==========================================

  useEffect(() => {
    let activo = true

    async function cargarCategorias() {
      try {
        setCargando(true)
        setError(null)

        const respuesta = await obtenerVentasCategorias()

        if (activo) {
          setCategorias(respuesta.categorias)
        }

      } catch (err) {
        if (activo) {
          setError(
            err instanceof Error
              ? err.message
              : 'No se pudieron cargar las categorías'
          )
        }

      } finally {
        if (activo) {
          setCargando(false)
        }
      }
    }

    cargarCategorias()

    return () => {
      activo = false
    }
  }, [])

  // ==========================================
  // 4. PREPARAR DATOS PARA RECHARTS
  // ==========================================

  const datosGrafico = categorias.map((categoria) => ({
    categoria: categoria.categoria,
    ventas: Number(categoria.ventas_totales),
  }))

  // ==========================================
  // 5. ESTADOS DE LA INTERFAZ
  // ==========================================

  if (cargando) {
    return <p>Cargando ventas por categoría...</p>
  }

  if (error) {
    return <p role="alert">Error: {error}</p>
  }

  if (datosGrafico.length === 0) {
    return <p>No hay ventas por categoría disponibles.</p>
  }

  // ==========================================
  // 6. GRÁFICO CIRCULAR
  // ==========================================

  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie
          data={datosGrafico}
          dataKey="ventas"
          nameKey="categoria"
          cx="50%"
          cy="45%"
          outerRadius={75}
          labelLine={false}
        >
          {datosGrafico.map((categoria, index) => (
            <Cell
              key={categoria.categoria}
              fill={COLORES[index % COLORES.length]}
            />
          ))}
        </Pie>

        <Tooltip
          formatter={(valor) =>
            `S/ ${Number(valor).toFixed(2)}`
          }
        />

        <Legend
          verticalAlign="bottom"
          iconType="circle"
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

export default VentasPorCategoriaChart
