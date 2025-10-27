import { useEffect, useState } from 'react'
import api from '../services/api'
import { toast } from 'sonner'
import { format } from 'date-fns'

export default function ManifiestosPage() {
  const [manifiestos, setManifiestos] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 1 })

  useEffect(() => {
    loadManifiestos()
  }, [pagination.page])

  const loadManifiestos = async () => {
    try {
      const response = await api.get(`/manifiestos?page=${pagination.page}`)
      setManifiestos(response.data.items)
      setPagination(response.data.pagination)
    } catch (error) {
      toast.error('Error cargando manifiestos')
    } finally {
      setLoading(false)
    }
  }

  const getEstadoBadge = (estado) => {
    const badges = {
      'en_proceso': 'badge-blue',
      'en_transito': 'badge-yellow',
      'entregado': 'badge-green',
      'cancelado': 'badge-red'
    }
    return badges[estado] || 'badge-gray'
  }

  const getEstadoLabel = (estado) => {
    const labels = {
      'en_proceso': 'En Proceso',
      'en_transito': 'En Tránsito',
      'entregado': 'Entregado',
      'cancelado': 'Cancelado'
    }
    return labels[estado] || estado
  }

  if (loading) {
    return <div>Cargando manifiestos...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Manifiestos de Entrega</h1>
      </div>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">Número</th>
                <th className="table-header-cell">Cliente</th>
                <th className="table-header-cell">Estado</th>
                <th className="table-header-cell">Fecha Creación</th>
                <th className="table-header-cell">Productos</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {manifiestos.map((manifiesto) => (
                <tr key={manifiesto.id}>
                  <td className="table-cell font-medium">{manifiesto.numero_manifiesto}</td>
                  <td className="table-cell">{manifiesto.cliente?.nombre}</td>
                  <td className="table-cell">
                    <span className={getEstadoBadge(manifiesto.estado)}>
                      {getEstadoLabel(manifiesto.estado)}
                    </span>
                  </td>
                  <td className="table-cell">
                    {manifiesto.fecha_creacion && format(new Date(manifiesto.fecha_creacion), 'dd/MM/yyyy HH:mm')}
                  </td>
                  <td className="table-cell">{manifiesto.total_productos || 0}</td>
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
