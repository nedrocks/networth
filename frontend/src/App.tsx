import React, { useEffect, useState } from 'react';
import { Item, ItemList } from './types';
import { useTheme } from './contexts/ThemeContext';
import { ThemeSwitch } from './components/ThemeSwitch';

function App() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { theme } = useTheme();

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/items');
      if (!response.ok) {
        throw new Error('Failed to fetch items');
      }
      const data: ItemList = await response.json();
      setItems(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      completed: {
        light: 'bg-green-100 text-green-800 border-green-200',
        dark: 'bg-green-900 text-green-100 border-green-800'
      },
      in_progress: {
        light: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        dark: 'bg-yellow-900 text-yellow-100 border-yellow-800'
      },
      pending: {
        light: 'bg-gray-100 text-gray-800 border-gray-200',
        dark: 'bg-gray-700 text-gray-100 border-gray-600'
      }
    };

    const statusKey = status.toLowerCase() as keyof typeof colors;
    return colors[statusKey]?.[theme] || colors.pending[theme];
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center dark:bg-gray-900 transition-colors duration-200">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary dark:border-blue-400"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center dark:bg-gray-900 transition-colors duration-200">
        <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-100 px-4 py-3 rounded-lg shadow-sm" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'
    }`}>
      <ThemeSwitch />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight dark:text-white transition-colors duration-200">
            Items List
          </h1>
          <p className="mt-4 text-xl text-gray-600 dark:text-gray-400 transition-colors duration-200">
            Manage and track your items
          </p>
        </header>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <article
              key={item.id}
              className={`rounded-lg shadow-sm overflow-hidden transition-all duration-200 ${
                theme === 'dark' 
                  ? 'bg-gray-800 hover:bg-gray-750' 
                  : 'bg-white hover:shadow-md'
              }`}
            >
              <div className="p-6">
                <h2 className="text-xl font-semibold mb-2 dark:text-white transition-colors duration-200">
                  {item.name}
                </h2>
                <p className="text-gray-600 dark:text-gray-300 mb-4 transition-colors duration-200">
                  {item.description}
                </p>
                <div className="flex items-center justify-between">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(item.status)} transition-colors duration-200`}>
                    {item.status.replace('_', ' ')}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400 transition-colors duration-200">
                    ID: {item.id}
                  </span>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;