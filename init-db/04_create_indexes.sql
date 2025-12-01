-- Customers
CREATE INDEX IF NOT EXISTS idx_customers_city_id
ON customers(city_id);

CREATE INDEX IF NOT EXISTS idx_customers_category_id
ON customers(category_id);

-- Phone Numbers
CREATE INDEX IF NOT EXISTS idx_phone_numbers_customer_id
ON phone_numbers(customer_id);

-- Calls
-- Fast join for outgoing calls
CREATE INDEX IF NOT EXISTS idx_calls_from_customer_id
ON calls(from_customer_id);

-- Fast join for incoming calls
CREATE INDEX IF NOT EXISTS idx_calls_to_customer_id
ON calls(to_customer_id);

-- Index for started_at for monthly/yearly aggregation
CREATE INDEX IF NOT EXISTS idx_calls_started_at
ON calls(started_at);

-- Composite index for fast aggregation: customer + date
CREATE INDEX IF NOT EXISTS idx_calls_customer_started_at
ON calls(from_customer_id, started_at);

-- Partial index for only finished calls (speeds up debt and aggregation queries)
CREATE INDEX IF NOT EXISTS idx_calls_finished
ON calls(from_customer_id)
WHERE status = 'FINISHED';

-- Payments
CREATE INDEX IF NOT EXISTS idx_payments_customer_id
ON payments(customer_id);

CREATE INDEX IF NOT EXISTS idx_payments_created_at
ON payments(created_at);

-- Categories
CREATE INDEX IF NOT EXISTS idx_categories_rate_id
ON categories(rate_id);

-- Cities
CREATE INDEX IF NOT EXISTS idx_cities_country_id
ON cities(country_id);
