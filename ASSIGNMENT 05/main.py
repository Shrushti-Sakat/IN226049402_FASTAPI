from math import ceil

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


app = FastAPI(title="FastAPI Day 6 Assignment")


products = [
    {"id": 1, "name": "Wireless Mouse", "category": "Electronics", "price": 499},
    {"id": 2, "name": "Notebook", "category": "Stationery", "price": 99},
    {"id": 3, "name": "USB Hub", "category": "Electronics", "price": 799},
    {"id": 4, "name": "Pen Set", "category": "Stationery", "price": 49},
]

orders = []


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    product_ids: list[int] = Field(..., min_length=1)


def calculate_total_pages(total_items: int, limit: int) -> int:
    return ceil(total_items / limit) if total_items else 0


def validate_sort_params(sort_by: str, order: str) -> str | None:
    if sort_by not in {"price", "name"}:
        return "sort_by must be 'price' or 'name'"
    if order not in {"asc", "desc"}:
        return "order must be 'asc' or 'desc'"
    return None


@app.get("/")
def home():
    return {
        "message": "FastAPI Day 6 Assignment API",
        "docs": "/docs",
        "total_products": len(products),
        "total_orders": len(orders),
    }


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


@app.get("/products/search")
def search_products(keyword: str = Query(..., min_length=1)):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(results), "products": results}


@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc"),
):
    error = validate_sort_params(sort_by, order)
    if error:
        return {"error": error}

    sorted_products = sorted(
        products,
        key=lambda product: product[sort_by],
        reverse=(order == "desc"),
    )
    return {
        "sort_by": sort_by,
        "order": order,
        "total": len(sorted_products),
        "products": sorted_products,
    }


@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=20),
):
    start = (page - 1) * limit
    paged_products = products[start : start + limit]
    return {
        "page": page,
        "limit": limit,
        "total": len(products),
        "total_pages": calculate_total_pages(len(products), limit),
        "products": paged_products,
    }


@app.get("/orders")
def get_orders():
    return {"orders": orders, "total": len(orders)}


@app.post("/orders")
def create_order(order: OrderCreate):
    selected_products = [product for product in products if product["id"] in order.product_ids]
    if len(selected_products) != len(order.product_ids):
        raise HTTPException(status_code=404, detail="One or more product IDs are invalid")

    new_order = {
        "order_id": len(orders) + 1,
        "customer_name": order.customer_name,
        "product_ids": order.product_ids,
        "products": selected_products,
        "total_amount": sum(product["price"] for product in selected_products),
    }
    orders.append(new_order)
    return {"message": "Order created successfully", "order": new_order}


@app.get("/orders/search")
def search_orders(customer_name: str = Query(..., min_length=1)):
    results = [
        order
        for order in orders
        if customer_name.lower() in order["customer_name"].lower()
    ]
    if not results:
        return {"message": f"No orders found for: {customer_name}"}
    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results,
    }


@app.get("/products/sort-by-category")
def sort_products_by_category():
    sorted_products = sorted(products, key=lambda product: (product["category"], product["price"]))
    return {"products": sorted_products, "total": len(sorted_products)}


@app.get("/products/browse")
def browse_products(
    keyword: str | None = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20),
):
    error = validate_sort_params(sort_by, order)
    if error:
        return {"error": error}

    result = products
    if keyword:
        result = [product for product in result if keyword.lower() in product["name"].lower()]

    result = sorted(
        result,
        key=lambda product: product[sort_by],
        reverse=(order == "desc"),
    )

    total_found = len(result)
    start = (page - 1) * limit
    paged_products = result[start : start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total_found,
        "total_pages": calculate_total_pages(total_found, limit),
        "products": paged_products,
    }


@app.get("/orders/page")
def paginate_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start = (page - 1) * limit
    paged_orders = orders[start : start + limit]
    return {
        "page": page,
        "limit": limit,
        "total": len(orders),
        "total_pages": calculate_total_pages(len(orders), limit),
        "orders": paged_orders,
    }


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")