import React, { useState, useEffect } from 'react';
import LeadList from './components/LeadList';
import LeadForm from './components/LeadForm';
import EmailGenerator from './components/EmailGenerator';
import { fetchTenants, fetchLeads, createLead, updateLead, deleteLead } from './api/client';
import './App.css';

function App() {
  const [tenants, setTenants] = useState([]);
  const [leads, setLeads] = useState([]);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [editingLead, setEditingLead] = useState(null);
  const [showEmailGenerator, setShowEmailGenerator] = useState(false);
  const [selectedLeadForEmail, setSelectedLeadForEmail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTenants();
  }, []);

  useEffect(() => {
    if (selectedTenant) {
      loadLeads();
    }
  }, [selectedTenant]);

  const loadTenants = async () => {
    try {
      const data = await fetchTenants();
      setTenants(data);
      if (data.length > 0 && !selectedTenant) {
        setSelectedTenant(data[0].id);
      }
    } catch (err) {
      setError('Failed to load tenants');
      console.error(err);
    }
  };

  const loadLeads = async () => {
    try {
      setLoading(true);
      const filters = selectedTenant ? { tenant_id: selectedTenant } : {};
      const data = await fetchLeads(filters);
      setLeads(data);
    } catch (err) {
      setError('Failed to load leads');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLead = async (leadData) => {
    try {
      await createLead({ ...leadData, tenant_id: selectedTenant });
      await loadLeads();
      setEditingLead(null);
    } catch (err) {
      setError('Failed to create lead');
      console.error(err);
    }
  };

  const handleUpdateLead = async (leadId, leadData) => {
    try {
      await updateLead(leadId, leadData);
      await loadLeads();
      setEditingLead(null);
    } catch (err) {
      setError('Failed to update lead');
      console.error(err);
    }
  };

  const handleDeleteLead = async (leadId) => {
    if (window.confirm('Are you sure you want to delete this lead?')) {
      try {
        await deleteLead(leadId);
        await loadLeads();
      } catch (err) {
        setError('Failed to delete lead');
        console.error(err);
      }
    }
  };

  const handleGenerateEmail = (lead) => {
    setSelectedLeadForEmail(lead);
    setShowEmailGenerator(true);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 Sales CRM</h1>
        <p>Manage your leads effectively</p>
      </header>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="app-content">
        <aside className="sidebar">
          <div className="tenant-selector">
            <label>Tenant:</label>
            <select
              value={selectedTenant || ''}
              onChange={(e) => setSelectedTenant(Number(e.target.value))}
            >
              {tenants.map((tenant) => (
                <option key={tenant.id} value={tenant.id}>
                  {tenant.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-section">
            <h2>{editingLead ? 'Edit Lead' : 'New Lead'}</h2>
            <LeadForm
              lead={editingLead}
              onSubmit={editingLead ? handleUpdateLead : handleCreateLead}
              onCancel={() => setEditingLead(null)}
            />
          </div>
        </aside>

        <main className="main-content">
          <LeadList
            leads={leads}
            loading={loading}
            onEdit={setEditingLead}
            onDelete={handleDeleteLead}
            onGenerateEmail={handleGenerateEmail}
          />
        </main>
      </div>

      {showEmailGenerator && selectedLeadForEmail && (
        <EmailGenerator
          lead={selectedLeadForEmail}
          onClose={() => {
            setShowEmailGenerator(false);
            setSelectedLeadForEmail(null);
          }}
        />
      )}
    </div>
  );
}

export default App;

