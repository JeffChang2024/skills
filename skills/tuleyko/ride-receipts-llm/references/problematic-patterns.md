# Problematic extraction patterns to watch for

Use this reference when quality drops on reruns.

## Yandex

### Currency / amount variants

Observed valid total formats:
- `р.14.8` → `currency: "BYN"`, `amount: 14.8`
- `BYN27.1` → `currency: "BYN"`, `amount: 27.1`
- `₽757` → `currency: "RUB"`, `amount: 757`

Common labels around totals:
- `Ride cost (including applied taxes)`
- `Ride price (including applied taxes)`
- `Total price`
- `Total ride fare`
- `Total ride fare with a Yandex Plus subscription`

### Route blocks with extra stops

Some receipts include an intermediate stop or `Destination changed` marker, for example:
- `PickupAddr 02:20 Stop1 FinalDropoff 02:48 Destination changed`

Rule:
- pickup = first address
- start_time_text = first time
- dropoff = final destination address
- end_time_text = last route time

Do not stop at the first drop-like address if more route content follows before Payment/Details.

## Bolt

### Older 2019-style receipts

Pattern:
- `Total 1.30€`
- `Ride distance 3 km`
- `Ride duration 00:06`
- then later route timestamps like `09:29` and `09:36`

Rule:
- `duration_text = 00:06`
- `start_time_text/end_time_text` must come from the later route timestamps
- do not shift `Ride duration` into `start_time_text`

### Newer receipts with weak snippets

Some Gmail snippets contain almost no fare detail even when the HTML does.
Rule:
- trust `text_html` first
- do not give up just because snippet is generic like `Thanks for choosing Bolt — here's your ride receipt!`

## Uber

### Cancellation / fee adjustment receipts

These may contain:
- `Cancellation Fee PLN 5.00`
- `Here's the receipt for your canceled trip`
- `fare adjustment`

Rule:
- it is valid for pickup/dropoff/time/distance to be null
- preserve payment and fare fields
- optionally set a note indicating cancellation/adjustment
