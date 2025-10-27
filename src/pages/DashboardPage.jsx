import { useEffect, useState } from 'react'
import api from '../services/api'
import { Package, AlertTriangle, TruckIcon } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    pendingManifests: 0,
    lowStock: 0,
    todayDeliveries: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      // Load pending manifests
      const manifestsRes = await api.get('/manifiestos?estado=en_proceso,en_transito&per_page=100')

      // Load all products to check stock
      const productsRes = await api.get('/productos?per_page=100')
      const lowStockProducts = productsRes.data.items.filter(p => p.cantidad < 10)

      setStats({
        pendingManifests: manifestsRes.data.pagination.total,
        lowStock: lowStockProducts.length,
        todayDeliveries: 0 // Could calculate from manifests
      })
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div>Cargando...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Manifiestos Pendientes</p>
              <p className="text-3xl font-bold text-primary-600">{stats.pendingManifests}</p>
            </div>
            <TruckIcon className="text-primary-600" size={40} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Productos Bajo Stock</p>
              <p className="text-3xl font-bold text-warning">{stats.lowStock}</p>
            </div>
            <AlertTriangle className="text-warning" size={40} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Entregas Hoy</p>
              <p className="text-3xl font-bold text-success">{stats.todayDeliveries}</p>
            </div>
            <Package className="text-success" size={40} />
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Bienvenido al Sistema de Inventario</h2>
        <p className="text-gray-600">
          Utiliza el menú lateral para navegar entre las diferentes secciones del sistema.
        </p>
      </div>
    </div>
  )
}
