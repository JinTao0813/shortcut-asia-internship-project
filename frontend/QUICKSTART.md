# Coffee Assistant - Quick Start Guide

## 🚀 Getting Started

### Step 1: Install Dependencies

```bash
cd frontend/frontend
npm install
```

### Step 2: Configure Environment

The `.env.local` file is already configured with:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Update this URL if your backend runs on a different port.

### Step 3: Start the Development Server

```bash
npm run dev
```

The app will be available at: **http://localhost:3000**

## 📱 Application Flow

### For Staff/Users

1. **Access Main Page** - Open http://localhost:3000
2. **Use Chat Interface** - Type questions about coffee outlets or drinkware products
3. **Get AI Responses** - The RAG assistant retrieves and provides relevant information
4. **Try Example Queries** - Click on example buttons to quickly test the system

### For Administrators

1. **Click "Admin Login"** - Top-right corner of the main page
2. **Enter Password** - Login with admin credentials
3. **Access Dashboard** - Automatically redirected to `/admin`
4. **Manage Data**:
   - Switch between "Outlet Management" and "Product Management" tabs
   - Add new items using the "+ Add" button
   - Edit items by clicking the pencil icon
   - Delete items by clicking the trash icon
5. **Logout** - Click the "Logout" button when done

## 🎨 Features Overview

### Main Chat Page (`/`)

- **Header**: Logo, brand name, and admin login button
- **Chat Panel**:
  - Scrollable conversation area
  - Input box for questions
  - Send button
  - Example query buttons
- **AI Assistant**: Powered by RAG for accurate responses

### Admin Dashboard (`/admin`)

- **Protected Route**: Only accessible after login
- **Outlet Management Tab**:
  - Table with: Name, Category, Address, Stock Status
  - CRUD operations (Create, Read, Update, Delete)
  - Stock status indicators (In Stock / Out of Stock)
- **Product Management Tab**:
  - Table with: Name, Category, Price, Image
  - Full CRUD operations
  - Image preview thumbnails
- **Logout Button**: Clears session and redirects to main page

## 🎨 Theme & Design

- **Primary Color**: #0E186C (Deep navy blue)
- **Background**: Gradient from #f5f7fa to #e8ebf0
- **Border Radius**: Rounded corners (12px - 16px)
- **Shadows**: Soft, modern shadows
- **Typography**: Clean, readable sans-serif fonts
- **Responsive**: Works on desktop, tablet, and mobile

## 🔧 Troubleshooting

### Backend Connection Issues

If you see "Failed to fetch" or similar errors:

1. Ensure backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is enabled in backend

### Authentication Issues

If admin login doesn't work:

1. Check backend `/admin/login` endpoint
2. Verify session/cookie handling
3. Check browser console for errors

### Build Issues

If you encounter build errors:

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json .next
npm install
npm run dev
```

## 📦 Project Structure

```
frontend/
├── app/
│   ├── admin/page.tsx       # Admin dashboard
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main chat page
│   └── globals.css          # Global styles
├── components/
│   ├── LoginModal.tsx       # Login modal
│   └── ProtectedRoute.tsx   # Route guard
├── contexts/
│   └── AuthContext.tsx      # Auth state management
├── lib/
│   └── api.ts               # API client
├── types/
│   └── index.ts             # TypeScript types
└── .env.local               # Environment variables
```

## 🔌 API Integration

Ensure your backend implements these endpoints:

**Chat**

- `POST /chat` - Body: `{ message: string }`

**Auth**

- `POST /admin/login` - Body: `{ password: string }`
- `POST /admin/logout`
- `GET /admin/check`

**Outlets**

- `GET /outlets`
- `POST /outlets` - Body: `{ name, category, address, maps_url, stock }`
- `PUT /outlets/:id` - Body: `{ name, category, address, maps_url, stock }`
- `DELETE /outlets/:id`

**Products**

- `GET /products`
- `POST /products` - Body: `{ name, link, category, price, image_url }`
- `PUT /products/:id` - Body: `{ name, link, category, price, image_url }`
- `DELETE /products/:id`

## 🚢 Production Deployment

### Build for Production

```bash
npm run build
```

### Start Production Server

```bash
npm start
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## 💡 Tips

1. **Testing**: Use example queries to quickly test the RAG system
2. **Admin Access**: Keep admin password secure
3. **Data Management**: Changes in admin dashboard reflect immediately in chat
4. **Mobile**: Interface is fully responsive - test on different devices
5. **Performance**: Use production build for better performance

## 📞 Support

For issues or questions, refer to:

- `README_FRONTEND.md` for detailed documentation
- Backend API documentation
- Next.js documentation: https://nextjs.org/docs

---

**Happy Coding! ☕**
