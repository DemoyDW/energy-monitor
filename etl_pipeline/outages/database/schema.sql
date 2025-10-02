-- Category table (seeded manually, fine as is)
CREATE TABLE category (
    category_id INT PRIMARY KEY,
    category VARCHAR(100) NOT NULL UNIQUE
);

-- Outage table
CREATE TABLE outage (
    outage_id VARCHAR(50) PRIMARY KEY,        
    start_time TIMESTAMPTZ,
    etr TIMESTAMPTZ,
    category_id INT NOT NULL,
    status VARCHAR(20) NOT NULL,                
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);

-- Postcode table
CREATE TABLE postcode (
    postcode_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    postcode VARCHAR(20) NOT NULL UNIQUE
);

-- Outage ↔ Postcode link table
CREATE TABLE outage_postcode_link (
    outage_id VARCHAR(50) NOT NULL,
    postcode_id INT NOT NULL,
    PRIMARY KEY (outage_id, postcode_id),       
    FOREIGN KEY(outage_id) REFERENCES outage(outage_id),
    FOREIGN KEY(postcode_id) REFERENCES postcode(postcode_id)
);

-- Clear out old values (optional, use with care in dev environments)
TRUNCATE TABLE category RESTART IDENTITY CASCADE;

-- Seed categories with fixed IDs
INSERT INTO category (category_id, category) VALUES
    (1,  'HV ISOLATION'),
    (2,  'LV GENERIC'),
    (3,  'LV OVERHEAD'),
    (4,  'LV UNDERGROUND'),
    (5,  'HV OVERHEAD'),
    (6,  'LV ISOLATION'),
    (7,  'LV FUSE'),
    (8,  'HV GENERIC'),
    (9,  'HV DAMAGE'),
    (10, 'LV DAMAGE'),
    (11, 'HV FUSE'),
    (12, 'HV UNDERGROUND'),
    (13, 'EHV OVERHEAD'),
    (14, 'HV PLANT');