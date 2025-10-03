-- Energy monitor schema

-- Category table
CREATE TABLE category (
    category_id INT PRIMARY KEY,
    category    VARCHAR(100) NOT NULL UNIQUE
);

-- Outage table 
CREATE TABLE outage (
    outage_id   VARCHAR(50) PRIMARY KEY,
    start_time  TIMESTAMPTZ,
    etr         TIMESTAMPTZ,
    category_id INT NOT NULL,
    status      VARCHAR(20) NOT NULL CHECK (status IN ('current','historical')),
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);


-- region table
CREATE TABLE region (
    region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL
);


-- Postcode table
CREATE TABLE postcode (
    postcode_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    postcode    VARCHAR(20) NOT NULL UNIQUE
);

-- Outage postcode link table
CREATE TABLE outage_postcode_link (
    outage_postcode_link_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    outage_id   VARCHAR(50) UNIQUE NOT NULL,
    postcode_id INT  UNIQUE NOT NULL,
    CONSTRAINT uq_outage_postcode UNIQUE (outage_id, postcode_id),
    FOREIGN KEY (outage_id)  REFERENCES outage(outage_id),
    FOREIGN KEY (postcode_id) REFERENCES postcode(postcode_id)
);

-- Customer table
CREATE TABLE customer (
    customer_id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_name        VARCHAR(100) NOT NULL,
    customer_email       VARCHAR(100) NOT NULL UNIQUE,
    summary_subscription  BOOLEAN
);


-- Customer postcode link table
CREATE TABLE customer_postcode_link (
    customer_postcode_link_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  INT NOT NULL,
    postcode_id  INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (postcode_id) REFERENCES postcode(postcode_id)
);



-- Power Reading table 
CREATE TABLE power_reading(
    power_reading_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_time TIMESTAMP,    
    biomass float NOT NULL,
    coal float NOT NULL,
    imports float NOT NULL,
    gas float NOT NULL,
    nuclear float NOT NULL,
    other float NOT NULL,
    hydro float NOT NULL,
    solar float NOT NULL,
    wind float NOT NULL,
    price float NOT NULL,
    demand float NOT NULL,
    belgium float NOT NULL,
    denmark float NOT NULL,
    france float NOT NULL,
    ireland float NOT NULL,
    netherlands float NOT NULL,
    n_ireland float NOT NULL,
    norway float NOT NULL
    );



-- Carbon Reading table 
CREATE TABLE carbon_reading(
    carbon_reading_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_time TIMESTAMP,
    carbon_intensity int NOT NULL,
    region_id int NOT NULL,      
    gas float NOT NULL,
    coal float NOT NULL,
    biomass float NOT NULL,
    nuclear float NOT NULL,
    hydro float NOT NULL,
    imports float NOT NULL,
    other float NOT NULL,
    wind float NOT NULL,
    solar float NOT NULL
    );


CREATE INDEX idx_outage_category_id ON outage(category_id);
CREATE INDEX idx_link_postcode_id   ON outage_postcode_link(postcode_id);
CREATE INDEX idx_link_outage_id     ON outage_postcode_link(outage_id);