'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getToken } from '@/lib/auth';
import { CUSTOMER_ID } from '@/lib/api-client';
import ProtectedRoute from '@/components/ProtectedRoute';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100';

interface CartItem {
  id: number;
  product_id: number;
  product?: {
    name: string;
    brand?: string;
    category?: string;
  };
  quantity: number;
  price: number;
  subtotal: number;
}

interface Cart {
  id: string;
  items: CartItem[];
  item_count: number;
  total: number;
}

export default function CheckoutPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const cartId = searchParams.get('cart_id');

  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!cartId) {
      router.push('/cart');
      return;
    }
    loadCart();
  }, [cartId]);

  const loadCart = async () => {
    try {
      const token = getToken();
      const response = await fetch(`${API_BASE_URL}/cart/${cartId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to load cart');

      const data = await response.json();
      setCart(data);
    } catch (err) {
      setError('Failed to load cart details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePay = async () => {
    if (!cartId) return;

    setPaying(true);
    setError('');

    try {
      const token = getToken();

      // Call the finalize endpoint directly to create the order
      const response = await fetch(`${API_BASE_URL}/checkout/finalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          payment_intent_id: `demo-intent-${Date.now()}`, // Demo payment intent
          cart_id: cartId,
          customer_id: CUSTOMER_ID
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Payment failed');
      }

      const order = await response.json();

      // Success! Redirect to success page or home
      alert(`Order placed successfully!\n\nOrder Number: ${order.order_number}\nTotal: $${order.total.toFixed(2)}\n\nThank you for your purchase!`);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Payment processing failed. Please try again.');
      console.error(err);
    } finally {
      setPaying(false);
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="text-center py-12 text-gray-500">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          Loading checkout...
        </div>
      </ProtectedRoute>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <ProtectedRoute>
        <div className="card text-center">
          <h1 className="text-3xl font-bold mb-4">No Items to Checkout</h1>
          <p className="text-gray-600 mb-6">Your cart is empty.</p>
          <button
            onClick={() => router.push('/')}
            className="btn-primary"
          >
            Continue Shopping
          </button>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="max-w-4xl mx-auto">
        <div className="card">
          <h1 className="text-3xl font-bold mb-6">Checkout</h1>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-800 rounded-md">
              {error}
            </div>
          )}

          {/* Order Summary */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="divide-y divide-gray-200">
                {cart.items.map((item) => (
                  <div key={item.id} className="py-4 first:pt-0 last:pb-0">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium">{item.product?.name || `Product #${item.product_id}`}</h3>
                        {item.product?.brand && (
                          <p className="text-sm text-gray-500">{item.product.brand}</p>
                        )}
                        <p className="text-sm text-gray-600 mt-1">
                          Quantity: {item.quantity} × ${item.price.toFixed(2)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">${item.subtotal.toFixed(2)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Total */}
              <div className="mt-6 pt-6 border-t-2 border-gray-300">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-gray-600">Total ({cart.item_count} {cart.item_count === 1 ? 'item' : 'items'})</p>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-blue-600">${cart.total.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Payment Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Payment</h2>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">Demo Payment</h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>This is a demonstration system. Clicking "Pay Now" will:</p>
                    <ul className="list-disc ml-5 mt-2 space-y-1">
                      <li>Create your order</li>
                      <li>Save items to your purchase history</li>
                      <li>Update inventory</li>
                      <li>Enable AI recommendations based on your purchases</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/cart')}
              disabled={paying}
              className="flex-1 px-6 py-3 border border-gray-300 rounded-md text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >               Back to Cart
            </button>
            <button
              onClick={handlePay}
              disabled={paying}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg"
            >               {paying ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                'Pay Now'
              )}
            </button>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
