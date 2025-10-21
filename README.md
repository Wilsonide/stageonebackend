# StageOneBackend API

## Overview
This project implements a Python FastAPI application designed for analyzing and managing string data. It stores strings along with their computed properties in a PostgreSQL database using SQLAlchemy.

## Features
-   **FastAPI**: Provides a robust and high-performance API framework for building the backend services.
-   **SQLAlchemy**: Used as the Object Relational Mapper (ORM) for efficient interaction with the PostgreSQL database.
-   **PostgreSQL**: Serves as the persistent data store for string records and their analytical properties.
-   **String Analysis**: Automatically computes properties for each stored string, including length, palindrome status, unique character count, word count, SHA-256 hash, and character frequency.
-   **Querying and Filtering**: Supports retrieval of string records using direct query parameters on their properties or through natural language interpretation of search queries.
-   **Dockerization**: Containerized using Docker for simplified setup and deployment.

## Getting Started
### Installation
To set up and run the project locally, follow these steps:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/stageonebackend.git # Replace with your repository URL
    cd stageonebackend
    ```

2.  **Install `uv` (if not already installed)**:
    This project uses `uv` for efficient dependency management.
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    Ensure `uv` is in your system's PATH.

3.  **Install Dependencies**:
    ```bash
    uv sync
    ```

4.  **Database Setup**:
    Ensure you have a PostgreSQL database instance running and accessible. Create a new database for this project.

5.  **Run Database Migrations**:
    The application is configured to automatically create the necessary `strings_record` table on startup if it does not exist.

### Environment Variables
The following environment variable must be configured for the application to function correctly:

-   `db_url`: The connection string for your PostgreSQL database.
    
    _Example_:
    ```
    db_url="postgresql://user:password@host:port/database_name"
    ```

### Running the Application
After setting up the environment variables, you can start the FastAPI application locally:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be accessible at `http://localhost:8000/api`.

## API Documentation
### Base URL
`http://localhost:8000/api`

### Endpoints

#### POST /api/strings
Creates a new string record, analyzes its properties, and stores it in the database.

**Request**:
```json
{
  "value": "string"
}
```
_Example Payload_:
```json
{
  "value": "Hello World"
}
```

**Response**:
_Success (200 OK)_:
```json
{
  "id": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
  "value": "Hello World",
  "properties": {
    "length": 11,
    "is_palindrome": false,
    "unique_characters": 9,
    "word_count": 2,
    "sha256_hash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
    "character_frequency_map": {
      "H": 1, "e": 1, "l": 3, "o": 2, " ": 1, "W": 1, "r": 1, "d": 1
    }
  },
  "created_at": "2023-10-27T10:00:00Z"
}
```

**Errors**:
-   `400 Bad Request`: Invalid request body or missing "value" field.
-   `409 Conflict`: String already exists in the system.

#### GET /api/strings
Retrieves a list of string records, with optional filtering based on their computed properties. Filters are applied as OR conditions.

**Request**:
_Example Query Parameters_:
```
GET /api/strings?is_palindrome=true&word_count=1
```
_Supported filters (case-insensitive keys)_:
-   `length`: Integer, e.g., `length=5`
-   `is_palindrome`: Boolean, e.g., `is_palindrome=true` or `is_palindrome=false`
-   `unique_characters`: Integer, e.g., `unique_characters=3`
-   `word_count`: Integer, e.g., `word_count=1`
-   `sha256_hash`: String, e.g., `sha256_hash=...` (full hash value)

**Response**:
_Success (200 OK)_:
```json
{
  "data": [
    {
      "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "value": "madam",
      "properties": {
        "length": 5,
        "is_palindrome": true,
        "unique_characters": 3,
        "word_count": 1,
        "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "character_frequency_map": {
          "m": 2, "a": 2, "d": 1
        }
      },
      "created_at": "2023-10-27T10:00:00Z"
    }
  ],
  "count": 1,
  "filters_applied": {
    "is_palindrome": true,
    "word_count": 1
  }
}
```

**Errors**:
-   No specific API-defined error responses. Standard HTTP errors (e.g., `422 Unprocessable Entity` for invalid query parameters) may occur.

#### GET /api/strings/filter-by-natural-language
Retrieves a list of string records by interpreting a natural language query string. Filters are applied as OR conditions.

**Request**:
_Example Query Parameter_:
```
GET /api/strings/filter-by-natural-language?query=all palindromic strings with a single word
```
_Supported natural language phrases for `query` parameter_:
-   "palindrome", "palindromic" -> `is_palindrome=true`
-   "not palindrome", "not palindromic" -> `is_palindrome=false`
-   "single word", "one word" -> `word_count=1`
-   "two words", "2 words" -> `word_count=2`
-   "contains [character]" -> filters by string containing the specified character (e.g., "contains a")

**Response**:
_Success (200 OK)_:
```json
{
  "data": [
    {
      "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "value": "madam",
      "properties": {
        "length": 5,
        "is_palindrome": true,
        "unique_characters": 3,
        "word_count": 1,
        "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "character_frequency_map": {
          "m": 2, "a": 2, "d": 1
        }
      },
      "created_at": "2023-10-27T10:00:00Z"
    }
  ],
  "count": 1,
  "interpreted_query": {
    "original": "all palindromic strings with a single word",
    "parsed_filters": {
      "is_palindrome": true,
      "word_count": 1
    }
  }
}
```

**Errors**:
-   No specific API-defined error responses. Standard HTTP errors may occur.

#### GET /api/strings/{string_value}
Retrieves a single string record by its original `string_value`.

**Request**:
_Example Path Parameter_:
```
GET /api/strings/madam
```

**Response**:
_Success (200 OK)_:
```json
{
  "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "value": "madam",
  "properties": {
    "length": 5,
    "is_palindrome": true,
    "unique_characters": 3,
    "word_count": 1,
    "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "character_frequency_map": {
      "m": 2, "a": 2, "d": 1
    }
  },
  "created_at": "2023-10-27T10:00:00Z"
}
```

**Errors**:
-   `404 Not Found`: String does not exist in the system.

#### DELETE /api/strings/{string_value}
Deletes a string record by its original `string_value`.

**Request**:
_Example Path Parameter_:
```
DELETE /api/strings/madam
```

**Response**:
_Success (204 No Content)_:
(No content is returned for a 204 status)

**Errors**:
-   `404 Not Found`: String does not exist in the system.

[![Readme was generated by Dokugen](https://img.shields.io/badge/Readme%20was%20generated%20by-Dokugen-brightgreen)](https://www.npmjs.com/package/dokugen)