# Plan Itinerary

Plan single-day or multi-day travel itineraries, organize multi-destination trips, optimize travel routes, estimate budgets, or create detailed day-by-day travel schedules. Supports domestic and international travel, solo trips, family travel, and group travel scenarios.

A comprehensive trip itinerary planning reference that generates structured, day-by-day travel plans based on user requirements. Derived from production travel AI systems with real-world planning expertise.

## Table of Contents

- [Core Capabilities](#core-capabilities)
- [Trigger Conditions](#trigger-conditions)
- [Workflow](#workflow)
    - [Step 1: Requirement Analysis](#step-1-requirement-analysis)
    - [Step 2: Destination Analysis](#step-2-destination-analysis)
    - [Step 3: Transportation Planning](#step-3-transportation-planning)
    - [Step 4: Itinerary Assembly](#step-4-itinerary-assembly)
    - [Step 5: Budget Estimation](#step-5-budget-estimation)
    - [Step 6: Output Generation](#step-6-output-generation)
- [Expression Rules](#expression-rules)
- [General Rules](#general-rules)
- [Usage Examples](#usage-examples)

---

## Core Capabilities

- Single-day and multi-day itinerary generation
- Multi-destination route optimization
- Transportation mode analysis (flights, trains, driving, transit)
- Budget estimation and cost breakdown
- Accommodation placement strategy
- Activity and attraction scheduling
- Family/group travel considerations
- Domestic and international trip support

## Trigger Conditions

Activate this skill when the user:

- Asks to "plan a trip", "create an itinerary", "arrange a travel schedule"
- Mentions multi-day travel with specific destinations
- Requests day-by-day travel arrangements
- Asks for route optimization across multiple cities
- Needs help organizing travel logistics (transport + hotel + activities)
- Uses phrases like: "help me plan", "travel itinerary", "trip schedule",
  "how should I arrange my days in [destination]"

Do NOT activate for:

- Single-point questions like "What's fun in Paris?" (use general knowledge)
- Pure ticket booking or hotel search (not itinerary planning)
- Real-time queries like weather or prices (use web search)

---

## Workflow

### Step 1: Requirement Analysis

Extract and confirm the following from the user's input:

| Parameter        | Required | Description                                    |
|------------------|----------|------------------------------------------------|
| destinations     | Yes      | Target cities/countries in visit order          |
| travel_dates     | Yes      | Start date, end date, or total days             |
| travelers        | No       | Number of adults, children, elderly; solo/group |
| budget_level     | No       | Budget/mid-range/luxury; or specific amount     |
| interests        | No       | Culture, food, nature, shopping, adventure, etc |
| constraints      | No       | Mobility limits, visa restrictions, diet needs  |
| pace_preference  | No       | Relaxed / moderate / intensive                  |

**Rules:**
- If destinations or dates are missing, ask the user before proceeding
- If only a destination is given without dates, suggest a reasonable duration
  based on the [Recommended Stay Duration](#recommended-stay-duration) table
- Infer budget_level from context clues (e.g. "backpacking" = budget)
- Default pace is "moderate" if not specified

---

### Step 2: Destination Analysis

For each destination, analyze:

1. **Optimal stay duration**: How many days are ideal
2. **Must-see attractions**: Top landmarks, cultural sites, natural scenery
3. **Local specialties**: Food, shopping, unique experiences
4. **Geographic layout**: How attractions cluster geographically
5. **Seasonal factors**: Weather, peak/off-peak, festivals during travel dates

**Multi-destination rules:**
- Allocate days proportionally based on destination richness
- First and last days account for transit overhead
- Minimum 1 full day per major city (exclude transit days)

#### Recommended Stay Duration

##### By Destination Type

| Destination Type           | Recommended Days | Examples                        |
|----------------------------|------------------|---------------------------------|
| Global megacity            | 4-6 days         | Tokyo, London, New York, Paris  |
| Major city                 | 3-4 days         | Barcelona, Bangkok, Istanbul    |
| Medium city                | 2-3 days         | Kyoto, Florence, Chiang Mai     |
| Small city / town          | 1-2 days         | Bruges, Hallstatt, Luang Prabang|
| Beach / resort destination | 3-5 days         | Bali, Maldives, Phuket         |
| Nature / national park     | 2-4 days         | Yellowstone, Zhangjiajie       |
| Cultural heritage site     | 1-2 days         | Angkor Wat, Machu Picchu       |

##### Adjustment Factors

- **First visit**: Add 1 day vs repeat visit
- **With children**: Add 1 day (slower pace, nap time)
- **Photography focus**: Add 0.5-1 day (golden hour, revisits)
- **Festival period**: Add 1 day to experience events
- **Relaxed pace**: Multiply by 1.3x
- **Intensive pace**: Multiply by 0.7x

#### Attraction Density Analysis

##### High-density destinations (many sights per km2)
- Strategy: Walk between sights, cluster by neighborhood
- Examples: Rome (historic center), Kyoto (temple district), Prague (old town)
- Plan: 3-4 major sights per day + meals + shopping

##### Medium-density destinations
- Strategy: Mix of walking and transit, 2-3 areas per day
- Examples: Tokyo (districts spread out), Bangkok (BTS/MRT connected)
- Plan: 2-3 major sights per day + transit time

##### Low-density destinations (sights spread far apart)
- Strategy: Dedicate half/full days to single areas
- Examples: Los Angeles, Australian outback, countryside regions
- Plan: 1-2 major areas per day, significant transit

#### Geographic Clustering Rules

1. Map all target attractions for a destination
2. Identify natural clusters (sights within 2 km of each other)
3. Assign each cluster to a half-day or full-day block
4. Order clusters to minimize backtracking
5. Place the most remote cluster on a dedicated day

#### Seasonal Considerations

##### Weather impact on itinerary

| Season Factor     | Adjustment                                        |
|-------------------|---------------------------------------------------|
| Extreme heat      | Schedule outdoor sights early morning or evening   |
| Rainy season      | Prepare indoor alternatives for each day           |
| Extreme cold      | Limit outdoor time; plan warm indoor breaks        |
| Peak tourist season| Pre-book everything; expect crowds; go early       |
| Off-season        | Some attractions may close; check before planning  |

##### Best travel seasons (general reference)

| Region               | Best Months        | Avoid              |
|----------------------|--------------------|--------------------|
| Southeast Asia       | Nov - Mar          | Jun - Sep (monsoon)|
| Japan                | Mar-May, Oct-Nov   | Jun-Jul (rainy)    |
| Europe               | May - Sep          | Nov - Feb (cold)   |
| Australia/NZ         | Oct - Mar          | Jun - Aug (winter) |
| East Africa (safari) | Jun - Oct          | Mar - May (rain)   |
| South America        | May - Sep (dry)    | Dec - Mar (wet)    |

*Note: These are general guidelines. Specific destinations within
regions may differ. Always recommend users verify current conditions.*

#### Destination Pairing Rules

When users visit multiple destinations:

1. **Same country/region first**: Minimize long-haul transit
2. **North-to-south or east-to-west**: Follow a logical geographic path
3. **Big city + small town**: Alternate pace for variety
4. **Hub-and-spoke**: Use a central city as base for day trips when possible
5. **Avoid backtracking**: Route should not cross the same path twice
6. **Transit hub placement**: Plan overnight stays near transport hubs for
   early departures

#### Cultural Awareness Notes

When analyzing a destination, consider:

- **Local customs**: Dress codes for religious sites, tipping norms,
  greeting etiquette
- **Business hours**: Siesta culture (Spain, Italy afternoon closures),
  early closures (Japan, some shops close by 20:00)
- **Weekly patterns**: Many museums close on Mondays (Europe); Friday
  prayers may affect schedules (Middle East)
- **Holidays**: National holidays may close attractions or cause
  transport disruptions; but can offer unique festival experiences

---

### Step 3: Transportation Planning

Determine inter-city and intra-city transport:

#### Inter-city (between destinations)

| Distance        | Recommended Modes                  |
|-----------------|-------------------------------------|
| < 200 km        | Driving, high-speed rail, bus       |
| 200-800 km      | High-speed rail (preferred), flight |
| 800-2000 km     | Flight (preferred), overnight train |
| > 2000 km       | Flight                              |
| Cross-border    | Flight (check visa transit rules)   |

#### Intra-city (within destination)

- Use metro/subway where available (most cost-effective)
- Walking for clustered attractions (< 2 km apart)
- Taxi/ride-hailing for remote spots or with children/elderly
- Rent a car only for road-trip-style or rural areas

**Rules:**
- Place transit between cities in mornings or evenings to maximize
  sightseeing time
- For flights, account for 2-3 hours of airport overhead
- For high-speed rail, account for 30 min station overhead

#### Inter-City Transportation Decision Matrix

##### Distance-based recommendation (detailed)

| Distance (km) | Primary Choice      | Secondary Choice     | Notes                              |
|----------------|---------------------|----------------------|------------------------------------|
| 0 - 100        | Driving / Taxi      | Regional bus/train   | Door-to-door most convenient       |
| 100 - 300      | High-speed rail     | Driving              | Rail often faster than driving     |
| 300 - 800      | High-speed rail     | Short-haul flight    | Rail: no airport overhead          |
| 800 - 1500     | Flight              | Overnight train      | Flight saves a full day            |
| 1500+          | Flight              | -                    | Only viable option                 |
| Cross-border   | Flight              | Intl rail (if avail) | Check visa transit requirements    |

##### Time overhead per transport mode

| Mode              | Overhead (beyond travel time)      |
|-------------------|------------------------------------|
| Flight            | 2.5 - 3.5 hours (check-in, security, boarding, baggage) |
| High-speed rail   | 30 - 45 minutes (station arrival, boarding) |
| Long-distance bus  | 15 - 30 minutes                   |
| Driving (own car) | 0 minutes (but parking at destination) |
| Ferry             | 30 - 60 minutes (check-in, boarding) |

##### Cost comparison (general tiers)

| Mode          | Cost Level | Best For                           |
|---------------|------------|------------------------------------|
| Bus           | Lowest     | Budget travel, short routes        |
| Train (regular)| Low-Medium | Medium distance, scenic routes     |
| High-speed rail| Medium    | 300-800 km, time-sensitive         |
| Budget airline | Medium    | 800+ km, booked early             |
| Full-service airline | High | Long-haul, comfort priority      |
| Private car/taxi| High     | Groups, door-to-door, flexibility |

#### Intra-City Mode Selection

| Scenario                        | Recommended Mode                  |
|---------------------------------|-----------------------------------|
| City with metro system          | Metro + walking (primary)         |
| Attractions < 2 km apart        | Walking                           |
| With young children or elderly  | Taxi / ride-hailing               |
| Rural area or outskirts         | Rental car or local tour          |
| Night activity / late return    | Taxi / ride-hailing               |
| Group of 3-4 people             | Taxi (often same cost as transit) |
| Budget solo traveler            | Public transit + walking          |

##### Metro/subway tips by region

- **East Asia** (Tokyo, Seoul, Shanghai): Excellent coverage, IC cards
  available, English signage in most stations
- **Europe** (London, Paris, Berlin): Good coverage in center, zone-based
  pricing, multi-day passes available
- **Southeast Asia** (Bangkok, Singapore, KL): Limited coverage, supplement
  with taxi/ride-hailing
- **Americas** (NYC, Mexico City): Reliable but check safety by line/time

#### Transit Scheduling Rules

##### Optimal transit times for itinerary placement

| Transit Type    | Best Schedule Slot           | Reason                          |
|-----------------|------------------------------|---------------------------------|
| Morning flight   | Depart 07:00-09:00          | Arrive by lunch, half-day free  |
| Afternoon flight | Depart 14:00-16:00          | Morning free, arrive by dinner  |
| Evening flight   | Avoid if possible            | Wastes an evening, fatigue      |
| Red-eye flight   | For long-haul only           | Saves a hotel night + full day  |
| HSR morning      | Depart 08:00-10:00           | No airport overhead, arrive by lunch |
| HSR evening      | Depart after 17:00           | Full day at origin, arrive for dinner |

##### Connection time buffers

| Connection Type             | Minimum Buffer  |
|-----------------------------|-----------------|
| Domestic flight to flight    | 90 minutes     |
| International flight to flight| 2.5 hours     |
| Train to train               | 30 minutes     |
| Flight to train/hotel        | 2 hours (incl. baggage + transfer) |
| Train to hotel               | 45 minutes     |

#### Luggage Strategy

| Trip Pattern             | Luggage Advice                          |
|--------------------------|----------------------------------------|
| Single-city stay         | Any luggage size; store at hotel        |
| Multi-city, same hotel   | Day bag only for city switches          |
| Multi-city, hotel changes| Carry-on preferred; use luggage forwarding services |
| Road trip                | Trunk storage; no weight concerns       |
| Budget airline multi-leg | Carry-on only to avoid per-leg fees     |

#### Regional Transport Highlights

##### East Asia
- Japan: JR Pass for multi-city rail; Suica/Pasmo IC cards for local transit
- China: High-speed rail network excellent; book on 12306 or Trip.com
- South Korea: KTX for inter-city; T-money card for Seoul transit

##### Europe
- Eurail Pass for multi-country rail travel
- Budget airlines (Ryanair, EasyJet) for cross-country flights
- Flixbus for budget inter-city buses

##### Southeast Asia
- Grab (ride-hailing) widely available across the region
- AirAsia for budget intra-region flights
- Boats/ferries for island hopping (Thailand, Indonesia, Philippines)

##### North America
- Driving/road trips are the norm outside major metros
- Amtrak for scenic but slow rail options
- Domestic budget airlines (Southwest, JetBlue) for inter-city

*Note: This guide provides framework-level recommendations.
Specific routes, schedules, and prices should be verified with current sources.*

---

### Step 4: Itinerary Assembly

Build the day-by-day schedule following these principles:

#### Time allocation per day

| Time Block    | Duration  | Activity Type                        |
|---------------|-----------|--------------------------------------|
| Morning       | 08:00-12:00 | Major attractions, outdoor activities |
| Lunch         | 12:00-13:30 | Local cuisine experience             |
| Afternoon     | 13:30-17:30 | Museums, shopping, secondary sights  |
| Dinner        | 17:30-19:00 | Dining experience                    |
| Evening       | 19:00-21:30 | Night markets, shows, city walks     |

#### Assembly rules

1. **Geographic clustering**: Group nearby attractions in the same half-day
2. **Energy curve**: Place physically demanding activities in the morning;
   indoor/relaxing activities in the afternoon
3. **Meal integration**: Schedule meals near planned attraction areas
4. **Buffer time**: Add 30-min buffers between activities for transit/rest
5. **First day**: Lighter schedule if arriving after noon; check-in + nearby
6. **Last day**: Reserve morning for packing and checkout; airport/station
   transit by early afternoon
7. **Rest day**: For trips > 5 days, insert a half-rest day mid-trip
8. **Rain plan**: Note indoor alternatives for outdoor activities

#### Family/group adjustments

- With children (< 6 yrs): Max 2 major attractions per day; add nap time
- With elderly: Reduce walking; add rest stops; avoid steep terrain
- Group travel: Choose activities with broad appeal; build in free time

Use the [Output Templates](#output-templates) in Step 6 for the day-by-day
output format.

---

### Step 5: Budget Estimation

Provide a cost breakdown per person per day:

| Category       | Budget       | Mid-range    | Luxury       |
|----------------|--------------|--------------|--------------|
| Accommodation  | Hostel/budget hotel | 3-4 star hotel | 5-star/resort |
| Meals          | Street food/local | Mix of local & restaurants | Fine dining |
| Transport      | Public transit | Transit + occasional taxi | Taxi/private car |
| Activities     | Free/low-cost sights | Mix of paid & free | Premium experiences |

**Rules:**
- Use the destination's local currency and provide approximate conversion
- Separate fixed costs (flights, hotel) from daily variable costs
- Note peak season surcharges when applicable
- For families: mention child ticket discounts where common

#### Budget Tiers Definition

| Tier       | Description                                               |
|------------|-----------------------------------------------------------|
| Budget     | Hostels, street food, public transit, free attractions     |
| Mid-range  | 3-4 star hotels, mix of restaurants, occasional taxi       |
| Luxury     | 5-star hotels, fine dining, private transfers, premium exp |

#### Daily Cost Reference by Region

All amounts in USD equivalent, per person.

##### East Asia

| Country   | Budget     | Mid-range  | Luxury     |
|-----------|------------|------------|------------|
| Japan     | $80-120    | $150-250   | $400+      |
| S. Korea  | $60-100    | $120-200   | $350+      |
| China     | $40-80     | $100-180   | $300+      |
| Taiwan    | $50-80     | $100-160   | $250+      |

##### Southeast Asia

| Country    | Budget    | Mid-range  | Luxury     |
|------------|-----------|------------|------------|
| Thailand   | $30-50    | $80-150    | $300+      |
| Vietnam    | $25-40    | $60-120    | $250+      |
| Indonesia  | $25-45    | $70-140    | $300+      |
| Malaysia   | $30-50    | $80-140    | $280+      |
| Singapore  | $60-100   | $150-250   | $450+      |

##### Europe

| Region          | Budget    | Mid-range  | Luxury     |
|-----------------|-----------|------------|------------|
| Western Europe  | $80-120   | $180-300   | $500+      |
| Eastern Europe  | $40-70    | $100-180   | $300+      |
| Scandinavia     | $100-150  | $200-350   | $550+      |
| UK              | $80-130   | $180-300   | $500+      |

##### Americas

| Region            | Budget    | Mid-range  | Luxury     |
|-------------------|-----------|------------|------------|
| USA (major cities)| $80-130   | $200-350   | $500+      |
| USA (rural/small) | $60-90    | $120-200   | $350+      |
| Canada            | $70-110   | $170-280   | $450+      |
| Mexico            | $30-50    | $80-150    | $300+      |
| Central America   | $25-45    | $70-130    | $250+      |
| South America     | $30-60    | $80-160    | $300+      |

##### Oceania

| Country     | Budget    | Mid-range  | Luxury     |
|-------------|-----------|------------|------------|
| Australia   | $80-120   | $180-300   | $500+      |
| New Zealand | $70-110   | $160-280   | $450+      |

*These are rough estimates. Actual costs vary by city, season, and
personal choices. Always recommend users verify current rates.*

#### Cost Category Breakdown

##### Typical budget allocation

| Category        | Budget Tier | Mid-range   | Luxury       |
|-----------------|-------------|-------------|--------------|
| Accommodation   | 25-30%      | 35-40%      | 40-50%       |
| Meals           | 30-35%      | 25-30%      | 20-25%       |
| Transportation  | 20-25%      | 15-20%      | 10-15%       |
| Activities      | 10-15%      | 15-20%      | 15-20%       |
| Miscellaneous   | 5-10%       | 5-10%       | 5-10%        |

##### Fixed vs variable costs

| Fixed Costs (book in advance)    | Variable Costs (daily spending)  |
|----------------------------------|----------------------------------|
| International flights            | Meals                            |
| Inter-city trains/flights        | Local transport                  |
| Hotel/accommodation              | Shopping                         |
| Major attraction pre-bookings    | Snacks and drinks                |
| Travel insurance                 | Tips and gratuities              |
| Visa fees                        | Miscellaneous (SIM, laundry)     |

#### Special Considerations

##### Peak season surcharges
- Expect 30-80% higher accommodation and flight costs during:
    - Christmas / New Year (global)
    - Chinese New Year / Golden Week (East Asia)
    - Summer holidays Jul-Aug (Europe, North America)
    - Cherry blossom season (Japan, late March - mid April)
    - Local festivals and events

##### Family cost adjustments
- Children under 2: usually free on flights (lap seat), free at hotels
- Children 2-11: typically 50-75% of adult flight cost
- Many attractions offer family tickets or child discounts
- Accommodation: family rooms vs 2 standard rooms (compare costs)
- Budget extra for child entertainment, snacks, emergency purchases

##### Money-saving tips to include in itineraries
- Book flights 6-8 weeks in advance for best prices
- Consider accommodation with kitchen for longer stays
- Use city tourism passes (e.g., Paris Museum Pass, JR Pass)
- Eat lunch at restaurants (often cheaper set menus) and cook dinner
- Free walking tours (tip-based) for city orientation
- Student / senior discounts (remind travelers to carry ID)

##### Currency and payment notes
- Always note the local currency for each destination
- Remind users about foreign transaction fees on credit cards
- Cash-heavy destinations: Japan, Germany, Southeast Asia
- Card-friendly destinations: Scandinavia, UK, South Korea
- Recommend exchanging small amount before arrival for immediate needs

---

### Step 6: Output Generation

Generate the final itinerary using the output templates below.

**Output must include:**
1. Trip overview (destinations, dates, travelers, budget summary)
2. Day-by-day detailed schedule
3. Budget estimation table
4. Preparation checklist

#### Output Templates

##### Trip Overview Block

```
## Trip Overview

| Item          | Details                              |
|---------------|--------------------------------------|
| Destinations  | {city1} -> {city2} -> ...            |
| Dates         | {start_date} to {end_date} ({N} days)|
| Travelers     | {description}                        |
| Pace          | {relaxed / moderate / intensive}     |
| Est. Budget   | {currency} {amount} per person       |
```

##### Day-by-Day Block

Each day follows this structure:

```
### Day {N}: {City} - {Theme of the Day}

**Morning (08:00-12:00)**
- {Activity 1}: {brief description} ({duration})
- {Activity 2}: {brief description} ({duration})
- Tip: {practical advice}

**Lunch (12:00-13:30)**
- {Restaurant/area recommendation}: {what to try}

**Afternoon (13:30-17:30)**
- {Activity 3}: {brief description} ({duration})
- {Activity 4}: {brief description} ({duration})

**Dinner (17:30-19:00)**
- {Dining recommendation}: {what to try}

**Evening (19:00-21:30)**
- {Evening activity}: {brief description}

**Accommodation**: {area/type recommendation}

**Transit note**: {if applicable, inter-city travel details}
```

##### Transit Day Template

For days primarily spent on inter-city travel:

```
### Day {N}: {Origin} -> {Destination} (Transit Day)

**Morning**
- Check out from hotel
- {Transit mode} to {destination} (depart {time}, arrive {time})

**Afternoon**
- Arrive and check in at {area}
- Explore the hotel neighborhood
- {One light activity near accommodation}

**Evening**
- {Dinner spot near hotel}
- Rest and prepare for tomorrow's itinerary
```

##### First Day Template (Late Arrival)

```
### Day 1: Arrive in {City}

**Afternoon/Evening**
- Arrive at {airport/station}, transfer to hotel ({transit advice})
- Check in at {accommodation area}
- Explore the neighborhood on foot
- {Dinner recommendation}: {local specialty to start the trip}
- Early rest to adjust
```

##### Last Day Template

```
### Day {N}: {City} - Departure

**Morning (until {checkout_time})**
- Hotel checkout, store luggage if needed
- {One nearby activity or last-minute shopping}
- {Brunch/lunch recommendation}

**Afternoon**
- Transfer to {airport/station} ({allow X hours before departure})
- Departure

**Reminder**: Keep boarding pass, passport, and essentials accessible.
```

##### Budget Summary Block

```
## Budget Estimation (per person)

| Category        | Est. Cost ({currency}) | Notes                    |
|-----------------|------------------------|--------------------------|
| Flights/Train   | {amount}               | {route details}          |
| Accommodation   | {amount}               | {N} nights x {per night} |
| Local Transport  | {amount}              | Metro, taxi, etc.        |
| Meals           | {amount}               | {per day} x {N} days     |
| Activities      | {amount}               | Tickets, tours, etc.     |
| Miscellaneous   | {amount}               | Shopping, tips, SIM card |
| **Total**       | **{total}**            |                          |

*Prices are estimates based on {budget_level} level.
Verify current rates before booking.*
```

##### Compact Table Format (for trips > 7 days)

Use this summary before day-by-day details:

```
## Itinerary At-a-Glance

| Day | Date       | City      | Highlights                    | Transport      |
|-----|------------|-----------|-------------------------------|----------------|
| 1   | {date}     | {city}    | Arrival, {activity}           | Flight         |
| 2   | {date}     | {city}    | {highlight1}, {highlight2}    | Metro          |
| ... | ...        | ...       | ...                           | ...            |
| N   | {date}     | {city}    | Departure                     | Flight         |
```

#### Travel Preparation Checklist

Include this checklist at the end of every itinerary output.

##### 4+ Weeks Before Departure

**Documents:**
- [ ] Passport valid for 6+ months beyond return date
- [ ] Visa applications submitted (check processing times)
- [ ] Travel insurance purchased (medical, trip cancellation, baggage)
- [ ] International driving permit (if planning to drive)
- [ ] Copy important documents (passport, visa, insurance) digitally and on paper

**Health:**
- [ ] Check destination vaccination requirements
- [ ] Visit travel clinic if needed (some vaccines need weeks to take effect)
- [ ] Refill prescription medications for trip duration + buffer
- [ ] Get a dental/medical checkup for long trips

**Booking:**
- [ ] Flights or major transport booked
- [ ] Accommodation booked (at least first and last nights)
- [ ] Major attraction tickets pre-booked if required (popular museums, shows)

##### 1-2 Weeks Before Departure

**Finance:**
- [ ] Notify bank of travel dates and destinations
- [ ] Order foreign currency (small amount for arrival)
- [ ] Confirm credit card works internationally (check foreign transaction fees)
- [ ] Note emergency card cancellation numbers

**Communication:**
- [ ] Arrange international phone plan or local SIM card
- [ ] Download offline maps for all destinations
- [ ] Download translation app with offline packs
- [ ] Share itinerary with emergency contact at home

**Logistics:**
- [ ] Arrange airport transfer or parking
- [ ] Arrange pet care / house sitting if needed
- [ ] Set mail hold or arrange pickup
- [ ] Check luggage weight limits for your airline

##### 2-3 Days Before Departure

**Packing Essentials:**
- [ ] Passport and travel documents
- [ ] Printed copies of bookings (hotel, flights, activities)
- [ ] Medications in carry-on (with prescription labels)
- [ ] Phone charger and power adapter for destination
- [ ] Comfortable walking shoes (broken in, not new)
- [ ] Weather-appropriate clothing (check forecast)
- [ ] Small daypack for daily excursions

**Tech:**
- [ ] Portable battery pack (charged)
- [ ] Headphones / earbuds
- [ ] Camera and memory cards
- [ ] Universal power adapter

**Comfort:**
- [ ] Neck pillow for long flights
- [ ] Eye mask and earplugs
- [ ] Snacks for transit
- [ ] Reusable water bottle (empty for security)

##### Day of Departure

- [ ] Recheck passport, tickets, and wallet
- [ ] Lock all windows and doors
- [ ] Turn off unnecessary appliances
- [ ] Arrive at airport/station with adequate buffer time
    - International flights: 3 hours before
    - Domestic flights: 2 hours before
    - High-speed rail: 30-45 minutes before
- [ ] Check in online if available

##### Family Travel Additions

**With Children:**
- [ ] Child passport and birth certificate
- [ ] Consent letter if traveling without both parents
- [ ] Child-appropriate snacks and entertainment
- [ ] Car seat or booster if needed
- [ ] Children's medications (fever reducer, anti-nausea)
- [ ] Extra change of clothes in carry-on

**With Elderly:**
- [ ] Medical records summary in English
- [ ] Comfortable shoes with good support
- [ ] Wheelchair or mobility aid arrangement at airports
- [ ] List of medications with generic names
- [ ] Travel insurance with adequate medical coverage

##### During the Trip

- [ ] Keep documents secure (hotel safe or money belt)
- [ ] Back up photos daily (cloud or portable storage)
- [ ] Stay hydrated and respect jet lag recovery
- [ ] Keep emergency numbers accessible:
    - Local emergency: varies by country
    - Embassy/consulate contact
    - Insurance emergency hotline
    - Bank card emergency number

---

## Expression Rules

- Use the user's language for the entire response
- Keep each day's description concise: 3-5 bullet points per time block
- Use clear time markers (morning/afternoon/evening or specific times)
- Highlight must-do items with emphasis
- Include practical tips inline (e.g. "arrive early to avoid queues")
- Provide the full itinerary in a single response; do not split across
  multiple messages
- For trips > 7 days, provide a summary table first, then day-by-day details
- Do not fabricate specific prices; use ranges or say "check current rates"
- Do not fabricate opening hours; use general guidance or say "verify locally"

## General Rules

- Always respect the user's stated budget and pace preference
- For international trips, remind about visa, insurance, and currency exchange
- For destinations with safety concerns, include relevant travel advisories
- Suggest travel insurance for all international trips
- If the user's plan is unrealistic (too many cities, too few days), provide
  honest feedback and suggest alternatives
- When uncertain about specific local details, recommend the user verify
  with local sources rather than guessing
- Adapt the level of detail to the user's apparent experience level
  (first-time travelers get more tips; experienced travelers get less)

## Usage Examples

- "Help me plan a 5-day trip to Tokyo and Osaka"
- "Plan a family trip to Thailand for 7 days with 2 kids"
- "I have 3 days in Paris, what's the best itinerary?"
- "Plan a budget backpacking route through Southeast Asia for 2 weeks"
- "Create a honeymoon itinerary for Bali and Singapore, 10 days"
- "Help me arrange a road trip from Los Angeles to San Francisco"
