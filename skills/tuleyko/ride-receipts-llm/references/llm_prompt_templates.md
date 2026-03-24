# LLM prompt templates (ride-receipts-llm)

Use these templates for one-email-at-a-time semantic repair or fallback extraction.

Execution model:
- First run deterministic local extraction into `data/rides/<gmail_message_id>.json`.
- Validate the extracted ride set with `scripts/validate_extracted_rides.py`.
- For each flagged email, read the email object from `data/emails/<gmail_message_id>.json` plus the current partial ride object from `data/rides/<gmail_message_id>.json`.
- Send one targeted Gateway-backed LLM request for that one flagged email.
- Use the one-shot prompt only when the local extractor produced no usable ride object; otherwise prefer the repair prompt.
- Merge non-null repaired fields only.
- Write the final object back to `data/rides/<gmail_message_id>.json`.
- After the repair pass, re-run validation before SQLite import.

## One-shot extraction prompt (per email)

System/user message to the LLM (adapt as needed):

- Input: one email JSON object with keys like:
  `provider, gmail_message_id, email_date, subject, from, snippet, text_html`

Prompt:

> You are extracting a structured ride record from ONE ride receipt email.
>
> Use `text_html` as primary (raw HTML). Use `snippet` only if `text_html` is empty.
>
> Return EXACTLY one JSON object matching this schema:
>
> {
>   "provider": "Uber|Bolt|Yandex|Lyft|FreeNow",
>   "source": {"gmail_message_id":"...","email_date":"YYYY-MM-DD HH:MM","subject":"..."},
>   "ride": {
>     "start_time_text": "...",
>     "end_time_text": "...",
>     "total_text": "...",
>     "currency": "3-letter ISO-4217 code like EUR|PLN|USD|BYN|RUB|UAH|TRY|GBP|CHF|AED|SAR|JPY|... or null if truly unknown",
>     "amount": 12.34,
>     "pickup": "...",
>     "dropoff": "...",
>     "pickup_city": "...",
>     "pickup_country": "...",
>     "dropoff_city": "...",
>     "dropoff_country": "...",
>     "payment_method": "...",
>     "driver": "...",
>     "distance_text": "...",
>     "duration_text": "...",
>     "notes": "..."
>   }
> }
>
> Constraints:
> - Never hallucinate. If missing/unclear, use null.
> - Keep addresses verbatim.
> - Normalize currency to a 3-letter ISO-4217 code when confidently inferable from the receipt. For this mailbox's Yandex receipts, treat `р.` as Belarusian rubles (`BYN`). If a Yandex receipt shows `BYN27.1`-style totals, extract `currency: "BYN"` and `amount: 27.1`. If a Yandex receipt shows `₽757`-style totals, extract `currency: "RUB"`.
> - `amount` must be numeric; if you only have text, set amount=null and put the text in total_text.
> - Use the email’s exact wording for times/addresses; do not normalize.
> - For Yandex route blocks with extra intermediate stops or `Destination changed`, keep the first address/time as pickup/start and the final address/time as dropoff/end.
> - For older Bolt receipts, do not mistake `Ride duration 00:06` for `start_time_text`; duration belongs in `duration_text`, while trip start/end times come from the later route timestamps.
> - For Uber cancellation-fee or fare-adjustment receipts, route/time/distance fields may legitimately be null.

## Repair prompt (only when important fields are missing)

Inputs:
- the same email JSON object
- the previously extracted ride JSON object
- a list of missing important fields

Prompt:

> You are repairing a previously extracted ride record.
>
> Goal: fill ONLY these missing fields (leave everything else unchanged): <MISSING_FIELDS>
>
> Use the email body (`text_html`, and `snippet` as fallback) to find values.
>
> Rules:
> - Do NOT overwrite any existing non-null value.
> - Never hallucinate; if not present, keep null.
> - Return EXACTLY one JSON object with the SAME schema as before.
>
> Provide values only if supported by the email.

## City/country enrichment prompt (one ride at a time, Gateway-backed LLM)

Inputs:
- one extracted ride JSON object from `data/rides/<gmail_message_id>.json`
- no raw email HTML is needed for this step unless the user explicitly asks for a deeper recovery pass

Prompt:

> You are enriching one extracted ride record.
>
> Goal: infer ONLY these fields when they are currently null:
> - `pickup_city`
> - `pickup_country`
> - `dropoff_city`
> - `dropoff_country`
>
> Use only the existing `pickup` and `dropoff` address text in the ride JSON.
>
> Rules:
> - Process one ride at a time.
> - Do NOT change any non-city/country field.
> - Do NOT rewrite or normalize `pickup` or `dropoff`.
> - Do NOT overwrite any existing non-null city/country value.
> - If an address is ambiguous, leave the target field null.
> - Infer city/country from address text alone; do not browse, geocode, or call external APIs.
> - If one side's country is confidently known and the other side's country is null, copy the known country to the missing side within the same ride.
> - Do not copy or infer city values from the other side; only country may be propagated this way.
> - Return EXACTLY one full JSON object with the SAME schema as before.
>
> Provide only confident city/country values; otherwise keep null.
ull.
