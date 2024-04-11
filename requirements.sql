-- Create countries table
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    iso2 VARCHAR(255),
    iso3 VARCHAR(255)
);

-- Create cities table
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    country_id INTEGER NOT NULL,
    lat FLOAT,
    lon FLOAT,
    FOREIGN KEY (country_id) REFERENCES countries(id)
);

-- Create weather table
CREATE TABLE IF NOT EXISTS weather (
    id SERIAL PRIMARY KEY,
    city_id INTEGER NOT NULL,
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    forecast_type VARCHAR(255) NOT NULL,
    temperature VARCHAR(255),
    pressure VARCHAR(255),
    humidity VARCHAR(255),
    visibility VARCHAR(255),
    FOREIGN KEY (city_id) REFERENCES cities(id)
);
