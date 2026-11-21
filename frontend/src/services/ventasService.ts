
/* ==========================================
   SERVICIO DE VENTAS - FASTAPI
========================================== */

// Estructura de datos que devuelve nuestro Backend
export interface ResumenVentas {
  total_transacciones: number
  unidades_vendidas: number
  ventas_totales: string
  total_tiendas: number
  total_productos: number
  ticket_promedio: string
}

// Consultar los indicadores generales de ventas
export async function obtenerResumenVentas(): Promise<ResumenVentas> {
  const respuesta = await fetch('/api/ventas/resumen')

  if (!respuesta.ok) {
    throw new Error(
      `Error al consultar ventas: ${respuesta.status}`
    )
  }

  const datos: ResumenVentas = await respuesta.json()

  return datos
}

/* ==========================================
   VENTAS POR TIENDA
========================================== */

// Representa una tienda y sus indicadores
export interface VentaTienda {
  tienda: string
  total_transacciones: number
  unidades_vendidas: number
  ventas_totales: string
}

// Respuesta del endpoint de tiendas
export interface RespuestaVentasTiendas {
  total_tiendas: number
  tiendas: VentaTienda[]
}

// Consultar las ventas agrupadas por tienda
export async function obtenerVentasTiendas(): Promise<RespuestaVentasTiendas> {
  const respuesta = await fetch('/api/ventas/tiendas')

  if (!respuesta.ok) {
    throw new Error(
      `Error al consultar ventas por tienda: ${respuesta.status}`
    )
  }

  const datos: RespuestaVentasTiendas = await respuesta.json()

  return datos
}

/* ==========================================
   VENTAS POR PRODUCTO
========================================== */

// Representa un producto de la capa Gold
export interface VentaProducto {
  producto_id: string
  producto: string
  categoria: string
  unidades_vendidas: number
  ventas_totales: string
}

// Respuesta del Backend
export interface RespuestaVentasProductos {
  total_productos: number
  productos: VentaProducto[]
}

// Consultar las ventas agrupadas por producto
export async function obtenerVentasProductos(): Promise<RespuestaVentasProductos> {

  const respuesta = await fetch('/api/ventas/productos')

  if (!respuesta.ok) {
    throw new Error(
      `Error al consultar ventas por producto: ${respuesta.status}`
    )
  }

  const datos: RespuestaVentasProductos = await respuesta.json()

  return datos
}

/* ==========================================
   VENTAS POR CATEGORIA
========================================== */

// Representa una categoría de la capa Gold
export interface VentaCategoria {
  categoria: string
  total_transacciones: number
  unidades_vendidas: number
  ventas_totales: string
}

// Respuesta del Backend
export interface RespuestaVentasCategorias {
  total_categorias: number
  categorias: VentaCategoria[]
}

// Consultar ventas agrupadas por categoría
export async function obtenerVentasCategorias(): Promise<RespuestaVentasCategorias> {

  const respuesta = await fetch('/api/ventas/categorias')

  if (!respuesta.ok) {
    throw new Error(
      `Error al consultar ventas por categoría: ${respuesta.status}`
    )
  }

  const datos: RespuestaVentasCategorias = await respuesta.json()

  return datos
}
