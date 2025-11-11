-- Sales CRM Database Schema

CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    status VARCHAR(50) DEFAULT 'new',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO tenants (name) VALUES ('Demo Company') ON CONFLICT DO NOTHING;
INSERT INTO leads (tenant_id, name, email, company, status) VALUES
    (1, 'John Doe', 'john@acme.com', 'Acme Corp', 'new'),
    (1, 'Jane Smith', 'jane@techstart.com', 'TechStart', 'contacted')
ON CONFLICT DO NOTHING;

