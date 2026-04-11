CREATE TABLE IF NOT EXISTS routes (
  route_id SERIAL PRIMARY KEY,
  origin_city TEXT NOT NULL,
  destination_city TEXT NOT NULL,
  route_type TEXT NOT NULL,
  estimated_hours INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suppliers (
  supplier_id SERIAL PRIMARY KEY,
  supplier_name TEXT NOT NULL,
  city TEXT NOT NULL,
  country_code TEXT NOT NULL,
  reliability_score NUMERIC(5,2) NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shipments (
  shipment_id SERIAL PRIMARY KEY,
  route_id INTEGER REFERENCES routes(route_id),
  supplier_id INTEGER REFERENCES suppliers(supplier_id),
  departure_ts TIMESTAMP NOT NULL,
  expected_arrival_ts TIMESTAMP NOT NULL,
  status TEXT NOT NULL,
  temperature_threshold_c NUMERIC(4,1) DEFAULT 8.0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO routes (origin_city, destination_city, route_type, estimated_hours)
VALUES
  ('Hamburg', 'Berlin', 'domestic', 4),
  ('Munich', 'Frankfurt', 'domestic', 5),
  ('Cologne', 'Stuttgart', 'domestic', 6)
ON CONFLICT DO NOTHING;

INSERT INTO suppliers (supplier_name, city, country_code, reliability_score)
VALUES
  ('NordLogistik GmbH', 'Hamburg', 'DE', 92.50),
  ('Bayern Freight AG', 'Munich', 'DE', 88.30),
  ('Rhein Cargo GmbH', 'Cologne', 'DE', 85.40)
ON CONFLICT DO NOTHING;

INSERT INTO shipments (route_id, supplier_id, departure_ts, expected_arrival_ts, status)
VALUES
  (1, 1, NOW() - INTERVAL '2 hours', NOW() + INTERVAL '2 hours', 'in_transit'),
  (2, 2, NOW() - INTERVAL '1 hours', NOW() + INTERVAL '4 hours', 'in_transit'),
  (3, 3, NOW() - INTERVAL '4 hours', NOW() + INTERVAL '2 hours', 'delayed')
ON CONFLICT DO NOTHING;
