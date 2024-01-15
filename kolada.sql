-- Table schemas used in the Sqlite database

CREATE TABLE IF NOT EXISTS kpis (
    kpi_id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    municipality_type TEXT CHECK(municipality_type IN ('L', 'K', 'A')),
    is_divided_by_gender BOOLEAN,
    has_organization_values BOOLEAN,
    operating_area TEXT
);

CREATE TABLE IF NOT EXISTS municipalities (
    municipality_id TEXT PRIMARY KEY,
    title TEXT,
    type TEXT CHECK(type IN ('L', 'K'))
);

CREATE TABLE IF NOT EXISTS organizations (
    organization_id TEXT PRIMARY KEY,
    title TEXT,
    municipality_id TEXT,
    FOREIGN KEY(municipality_id) REFERENCES municipality(id)
);


-- Tables for grouping municipalities and kpis
CREATE TABLE IF NOT EXISTS municipality_groups (
    municipality_group_id TEXT PRIMARY KEY,
    title TEXT
);

CREATE TABLE IF NOT EXISTS municipality_group_members (
    municipality_group_id TEXT,
    municipality_id TEXT,
    PRIMARY KEY (municipality_group_id, municipality_id),
    FOREIGN KEY(municipality_group_id) REFERENCES municipality_groups(municipality_group_id),
    FOREIGN KEY(municipality_id) REFERENCES municipalities(municipality_id)
);

CREATE TABLE IF NOT EXISTS kpi_groups (
    kpi_group_id TEXT PRIMARY KEY,
    title TEXT
);

CREATE TABLE IF NOT EXISTS kpi_group_members (
    kpi_group_id TEXT,
    kpi_id TEXT,
    PRIMARY KEY (kpi_group_id, kpi_id),
    FOREIGN KEY(kpi_group_id) REFERENCES kpi_groups(kpi_group_id),
    FOREIGN KEY(kpi_id) REFERENCES kpis(kpi_id)
);


-- Tables for storing data

CREATE TABLE IF NOT EXISTS municipality_data (
    kpi_id TEXT,
    municipality_id TEXT,
    year INTEGER,
    gender TEXT,
    value REAL,
    PRIMARY KEY (kpi_id, municipality_id, year, gender),
    FOREIGN KEY(kpi_id) REFERENCES kpis(kpi_id),
    FOREIGN KEY(municipality_id) REFERENCES municipalities(municipality_id)
);

CREATE TABLE IF NOT EXISTS organization_data (
    kpi_id TEXT,
    organization_id TEXT,
    year INTEGER,
    gender TEXT, 
    value REAL,
    PRIMARY KEY (kpi_id, organization_id, year, gender),
    FOREIGN KEY(kpi_id) REFERENCES kpis(kpi_id),
    FOREIGN KEY(organization_id) REFERENCES organizations(organization_id)
);

