from datetime import datetime, timezone

import psycopg
from fastapi import FastAPI, HTTPException, status

from app import models
from app.database import DB

app = FastAPI(title="Library API")


@app.post("/books", status_code=status.HTTP_201_CREATED)
def add_book(book: models.Book, conn=DB):
    """Create new book record."""
    with conn.transaction():
        try:
            conn.execute(
                "INSERT INTO books(serial_number, title, author) VALUES (%s, %s, %s)",
                (book.serial_number, book.title, book.author),
            )
        except psycopg.errors.UniqueViolation:
            raise HTTPException(409, "Book with this serial_number already exists.")


@app.delete("/books/{serial_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(serial_number: str, conn=DB):
    """Remove book record."""
    with conn.transaction():
        cur = conn.execute(
            "DELETE FROM books WHERE serial_number = %s",
            (serial_number,),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Book not found.")


@app.get("/books", status_code=status.HTTP_200_OK)
def list_books(conn=DB) -> list[models.Book]:
    """List all avialable books."""
    rows = conn.execute(
        "SELECT serial_number, title, author FROM books ORDER BY title"
    ).fetchall()
    return [models.Book(serial_number=r[0], title=r[1], author=r[2]) for r in rows]


@app.post("/books/{serial_number}/status", status_code=status.HTTP_200_OK)
def update_book_status(
    serial_number: str, client: models.Client | None = None, conn=DB
):
    """
    If the book is taken, close the active loan (add return date).
    If the book is available, create a new loan record.
    """
    book = conn.execute(
        "SELECT 1 FROM books WHERE serial_number = %s",
        (serial_number,),
    ).fetchone()
    if not book:
        raise HTTPException(404, "Book not found")

    with conn.transaction():
        active_loan = conn.execute(
            "SELECT id FROM loans WHERE serial_number = %s and returned_at IS NULL",
            (serial_number,),
        ).fetchone()

        if active_loan:
            ts = datetime.now(timezone.utc)
            conn.execute(
                "UPDATE loans SET returned_at = %s WHERE id = %s",
                (ts, active_loan[0]),
            )
            return models.BookStatus(
                serial_number=serial_number,
                status="available",
                returned_at=ts,
            )

        if client is None:
            raise HTTPException(400, "To borrow a book, client is required.")

        conn.execute(
            """
            INSERT INTO clients(card_number, name)
            VALUES (%s, %s)
            ON CONFLICT (card_number)
            DO UPDATE SET name = COALESCE(EXCLUDED.name, clients.name)
            """,
            (client.card_number, client.name),
        )

        try:
            row = conn.execute(
                """
                INSERT INTO loans(serial_number, card_number)
                VALUES (%s, %s)
                RETURNING id, borrowed_at
                """,
                (serial_number, client.card_number),
            ).fetchone()
        except psycopg.errors.UniqueViolation:
            raise HTTPException(409, "Book is already taken.")

    return models.BookStatus(
        serial_number=serial_number,
        status="taken",
        loan_id=row[0],
        borrowed_at=row[1],
    )

@app.get("/health", status_code=status.HTTP_200_OK)
def healthcheck(conn=DB):
    """Check if API and database are healthy."""
    try:
        conn.execute("SELECT 1")
    except Exception:
        raise HTTPException(503, "Database is unavailable")
    return {"status": "ok"}