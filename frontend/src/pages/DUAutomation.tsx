import React, { useState, useEffect } from 'react';
import api from '../api';

interface System {
  id: number;
  name: string;
  tenant: string | null;
  stage: string;
  hostname: string;
  alm_port: string;
}

interface TaskStatus {
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILURE';
  filename: string | null;
  diff_text: string | null;
  error_message: string | null;
}

const DUAutomation: React.FC = () => {
  const [systems, setSystems] = useState<System[]>([]);
  const [sourceId, setSourceId] = useState('');
  const [duName, setDuName] = useState('HANA_SIT_AM_TEN_RISE');
  const [duList, setDuList] = useState('');
  const [exportTask, setExportTask] = useState<TaskStatus | null>(null);
  const [importTask, setImportTask] = useState<TaskStatus | null>(null);
  const [selectedStages, setSelectedStages] = useState<string[]>([]);
  const [specificTargetId, setSpecificTargetId] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSystems();
  }, []);

  const fetchSystems = async () => {
    try {
      const res = await api.get('/du-automation/systems/');
      setSystems(res.data);
    } catch (err) {
      console.error('Failed to fetch systems');
    }
  };

  const handleSyncRegistry = async () => {
    setLoading(true);
    try {
      await api.post('/du-automation/sync-systems/');
      alert('Systems synchronized successfully!');
      fetchSystems();
    } catch (err) {
      alert('Failed to sync registry');
    } finally {
      setLoading(false);
    }
  };

  const handleListDUs = async () => {
    if (!sourceId) return alert('Select source system');
    setDuList('Fetching...');
    try {
      const res = await api.get(`/du-automation/list-dus/?system_id=${sourceId}`);
      setDuList(res.data.output);
    } catch (err) {
      setDuList('Error fetching DUs');
    }
  };

  const handleStartExport = async () => {
    if (!sourceId || !duName) return alert('Source system and DU name are required');
    setLoading(true);
    setExportTask({ status: 'PENDING', filename: null, diff_text: null, error_message: null });
    try {
      const res = await api.post('/du-automation/start-export/', { system_id: sourceId, du_name: duName });
      pollTask(res.data.task_id, 'export');
    } catch (err) {
      setExportTask({ status: 'FAILURE', filename: null, diff_text: null, error_message: 'Failed to start export task' });
      setLoading(false);
    }
  };

  const pollTask = async (taskId: number, type: 'export' | 'import') => {
    try {
      const res = await api.get(`/du-automation/task-status/${taskId}/`);
      const data = res.data;
      if (type === 'export') setExportTask(data); else setImportTask(data);

      if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
        setLoading(false);
      } else {
        setTimeout(() => pollTask(taskId, type), 2000);
      }
    } catch (err) {
      setLoading(false);
    }
  };

  const handleDeploy = async () => {
    if (!selectedStages.length && !specificTargetId) return alert('Select target stages or a specific system');
    setLoading(true);
    setImportTask({ status: 'PENDING', filename: null, diff_text: null, error_message: null });
    try {
      const res = await api.post('/du-automation/start-import/', {
        source_id: sourceId,
        stages: selectedStages,
        specific_id: specificTargetId,
        filename: exportTask?.filename,
        du_name: duName
      });
      pollTask(res.data.task_id, 'import');
    } catch (err) {
      setImportTask({ status: 'FAILURE', filename: null, diff_text: null, error_message: 'Failed to start import task' });
      setLoading(false);
    }
  };

  const toggleStage = (stage: string) => {
    setSelectedStages(prev => prev.includes(stage) ? prev.filter(s => s !== stage) : [...prev, stage]);
  };

  const renderDiff = (diff: string | null) => {
    if (!diff) return null;
    return (
      <div className="bg-white border rounded p-4 mt-4 overflow-x-auto">
        <h5 className="font-bold text-gray-500 mb-2">🔍 Diff Viewer</h5>
        <div className="font-mono text-sm whitespace-pre">
          {diff.split('\n').map((line, i) => {
            let color = 'text-gray-700';
            if (line.startsWith('+')) color = 'text-green-700 bg-green-50';
            else if (line.startsWith('-')) color = 'text-red-700 bg-red-50';
            else if (line.startsWith('@@')) color = 'text-blue-600 bg-blue-50 font-bold';
            return <div key={i} className={color}>{line}</div>;
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* 1. Source & Export */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="bg-sap-blue p-4 flex justify-between items-center text-white font-bold">
          <span>1. Source & Export</span>
          <button onClick={handleSyncRegistry} disabled={loading} className="bg-white/20 hover:bg-white/30 px-3 py-1 rounded text-sm transition-colors">
            🔄 Sync Registry
          </button>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="md:col-span-3">
              <label className="block text-sm font-semibold text-gray-600 mb-1">Select Source System</label>
              <select value={sourceId} onChange={(e) => setSourceId(e.target.value)} className="w-full border rounded p-2 outline-none focus:ring-2 focus:ring-sap-blue">
                <option value="">-- Choose Source --</option>
                {systems.map(sys => (
                  <option key={sys.id} value={sys.id}>{sys.name} {sys.tenant ? `(${sys.tenant})` : ''} - {sys.stage} - {sys.hostname}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button onClick={handleListDUs} className="w-full py-2 bg-gray-100 hover:bg-gray-200 rounded font-semibold text-gray-700 transition-colors">
                List Available DUs
              </button>
            </div>
          </div>

          {duList && <pre className="bg-gray-900 text-green-400 p-4 rounded text-sm mb-6 max-h-40 overflow-y-auto">{duList}</pre>}

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-3">
              <label className="block text-sm font-semibold text-gray-600 mb-1">Delivery Unit Name</label>
              <input type="text" value={duName} onChange={(e) => setDuName(e.target.value)} className="w-full border rounded p-2 outline-none focus:ring-2 focus:ring-sap-blue" />
            </div>
            <div className="flex items-end">
              <button onClick={handleStartExport} disabled={loading} className="w-full py-2 bg-sap-blue text-white rounded font-bold hover:bg-sap-darkBlue transition-colors disabled:opacity-50">
                Export & Compare
              </button>
            </div>
          </div>

          {exportTask && (
            <div className="mt-4 p-4 rounded border flex items-center gap-3">
              {exportTask.status === 'RUNNING' && <span className="animate-spin">⏳</span>}
              {exportTask.status === 'SUCCESS' && <span className="text-green-600">✅ Export successful: {exportTask.filename}</span>}
              {exportTask.status === 'FAILURE' && <span className="text-red-600">❌ Export failed: {exportTask.error_message}</span>}
            </div>
          )}

          {exportTask?.diff_text && renderDiff(exportTask.diff_text)}
        </div>
      </div>

      {/* 2. Target & Deploy */}
      {exportTask?.status === 'SUCCESS' && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden animate-in fade-in duration-500">
          <div className="bg-sap-green p-4 text-white font-bold">2. Target & Deploy</div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 p-6 bg-gray-50 rounded-lg border">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-4 uppercase tracking-wider">Bulk Deploy by Stage:</label>
                <div className="flex flex-wrap gap-4">
                  {['P', 'Q', 'T', 'S'].map(stage => (
                    <label key={stage} className="flex items-center gap-2 bg-white px-4 py-2 border rounded cursor-pointer hover:border-sap-green transition-colors shadow-sm">
                      <input type="checkbox" checked={selectedStages.includes(stage)} onChange={() => toggleStage(stage)} className="w-4 h-4 text-sap-green" />
                      <span className="font-semibold text-gray-700">{stage === 'P' ? 'Production' : stage === 'Q' ? 'Quality' : stage === 'T' ? 'Test' : 'Sandbox'} ({stage})</span>
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-4 uppercase tracking-wider">OR Specific System:</label>
                <select value={specificTargetId} onChange={(e) => setSpecificTargetId(e.target.value)} className="w-full border rounded p-2 outline-none focus:ring-2 focus:ring-sap-green bg-white shadow-sm">
                  <option value="">-- Choose specific --</option>
                  {systems.map(sys => (
                    <option key={sys.id} value={sys.id} disabled={sys.id.toString() === sourceId}>{sys.name} {sys.tenant ? `(${sys.tenant})` : ''} - {sys.stage}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end">
              <button onClick={handleDeploy} disabled={loading} className="px-8 py-3 bg-sap-green text-white rounded font-bold hover:bg-green-700 transition-all shadow-md active:scale-95 disabled:opacity-50">
                🚀 Deploy DU
              </button>
            </div>

            {importTask && (
              <div className="mt-6 p-6 rounded border bg-gray-50">
                <h6 className="font-bold mb-3 border-b pb-2">Deployment Status</h6>
                <div className="flex items-center gap-3 mb-4">
                   {importTask.status === 'RUNNING' && <span className="animate-spin text-xl">⏳</span>}
                   {importTask.status === 'SUCCESS' && <span className="text-green-600 text-xl font-bold">✅ Deployment Complete!</span>}
                   {importTask.status === 'FAILURE' && <span className="text-red-600 text-xl font-bold">❌ Deployment Failed</span>}
                </div>
                {importTask.error_message && <pre className="text-xs font-mono bg-white p-4 border rounded whitespace-pre-wrap">{importTask.error_message}</pre>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DUAutomation;
