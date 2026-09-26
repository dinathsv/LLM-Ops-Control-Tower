# LLM Ops Control Tower

A comprehensive backend platform for managing, monitoring, and tracing Large Language Model (LLM) operations. The system features a robust architecture utilizing FastAPI, PostgreSQL, ChromaDB, and Kafka for scalable asynchronous ingestion and processing of LLM traces.

## Architecture overview

The control tower consists of several core components designed for high-performance telemetry and insights:

1. **API Layer (`backend/api`)**: High-performance RESTful API built with FastAPI.
2. **Data Layer (`backend/core`)**: Relational structured data management using PostgreSQL & SQLAlchemy, handling entity modeling, API keys, and prompt templates.
3. **SDK & Middleware (`backend/sdk`)**: Middleware designed to wrap application LLM calls and push trace payloads to the message broker.
4. **Message Broker / Streaming**: Uses **Confluent Kafka** to asynchronously buffer and distribute incoming payload traces to workers without blocking the main application.
5. **Ingestion Workers (`backend/workers`)**: Consumes traces from Kafka, processes and saves trace metadata to PostgreSQL, and indexes vector embeddings into **ChromaDB**.

## Technology Stack

- **Framework**: FastAPI (Python)
- **Message Broker**: Confluent Kafka
- **Relational Database**: PostgreSQL (via SQLAlchemy / psycopg2)
- **Vector Database**: ChromaDB
- **Infrastructure**: Docker & Docker Compose

## Repository Structure

```
.
├── backend/
│   ├── api/            # FastAPI endpoints and route handlers
│   ├── core/           # Database models, Pydantic schemas, and configurations
│   ├── sdk/            # Middleware and tracking SDK for integrating LLM calls
│   ├── workers/        # Kafka consumers and ingestion services (e.g. ingestion.py)
│   └── requirements.txt# Python dependencies
├── docker-compose.yml  # Container orchestration for infrastructure (Kafka, PG, etc)
└── README.md           # This file
```

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose

### 1. Start Infrastructure

Start the supporting services (PostgreSQL, Kafka, Zookeeper, etc.) using Docker Compose:

```bash
docker-compose up -d
```

### 2. Install Dependencies

Install the required Python packages from the backend directory. We recommend using a virtual environment.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Services

You can run the API server and the background workers independently:

**Start the FastAPI Server:**
```bash
cd backend
uvicorn api.mock_app:app --reload
```

**Start the Ingestion Worker:**
```bash
cd backend
python -m workers.ingestion
```
