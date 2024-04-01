CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    domain VARCHAR(255) NOT NULL UNIQUE,
    linkedin_endpoint VARCHAR(1024) UNIQUE,
    linkedin_jobs_endpoint VARCHAR(4096) UNIQUE,
    description TEXT,
    location VARCHAR(1024),
    founded_year INT,
    industry VARCHAR(512),
    head_count INT,
    logo_url VARCHAR(1024),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON companies (domain);
CREATE INDEX ON companies (linkedin_endpoint);
CREATE INDEX ON companies (linkedin_jobs_endpoint);