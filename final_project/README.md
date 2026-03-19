# FastAPI Final Project - Library Book System

This project implements the **Library Book System** option from the internship final assignment using FastAPI.

## Implemented Concepts (Day 1 to Day 6)

- GET APIs + JSON responses
- POST APIs with Pydantic validation
- Helper functions
- CRUD operations
- Multi-step workflow (borrow queue + return + auto re-assign)
- Search, sorting, and pagination

## Project Files

- `main.py` - complete FastAPI backend
- `requirements.txt` - dependencies
- `screenshots/` - Swagger evidence images for Q1 to Q20

## Screenshots

- All API testing screenshots are stored in `screenshots/`.
- Files follow question-based naming for easy review, for example:
  - `Q1_home_route.png`
  - `Q2_get_all_books.png`
  - `Q20_combined_browse.png`
- Multi-capture questions are saved with numeric suffixes such as `_1`, `_2`, `_3`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open Swagger UI at:

- http://127.0.0.1:8000/docs

## Route Coverage (Task-wise)

### Core
- `GET /`
- `GET /books`
- `GET /books/{book_id}`
- `GET /borrow-records`
- `GET /books/summary`

### Borrow + Validation + Helpers
- `POST /borrow`
- Helpers in code:
  - `find_book(book_id)`
  - `calculate_due_date(borrow_days, member_type)`
  - `filter_books_logic(...)`

### CRUD
- `POST /books`
- `PUT /books/{book_id}`
- `DELETE /books/{book_id}`

### Queue Workflow
- `POST /queue/add`
- `GET /queue`
- `POST /return/{book_id}`

### Filter/Search/Sort/Pagination
- `GET /books/filter`
- `GET /books/search`
- `GET /books/sort`
- `GET /books/page`
- `GET /books/browse`
- `GET /borrow-records/search`
- `GET /borrow-records/page`

## Notes

- Fixed routes are placed before variable routes (for example, `/books/summary` before `/books/{book_id}`).
- Duplicate book title checks are case-insensitive.
- Queue auto-assignment is handled when a returned book has waiting members.
