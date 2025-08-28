from fastapi import FastAPI, status

from app import models

app = FastAPI(title="Library API")


@app.post("/books", status_code=status.HTTP_201_CREATED)
def add_book(book: models.Book):
    """Create new book record."""
    ...


@app.delete("/books/{serial_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(serial_number: str):
    """Remove book record."""
    ...


@app.get("/books", status_code=status.HTTP_200_OK)
def list_books() -> list[models.Book]:
    """List all avialable books."""
    ...


@app.post("/books/{serial_number}/status", status_code=status.HTTP_200_OK)
def uptade_book_status(serial_number: str, payload: models.BookStatusChange):
    """
    If the book is taken, close the active loan (add return date).
    If the book is available, create a new loan record.
    """
    ...
