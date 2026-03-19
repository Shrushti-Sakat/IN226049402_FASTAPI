from math import ceil
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Library Book System API")

# In-memory data store
books = [
    {
        "id": 1,
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "genre": "Tech",
        "is_available": True,
    },
    {
        "id": 2,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "genre": "Tech",
        "is_available": True,
    },
    {
        "id": 3,
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "genre": "History",
        "is_available": False,
    },
    {
        "id": 4,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Fiction",
        "is_available": True,
    },
    {
        "id": 5,
        "title": "A Brief History of Time",
        "author": "Stephen Hawking",
        "genre": "Science",
        "is_available": False,
    },
    {
        "id": 6,
        "title": "The Martian",
        "author": "Andy Weir",
        "genre": "Science",
        "is_available": True,
    },
]

borrow_records = []
record_counter = 1
queue = []


class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0, le=60)
    member_id: str = Field(..., min_length=4)
    member_type: str = Field(default="regular", min_length=3)


class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True


# Day 3 helper functions

def find_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return None


def calculate_due_date(borrow_days: int, member_type: str = "regular") -> str:
    normalized_type = member_type.lower()
    if normalized_type == "premium":
        if borrow_days > 60:
            raise ValueError("Premium members can borrow for up to 60 days")
    else:
        if borrow_days > 30:
            raise ValueError("Regular members can borrow for up to 30 days")

    return f"Return by: Day {15 + borrow_days}"


def filter_books_logic(
    source_books: list,
    genre: Optional[str] = None,
    author: Optional[str] = None,
    is_available: Optional[bool] = None,
):
    filtered = source_books

    if genre is not None:
        filtered = [
            book for book in filtered if book["genre"].lower() == genre.lower()
        ]

    if author is not None:
        filtered = [
            book for book in filtered if author.lower() in book["author"].lower()
        ]

    if is_available is not None:
        filtered = [
            book for book in filtered if book["is_available"] == is_available
        ]

    return filtered


def build_borrow_record(
    member_name: str,
    member_id: str,
    member_type: str,
    book: dict,
    borrow_days: int,
):
    global record_counter

    due_date = calculate_due_date(borrow_days, member_type)
    record = {
        "record_id": record_counter,
        "member_name": member_name,
        "member_id": member_id,
        "member_type": member_type.lower(),
        "book_id": book["id"],
        "book_title": book["title"],
        "borrow_days": borrow_days,
        "due_date": due_date,
        "status": "borrowed",
    }
    borrow_records.append(record)
    record_counter += 1
    return record


def search_books_logic(source_books: list, keyword: str):
    k = keyword.lower()
    return [
        book
        for book in source_books
        if k in book["title"].lower() or k in book["author"].lower()
    ]


def sort_books_logic(source_books: list, sort_by: str, order: str):
    allowed_sort = {"title", "author", "genre"}
    if sort_by not in allowed_sort:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_by. Allowed: title, author, genre",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=400, detail="Invalid order. Allowed: asc, desc"
        )

    reverse = order == "desc"
    return sorted(source_books, key=lambda b: b[sort_by].lower(), reverse=reverse)


def paginate_logic(items: list, page: int, limit: int):
    total = len(items)
    total_pages = ceil(total / limit) if total > 0 else 0
    start = (page - 1) * limit
    paged = items[start : start + limit]
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "items": paged,
    }


@app.get("/")
def home():
    return {"message": "Welcome to City Public Library"}


# Q2
@app.get("/books")
def get_books():
    available_count = len([b for b in books if b["is_available"]])
    return {"books": books, "total": len(books), "available_count": available_count}


# Q4
@app.get("/borrow-records")
def get_borrow_records():
    return {"borrow_records": borrow_records, "total": len(borrow_records)}


# Q5 - fixed route above /books/{book_id}
@app.get("/books/summary")
def get_books_summary():
    genre_breakdown = {}
    for book in books:
        genre = book["genre"]
        genre_breakdown[genre] = genre_breakdown.get(genre, 0) + 1

    available_count = len([b for b in books if b["is_available"]])
    borrowed_count = len(books) - available_count

    return {
        "total_books": len(books),
        "available_count": available_count,
        "borrowed_count": borrowed_count,
        "genre_breakdown": genre_breakdown,
    }


# Q10
@app.get("/books/filter")
def filter_books(
    genre: Optional[str] = None,
    author: Optional[str] = None,
    is_available: Optional[bool] = None,
):
    filtered = filter_books_logic(books, genre, author, is_available)
    return {"books": filtered, "count": len(filtered)}


# Q16
@app.get("/books/search")
def search_books(keyword: str = Query(..., min_length=1)):
    result = search_books_logic(books, keyword)
    if not result:
        return {
            "message": "No books found for the given keyword",
            "total_found": 0,
            "books": [],
        }
    return {"keyword": keyword, "total_found": len(result), "books": result}


# Q17
@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    sorted_books = sort_books_logic(books, sort_by, order)
    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_books),
        "books": sorted_books,
    }


# Q18
@app.get("/books/page")
def paginate_books(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=3, ge=1, le=10),
):
    payload = paginate_logic(books, page, limit)
    return {
        "page": payload["page"],
        "limit": payload["limit"],
        "total": payload["total"],
        "total_pages": payload["total_pages"],
        "books": payload["items"],
    }


# Q20
@app.get("/books/browse")
def browse_books(
    keyword: Optional[str] = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=3, ge=1, le=20),
):
    filtered = books

    if keyword is not None:
        filtered = search_books_logic(filtered, keyword)

    sorted_data = sort_books_logic(filtered, sort_by, order)
    paged = paginate_logic(sorted_data, page, limit)

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": paged["page"],
        "limit": paged["limit"],
        "total": paged["total"],
        "total_pages": paged["total_pages"],
        "books": paged["items"],
    }


# Q11
@app.post("/books")
def create_book(payload: NewBook, response: Response):
    duplicate = next(
        (b for b in books if b["title"].strip().lower() == payload.title.strip().lower()),
        None,
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="Book title already exists")

    new_id = max([b["id"] for b in books], default=0) + 1
    book = {
        "id": new_id,
        "title": payload.title,
        "author": payload.author,
        "genre": payload.genre,
        "is_available": payload.is_available,
    }
    books.append(book)
    response.status_code = 201
    return book


# Q14
@app.post("/queue/add")
def add_to_queue(member_name: str = Query(..., min_length=2), book_id: int = Query(..., gt=0)):
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    if book["is_available"]:
        raise HTTPException(
            status_code=400,
            detail="Book is currently available. Borrow directly instead of joining queue",
        )

    existing = next(
        (
            q
            for q in queue
            if q["book_id"] == book_id
            and q["member_name"].strip().lower() == member_name.strip().lower()
        ),
        None,
    )
    if existing:
        raise HTTPException(status_code=400, detail="Member already in queue for this book")

    queue_item = {"member_name": member_name, "book_id": book_id}
    queue.append(queue_item)
    return {"message": "Added to queue", "queue_item": queue_item}


# Q14
@app.get("/queue")
def get_queue():
    return {"queue": queue, "total_waiting": len(queue)}


# Q19 fixed routes
@app.get("/borrow-records/search")
def search_borrow_records(member_name: str = Query(..., min_length=1)):
    result = [
        record
        for record in borrow_records
        if member_name.lower() in record["member_name"].lower()
    ]
    return {
        "member_name": member_name,
        "total_found": len(result),
        "borrow_records": result,
    }


# Q19 fixed routes
@app.get("/borrow-records/page")
def paginate_borrow_records(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=3, ge=1, le=20),
):
    payload = paginate_logic(borrow_records, page, limit)
    return {
        "page": payload["page"],
        "limit": payload["limit"],
        "total": payload["total"],
        "total_pages": payload["total_pages"],
        "borrow_records": payload["items"],
    }


# Q3 - variable route placed after fixed /books/* routes
@app.get("/books/{book_id}")
def get_book_by_id(book_id: int):
    book = find_book(book_id)
    if book is None:
        return {"error": "Book not found"}
    return book


# Q8 + Q9
@app.post("/borrow")
def borrow_book(payload: BorrowRequest):
    book = find_book(payload.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    if not book["is_available"]:
        raise HTTPException(status_code=400, detail="Book is currently unavailable")

    try:
        record = build_borrow_record(
            member_name=payload.member_name,
            member_id=payload.member_id,
            member_type=payload.member_type,
            book=book,
            borrow_days=payload.borrow_days,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    book["is_available"] = False
    return record


# Q12
@app.put("/books/{book_id}")
def update_book(
    book_id: int,
    genre: Optional[str] = None,
    is_available: Optional[bool] = None,
):
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    if genre is not None:
        book["genre"] = genre
    if is_available is not None:
        book["is_available"] = is_available

    return book


# Q13
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    books.remove(book)
    return {"message": f"Deleted book: {book['title']}"}


# Q15
@app.post("/return/{book_id}")
def return_book(book_id: int):
    book = find_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    book["is_available"] = True

    waiting_index = next((i for i, q in enumerate(queue) if q["book_id"] == book_id), None)
    if waiting_index is None:
        return {
            "message": "returned and available",
            "book_id": book_id,
            "book_title": book["title"],
        }

    next_in_line = queue.pop(waiting_index)

    auto_record = build_borrow_record(
        member_name=next_in_line["member_name"],
        member_id="QUEUE-AUTO",
        member_type="regular",
        book=book,
        borrow_days=7,
    )
    book["is_available"] = False

    return {
        "message": "returned and re-assigned",
        "book_id": book_id,
        "book_title": book["title"],
        "auto_assigned_to": next_in_line["member_name"],
        "borrow_record": auto_record,
    }
