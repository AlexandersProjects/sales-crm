import React from 'react';
import './LeadList.css';

function LeadList({ leads, loading, onEdit, onDelete, onGenerateEmail }) {
  if (loading) {
    return (
      <div className="lead-list-container">
        <div className="loading">Loading leads...</div>
      </div>
    );
  }

  if (leads.length === 0) {
    return (
      <div className="lead-list-container">
        <div className="empty-state">
          <h3>📋 No leads yet</h3>
          <p>Create your first lead using the form on the left.</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    const colors = {
      new: '#3b82f6',
      contacted: '#8b5cf6',
      qualified: '#10b981',
      proposal: '#f59e0b',
      negotiation: '#ef4444',
      won: '#22c55e',
      lost: '#6b7280',
    };
    return colors[status] || '#6b7280';
  };

  return (
    <div className="lead-list-container">
      <h2>Leads ({leads.length})</h2>
      <div className="lead-grid">
        {leads.map((lead) => (
          <div key={lead.id} className="lead-card">
            <div className="lead-header">
              <h3>{lead.name}</h3>
              <span
                className="status-badge"
                style={{ backgroundColor: getStatusColor(lead.status) }}
              >
                {lead.status}
              </span>
            </div>

            <div className="lead-details">
              {lead.company && (
                <div className="detail-item">
                  <span className="icon">🏢</span>
                  <span>{lead.company}</span>
                </div>
              )}
              {lead.email && (
                <div className="detail-item">
                  <span className="icon">✉️</span>
                  <a href={`mailto:${lead.email}`}>{lead.email}</a>
                </div>
              )}
              {lead.phone && (
                <div className="detail-item">
                  <span className="icon">📞</span>
                  <a href={`tel:${lead.phone}`}>{lead.phone}</a>
                </div>
              )}
              {lead.notes && (
                <div className="detail-item notes">
                  <span className="icon">📝</span>
                  <span>{lead.notes}</span>
                </div>
              )}
            </div>

            <div className="lead-actions">
              <button
                className="action-btn edit-btn"
                onClick={() => onEdit(lead)}
                title="Edit lead"
              >
                ✏️ Edit
              </button>
              <button
                className="action-btn email-btn"
                onClick={() => onGenerateEmail(lead)}
                title="Generate AI email"
              >
                🤖 Email
              </button>
              <button
                className="action-btn delete-btn"
                onClick={() => onDelete(lead.id)}
                title="Delete lead"
              >
                🗑️
              </button>
            </div>

            <div className="lead-footer">
              <small>Created: {new Date(lead.created_at).toLocaleDateString()}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default LeadList;

