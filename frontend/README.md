# E-Commerce Frontend Application

Modern Next.js-based e-commerce frontend with AI-powered search and recommendations.

## Tech Stack

- **Framework**: Next.js 14.2.13 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **API Client**: openapi-fetch (type-safe API calls)
- **React**: 18.3.1

## Features

### 1. Products Page (Home - `/`)
- Display all available products with pagination support
- **AI-Powered Recommendations**: Personalized product suggestions based on customer preferences
- Product cards with images, pricing, and details
- One-click "Add to Cart" functionality
- Visual indicators for AI-recommended products

### 2. AI Chat Page (`/chat`)
- ChatGPT-like conversational interface
- **Natural Language Search**: Type queries like "waterproof hiking boots" or "red running shoes"
- Real-time AI product search with relevance scoring
- Inline product cards in chat with "Add to Cart" buttons
- Confidence scores for search results
- Scrollable chat history with smooth animations

### 3. Cart Page (`/cart`)
- View all items added to shopping cart
- **Quantity Management**:
  - Plus (+) button to increase quantity
  - Minus (-) button to decrease quantity
- Real-time subtotal calculations
- Total price and item count display
- Checkout functionality with payment processing
- Empty cart state with call-to-action

### 4. Admin Page (`/admin`)
- **Inventory Management**: View and manage product stock levels
- Visual indicators for low-stock items
- Quick stock adjustment buttons (-10, -1, +1, +10, +50)
- Inventory statistics dashboard:
  - Total items count
  - Low stock alerts
  - Total units available
  - Reserved units tracking

## Getting Started

### Prerequisites

- Node.js 20+ installed
- Backend API running on `http://localhost:8100`

### Installation

```bash
npm install
```

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8100
```

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js App Router pages
│   │   ├── layout.tsx       # Root layout with navigation
│   │   ├── page.tsx         # Products page (home)
│   │   ├── chat/
│   │   │   └── page.tsx     # AI chat interface
│   │   ├── cart/
│   │   │   └── page.tsx     # Shopping cart
│   │   └── admin/
│   │       └── page.tsx     # Inventory management
│   └── lib/
│       ├── api-client.ts    # OpenAPI fetch client configuration
│       └── api-types.ts     # TypeScript type definitions
├── public/                   # Static assets
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts
```

## API Integration

### API Client

The application uses `openapi-fetch` for type-safe API calls:

```typescript
import apiClient from '@/lib/api-client';

// Example: Fetch products
const { data } = await apiClient.GET('/products', {
  params: { query: { limit: 20 } }
});
```

### Available Endpoints

- `GET /products` - List all products
- `GET /recommendations` - Get AI-powered recommendations
- `GET /search/nl` - Natural language product search
- `GET /cart/{cart_id}` - Get cart contents
- `POST /cart/add` - Add item to cart
- `POST /cart/remove` - Remove item from cart
- `GET /admin/inventory` - Get inventory status
- `POST /admin/stock` - Update stock levels
- `POST /checkout/prepare` - Prepare checkout
- `POST /checkout/finalize` - Complete order

## Key Features Explained

### Natural Language Search

The chat interface uses the `/search/nl` endpoint to process natural language queries:

```typescript
const { data } = await apiClient.GET('/search/nl', {
  params: { query: { q: "waterproof hiking boots" } }
});
```

Returns products with relevance scores and confidence metrics.

### AI Recommendations

The products page fetches personalized recommendations:

```typescript
const { data } = await apiClient.GET('/recommendations', {
  params: {
    query: {
      customer_id: CUSTOMER_ID,
      limit: 4,
      use_agent: true
    }
  }
});
```

### Cart Management

Cart operations use a persistent cart ID:

```typescript
// Add to cart
await apiClient.POST('/cart/add', {
  body: {
    cart_id: CART_ID,
    product_id: productId,
    quantity: 1
  }
});

// Remove from cart
await apiClient.POST('/cart/remove', {
  body: {
    cart_id: CART_ID,
    product_id: productId,
    quantity: 1
  }
});
```

## Styling

### Tailwind CSS Utilities

Custom utility classes defined in `globals.css`:

- `.btn-primary` - Primary action buttons (blue)
- `.btn-secondary` - Secondary buttons (gray)
- `.btn-danger` - Delete/remove buttons (red)
- `.card` - Card container with shadow
- `.input-field` - Text input fields with focus states

### Responsive Design

All pages are fully responsive:
- Mobile-first approach
- Grid layouts adjust for different screen sizes
- Navigation adapts to smaller viewports

## Type Safety

TypeScript interfaces defined in `api-types.ts`:

```typescript
interface Product {
  id: number;
  sku: string;
  name: string;
  description?: string;
  price: number;
  category?: string;
  brand?: string;
  color?: string;
  relevance_score?: number;
  recommendation_score?: number;
}
```

## Performance Optimizations

- **Parallel Data Fetching**: Products and recommendations load simultaneously
- **Client-Side Rendering**: Fast interactions with `use client` directive
- **Optimized Re-renders**: State management minimizes unnecessary updates
- **Smooth Animations**: CSS transitions for better UX

## Future Enhancements

- User authentication and personalized accounts
- Product image uploads
- Advanced filtering and sorting
- Order history tracking
- Payment gateway integration
- Real-time inventory updates with WebSockets
