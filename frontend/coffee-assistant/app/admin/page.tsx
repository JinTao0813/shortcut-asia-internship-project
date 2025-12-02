'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Coffee, LogOut, Store, Package, Pencil, Trash2, Plus, X } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { outletsAPI, productsAPI } from '@/lib/api';
import { Outlet, Product } from '@/types';
import Image from 'next/image';

type TabType = 'outlets' | 'products';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('outlets');
  const [outlets, setOutlets] = useState<Outlet[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Outlet | Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { logout } = useAuth();
  const router = useRouter();

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'outlets') {
        const data = await outletsAPI.getAll();
        setOutlets(data);
      } else {
        const data = await productsAPI.getAll();
        setProducts(data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  const handleAdd = () => {
    setEditingItem(null);
    setIsModalOpen(true);
  };

  const handleEdit = (item: Outlet | Product) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
      if (activeTab === 'outlets') {
        await outletsAPI.delete(id);
      } else {
        await productsAPI.delete(id);
      }
      fetchData();
    } catch (error) {
      console.error('Error deleting item:', error);
      alert('Failed to delete item');
    }
  };

  const handleSave = async (data: Outlet | Product) => {
    try {
      if (activeTab === 'outlets') {
        const outletData = data as Outlet;
        if (editingItem && 'id' in editingItem) {
          await outletsAPI.update(editingItem.id!, outletData);
        } else {
          await outletsAPI.create(outletData);
        }
      } else {
        const productData = data as Product;
        if (editingItem && 'id' in editingItem) {
          await productsAPI.update(editingItem.id!, productData);
        } else {
          await productsAPI.create(productData);
        }
      }
      setIsModalOpen(false);
      fetchData();
    } catch (error) {
      console.error('Error saving item:', error);
      alert('Failed to save item');
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-linear-to-br from-[#f5f7fa] to-[#e8ebf0]">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="bg-[#0E186C] p-2 rounded-xl">
                <Coffee className="text-white" size={28} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-[#0E186C]">Admin Dashboard</h1>
                <p className="text-sm text-gray-600">Manage outlets and products</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 bg-red-600 text-white px-6 py-2.5 rounded-xl hover:bg-red-700 transition-colors font-medium"
            >
              <LogOut size={20} />
              <span>Logout</span>
            </button>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            {/* Tabs */}
            <div className="border-b border-gray-200">
              <div className="flex">
                <button
                  onClick={() => setActiveTab('outlets')}
                  className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors border-b-2 ${
                    activeTab === 'outlets'
                      ? 'border-[#0E186C] text-[#0E186C]'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Store size={20} />
                  <span>Outlet Management</span>
                </button>
                <button
                  onClick={() => setActiveTab('products')}
                  className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors border-b-2 ${
                    activeTab === 'products'
                      ? 'border-[#0E186C] text-[#0E186C]'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Package size={20} />
                  <span>Product Management</span>
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-800">
                  {activeTab === 'outlets' ? 'Outlets' : 'Products'}
                </h2>
                <button
                  onClick={handleAdd}
                  className="flex items-center space-x-2 bg-[#0E186C] text-white px-4 py-2 rounded-xl hover:bg-[#0a1150] transition-colors"
                >
                  <Plus size={20} />
                  <span>Add {activeTab === 'outlets' ? 'Outlet' : 'Product'}</span>
                </button>
              </div>

              {isLoading ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-[#0E186C] border-t-transparent"></div>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  {activeTab === 'outlets' ? (
                    <OutletsTable outlets={outlets} onEdit={handleEdit} onDelete={handleDelete} />
                  ) : (
                    <ProductsTable products={products} onEdit={handleEdit} onDelete={handleDelete} />
                  )}
                </div>
              )}
            </div>
          </div>
        </main>

        {/* Modal */}
        {isModalOpen && (
          <ItemModal
            type={activeTab}
            item={editingItem}
            onClose={() => setIsModalOpen(false)}
            onSave={handleSave}
          />
        )}
      </div>
    </ProtectedRoute>
  );
}

// Outlets Table Component
function OutletsTable({
  outlets,
  onEdit,
  onDelete,
}: {
  outlets: Outlet[];
  onEdit: (outlet: Outlet) => void;
  onDelete: (id: number) => void;
}) {
  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Name
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Category
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Address
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Stock
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Actions
          </th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {outlets.map((outlet) => (
          <tr key={outlet.id}>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {outlet.name}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{outlet.category}</td>
            <td className="px-6 py-4 text-sm text-gray-500">{outlet.address}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  outlet.stock ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}
              >
                {outlet.stock ? 'In Stock' : 'Out of Stock'}
              </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                onClick={() => onEdit(outlet)}
                className="text-[#0E186C] hover:text-[#0a1150] mr-4"
              >
                <Pencil size={18} />
              </button>
              <button
                onClick={() => onDelete(outlet.id!)}
                className="text-red-600 hover:text-red-800"
              >
                <Trash2 size={18} />
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Products Table Component
function ProductsTable({
  products,
  onEdit,
  onDelete,
}: {
  products: Product[];
  onEdit: (product: Product) => void;
  onDelete: (id: number) => void;
}) {
  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Name
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Category
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Price
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Image
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Actions
          </th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {products.map((product) => (
          <tr key={product.id}>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {product.name}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.category}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.price}</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {product.image_url && (
                <Image
                  src={product.image_url}
                  alt={product.name}
                  width={40}
                  height={40}
                  className="h-10 w-10 rounded-lg object-cover"
                />
              )}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                onClick={() => onEdit(product)}
                className="text-[#0E186C] hover:text-[#0a1150] mr-4"
              >
                <Pencil size={18} />
              </button>
              <button
                onClick={() => onDelete(product.id!)}
                className="text-red-600 hover:text-red-800"
              >
                <Trash2 size={18} />
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Item Modal Component
function ItemModal({
  type,
  item,
  onClose,
  onSave,
}: {
  type: TabType;
  item: Outlet | Product | null;
  onClose: () => void;
  onSave: (data: Outlet | Product) => void;
}) {
  const initialData = item ||
    (type === 'outlets'
      ? { name: '', category: '', address: '', maps_url: '', stock: 1 }
      : { name: '', link: '', category: '', price: '', image_url: '' });
  
  const [formData, setFormData] = useState(initialData);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'stock' ? parseInt(value) : value,
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X size={24} />
        </button>

        <h2 className="text-2xl font-bold text-[#0E186C] mb-6">
          {item ? 'Edit' : 'Add'} {type === 'outlets' ? 'Outlet' : 'Product'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {type === 'outlets' ? (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <input
                  type="text"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
                <input
                  type="text"
                  name="address"
                  value={'address' in formData ? formData.address : ''}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Maps URL</label>
                <input
                  type="url"
                  name="maps_url"
                  value={'maps_url' in formData ? formData.maps_url : ''}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Stock Status</label>
                <select
                  name="stock"
                  value={'stock' in formData ? formData.stock : 1}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                >
                  <option value={1}>In Stock</option>
                  <option value={0}>Out of Stock</option>
                </select>
              </div>
            </>
          ) : (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Product Link</label>
                <input
                  type="url"
                  name="link"
                  value={'link' in formData ? formData.link : ''}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <input
                  type="text"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Price</label>
                <input
                  type="text"
                  name="price"
                  value={'price' in formData ? formData.price : ''}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Image URL</label>
                <input
                  type="url"
                  name="image_url"
                  value={'image_url' in formData ? formData.image_url : ''}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0E186C]"
                  required
                />
              </div>
            </>
          )}

          <div className="flex space-x-3 pt-4">
            <button
              type="submit"
              className="flex-1 bg-[#0E186C] text-white py-3 rounded-xl font-medium hover:bg-[#0a1150] transition-colors"
            >
              Save
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-xl font-medium hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
