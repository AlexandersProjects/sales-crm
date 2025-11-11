import React, { useState } from 'react';
import { generateEmail } from '../api/client';
import './EmailGenerator.css';

function EmailGenerator({ lead, onClose }) {
  const [tone, setTone] = useState('professional');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedEmail, setGeneratedEmail] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await generateEmail({
        lead_name: lead.name,
        company: lead.company,
        tone: tone,
      });
      setGeneratedEmail(result);
    } catch (err) {
      setError(err.message || 'Failed to generate email. Make sure OpenAI API key is configured.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🤖 AI Email Generator</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="lead-info">
            <h3>{lead.name}</h3>
            {lead.company && <p>🏢 {lead.company}</p>}
            {lead.email && <p>✉️ {lead.email}</p>}
          </div>

          <div className="tone-selector">
            <label>Email Tone:</label>
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              <option value="professional">Professional</option>
              <option value="friendly">Friendly</option>
              <option value="casual">Casual</option>
              <option value="formal">Formal</option>
            </select>
          </div>

          {!generatedEmail && !loading && (
            <button className="generate-btn" onClick={handleGenerate}>
              ✨ Generate Email
            </button>
          )}

          {loading && (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Generating personalized email...</p>
            </div>
          )}

          {error && (
            <div className="error-message">
              <p>⚠️ {error}</p>
            </div>
          )}

          {generatedEmail && (
            <div className="email-result">
              <div className="email-section">
                <div className="email-section-header">
                  <strong>Subject:</strong>
                  <button
                    className="copy-btn"
                    onClick={() => copyToClipboard(generatedEmail.subject)}
                  >
                    ���� Copy
                  </button>
                </div>
                <p className="email-subject">{generatedEmail.subject}</p>
              </div>

              <div className="email-section">
                <div className="email-section-header">
                  <strong>Body:</strong>
                  <button
                    className="copy-btn"
                    onClick={() => copyToClipboard(generatedEmail.body)}
                  >
                    📋 Copy
                  </button>
                </div>
                <pre className="email-body">{generatedEmail.body}</pre>
              </div>

              <div className="email-actions">
                <button className="generate-btn" onClick={handleGenerate}>
                  🔄 Regenerate
                </button>
                <button
                  className="copy-all-btn"
                  onClick={() =>
                    copyToClipboard(
                      `Subject: ${generatedEmail.subject}\n\n${generatedEmail.body}`
                    )
                  }
                >
                  📋 Copy All
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default EmailGenerator;

