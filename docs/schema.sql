-- PostgreSQL schema

CREATE TABLE stores (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  location TEXT,
  instacart_store_id TEXT,
  active BOOLEAN DEFAULT TRUE
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  normalized_unit TEXT
);

CREATE TABLE product_variants (
  id SERIAL PRIMARY KEY,
  product_id INT REFERENCES products(id),
  brand TEXT,
  size TEXT,
  unit TEXT,
  upc TEXT,
  normalized_size TEXT
);

CREATE TABLE price_observations (
  id SERIAL PRIMARY KEY,
  product_variant_id INT REFERENCES product_variants(id),
  store_id INT REFERENCES stores(id),
  price NUMERIC(10,2),
  date DATE,
  source_type TEXT,
  source_ref TEXT
);

CREATE TABLE circulars (
  id SERIAL PRIMARY KEY,
  store_id INT REFERENCES stores(id),
  week_start DATE,
  source_url TEXT,
  raw_file_path TEXT
);

CREATE TABLE circular_items (
  id SERIAL PRIMARY KEY,
  circular_id INT REFERENCES circulars(id),
  raw_text TEXT,
  product_variant_id INT REFERENCES product_variants(id),
  price NUMERIC(10,2),
  size TEXT
);

CREATE TABLE instacart_items (
  id SERIAL PRIMARY KEY,
  store_id INT REFERENCES stores(id),
  url TEXT,
  raw_text TEXT,
  product_variant_id INT REFERENCES product_variants(id),
  price NUMERIC(10,2),
  size TEXT
);

CREATE TABLE receipts (
  id SERIAL PRIMARY KEY,
  store_id INT REFERENCES stores(id),
  uploaded_at TIMESTAMP DEFAULT NOW(),
  raw_file_path TEXT
);

CREATE TABLE receipt_items (
  id SERIAL PRIMARY KEY,
  receipt_id INT REFERENCES receipts(id),
  raw_text TEXT,
  product_variant_id INT REFERENCES product_variants(id),
  price NUMERIC(10,2)
);

CREATE TABLE crowd_submissions (
  id SERIAL PRIMARY KEY,
  store_id INT REFERENCES stores(id),
  product_variant_id INT REFERENCES product_variants(id),
  price NUMERIC(10,2),
  submitted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE confidence_scores (
  id SERIAL PRIMARY KEY,
  product_variant_id INT REFERENCES product_variants(id),
  store_id INT REFERENCES stores(id),
  score NUMERIC(4,2),
  updated_at TIMESTAMP DEFAULT NOW()
);
