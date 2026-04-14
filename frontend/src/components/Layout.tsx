import React from 'react';
import { useNavigate, Link } from 'react-router-dom';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const username = localStorage.getItem('username');

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-sap-header text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <Link to="/" className="text-xl font-bold flex items-center">
            <span className="mr-2 text-2xl">📦</span> HANA Auth Service Portal
          </Link>
          {username && (
            <div className="flex items-center gap-4">
              <span className="text-sm opacity-90">Welcome, {username}</span>
              <button 
                onClick={handleLogout}
                className="text-sm border border-white/30 px-3 py-1 rounded hover:bg-white/10 transition-colors"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </nav>
      <main className="flex-grow container mx-auto py-8 px-4">
        {children}
      </main>
    </div>
  );
};

export default Layout;
