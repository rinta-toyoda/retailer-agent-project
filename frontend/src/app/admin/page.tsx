'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api-client';
import ProtectedRoute from '@/components/ProtectedRoute';

interface Product {
  name: string;
  description: string;
  image_url: string | null;
  brand: string;
  category: string;
}

interface InventoryItem {
  id: number;
  sku: string;
  product_id: number;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
  product?: Product;
}

export default function AdminPage() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [updateLoading, setUpdateLoading] = useState<string | null>(null);
  const [editingStock, setEditingStock] = useState<{ [sku: string]: string }>({});

  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    try {
      const { data } = await apiClient.GET('/admin/inventory');
      if (data) setInventory(data.inventory);
    } catch (err) {
      setMessage('Failed to load inventory');
    } finally {
      setLoading(false);
    }
  };

  const handleSetStock = async (sku: string, newQuantity: string) => {
    const quantity = parseInt(newQuantity);

    if (isNaN(quantity) || quantity < 0) {
      setMessage('Please enter a valid quantity (0 or greater)');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    setUpdateLoading(sku);
    try {
      const { data } = await apiClient.POST('/admin/stock/set', {
        params: { query: { sku, quantity } }
      });

      // Update only the specific item in the inventory array to prevent reordering
      if (data) {
        setInventory(prevInventory =>
          prevInventory.map(item =>
            item.sku === sku
              ? { ...item, quantity: data.quantity, available_quantity: data.available_quantity, is_low_stock: data.is_low_stock }
              : item
          )
        );
      }

      setMessage(`Successfully updated stock for ${sku}`);
      setTimeout(() => setMessage(''), 3000);
      setEditingStock({ ...editingStock, [sku]: '' });
    } catch (err) {
      setMessage('Failed to update stock');
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setUpdateLoading(null);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading inventory...</div>;
  }

  return (
    <ProtectedRoute>
    <div>
      <div className="card">
        <h1 className="text-3xl font-bold mb-2">Inventory Management</h1>
        <p className="text-gray-600 mb-6">Manage product stock levels. Items below threshold are highlighted.</p>

        {message && (
          <div className={`mb-4 p-4 border rounded-md ${
            message.includes('Failed') || message.includes('valid')
              ? 'bg-red-50 border-red-200 text-red-800'
              : 'bg-green-50 border-green-200 text-green-800'
          }`}>
            {message}
          </div>
        )}

        {inventory.length === 0 ? (
          <p className="text-center py-8 text-gray-500">No inventory items found.</p>
        ) : (
          <div className="space-y-4">
            {inventory.map((item) => (
              <div
                key={item.id}
                className={`flex gap-4 items-start p-4 rounded-lg ${
                  item.is_low_stock ? 'bg-red-50 border-2 border-red-500' : 'bg-gray-50'
                }`}
              >
                {/* Product Image */}
                <div className="w-24 h-24 flex-shrink-0">
                  {item.product?.image_url ? (
                    <img
                      src={item.product.image_url}
                      alt={item.product.name}
                      className="w-full h-full object-cover rounded-md"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-200 rounded-md flex items-center justify-center text-gray-400 text-xs">
                      No Image
                    </div>
                  )}
                </div>

                {/* Product Details */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-lg">
                      {item.product?.name || 'Unknown Product'}
                    </h3>
                    <span className="text-sm text-gray-500">({item.sku})</span>
                    {item.is_low_stock && (
                      <span className="bg-red-600 text-white text-xs px-2 py-1 rounded font-semibold">
                        LOW STOCK
                      </span>
                    )}
                  </div>

                  {item.product?.description && (
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                      {item.product.description}
                    </p>
                  )}

                  <div className="text-sm text-gray-600 space-y-1">
                    {item.product?.brand && (
                      <p><strong>Brand:</strong> {item.product.brand}</p>
                    )}
                    {item.product?.category && (
                      <p><strong>Category:</strong> {item.product.category}</p>
                    )}
                    <p>
                      <strong>Total:</strong> {item.quantity} units •{' '}
                      <strong>Reserved:</strong> {item.reserved_quantity} •{' '}
                      <strong>Available:</strong> {item.available_quantity}
                    </p>
                    <p><strong>Threshold:</strong> {item.low_stock_threshold} units</p>
                  </div>
                </div>

                {/* Set Stock Control */}
                <div className="flex flex-col gap-2 items-end min-w-[200px]">
                  <div className="text-sm text-gray-600">
                    <strong>Current Stock:</strong> {item.quantity}
                  </div>
                  <div className="flex gap-2 w-full">
                    <input
                      type="number"
                      min="0"
                      placeholder="New quantity"
                      value={editingStock[item.sku] || ''}
                      onChange={(e) => setEditingStock({ ...editingStock, [item.sku]: e.target.value })}
                      disabled={updateLoading === item.sku}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={() => handleSetStock(item.sku, editingStock[item.sku] || '')}
                      disabled={updateLoading === item.sku || !editingStock[item.sku]}
                      className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                    >
                      {updateLoading === item.sku ? 'Setting...' : 'Set Stock'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Inventory Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Total Items</p>
            <p className="text-3xl font-bold">{inventory.length}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Low Stock Items</p>
            <p className="text-3xl font-bold text-red-600">
              {inventory.filter(item => item.is_low_stock).length}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Total Units</p>
            <p className="text-3xl font-bold">
              {inventory.reduce((sum, item) => sum + item.quantity, 0)}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-500 mb-1">Reserved Units</p>
            <p className="text-3xl font-bold text-blue-600">
              {inventory.reduce((sum, item) => sum + item.reserved_quantity, 0)}
            </p>
          </div>
        </div>
      </div>
    </div>
    </ProtectedRoute>
  );
}
