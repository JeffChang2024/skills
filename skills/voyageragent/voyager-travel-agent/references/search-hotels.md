# Search Hotels

Search hotels for complex queries based on city, landmark(POI), hotel name, or brand names.

## Usage

When user asks about hotels with explicit geographic or hotel entity identifiers:
- city name (市, 城市)
- point of interest (POI, 地标, 景点, 公园)
- hotel name (酒店名, 饭店名)
- brand names (品牌, 连锁酒店)

## Workflow

1. **Collect Search Parameters**: Extract key parameters from the user's query:
   - `checkInDate`: Check-in date (YYYY-MM-DD), defaults to today + 7 days (T+7)
   - `checkOutDate`: Check-out date (YYYY-MM-DD), defaults to today + 8 days (T+8)
   - `city`: City name, defaults to user's current city
   - `country`: Country name
   - `nearby`: A single POI for proximity search
   - `hotelNames`: List of specific hotel names
   - `brandNames`: List of hotel brand names
   - `subQuery`: **(Required)** Original query segment or user intention

2. **Handle Silent Defaults**: Apply defaults **silently** without asking user:
   - Missing checkInDate → today + 7 days
   - Missing checkOutDate → today + 8 days
   - Missing city → user's current city
   - **Do NOT ask the user for missing information**

3. **Decompose and Structure Queries**:
   - Simple query: "hotels near Disneyland" → single search object
   - Complex query: "hotels near Mong Kok and Yau Ma Tei" → multiple search tasks
   - **Each task needs a separate query object**

4. **Call search-hotels Tool**: Collect all search query objects into a List, serialize to JSON string, call `node scripts/search-hotels.sh '[{查询对象}]'`. ALL recommendations MUST come from this tool's actual response.

5. **Data Validation**:
   - Parse JSON response
   - Use only actual hotel information from the response
   - If search-hotels returns no data: explicitly state "search-hotels未返回符合要求的酒店"
   - **Never invent or assume hotels**

## Important Notes
* **Strict `nearby` Handling**: `nearby` must be a **single POI**. Multiple POIs **must** be decomposed into multiple search query objects.
* **Pure Brand Names**: Extract `brandNames` as pure brand names without any business type or suffix (e.g., '万豪', not '万豪酒店集团').
* **Parallel Execution**: The skill packages all decomposed tasks into a single list. The `search-hotels` tool handles parallel execution.
* **POI Expansion**: If no POI provided (e.g., "成都酒店推荐"), infer 1-3 most suitable POIs based on user intent and recommend hotels accordingly.
