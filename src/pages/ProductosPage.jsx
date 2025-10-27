import { useEffect, useState } from 'react'
import api from '../services/api'
import { toast } from 'sonner'

export default function ProductosPage() {
  const [productos, setProductos] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 1 })

  useEffect(() => {
    loadProductos()
  }, [pagination.page])

  const loadProductos = async () => {
    try {
      const response = await api.get(`/productos?page=${pagination.page}`)
      setProductos(response.data.items)
      setPagination(response.data.pagination)
    } catch (error) {
      toast.error('Error cargando productos')
    } finally {
      setLoading(false)
    }
  }

  const getEstadoBadge = (estado) => {
    const badges = {
      'No terminado': 'badge-red',
      'En proceso': 'badge-yellow',
      'Terminado': 'badge-green'
    }
    return badges[estado] || 'badge-gray'
  }

  if (loading) {
    return <div>Cargando productos...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Productos</h1>
      </div>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">Nombre</th>
                <th className="table-header-cell">Categoría</th>
                <th className="table-header-cell">Estado</th>
                <th className="table-header-cell">Cantidad</th>
                <th className="table-header-cell">Medida</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {productos.map((producto) => (
                <tr key={producto.id}>
                  <td className="table-cell font-medium">{producto.nombre}</td>
                  <td className="table-cell">{producto.categoria?.nombre}</td>
                  <td className="table-cell">
                    <span className={getEstadoBadge(producto.estado)}>
                      {producto.estado}
                    </span>
                  </td>
                  <td className="table-cell">
                    <span className={producto.cantidad < 10 ? 'text-red-600 font-bold' : ''}>
                      {producto.cantidad}
                    </span>
                  </td>
                  <td className="table-cell">{producto.medida || 'unidades'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination.pages > 1 && (
          <div className="mt-4 flex justify-center gap-2">
            <button
              onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
              disabled={pagination.page === 1}
              className="btn-secondary"
            >
              Anterior
            </button>
            <span className="px-4 py-2">
              Página {pagination.page} de {pagination.pages}
            </span>
            <button
              onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}
              disabled={pagination.page === pagination.pages}
              className="btn-secondary"
            >
              Siguiente
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
