#!/usr/bin/env python3
"""
Extract ride details from provider email HTML using regex rules.

Usage:
    python extract_rides_xpath.py emails/16e784a8e81c228b.json
    python extract_rides_xpath.py emails/          # process all
    python extract_rides_xpath.py emails/ -o out/  # custom output dir
"""

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path


# ---------------------------------------------------------------------------
# Provider detection
# ---------------------------------------------------------------------------

PROVIDER_DOMAINS = {
    "bolt.eu": "Bolt",
    "taxify.eu": "Bolt",
    "uber.com": "Uber",
    "yandex": "Yandex",
    "lyftmail.com": "Lyft",
}


def detect_provider(email: dict) -> str | None:
    if p := email.get("provider"):
        return p
    sender = email.get("from", "").lower()
    for domain, provider in PROVIDER_DOMAINS.items():
        if domain in sender:
            return provider
    return None


# ---------------------------------------------------------------------------
# Template detection
# ---------------------------------------------------------------------------

def detect_template(provider: str, html_str: str) -> str:
    if provider == "Bolt":
        return "v2" if "captionBold" in html_str else "v1"
    if provider == "Uber":
        return "v2" if "data-testid" in html_str else "v1"
    return "v1"


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def regex_first(html_str: str, pattern: str, group: int = 1, idx: int = 0) -> str | None:
    """Return the idx-th regex match, capturing `group`."""
    matches = list(re.finditer(pattern, html_str, re.DOTALL))
    if len(matches) > idx:
        return matches[idx].group(group).strip()
    return None


def clean(val: str | None) -> str | None:
    """Decode HTML entities and normalize whitespace."""
    if val is None:
        return None
    val = unescape(val)
    val = val.replace("\xa0", " ").strip()
    val = re.sub(r"\s+", " ", val)
    return val or None


# ---------------------------------------------------------------------------
# Currency / amount parsing
# ---------------------------------------------------------------------------

CURRENCY_SYMBOLS = {
    "$": "USD", "€": "EUR", "£": "GBP", "₽": "RUB",
    "₺": "TRY", "zł": "PLN", "ZŁ": "PLN",
}

CURRENCY_CODES = {
    "TRY", "PLN", "EUR", "USD", "GBP", "RUB", "BYN",
}


def parse_currency_amount(total_text: str | None) -> tuple[str | None, float | None]:
    if not total_text:
        return None, None

    text = total_text.strip()

    # "р." prefix = BYN (Belarusian ruble, Cyrillic р)
    if text.startswith("р.") or text.startswith("р."):
        amount_str = text.split(".", 1)[1] if "." in text else text
        amount_str = re.sub(r"[^\d.]", "", amount_str)
        return "BYN", float(amount_str) if amount_str else None

    # Symbol prefix/suffix
    for sym, code in CURRENCY_SYMBOLS.items():
        if sym in text:
            amount_str = re.sub(r"[^\d.]", "", text)
            return code, float(amount_str) if amount_str else None

    # Code prefix like "TRY 98.99" or "PLN 25.94"
    m = re.match(r"([A-Z]{3})\s*([\d.]+)", text)
    if m and m.group(1) in CURRENCY_CODES:
        return m.group(1), float(m.group(2))

    # Fallback: just grab the number
    amount_str = re.sub(r"[^\d.]", "", text)
    return None, float(amount_str) if amount_str else None


# ---------------------------------------------------------------------------
# Per-provider extractors
# ---------------------------------------------------------------------------

def extract_bolt_v1(html_str: str) -> dict:
    addrs = [clean(m) for m in re.findall(
        r'<a href="" style="text-decoration:none; color:rgb\(0, 0, 0\);">([^<]+)</a>', html_str)]

    return {
        "total_text": clean(regex_first(html_str, r'white-space:nowrap[^>]*>([^<]+)</td>')),
        "pickup": addrs[0] if len(addrs) > 0 else None,
        "dropoff": addrs[1] if len(addrs) > 1 else None,
        "driver": clean(regex_first(html_str, r'>(\w[^<]*?) was your driver\.')),
        "distance_text": clean(regex_first(html_str, r'Ride distance</td>\s*<td[^>]*>([^<]+)</td>')),
        "duration_text": clean(regex_first(html_str, r'Ride duration</td>\s*<td[^>]*>([^<]+)</td>')),
        "start_time_text": clean(regex_first(html_str,
            r'<a href=""[^>]*>[^<]+</a>\s*</td>\s*<td[^>]*>\s*(\d{2}:\d{2})\s*</td>')),
        "end_time_text": clean(regex_first(html_str,
            r'border-top:1px solid rgb\(216, 216, 216\)[^>]*>\s*(\d{2}:\d{2})\s*</td>')),
        "payment_method": clean(regex_first(html_str,
            r'vertical-align:text-bottom[^>]*/>([^<]+)</td>')),
        "notes": None,
    }


def extract_bolt_v2(html_str: str) -> dict:
    addrs = [clean(m) for m in re.findall(
        r'<td class="color-contentPrimary">\s*<span>([^<]+)</span>', html_str)]

    hold = regex_first(html_str,
        r'class="bodySmall color-contentPrimary">(A temporary hold[^<]+)</span>')

    return {
        "total_text": clean(regex_first(html_str,
            r'class="captionBold color-contentPrimaryInverted">([^<]+)</span>')),
        "pickup": addrs[0] if len(addrs) > 0 else None,
        "dropoff": addrs[1] if len(addrs) > 1 else None,
        "driver": clean(regex_first(html_str,
            r'class="bodyLarge color-contentPrimary">([^<]+)</span>')),
        "distance_text": clean(regex_first(html_str,
            r'class="bodySmall spacing-bottom-40-sm color-contentSecondary">\s*'
            r'<span>[^<]+</span>\s*•\s*<span>([^<]+)</span>')),
        "duration_text": clean(regex_first(html_str,
            r'class="bodySmall spacing-bottom-40-sm color-contentSecondary">\s*'
            r'<span>([^<]+)</span>')),
        "start_time_text": clean(regex_first(html_str,
            r'word-break: keep-all;">(\d{2}:\d{2})</span>\s*</td>\s*</tr>\s*<tr>')),
        "end_time_text": clean(regex_first(html_str,
            r'word-break: keep-all;">(\d{2}:\d{2})</span>\s*</td>\s*</tr>\s*</table>')),
        "payment_method": clean(regex_first(html_str,
            r'<td align="left" class="bodyLarge\s*">\s*<span>([^<]+)</span>')),
        "notes": clean(hold),
    }


def extract_uber_v1(html_str: str) -> dict:
    # Times: all Uber18_text_p2 black entries that look like times
    times = re.findall(r'class="Uber18_text_p2 black"[^>]*>(\d+:\d+\s*[AP]M)', html_str)

    # Addresses: Uber18_text_p1 black immediately after time
    addr_pairs = re.findall(
        r'class="Uber18_text_p2 black"[^>]*>\d+:\d+\s*[AP]M</td></tr>'
        r'<tr><td class="Uber18_text_p1 black"[^>]*>([^<]+)', html_str)

    # Ride type badge
    ride_type = regex_first(html_str,
        r'border-radius:20px[^>]*>(?:<!--[^>]*>)?\s*(\w[^<]*?)(?:<!--[^>]*>)?\s*</div>')

    # Total: two v1 sub-variants
    total = (regex_first(html_str,
                r'Total\s*\n?\s*<span class="Uber18_text_p2"[^>]*>([^<]+)')
             or regex_first(html_str,
                r'Total</td><td[^>]*class="[^"]*total[^"]*"[^>]*>([^<]+)'))

    return {
        "total_text": clean(total),
        "pickup": clean(addr_pairs[0]) if len(addr_pairs) > 0 else None,
        "dropoff": clean(addr_pairs[1]) if len(addr_pairs) > 1 else None,
        "driver": clean(regex_first(html_str, r'>You rode with ([^<]+)</td>')),
        "distance_text": clean(regex_first(html_str,
            r'white-space:nowrap[^>]*>([^|<]+)\s*\|')),
        "duration_text": clean(regex_first(html_str,
            r'white-space:nowrap[^>]*>[^|]+\|\s*((?:\d+\s*h\s*)?\d+\s*min)')),
        "start_time_text": clean(times[0]) if len(times) > 0 else None,
        "end_time_text": clean(times[1]) if len(times) > 1 else None,
        "payment_method": clean(" + ".join(
            m.strip() for m in re.findall(r'font-weight:bolder">([^<]+)</td>', html_str)
        ) or None),
        "notes": clean(ride_type),
    }


def extract_uber_v2(html_str: str) -> dict:
    # Ride type from vehicle_type testid
    ride_type = regex_first(html_str,
        r'data-testid="vehicle_type"[^>]*>([^<]+)')

    return {
        "total_text": clean(regex_first(html_str,
            r'data-testid="total_fare_amount"[^>]*>([^<]+)')),
        "pickup": clean(regex_first(html_str,
            r'data-testid="address_point_0_address"[^>]*>([^<]+)')),
        "dropoff": clean(regex_first(html_str,
            r'data-testid="address_point_1_address"[^>]*>([^<]+)')),
        "driver": clean(regex_first(html_str,
            r'data-testid="driverInfo_title"[^>]*>You rode with ([^<]+)')),
        "distance_text": clean(regex_first(html_str,
            r'data-testid="distance_duration"[^>]*>([^,]+)')),
        "duration_text": clean(regex_first(html_str,
            r'data-testid="distance_duration"[^>]*>[^,]+,\s*(\d+\s*\w+)')),
        "start_time_text": clean(regex_first(html_str,
            r'data-testid="address_point_0_time"[^>]*>([^<]+)')),
        "end_time_text": clean(regex_first(html_str,
            r'data-testid="address_point_1_time"[^>]*>([^<]+)')),
        "payment_method": clean(regex_first(html_str,
            r'data-testid="payments_0_Card\.String"[^>]*>([^<]+)')),
        "notes": clean(ride_type),
    }


def extract_yandex(html_str: str) -> dict:
    return {
        "total_text": clean(regex_first(html_str,
            r'class="report__value report__value_main"[^>]*>\s*([^\s<][^<]*?)\s*</td>')),
        "pickup": clean(regex_first(html_str,
            r'border-bottom: 1px solid #E7E5E1;">\s*'
            r'<p class="route__point-name"[^>]*>([^<]+)')),
        "dropoff": clean(regex_first(html_str,
            r'border-bottom: 0;">\s*'
            r'<p class="route__point-name"[^>]*>([^<]+)')),
        "driver": clean(regex_first(html_str,
            r'Driver</p>\s*<p class="details__value"[^>]*>([^<]+)')),
        "distance_text": clean(regex_first(html_str,
            r'class="hint"[^>]*>(\d[\d.]*\s*km)</p>')),
        "duration_text": clean(regex_first(html_str,
            r'<p class="ride-time"[^>]*>([^<]+)</p>')),
        "start_time_text": clean(regex_first(html_str,
            r'border-bottom: 1px solid #E7E5E1;">\s*'
            r'<p class="route__point-name"[^>]*>[^<]+</p>\s*'
            r'<p class="hint"[^>]*>(\d{2}:\d{2})')),
        "end_time_text": clean(regex_first(html_str,
            r'border-bottom: 0;">\s*'
            r'<p class="route__point-name"[^>]*>[^<]+</p>\s*'
            r'<p class="hint"[^>]*>\s*(\d{2}:\d{2})')),
        "payment_method": clean(regex_first(html_str,
            r'class="card__name"[^>]*>\s*([^\s<][^<]*?)\s*</td>')),
        "notes": None,
    }


def extract_lyft(html_str: str) -> dict:
    # Addresses
    addrs = re.findall(
        r'<td class="mobileBodySmall"[^>]*>\s*<a[^>]*>([^<]+)</a>', html_str)

    # Discount note
    discount_name = regex_first(html_str, r'cc_lyft_credit\.png[^/]*/>\s*([^<]+)')
    discount_amt = None
    if discount_name:
        # Find the amount next to the discount
        m = re.search(
            re.escape(discount_name.strip()) + r'[^<]*</td>\s*<td[^>]*>\s*([^<]+)',
            html_str, re.DOTALL)
        if m:
            discount_amt = m.group(1).strip()
    notes = None
    if discount_name:
        parts = [f"Discount applied: {discount_name.strip()}"]
        if discount_amt:
            parts.append(f"({discount_amt})")
        notes = " ".join(parts)

    return {
        "total_text": clean(regex_first(html_str,
            r'class="value charge-total[^"]*"[^>]*>\s*<strong>\s*([^<]+?)\s*</strong>')),
        "pickup": clean(addrs[0]) if len(addrs) > 0 else None,
        "dropoff": clean(addrs[1]) if len(addrs) > 1 else None,
        "driver": clean(regex_first(html_str,
            r'Thanks for riding with\s*<span[^>]*>([^<]+)!</span>')),
        "distance_text": clean(regex_first(html_str, r'Lyft fare \(([^,]+),')),
        "duration_text": clean(regex_first(html_str, r'Lyft fare \([^,]+,\s*([^)]+)\)')),
        "start_time_text": clean(regex_first(html_str, r'AT\s+(\d+:\d+\s*[AP]M)')),
        "end_time_text": clean(regex_first(html_str,
            r'Drop-off.*?(\d+:\d+\s*[AP]M)</span>')),
        "payment_method": clean(regex_first(html_str,
            r'<span[^>]*padding-left[^>]*>([^<]+)</span></td>')),
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Main extraction router
# ---------------------------------------------------------------------------

EXTRACTORS = {
    ("Bolt", "v1"): extract_bolt_v1,
    ("Bolt", "v2"): extract_bolt_v2,
    ("Uber", "v1"): extract_uber_v1,
    ("Uber", "v2"): extract_uber_v2,
    ("Yandex", "v1"): extract_yandex,
    ("Lyft", "v1"): extract_lyft,
}


def extract_ride(email: dict) -> dict | None:
    provider = detect_provider(email)
    if not provider:
        return None

    html_str = email.get("text_html", "")
    if not html_str:
        return None

    template = detect_template(provider, html_str)
    extractor = EXTRACTORS.get((provider, template))
    if not extractor:
        print(f"  WARNING: no extractor for {provider}/{template}", file=sys.stderr)
        return None

    ride = extractor(html_str)
    currency, amount = parse_currency_amount(ride.get("total_text"))

    return {
        "provider": provider,
        "source": {
            "gmail_message_id": email.get("gmail_message_id"),
            "email_date": email.get("email_date"),
            "subject": email.get("subject"),
        },
        "ride": {
            "start_time_text": ride.get("start_time_text"),
            "end_time_text": ride.get("end_time_text"),
            "total_text": ride.get("total_text"),
            "currency": currency,
            "amount": amount,
            "pickup": ride.get("pickup"),
            "dropoff": ride.get("dropoff"),
            "pickup_city": None,
            "pickup_country": None,
            "dropoff_city": None,
            "dropoff_country": None,
            "payment_method": ride.get("payment_method"),
            "driver": ride.get("driver"),
            "distance_text": ride.get("distance_text"),
            "duration_text": ride.get("duration_text"),
            "notes": ride.get("notes"),
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def process_file(input_path: Path, output_dir: Path | None) -> dict | None:
    with open(input_path) as f:
        email = json.load(f)

    result = extract_ride(email)
    if result is None:
        print(f"  SKIP {input_path.name}: unknown provider", file=sys.stderr)
        return None

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / input_path.name
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return result


def main():
    parser = argparse.ArgumentParser(description="Extract ride details from email HTML")
    parser.add_argument("input", help="Email JSON file or directory of email JSONs")
    parser.add_argument("-o", "--output", help="Output directory (default: stdout for single file)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output) if args.output else None

    if input_path.is_file():
        result = process_file(input_path, output_dir)
        if result and not output_dir:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    elif input_path.is_dir():
        files = sorted(input_path.glob("*.json"))
        ok = skip = fail = 0
        for f in files:
            result = process_file(f, output_dir or Path("rides_extracted"))
            if result is None:
                skip += 1
            elif any(v is None for k, v in result["ride"].items()
                     if k in ("total_text", "pickup", "dropoff")):
                fail += 1
                missing = [k for k, v in result["ride"].items()
                           if k in ("total_text", "pickup", "dropoff", "driver") and v is None]
                print(f"  PARTIAL {f.name}: missing {missing}", file=sys.stderr)
            else:
                ok += 1
        dest = output_dir or Path("rides_extracted")
        print(f"Done: {ok} ok, {fail} partial, {skip} skipped → {dest}/", file=sys.stderr)
    else:
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
