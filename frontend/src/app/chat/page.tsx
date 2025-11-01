'use client';

import { useState, useRef, useEffect } from 'react';
import apiClient, { CART_ID, CUSTOMER_ID } from '@/lib/api-client';
import type { Product } from '@/lib/api-types';
import ProtectedRoute from '@/components/ProtectedRoute';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  products?: Product[];
  confidence?: number;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([{
    id: '0',
    role: 'assistant',
    content: 'Hello! I\'m your AI shopping assistant. Try asking me to find products like "breathable red running shoes" or "waterproof jacket for hiking".'
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const { data } = await apiClient.GET('/search/nl', { params: { query: { q: input } } });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data?.products && data.products.length > 0
          ? `I found ${data.products.length} products matching "${data.query}". Here are the results:`
          : `No products found for "${data?.query}". Try different keywords.`,
        products: data?.products || [],
        confidence: data?.confidence
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = async (productId: number, productName: string) => {
    try {
      await apiClient.POST('/cart/add', {
        body: { cart_id: CART_ID, product_id: productId, quantity: 1, customer_id: CUSTOMER_ID }
      });
      setSuccess(`Added "${productName}" to cart!`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Failed to add to cart:', err);
    }
  };

  return (
    <ProtectedRoute>
    <div>
      <div className="card mb-4">
        <h1 className="text-3xl font-bold mb-2">AI Shopping Assistant</h1>
        <p className="text-gray-600">
          Ask me to find products using natural language. Try: "find waterproof hiking boots" or "comfortable running shoes"
        </p>
      </div>

      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-800 rounded-md">
          {success}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm flex flex-col" style={{ height: 'calc(100vh - 280px)' }}>
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div key={message.id}>
              <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  {message.content}
                  {message.confidence !== undefined && (
                    <div className="text-xs mt-1 opacity-80">
                      Confidence: {(message.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              </div>

              {message.products && message.products.length > 0 && (
                <div className={`mt-3 ${message.role === 'assistant' ? 'mr-auto' : 'ml-auto'} max-w-[80%]`}>
                  <div className="space-y-2">
                    {message.products.map((product: any) => (
                      <div key={product.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden flex">
                        {/* Product Image */}
                        <div className="w-24 h-24 flex-shrink-0 bg-gray-100">
                          {product.image_url ? (
                            <img
                              src={product.image_url}
                              alt={product.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                              No Image
                            </div>
                          )}
                        </div>

                        {/* Product Info */}
                        <div className="flex-1 p-4 flex justify-between items-center">
                          <div className="flex-1">
                            <h4 className="font-semibold">{product.name}</h4>
                            <p className="text-sm text-gray-500">
                              {product.brand && `${product.brand} • `}{product.category}
                              {product.color && ` • ${product.color}`}
                            </p>
                            {product.description && (
                              <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                                {product.description}
                              </p>
                            )}
                            <p className="text-lg font-bold text-blue-600 mt-1">${product.price.toFixed(2)}</p>
                            {product.relevance_score && (
                              <p className="text-xs text-green-600 mt-1">
                                Match: {(product.relevance_score * 100).toFixed(0)}%
                              </p>
                            )}
                          </div>
                          <button
                            onClick={() => addToCart(product.id, product.name)}
                            className="btn-primary text-sm ml-4 whitespace-nowrap flex-shrink-0"
                          >
                            Add to Cart
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSearch} className="border-t border-gray-200 p-4 flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me to find products..."
            className="input-field"
            disabled={isLoading}
          />
          <button type="submit" className="btn-primary" disabled={isLoading || !input.trim()}>
            {isLoading ? 'Searching...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
    </ProtectedRoute>
  );
}
