-- Create the app user
CREATE USER app_user WITH PASSWORD '11111111';

-- Grant permissions to connect and use public schema
GRANT CONNECT ON DATABASE course_project TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;

-- Grant permissions to use all tables in public schema
GRANT SELECT, INSERT, UPDATE, DELETE
    ON ALL TABLES IN SCHEMA public TO app_user;

-- Grant permissions to use future tables in public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

-- Grant permissions to use all sequences in public schema
GRANT USAGE, SELECT, UPDATE
    ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Grant permissions to use future sequences in public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO app_user;
