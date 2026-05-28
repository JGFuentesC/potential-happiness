-- sql/silver/02_silver_users.sql
-- Transform bronze users → silver users
-- Redacts password, normalizes email, flattens nested structures

CREATE OR REPLACE TABLE fakestore_silver.silver_users AS
SELECT
  id AS user_id,
  username,
  LOWER(TRIM(email)) AS email,
  '(redacted)' AS password_hash,
  name.firstname AS first_name,
  name.lastname AS last_name,
  phone,
  address.street,
  address.city,
  address.zipcode,
  address.number AS address_number,
  address.geolocation.lat AS geo_lat,
  address.geolocation.long AS geo_long,
  _ingested_at
FROM fakestore_raw.raw_users;
