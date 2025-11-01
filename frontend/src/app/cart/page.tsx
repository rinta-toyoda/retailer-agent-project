'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient, { API_BASE_URL, CART_ID } from '@/lib/api-client';
import type { Cart, CartItem } from '@/lib/api-types';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function CartPage() {
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const { data } = await apiClient.GET('/cart/{cart_id}', {
        params: { path: { cart_id: CART_ID } }
      });
      if (data) setCart(data);
    } catch (err) {
      console.log('Cart not found');
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (item: CartItem, delta: number) => {
    try {
      const endpoint = delta > 0 ? '/cart/add' : '/cart/remove';
      const { data } = await apiClient.POST(endpoint, {
        body: { cart_id: CART_ID, product_id: item.product_id, quantity: Math.abs(delta) }
      });
      if (data) setCart(data);
    } catch (err) {
      setMessage('Failed to update cart');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleCheckout = () => {
    // Redirect to checkout page
    router.push(`/checkout?cart_id=${CART_ID}`);
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading cart...</div>;
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="card text-center">
        <h1 className="text-3xl font-bold mb-4">Your Cart is Empty</h1>
        <p className="text-gray-600 mb-6">Start shopping to add items to your cart!</p>
        <Link href="/" className="btn-primary inline-block">
          Browse Products
        </Link>
      </div>
    );
  }

  return (
    <ProtectedRoute>
    <div>
      <div className="card">
        <h1 className="text-3xl font-bold mb-6">Shopping Cart</h1>
        {message && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-800 rounded-md">
            {message}
          </div>
        )}

        <div className="divide-y divide-gray-200">
          {cart.items.map((item) => (
            <div key={item.id} className="py-4 flex justify-between items-center">
              <div className="flex-1">
                <h3 className="text-lg font-semibold">{item.product?.name || `Product #${item.product_id}`}</h3>
                <p className="text-sm text-gray-500">
                  ${item.price.toFixed(2)} each
                  {item.product?.brand && ` • ${item.product.brand}`}
                  {item.product?.category && ` • ${item.product.category}`}
                </p>
              </div>

              <div className="flex items-center gap-6">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => updateQuantity(item, -1)}
                    className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-blue-600 hover:text-white hover:border-blue-600 transition-colors"
                  >
                    -
                  </button>
                  <span className="font-semibold w-8 text-center">{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item, 1)}
                    className="w-8 h-8 rounded-full border border-gray-300 flex items-center justify-center hover:bg-blue-600 hover:text-white hover:border-blue-600 transition-colors"
                  >
                    +
                  </button>
                </div>

                <div className="min-w-[100px] text-right">
                  <span className="text-lg font-bold">${item.subtotal.toFixed(2)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-6 border-t-2 border-gray-200 text-right">
          <p className="text-lg text-gray-600 mb-2">
            Total ({cart.item_count} {cart.item_count === 1 ? 'item' : 'items'})
          </p>
          <h2 className="text-3xl font-bold mb-6">${cart.total.toFixed(2)}</h2>
          <button
            onClick={handleCheckout}
            className="btn-primary text-lg px-8 py-3"
          >
            Proceed to Checkout
          </button>
        </div>
      </div>
    </div>
    </ProtectedRoute>
  );
}
