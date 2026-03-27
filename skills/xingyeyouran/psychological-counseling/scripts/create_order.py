import sys
import json
import urllib.request
import urllib.error

CREATE_ORDER_URL = "https://ms.jr.jd.com/gw2/generic/hyqy/na/m/createOrder"


def create_order(question: str) -> tuple:
    """
    POST the user's question to the createOrder endpoint.
    Returns (order_no, amount) on success, or raises RuntimeError on failure.
    """
    payload = json.dumps({"question": question}).encode("utf-8")
    req = urllib.request.Request(
        CREATE_ORDER_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8")).get("resultData")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Order creation request failed: {e}") from e

    if body.get("responseCode") != 200:
        raise RuntimeError(
            f"Order creation failed: {body.get('message', 'unknown error')}"
        )

    order_no = body.get("orderNo")
    if not order_no:
        raise RuntimeError("Order creation response missing 'orderNo'")

    amount = body.get("amount")
    encrypted_data = body.get("encryptedData")
    pay_to = body.get("payTo")

    return order_no, amount, encrypted_data, pay_to


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: create_order.py <question>")
        sys.exit(1)

    question = sys.argv[1]

    try:
        order_no, amount, encrypted_data, pay_to = create_order(question)
    except RuntimeError as e:
        print(f"订单创建失败: {e}")
        sys.exit(1)

    print(f"ORDER_NO={order_no}")
    print(f"AMOUNT={amount}")
    print(f"ENCRYPTED_DATA={encrypted_data}")
    print(f"PAY_TO={pay_to}")
