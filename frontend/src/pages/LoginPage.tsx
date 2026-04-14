import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/token/', { username, password });
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('username', username);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-sap-bg flex flex-col items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-10">
          <span className="text-5xl mb-4 inline-block">📦</span>
          <h1 className="text-2xl font-bold text-sap-darkBlue">HANA Auth Service Portal</h1>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg border-t-4 border-sap-blue p-8">
          <h2 className="text-xl font-semibold text-center mb-8">Login</h2>
          
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-sap-blue focus:border-transparent outline-none transition-all"
                required 
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-sap-blue focus:border-transparent outline-none transition-all"
                required 
              />
            </div>

            {error && <div className="text-red-600 text-sm text-center">{error}</div>}
            
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-sap-blue text-white py-2 rounded font-bold hover:bg-sap-darkBlue transition-colors disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        </div>
        <p className="text-center mt-6 text-gray-500 text-sm">Use your corporate credentials.</p>
      </div>
    </div>
  );
};

export default LoginPage;
