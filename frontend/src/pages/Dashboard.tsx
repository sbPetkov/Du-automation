import React from 'react';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const services = [
    {
      title: 'Delivery Unit Automation',
      description: 'Export and import HANA Delivery Units across your landscape with automated diff checks.',
      path: '/du-automation',
      icon: '📦',
      status: 'Active'
    },
    {
      title: 'Pre/Post System Refresh',
      description: 'Automate the tedious pre-refresh exports and post-refresh imports of system configurations.',
      path: '#',
      icon: '🔄',
      status: 'Coming Soon'
    },
    {
      title: 'User Services',
      description: 'Self-service password resets and user role requests in your HANA databases.',
      path: '#',
      icon: '👤',
      status: 'Coming Soon'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {services.map((service) => (
        <div 
          key={service.title} 
          className={`card bg-white rounded-lg shadow-sm border-0 flex flex-col ${service.status !== 'Active' ? 'opacity-70 grayscale' : ''}`}
        >
          <div className={`p-4 text-center font-bold text-lg rounded-t-lg text-white ${service.status === 'Active' ? 'bg-sap-blue' : 'bg-gray-500'}`}>
            {service.title}
          </div>
          <div className="p-6 text-center flex-grow flex flex-col justify-between">
            <div className="text-4xl mb-4">{service.icon}</div>
            <p className="text-gray-600 mb-6">{service.description}</p>
            {service.status === 'Active' ? (
              <button 
                onClick={() => navigate(service.path)}
                className="w-full py-2 border-2 border-sap-blue text-sap-blue font-bold rounded hover:bg-sap-blue hover:text-white transition-all"
              >
                Open Service
              </button>
            ) : (
              <button disabled className="w-full py-2 border-2 border-gray-300 text-gray-400 font-bold rounded cursor-not-allowed">
                Coming Soon
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default Dashboard;
