// Type definitions based on backend OpenAPI schema

export interface Product {
  id: number;
  sku: string;
  name: string;
  description?: string;
  price: number;
  category?: string;
  brand?: string;
  color?: string;
  features?: string;
  image_url?: string;
  is_active?: boolean;
  relevance_score?: number;
  recommendation_score?: number;
}

export interface CartItem {
  id: number;
  product_id: number;
  product?: Product;
  quantity: number;
  price: number;
  subtotal: number;
}

export interface Cart {
  cart_id: string;
  items: CartItem[];
  total: number;
  item_count: number;
}

export interface InventoryItem {
  id: number;
  sku: string;
  product_id: number;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
}

export interface paths {
  '/products': {
    get: {
      parameters: {
        query?: {
          skip?: number;
          limit?: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              products: Product[];
            };
          };
        };
      };
    };
  };
  '/cart/add': {
    post: {
      requestBody: {
        content: {
          'application/json': {
            cart_id: string;
            product_id: number;
            quantity: number;
            customer_id?: number;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': Cart;
          };
        };
      };
    };
  };
  '/cart/remove': {
    post: {
      requestBody: {
        content: {
          'application/json': {
            cart_id: string;
            product_id: number;
            quantity: number;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': Cart;
          };
        };
      };
    };
  };
  '/cart/{cart_id}': {
    get: {
      parameters: {
        path: {
          cart_id: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': Cart;
          };
        };
      };
    };
  };
  '/search/nl': {
    get: {
      parameters: {
        query: {
          q: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              query: string;
              products: Product[];
              confidence: number;
              reasoning_logs: any[];
            };
          };
        };
      };
    };
  };
  '/recommendations': {
    get: {
      parameters: {
        query: {
          customer_id: number;
          limit?: number;
          use_agent?: boolean;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              customer_id: number;
              recommendations: Product[];
            };
          };
        };
      };
    };
  };
  '/admin/stock': {
    post: {
      parameters: {
        query: {
          sku: string;
          qty_delta: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': InventoryItem;
          };
        };
      };
    };
  };
  '/admin/stock/set': {
    post: {
      parameters: {
        query: {
          sku: string;
          quantity: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': InventoryItem;
          };
        };
      };
    };
  };
  '/admin/inventory': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              inventory: InventoryItem[];
            };
          };
        };
      };
    };
  };
}
