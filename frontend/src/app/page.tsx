'use client';

import { useState, useEffect } from 'react';
import apiClient, { CART_ID, CUSTOMER_ID } from '@/lib/api-client';
import type { Product } from '@/lib/api-types';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [recsLoading, setRecsLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadProducts();
    loadRecommendations();
  }, []);

  const loadProducts = async () => {
    try {
      const { data } = await apiClient.GET('/products', { params: { query: { limit: 20 } } });
      if (data) setProducts(data.products);
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setProductsLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const { data } = await apiClient.GET('/recommendations', {
        params: { query: { customer_id: CUSTOMER_ID, limit: 4, use_agent: true } }
      });
      if (data) setRecommendations(data.recommendations);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setRecsLoading(false);
    }
  };

  const addToCart = async (productId: number, name: string) => {
    try {
      await apiClient.POST('/cart/add', {
        body: { cart_id: CART_ID, product_id: productId, quantity: 1, customer_id: CUSTOMER_ID }
      });
      setMessage(`Added "${name}" to cart!`);
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('Failed to add to cart');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  return (
    <ProtectedRoute>
    <div>
      {message && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-800 rounded-md">
          {message}
        </div>
      )}

      <div className="card">
        <h2 className="text-2xl font-bold mb-2">AI Recommendations for You</h2>
        <p className="text-gray-600 mb-6">Personalized suggestions based on your preferences</p>
        {recsLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading recommendations...</span>
          </div>
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {recommendations.map((product) => (
              <ProductCard key={product.id} product={product} onAddToCart={addToCart} isRec />
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No recommendations available</p>
        )}
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-6">All Products</h2>
        {productsLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading products...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} onAddToCart={addToCart} />
            ))}
          </div>
        )}
      </div>
    </div>
    </ProtectedRoute>
  );
}

function ProductCard({ product, onAddToCart, isRec }: {
  product: Product;
  onAddToCart: (id: number, name: string) => void;
  isRec?: boolean;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
      {/* Product Image */}
      <div className="relative h-48 bg-gray-100">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="text-sm">No Image</span>
          </div>
        )}
        {isRec && (
          <span className="absolute top-2 right-2 bg-blue-600 text-white text-xs px-2 py-1 rounded">
            AI Recommended
          </span>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-1">{product.name}</h3>
        <p className="text-sm text-gray-500 mb-2">
          {product.brand && `${product.brand} • `}{product.category}
        </p>
        {product.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p>
        )}
        <div className="text-2xl font-bold text-blue-600 mb-2">${product.price.toFixed(2)}</div>
        {product.color && <p className="text-xs text-gray-500 mb-3">Color: {product.color}</p>}
        <button onClick={() => onAddToCart(product.id, product.name)} className="btn-primary w-full text-sm">
          Add to Cart
        </button>
      </div>
    </div>
  );
}
