# Coffee Assistant - Frontend

A modern, AI-powered coffee assistant application with RAG (Retrieval-Augmented Generation) capabilities.

## Features

### 1. Main Chat Page

- **RAG Assistant**: AI-powered chat interface for querying coffee outlets and drinkware products
- **Clean UI**: Modern design with rounded corners and theme color #0E186C
- **Example Queries**: Quick-start buttons with common questions
- **Real-time Chat**: Smooth conversation flow with typing indicators
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 2. Admin Authentication

- **Secure Login**: Password-protected admin access
- **Session Management**: Persistent authentication across page refreshes
- **Modal Login**: Clean modal interface for admin login

### 3. Admin Dashboard

Protected route accessible only after authentication:

#### Outlet Management

- View all coffee outlets
- Add new outlets (name, category, address, maps URL, stock status)
- Edit existing outlets
- Delete outlets
- Stock status indicators (In Stock / Out of Stock)

#### Product Management

- View all drinkware products
- Add new products (name, link, category, price, image URL)
- Edit existing products
- Delete products
- Image previews for products

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Context API

## Getting Started

### Prerequisites

- Node.js 20+ installed
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the project directory:

   ```bash
   cd frontend/frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Create a `.env.local` file (already created):

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. Run the development server:

   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/
│   ├── admin/
│   │   └── page.tsx          # Admin dashboard with outlet/product management
│   ├── layout.tsx            # Root layout with AuthProvider
│   ├── page.tsx              # Main chat page
│   └── globals.css           # Global styles
├── components/
│   ├── LoginModal.tsx        # Admin login modal
│   └── ProtectedRoute.tsx    # Route protection HOC
├── contexts/
│   └── AuthContext.tsx       # Authentication context and hooks
├── lib/
│   └── api.ts                # API client and endpoints
└── .env.local                # Environment variables
```

## API Endpoints

The frontend expects the following backend endpoints:

### Chat

- `POST /chat` - Send a message to the RAG assistant

### Authentication

- `POST /admin/login` - Admin login with password
- `POST /admin/logout` - Admin logout
- `GET /admin/check` - Check authentication status

### Outlets

- `GET /outlets` - Get all outlets
- `POST /outlets` - Create a new outlet
- `PUT /outlets/:id` - Update an outlet
- `DELETE /outlets/:id` - Delete an outlet

### Products

- `GET /products` - Get all products
- `POST /products` - Create a new product
- `PUT /products/:id` - Update a product
- `DELETE /products/:id` - Delete a product

## Design System

### Colors

- **Primary**: `#0E186C` (Deep blue)
- **Background**: `#f5f7fa` to `#e8ebf0` (Gradient)
- **White**: `#ffffff`
- **Text**: `#171717`
- **Gray shades**: Various for UI elements

### Components

- **Border Radius**: `rounded-xl` (0.75rem) and `rounded-2xl` (1rem)
- **Shadows**: Soft shadows for elevation
- **Transitions**: Smooth color and transform transitions
- **Custom Scrollbar**: Styled scrollbar matching the theme

## Features in Detail

### Chat Interface

- Welcome screen with example queries
- Message history with timestamps
- User messages (right-aligned, blue background)
- Assistant messages (left-aligned, gray background)
- Loading indicator during API calls
- Error handling with user-friendly messages

### Admin Dashboard

- Tabbed interface for outlets and products
- CRUD operations for both entities
- Modal-based forms for adding/editing
- Confirmation dialogs for deletions
- Real-time data updates after operations
- Responsive tables with action buttons

### Authentication

- Context-based authentication state
- Protected routes with loading states
- Automatic redirect for unauthenticated users
- Persistent sessions with cookie support

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

### Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

## Production Build

To create a production build:

```bash
npm run build
npm start
```

The application will be optimized and ready for deployment.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

This project is part of the Shortcut Asia Internship Project.
