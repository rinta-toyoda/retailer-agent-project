'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import apiClient, { CART_ID } from '@/lib/api-client';
import { isAuthenticated, removeToken } from '@/lib/auth';

export default function Navigation() {
  const pathname = usePathname();
  const router = useRouter();
  const [cartCount, setCartCount] = useState(0);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(isAuthenticated());
  }, [pathname]);

  useEffect(() => {
    loadCartCount();
    // Refresh cart count every 5 seconds
    const interval = setInterval(loadCartCount, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadCartCount = async () => {
    try {
      const { data } = await apiClient.GET('/cart/{cart_id}', {
        params: { path: { cart_id: CART_ID } }
      });
      if (data) {
        setCartCount(data.item_count || 0);
      }
    } catch (err) {
      // Cart doesn't exist yet, count is 0
      setCartCount(0);
    }
  };

  const isActive = (path: string) => pathname === path;
  const isLoginPage = pathname === '/login';

  const handleLogout = () => {
    removeToken();
    setIsLoggedIn(false);
    router.push('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="text-xl font-bold text-blue-600 hover:text-blue-700">
            Retailer AI Agent
          </Link>
          {!isLoginPage && (
            <div className="flex space-x-8 items-center">
              <Link
              href="/"
              className={`font-medium transition-colors ${
                isActive('/') ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Products
            </Link>
            <Link
              href="/chat"
              className={`font-medium transition-colors ${
                isActive('/chat') ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              AI Chat
            </Link>
            <Link
              href="/cart"
              className={`relative font-medium transition-colors ${
                isActive('/cart') ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Cart
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-6 bg-blue-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </Link>
            <Link
              href="/admin"
              className={`font-medium transition-colors ${
                isActive('/admin') ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              Admin
            </Link>

            {isLoggedIn ? (
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            ) : (
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
              >
                Login
              </Link>
            )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
