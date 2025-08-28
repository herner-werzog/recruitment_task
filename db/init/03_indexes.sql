CREATE UNIQUE INDEX IF NOT EXISTS uq_active_loan_per_book
ON loans (serial_number)
WHERE returned_at IS NULL;
