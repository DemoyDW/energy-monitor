-- Energy monitor schema

-- Settlement table
CREATE TABLE settlement (
    settlement_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

-- Energy price table 
CREATE TABLE energy_price(
    energy_price_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    price int NOT NULL,
    settlement_id int NOT NULL,
    FOREIGN KEY(settlement_id) REFERENCES settlement(settlement_id)
    );

-- Demand table 
CREATE TABLE demand(
    demand_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    demand int NOT NULL,
    settlement_id int NOT NULL,
    FOREIGN KEY(settlement_id) REFERENCES settlement(settlement_id)
    );

-- Import table 
CREATE TABLE import(
    import_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    settlement_id int NOT NULL,
    belgium int NOT NULL,
    france int NOT NULL,
    netherlands int NOT NULL,
    denmark int NOT NULL,
    norway int NOT NULL,
    ireland int NOT NULL,
    n_ireland int NOT NULL,
    FOREIGN KEY(settlement_id) REFERENCES settlement(settlement_id)
    );

-- Category table
CREATE TABLE category (
    category_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category VARCHAR(100) NOT NULL
);

-- Outage table 
CREATE TABLE outage (
    outage_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    start_time TIMESTAMP,
    etr TIMESTAMP,
    category_id int NOT NULL,
    settlement_id int NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(category_id),
    FOREIGN KEY(settlement_id) REFERENCES settlement(settlement_id)
    );


-- region table
CREATE TABLE region (
    region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL
);


-- Postcode table
CREATE TABLE postcode (
    postcode_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    postcode VARCHAR(100) NOT NULL UNIQUE,
    region_id int NOT NULL,
    FOREIGN KEY(region_id) REFERENCES region(region_id)

);

-- Outage postcode link table
CREATE TABLE outage_postcode_link (
    outage_postcode_link_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    postcode_id int NOT NULL,
    outage_id int NOT NULL,
    FOREIGN KEY(outage_id) REFERENCES outage(outage_id),
    FOREIGN KEY(postcode_id) REFERENCES postcode(postcode_id)
);


-- Customer table
CREATE TABLE customer (
    customer_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL, 
    email VARCHAR(100) NOT NULL UNIQUE,
    postcode_id int NOT NULL,
    FOREIGN KEY(postcode_id) REFERENCES postcode(postcode_id)
);


-- Reading Type table
CREATE TABLE reading_type (
    reading_type_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reading_type VARCHAR(100) NOT NULL
);


-- Reading table 
CREATE TABLE reading(
    reading_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    settlement_id int NOT NULL,
    region_id int NOT NULL,  
    reading_type_id int NOT NULL,      
    gas float NOT NULL,
    coal float NOT NULL,
    biomass float NOT NULL,
    nuclear float NOT NULL,
    hydro float NOT NULL,
    imports float NOT NULL,
    other float NOT NULL,
    wind float NOT NULL,
    solar float NOT NULL,
    FOREIGN KEY(settlement_id) REFERENCES settlement(settlement_id),
    FOREIGN KEY(region_id) REFERENCES region(region_id),
    FOREIGN KEY(reading_type_id) REFERENCES reading_type(reading_type_id)   
    );
