-- Function that calculates charge and duration of the call
CREATE OR REPLACE FUNCTION set_finished_and_price()
RETURNS trigger AS $$
DECLARE
    call_duration_minutes numeric;
    minute_cost numeric;
    discount numeric;
BEGIN
    -- Check if status changed to FINISHED
    IF NEW.status = 'FINISHED' AND (OLD.status IS DISTINCT FROM NEW.status) THEN

        -- Set finished_at timestamp
        NEW.finished_at := NOW();

        -- Calculate duration in minutes
        IF NEW.started_at IS NOT NULL THEN
            call_duration_minutes :=
                EXTRACT(EPOCH FROM (NEW.finished_at - NEW.started_at)) / 60.0;
        ELSE
            call_duration_minutes := 0;
        END IF;

        -- Get minute cost
        SELECT countries.minute_cost
        INTO minute_cost
        FROM customers
        JOIN cities      ON customers.city_id = cities.id
        JOIN countries  ON cities.country_id = countries.id
        WHERE customers.id = NEW.to_customer_id;

        IF minute_cost IS NULL THEN
            RAISE EXCEPTION 'minute_cost not found for customer_id=%', NEW.to_customer_id;
        END IF;

        -- Get discount multiplier
        SELECT categories.discount_mtp
        INTO discount
        FROM customers
        JOIN categories ON customers.category_id = categories.id
        WHERE customers.id = NEW.from_customer_id;

        IF discount IS NULL THEN
            RAISE EXCEPTION 'discount is not found for customer_id=%', NEW.from_customer_id;
        END IF;

        -- Set call charge
        NEW.charge := call_duration_minutes * minute_cost * discount;

        -- Set call duration
        NEW.duration := call_duration_minutes;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function that processes monthly charges for customers
CREATE OR REPLACE FUNCTION process_monthly_charges()
RETURNS void AS $$
DECLARE
    prev_month_start date;
    prev_month_end date;
BEGIN
    prev_month_start := date_trunc('month', current_date) - interval '1 month';
    prev_month_end   := date_trunc('month', current_date);

    INSERT INTO payments (
        customer_id,
        amount,
        status,
        created_at
    )
    SELECT
        c.id AS customer_id,
        (COALESCE(SUM(call.charge), 0) + r.cost) * 1.2 AS amount,
        'PENDING' AS status,
        now() AS created_at
    FROM customers c
    JOIN categories cat ON cat.id = c.category_id
    JOIN rates r ON r.id = cat.rate_id

    LEFT JOIN calls call
        ON call.from_customer_id = c.id
       AND call.status = 'FINISHED'
       AND call.finished_at >= prev_month_start
       AND call.finished_at < prev_month_end

    GROUP BY
        c.id,
        r.cost;
END;
$$ LANGUAGE plpgsql;


-- Row level trigger for calls
DROP TRIGGER IF EXISTS trg_set_finished_and_price ON calls;
CREATE TRIGGER trg_set_finished_and_price
BEFORE UPDATE ON calls
FOR EACH ROW
EXECUTE FUNCTION set_finished_and_price();

-- Cron run for monthly charges calculation (at 00:10 on the 1st day of the month)
SELECT cron.schedule(
    'process_monthly_charges',
    '10 0 * * *',
    $$ SELECT process_monthly_charges() $$
);
