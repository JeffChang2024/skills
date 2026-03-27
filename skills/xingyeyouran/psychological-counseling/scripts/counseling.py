import sys
import json
import urllib.request
import urllib.error

GET_RESULT_URL = "https://ms.jr.jd.com/gw2/generic/hyqy/na/m/getResult"


def counseling(question: str, order_no: str, credential: str) -> str:
    print("Counseling question is: " + question)
    if credential is None:
        return "Please enter your counseling credential"

    payload = json.dumps({
        "question": question,
        "orderNo": order_no,
        "credential": credential
    }).encode("utf-8")

    req = urllib.request.Request(
        GET_RESULT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8")).get("resultData")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Counseling request failed: {e}") from e

    if body.get("responseCode") != 200:
        raise RuntimeError(
            f"Counseling failed: {body.get('responseMessage', 'unknown error')}"
        )

    pay_status = body.get("payStatus")
    print(f"PAY_STATUS: {pay_status}")

    answer = body.get("answer")
    if not answer:
        raise RuntimeError("Counseling response missing 'answer'")

    return answer


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: counseling.py <question> <order_no> <credential>")
        sys.exit(1)

    question = sys.argv[1]
    order_no = sys.argv[2]
    credential = sys.argv[3]
    
    try:
        result = counseling(question, order_no, credential)
        print(result)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


