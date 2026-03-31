# Trello Clone - FastAPI Implementation

This project is a functional Trello clone derived from the `112-1-unit1-trello-clone` architecture. The backend has been re-engineered from the original Node.js/Express implementation to a high-performance **FastAPI** framework, utilizing asynchronous MongoDB drivers for improved throughput.

## Run the App

Follow the instructions in this section to run the app locally.

### 1. Setup Backend `.env`

Navigate to the backend directory and initialize your environment configuration.

```bash
cd backend
cp .env.example .env
```
Configure the following fields in .env with your specific credentials:

- PORT: The port number for the FastAPI server (e.g., 8000).
- MONGO_URL: Your MongoDB connection string (Atlas or Local).

```bash
PORT=8000
MONGO_URL="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
```

### 2. Setup Frontend `.env`

Navigate to the frontend directory and configure the API endpoint.

```bash
cd frontend
cp .env.example .env
```

Ensure `VITE_API_URL` aligns with your backend configuration:

```bash
VITE_API_URL="http://localhost:8000"
```

### 3. Start the Backend Server

Ensure you have your Python virtual environment activated and dependencies installed (`pip install -r requirements.txt`).

```bash
cd backend
# Running with Uvicorn (Asynchronous Server Gateway Interface)
uvicorn main:app --reload --port 8000
```

### 4. Start the Frontend Server

```bash
cd frontend
yarn dev
```

Visit `http://localhost:5173` to see the app in action

## Technical Implementation Details

### Backend Architecture (FastAPI & Motor)

Unlike the original Express version, this implementation utilizes **Motor**, an asynchronous Python driver for MongoDB. This allows for non-blocking I/O operations, which is critical for maintaining performance during concurrent database transactions.

### Data Consistency & Referential Integrity

Since this system operates without native cross-collection transactions, consistency is maintained at the application logic layer:

* **Creation Synchronization**: Upon card creation, the backend executes a `$push` operation to the parent list's `cards` array.

* **Cascade Deletion**: Deleting a list triggers a `delete_many` operation for all associated cards to prevent data orphans.

* **Cross-List Migration**: The `PUT /api/cards/{id}` logic handles the atomic-like removal (`$pull`) from the source list and addition (`$push`) to the target list when a `list_id` change is detected.

## Migration: From Node.js to FastAPI

This project marks a strategic migration from a Node.js/Express environment to a **FastAPI** architecture to achieve superior type safety and data consistency.

### Key Technical Enhancements

* **Strict Type Enforcement**: Replaced runtime manual checks with **Pydantic v2** models, ensuring that incoming payloads (e.g., `CreateCardPayload`) are validated at the entry point.
* **Asynchronous I/O Efficiency**: Leveraged the **Motor** driver to implement a fully non-blocking event loop for MongoDB operations, optimizing throughput for concurrent requests.
* **Automated Data Mapping**: Utilized `serialization_alias` to seamlessly map MongoDB's internal `_id` to the frontend's expected `id` field during the Pydantic serialization lifecycle.
* **Reduced Latency via Aggregation**: Implemented **MongoDB Aggregation Pipelines** ($lookup) to fetch a list and its child cards in a single database Round-Trip Time (RTT), eliminating the N+1 query problem.
* **Fail-fast Configuration**: Adopted `pydantic-settings` to enforce type-safe environment variable loading, preventing execution if the configuration (e.g., `MONGO_URL`) is invalid.

## API Documentation Summary

### Card Endpoints

#### GET `/api/cards`

- Description: Fetches all cards across all lists (Global fetch).

- Response Body: List[CardSchema]

#### GET `/api/cards/{id}`

- Description: Retrieves a specific card by its unique identifier.

- Response Body: CardSchema

#### POST `/api/cards`

- Description: Creates a new card and establishes a parent-child relationship.

- Request Body: `CreateCardPayload` (`{ "title": "str", "description": "str", "list_id": "str" }`)

- Internal Logic:

  1. Validates the existence of the target `list_id`.

  2. Inserts the card into the `cards` collection.

  3. Synchronously `$pushes` the new `card_id` into the `cards` array of the corresponding `List` document.

- Response: `{ "id": "string" }`

#### PUT `/api/cards/{id}`

- Description: Updates card details or performs a **Cross-List Migration**.

- Request Body: `UpdateCardPayload` (All fields optional).

- Migration Logic: If `list_id` is provided and differs from the current one:

  - Removes (`$pull`) the card reference from the old list.

  - Adds (`$push`) the card reference to the new list.

- Response: `OK`

#### DELETE `/api/cards/{id}`

- Description: Removes a card and cleans up parent references.

- Logic: Deletes the card document and simultaneously `$pulls` its ID from the parent list's `cards` array to maintain referential integrity.

- Response: `OK`

### List Endpoints

#### GET `/api/lists`

- Description: Retrieves a summary of all existing lists.

- Response Body: `List[ListSimpleResponse]`

  - Only projects `_id` (as `id`) and `name` fields for optimal payload size.

#### GET `/api/lists/{id}`

- Description: Retrieves a detailed list object, including all associated cards.

- Implementation Detail: Utilizes an **Aggregation Pipeline** with `$lookup` to join the `cards` collection, simulating a `populate` operation in a single database RTT.

- Response Body: `ListDetailResponse`

  - Includes `id`, `name`, and an array of `cards` (full `CardSchema` objects).

#### POST `/api/lists`

- Description: Creates a new empty list.

- Request Body: `CreateListPayload` (`{ "name": "string" }`)

- Response: `{ "id": "string" }`

#### PUT `/api/lists/{id}`

- Description: Updates the metadata (name) of a specific list.

- Response: `OK` (Status 200)

#### DELETE `/api/lists/{id}`

- Description: Performs a **Cascade Delete** of the list and its members.

- Logic: First deletes the list document, then executes `delete_many` on the `cards` collection for all documents matching the `list_id`.

- Response: `OK`

### Development Standards

#### Linting and Formatting

The project enforces strict standards via **ESLint** and **Prettier** for the frontend, and follows **PEP 8** for the Python backend.

```bash
# Frontend quality check
yarn lint
yarn format
```
