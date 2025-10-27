import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import axios from 'axios'
import { toast } from 'sonner'
import { CheckCircle } from 'lucide-react'

export default function ManifestVerificationPage() {
  const [searchParams] = useSearchParams()
  const codigo = searchParams.get('codigo')

  const [manifiesto, setManifiesto] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (codigo) {
      loadManifiesto()
    } else {
      setError('Código QR no proporcionado')
      setLoading(false)
    }
  }, [codigo])

  const loadManifiesto = async () => {
    try {
      // Extract manifest ID from codigo (format: MAN-QR-YYYYMMDDHHMMSS-XXXX)
      // We'll need to query by codigo_qr parameter
      // For simplicity, we'll try to find it
      const api = axios.create({
        baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
      })

      // Try to get manifests and find by codigo_qr
      const response = await api.get(`/manifiestos?per_page=100`)
      const found = response.data.items.find(m => m.codigo_qr === codigo)

      if (found) {
        setManifiesto(found)
      } else {
        setError('Manifiesto no encontrado')
      }
    } catch (err) {
      setError('Error cargando manifiesto')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando manifiesto...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="card max-w-md">
          <div className="text-center">
            <p className="text-red-600 font-semibold">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="card">
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Verificación de Manifiesto</h1>
          </div>

          {manifiesto && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold mb-2">Información del Manifiesto</h2>
                <div className="bg-gray-50 p-4 rounded space-y-2">
                  <p><span className="font-medium">Número:</span> {manifiesto.numero_manifiesto}</p>
                  <p><span className="font-medium">Cliente:</span> {manifiesto.cliente?.nombre}</p>
                  <p><span className="font-medium">Estado:</span> {manifiesto.estado}</p>
                </div>
              </div>

              {manifiesto.detalles && manifiesto.detalles.length > 0 && (
                <div>
                  <h2 className="text-lg font-semibold mb-2">Productos</h2>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Producto</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Cantidad</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {manifiesto.detalles.map((detalle, idx) => (
                          <tr key={idx}>
                            <td className="px-4 py-2 text-sm">{detalle.producto?.nombre}</td>
                            <td className="px-4 py-2 text-sm">{detalle.cantidad}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {manifiesto.estado === 'entregado' && (
                <div className="bg-green-50 border border-green-200 p-4 rounded flex items-center gap-3">
                  <CheckCircle className="text-green-600" size={24} />
                  <div>
                    <p className="font-semibold text-green-900">Manifiesto Entregado</p>
                    <p className="text-sm text-green-700">
                      Este manifiesto ya fue confirmado y firmado por el cliente.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
