ALTER TABLE books
    ADD CONSTRAINT ck_book_serial_number_6digits
    CHECK (serial_number ~ '^[0-9]{6}$');

ALTER TABLE clients
    ADD CONSTRAINT ck_client_card_number_6digits
    CHECK (card_number ~ '^[0-9]{6}$');

ALTER TABLE loans
  ADD CONSTRAINT ck_loans_return_after_borrow
  CHECK (returned_at IS NULL OR returned_at >= borrowed_at);
