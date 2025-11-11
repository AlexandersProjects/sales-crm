/**
 * API client for Sales CRM backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Tenants API
export const fetchTenants = async () => {
  const response = await fetch(`${API_URL}/api/tenants`);
  if (!response.ok) throw new Error('Failed to fetch tenants');
  return response.json();
};

export const createTenant = async (tenantData) => {
  const response = await fetch(`${API_URL}/api/tenants`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tenantData),
  });
  if (!response.ok) throw new Error('Failed to create tenant');
  return response.json();
};

// Leads API
export const fetchLeads = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.tenant_id) params.append('tenant_id', filters.tenant_id);
  if (filters.status) params.append('status', filters.status);

  const response = await fetch(`${API_URL}/api/leads?${params}`);
  if (!response.ok) throw new Error('Failed to fetch leads');
  return response.json();
};

export const createLead = async (leadData) => {
  const response = await fetch(`${API_URL}/api/leads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(leadData),
  });
  if (!response.ok) throw new Error('Failed to create lead');
  return response.json();
};

export const updateLead = async (leadId, leadData) => {
  const response = await fetch(`${API_URL}/api/leads/${leadId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(leadData),
  });
  if (!response.ok) throw new Error('Failed to update lead');
  return response.json();
};

export const deleteLead = async (leadId) => {
  const response = await fetch(`${API_URL}/api/leads/${leadId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete lead');
};

// AI Email Generation API
export const generateEmail = async (emailData) => {
  const response = await fetch(`${API_URL}/api/ai/generate-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(emailData),
  });
  if (!response.ok) throw new Error('Failed to generate email');
  return response.json();
};

