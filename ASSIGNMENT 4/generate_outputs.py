import json
import shutil
import textwrap
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont

import main


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "ASSIGNMENT 1"
CLIENT = TestClient(main.app)


def reset_state(clear_orders: bool = True) -> None:
    main.cart.clear()
    if clear_orders:
        main.orders.clear()


def pretty(data):
    return json.dumps(data, indent=2, ensure_ascii=True)


def get_font(size: int):
    font_candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/Consolas.ttf"),
        Path("C:/Windows/Fonts/cour.ttf"),
    ]
    for font_path in font_candidates:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default()


def render_output_image(title: str, content: str, file_name: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    width = 1700
    margin = 50
    wrap_width = 88
    lines = []
    for block in content.splitlines():
        wrapped = textwrap.wrap(block, width=wrap_width) or [""]
        lines.extend(wrapped)

    title_font = get_font(34)
    body_font = get_font(24)
    line_height = 34
    height = margin * 2 + 70 + max(len(lines), 1) * line_height

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((margin, margin), title, fill="black", font=title_font)

    y = margin + 70
    for line in lines:
        draw.text((margin, y), line, fill="black", font=body_font)
        y += line_height

    image.save(OUTPUT_DIR / file_name)


def ensure_submission_main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    shutil.copy2(BASE_DIR / "main.py", OUTPUT_DIR / "main.py")


def q1() -> str:
    reset_state()
    first = CLIENT.post("/cart/add", params={"product_id": 1, "quantity": 2})
    second = CLIENT.post("/cart/add", params={"product_id": 2, "quantity": 1})

    first_json = first.json()
    second_json = second.json()

    assert first.status_code == 200
    assert second.status_code == 200
    assert first_json["message"] == "Added to cart"
    assert second_json["message"] == "Added to cart"
    assert first_json["cart_item"]["subtotal"] == 998
    assert second_json["cart_item"]["subtotal"] == 99

    return "\n\n".join(
        [
            "Q1 - Add Items to the Cart",
            "POST /cart/add?product_id=1&quantity=2",
            f"Status: {first.status_code}",
            pretty(first_json),
            "POST /cart/add?product_id=2&quantity=1",
            f"Status: {second.status_code}",
            pretty(second_json),
        ]
    )


def q2() -> str:
    response = CLIENT.get("/cart")
    data = response.json()

    assert response.status_code == 200
    assert data["item_count"] == 2
    assert data["grand_total"] == 1097

    return "\n\n".join(
        [
            "Q2 - View the Cart and Verify the Total",
            "GET /cart",
            f"Status: {response.status_code}",
            pretty(data),
        ]
    )


def q3() -> str:
    out_of_stock = CLIENT.post("/cart/add", params={"product_id": 3})
    not_found = CLIENT.post("/cart/add", params={"product_id": 99})
    cart_response = CLIENT.get("/cart")

    out_of_stock_json = out_of_stock.json()
    not_found_json = not_found.json()
    cart_json = cart_response.json()

    assert out_of_stock.status_code == 400
    assert out_of_stock_json["detail"] == "USB Hub is out of stock"
    assert not_found.status_code == 404
    assert not_found_json["detail"] == "Product not found"
    assert cart_json["item_count"] == 2
    assert cart_json["grand_total"] == 1097

    return "\n\n".join(
        [
            "Q3 - Try Adding an Out-of-Stock Product",
            "POST /cart/add?product_id=3",
            f"Status: {out_of_stock.status_code}",
            pretty(out_of_stock_json),
            "POST /cart/add?product_id=99",
            f"Status: {not_found.status_code}",
            pretty(not_found_json),
            "GET /cart",
            f"Status: {cart_response.status_code}",
            pretty(cart_json),
        ]
    )


def q4() -> str:
    add_more = CLIENT.post("/cart/add", params={"product_id": 1, "quantity": 1})
    cart_response = CLIENT.get("/cart")

    add_more_json = add_more.json()
    cart_json = cart_response.json()

    assert add_more.status_code == 200
    assert add_more_json["message"] == "Cart updated"
    assert add_more_json["cart_item"]["quantity"] == 3
    assert add_more_json["cart_item"]["subtotal"] == 1497
    assert cart_json["item_count"] == 2
    assert cart_json["grand_total"] == 1596

    return "\n\n".join(
        [
            "Q4 - Add More Quantity of an Existing Cart Item",
            "POST /cart/add?product_id=1&quantity=1",
            f"Status: {add_more.status_code}",
            pretty(add_more_json),
            "GET /cart",
            f"Status: {cart_response.status_code}",
            pretty(cart_json),
        ]
    )


def q5() -> str:
    remove_item = CLIENT.delete("/cart/2")
    after_remove = CLIENT.get("/cart")
    checkout = CLIENT.post(
        "/cart/checkout",
        json={
            "customer_name": "Ravi Kumar",
            "delivery_address": "123 MG Road, Bangalore 560001",
        },
    )
    empty_cart = CLIENT.get("/cart")
    orders_response = CLIENT.get("/orders")

    remove_json = remove_item.json()
    after_remove_json = after_remove.json()
    checkout_json = checkout.json()
    empty_cart_json = empty_cart.json()
    orders_json = orders_response.json()

    assert remove_item.status_code == 200
    assert after_remove_json["item_count"] == 1
    assert after_remove_json["grand_total"] == 1497
    assert checkout.status_code == 200
    assert checkout_json["grand_total"] == 1497
    assert len(checkout_json["orders_placed"]) == 1
    assert empty_cart_json["message"] == "Cart is empty"
    assert orders_json["total_orders"] == 1

    return "\n\n".join(
        [
            "Q5 - Remove an Item Then Checkout",
            "DELETE /cart/2",
            f"Status: {remove_item.status_code}",
            pretty(remove_json),
            "GET /cart",
            f"Status: {after_remove.status_code}",
            pretty(after_remove_json),
            "POST /cart/checkout",
            f"Status: {checkout.status_code}",
            pretty(checkout_json),
            "GET /cart",
            f"Status: {empty_cart.status_code}",
            pretty(empty_cart_json),
            "GET /orders",
            f"Status: {orders_response.status_code}",
            pretty(orders_json),
        ]
    )


def q6() -> str:
    reset_state()

    customer1_add_mouse = CLIENT.post("/cart/add", params={"product_id": 1, "quantity": 1})
    customer1_add_pen = CLIENT.post("/cart/add", params={"product_id": 4, "quantity": 3})
    customer1_cart = CLIENT.get("/cart")
    customer1_checkout = CLIENT.post(
        "/cart/checkout",
        json={
            "customer_name": "Customer 1",
            "delivery_address": "11 First Street, Hyderabad",
        },
    )
    customer1_empty_cart = CLIENT.get("/cart")
    orders_after_customer1 = CLIENT.get("/orders")

    customer2_add_notebook = CLIENT.post("/cart/add", params={"product_id": 2, "quantity": 2})
    customer2_add_mouse = CLIENT.post("/cart/add", params={"product_id": 1, "quantity": 1})
    customer2_remove_notebook = CLIENT.delete("/cart/2")
    customer2_checkout = CLIENT.post(
        "/cart/checkout",
        json={
            "customer_name": "Customer 2",
            "delivery_address": "22 Second Avenue, Hyderabad",
        },
    )
    final_orders = CLIENT.get("/orders")

    customer1_cart_json = customer1_cart.json()
    customer1_checkout_json = customer1_checkout.json()
    orders_after_customer1_json = orders_after_customer1.json()
    customer2_checkout_json = customer2_checkout.json()
    final_orders_json = final_orders.json()

    assert customer1_add_mouse.status_code == 200
    assert customer1_add_pen.status_code == 200
    assert customer1_cart_json["grand_total"] == 646
    assert len(customer1_checkout_json["orders_placed"]) == 2
    assert customer1_empty_cart.json()["message"] == "Cart is empty"
    assert orders_after_customer1_json["total_orders"] == 2
    assert customer2_add_notebook.status_code == 200
    assert customer2_add_mouse.status_code == 200
    assert customer2_remove_notebook.status_code == 200
    assert len(customer2_checkout_json["orders_placed"]) == 1
    assert final_orders_json["total_orders"] == 3

    return "\n\n".join(
        [
            "Q6 - Full Cart System Flow - 2 Customers, 2 Sessions",
            "Customer 1 - POST /cart/add?product_id=1&quantity=1",
            f"Status: {customer1_add_mouse.status_code}",
            pretty(customer1_add_mouse.json()),
            "Customer 1 - POST /cart/add?product_id=4&quantity=3",
            f"Status: {customer1_add_pen.status_code}",
            pretty(customer1_add_pen.json()),
            "Customer 1 - GET /cart",
            f"Status: {customer1_cart.status_code}",
            pretty(customer1_cart_json),
            "Customer 1 - POST /cart/checkout",
            f"Status: {customer1_checkout.status_code}",
            pretty(customer1_checkout_json),
            "GET /orders after Customer 1",
            f"Status: {orders_after_customer1.status_code}",
            pretty(orders_after_customer1_json),
            "Customer 2 - POST /cart/add?product_id=2&quantity=2",
            f"Status: {customer2_add_notebook.status_code}",
            pretty(customer2_add_notebook.json()),
            "Customer 2 - POST /cart/add?product_id=1&quantity=1",
            f"Status: {customer2_add_mouse.status_code}",
            pretty(customer2_add_mouse.json()),
            "Customer 2 - DELETE /cart/2",
            f"Status: {customer2_remove_notebook.status_code}",
            pretty(customer2_remove_notebook.json()),
            "Customer 2 - POST /cart/checkout",
            f"Status: {customer2_checkout.status_code}",
            pretty(customer2_checkout_json),
            "GET /orders final",
            f"Status: {final_orders.status_code}",
            pretty(final_orders_json),
        ]
    )


def bonus() -> str:
    previous_order_count = len(main.orders)
    main.cart.clear()

    empty_cart = CLIENT.get("/cart")
    checkout = CLIENT.post(
        "/cart/checkout",
        json={
            "customer_name": "Bonus User",
            "delivery_address": "44 Empty Cart Lane",
        },
    )
    orders_response = CLIENT.get("/orders")

    empty_cart_json = empty_cart.json()
    checkout_json = checkout.json()
    orders_json = orders_response.json()

    assert empty_cart_json["message"] == "Cart is empty"
    assert checkout.status_code == 400
    assert orders_json["total_orders"] == previous_order_count

    return "\n\n".join(
        [
            "Bonus - Checkout with Empty Cart",
            "GET /cart",
            f"Status: {empty_cart.status_code}",
            pretty(empty_cart_json),
            "POST /cart/checkout",
            f"Status: {checkout.status_code}",
            pretty(checkout_json),
            "GET /orders",
            f"Status: {orders_response.status_code}",
            pretty(orders_json),
        ]
    )


def main_run() -> None:
    ensure_submission_main()

    outputs = {
        "Q1_Output.png": q1(),
        "Q2_Output.png": q2(),
        "Q3_Output.png": q3(),
        "Q4_Output.png": q4(),
        "Q5_Output.png": q5(),
        "Q6_Output.png": q6(),
        "Bonus_Output.png": bonus(),
    }

    for file_name, content in outputs.items():
        render_output_image(file_name.replace("_", " ").replace(".png", ""), content, file_name)

    print("Assignment outputs generated successfully.")
    for file_name in outputs:
        print(f"- {OUTPUT_DIR / file_name}")


if __name__ == "__main__":
    main_run()