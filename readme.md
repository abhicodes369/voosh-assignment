# Dog Breeds Data Pipeline

A complete ETL (Extract, Transform, Load) pipeline that fetches dog breed data from The Dog API, transforms it, stores it in a PostgreSQL database, and visualizes it through a Retool dashboard with monitoring capabilities.

## Table of Contents

- [API Selection](#api-selection)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Local Setup Instructions](#local-setup-instructions)
- [Pipeline Workflow](#pipeline-workflow)
- [Monitoring & Reliability](#monitoring--reliability)
- [Dashboard](#dashboard)
- [Production Improvements](#production-improvements)

## API Selection

**API Used:** [The Dog API](https://thedogapi.com/)

**Why This API?**

- **Reliable & Well-Documented:** Provides consistent data structure with comprehensive breed information
- **Free Tier Available:** No cost barriers for development and testing
- **Rich Dataset:** Contains detailed attributes (temperament, lifespan, origin, physical metrics) perfect for transformation logic
- **Personal Interest:** As a dog enthusiast, this project allows me to explore breed characteristics while building technical skills

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Dog API   │ --> │  Transform   │ --> │  PostgreSQL  │ --> │    Retool    │
│  (Extract)  │     │   (Clean)    │     │   (Store)    │     │  Dashboard   │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 v
                                          ┌──────────────┐
                                          │  Monitoring  │
                                          │     Logs     │
                                          └──────────────┘
```

## Prerequisites

- **Python:** 3.8 or higher
- **PostgreSQL Database:** Free tier from [Supabase](https://supabase.com/) or [Neon.tech](https://neon.tech/)
- **Dog API Key:** Sign up at [thedogapi.com](https://thedogapi.com/) for free
- **Git:** For cloning the repository

## Local Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/dog-breeds-pipeline.git
cd dog-breeds-pipeline
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**

```
requests==2.31.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Dog API Configuration
DOG_API_KEY=your_dog_api_key_here

# PostgreSQL Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# Example for Supabase:
# DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
```

**To get your credentials:**

- **Dog API Key:** Register at https://thedogapi.com/signup
- **PostgreSQL URL:**
  - Supabase: Project Settings → Database → Connection String (URI)
  - Neon: Dashboard → Connection Details → Connection String

### 4. Update Configuration Files

**In `extract.py`:**

```python
self.api_key = os.environ.get("DOG_API_KEY")
```

**In `loader.py`:**

```python
self.database_url = os.environ.get("DATABASE_URL")
```

### 5. Run the Pipeline

```bash
python etl.py
```

**Expected Output:**

```
🚀 Starting ETL pipeline...
INFO - Attempting to fetch data (attempt 1/3)
INFO - Successfully extracted 172 dog breeds
INFO - Transformed 172 records successfully
✅ Table created/verified
✅ Successfully processed 172 records into dog_breeds table
✅ ETL pipeline completed!
```

## Pipeline Workflow

### 1. **Extract** (`extract.py`)

- **Purpose:** Fetch raw dog breed data from The Dog API
- **Features:**
  - API key authentication
  - Retry logic with exponential backoff (3 attempts)
  - Timeout handling (10 seconds)
  - Connection error recovery
  - Comprehensive logging

**Error Handling:**

```python
- Timeout → Retry with 2^attempt seconds delay
- Connection Error → Retry with exponential backoff
- HTTP Error → Log and raise immediately
- Max retries: 3 attempts before failure
```

### 2. **Transform** (`transfom.py`)

- **Purpose:** Clean and enrich raw API data
- **Transformations Applied:**

| Transformation     | Description                                      | Example                         |
| ------------------ | ------------------------------------------------ | ------------------------------- |
| Field Renaming     | `id` → `breed_id`, `name` → `breed_name`         | Better SQL naming               |
| Null Handling      | Replace null/empty with "Unknown"                | Prevents data gaps              |
| Whitespace Cleanup | `.strip()` on all text fields                    | Clean data entry                |
| Metric Extraction  | Parse nested `weight.metric` and `height.metric` | Flatten structure               |
| Temperament Count  | Count traits from comma-separated list           | `"Friendly, Loyal, Active"` → 3 |
| Average Lifespan   | Calculate mean from range string                 | `"10 - 12 years"` → 11.0        |
| Timestamp          | Add `created_at` field                           | Track data freshness            |

**Calculated Fields Logic:**

```python
# Temperament Count
"Friendly, Loyal, Active" → Split by comma → Count = 3

# Average Lifespan
"10 - 12 years" → Extract [10, 12] → Average = 11.0
"15 years" → Extract [15] → Average = 15.0
```

### 3. **Load** (`loader.py`)

- **Purpose:** Store transformed data in PostgreSQL
- **Database Schema:**

```sql
CREATE TABLE IF NOT EXISTS dog_breeds (
    breed_id INTEGER PRIMARY KEY,
    breed_name TEXT NOT NULL,
    breed_group TEXT,
    bred_for TEXT,
    life_span TEXT,
    temperament TEXT,
    origin TEXT,
    weight_kg TEXT,
    height_cm TEXT,
    temperament_count INTEGER,
    avg_lifespan_years REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pipeline_logs (
    id SERIAL PRIMARY KEY,
    run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    records_processed INTEGER,
    error_message TEXT
);
```

**Features:**

- **Upsert Logic:** `ON CONFLICT (breed_id) DO UPDATE` prevents duplicates
- **Connection Pooling:** `NullPool` for serverless compatibility
- **Transaction Safety:** Uses `engine.begin()` for atomic operations
- **Auto-cleanup:** Disposes engine after each run

### 4. **Monitor** (`etl.py`)

- **Purpose:** Track pipeline health and execution history
- **Monitoring Features:**
  - Success/failure status logging
  - Record count tracking
  - Error message capture
  - Timestamp of each run
  - Queryable history for debugging

**Logs stored in:**

- Console output (real-time)
- `pipeline_logs` table (persistent)
- Application logs via Python logging module

### 5. **Display** (Retool Dashboard)

**Live Dashboard:** [Dog Breeds Dashboard](https://abhiramsharma369.retool.com/apps/3c1b8bac-d283-11f0-88b4-5726ef59d87a/Dog%20Breeds%20Dashboard/page1)

**Dashboard Components:**

- **Data Table:** Browse all 172+ dog breeds with filtering/sorting
- **Aggregate Metrics:**
  - Total breeds count
  - Average lifespan across all breeds
  - Most common breed groups
  - Temperament distribution
- **Pipeline Monitoring:**
  - Last successful run timestamp
  - Recent pipeline execution history
  - Error log viewer
  - Status indicator (OK/Failed)

## Monitoring & Reliability

### Current Implementation

**1. Error Logging:**

```python
- File-based: Console logs with timestamps
- Database: pipeline_logs table
- Severity levels: INFO, WARNING, ERROR
```

**2. Retry Mechanisms:**

```python
- API calls: 3 retries with exponential backoff
- Timeout: 10 seconds per request
- Connection errors: Auto-retry with delay
```

**3. Data Validation:**

```python
- Skip records missing critical fields (id, name)
- Log skipped records for review
- Continue processing on individual record failures
```

**4. Health Checks:**

- Record count verification
- Timestamp tracking for stale data detection
- Status codes in pipeline_logs table

### Viewing Monitoring Data

**Query recent pipeline runs:**

```sql
SELECT run_time, status, records_processed, error_message
FROM pipeline_logs
ORDER BY run_time DESC
LIMIT 10;
```

**Check pipeline health:**

```sql
SELECT status, COUNT(*)
FROM pipeline_logs
WHERE run_time > NOW() - INTERVAL '7 days'
GROUP BY status;
```

## Production Improvements

### 1. **Scalability Enhancements**

**Current Limitation:** Single-threaded, synchronous execution
**Improvements:**

- **Async Processing:** Use `asyncio` and `aiohttp` for concurrent API calls
- **Batch Processing:** Process data in chunks for memory efficiency
- **Distributed Task Queue:** Implement Celery + Redis for horizontal scaling
- **Incremental Loading:** Only fetch new/changed records using last_modified timestamps

**Example:**

```python
# Current: ~30 seconds for 172 breeds
# With async: ~5 seconds (6x faster)
import asyncio
import aiohttp

async def fetch_all_breeds():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_breed(session, i) for i in range(1, 173)]
        return await asyncio.gather(*tasks)
```

### 2. **Reliability & Resilience**

**Improvements:**

- **Circuit Breaker Pattern:** Stop calling failing APIs temporarily
- **Dead Letter Queue:** Store failed records for manual review
- **Idempotency Keys:** Ensure duplicate runs don't corrupt data
- **Health Check Endpoint:** `/health` API for orchestration tools
- **Graceful Degradation:** Serve cached data when API is down

**Example Circuit Breaker:**

```python
if failure_rate > 50% in last_10_calls:
    wait_30_seconds()
    use_cached_data()
```

### 3. **Automation & Orchestration**

**Current:** Manual execution via `python etl.py`
**Improvements:**

- **Scheduled Runs:**
  - Cron job: `0 2 * * * cd /app && python etl.py` (daily at 2 AM)
  - Airflow DAG for complex workflows
  - GitHub Actions for CI/CD triggered pipelines
- **Containerization:** Docker image for consistent environments
- **Infrastructure as Code:** Terraform for database/service provisioning

**Example Dockerfile:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "etl.py"]
```

### 4. **Monitoring & Observability**

**Current:** Basic console logs + database table
**Improvements:**

- **Centralized Logging:**
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - Datadog or New Relic for APM
- **Real-time Alerting:**
  - PagerDuty integration for failures
  - Slack webhooks for status updates
  - Email notifications via SendGrid
- **Metrics Dashboard:**
  - Grafana for time-series visualization
  - Track: latency, throughput, error rates, data freshness
- **Distributed Tracing:** OpenTelemetry for request tracking

**Example Alert:**

```python
if pipeline_status == "FAILED":
    send_slack_message(
        channel="#data-alerts",
        text=f"🚨 Dog Pipeline Failed: {error_message}"
    )
```

### 5. **Data Quality & Governance**

**Improvements:**

- **Data Validation Framework:**
  - Great Expectations for automated testing
  - Schema validation on ingestion
  - Anomaly detection (e.g., sudden 50% drop in records)
- **Data Lineage:** Track data flow from source to dashboard
- **Version Control:** Store historical snapshots for audit trails
- **SLA Monitoring:** Track data freshness SLAs (e.g., "data < 24 hours old")

**Example Validation:**

```python
expectations = {
    "breed_name": {"type": "string", "not_null": True},
    "avg_lifespan_years": {"min": 5, "max": 20},
    "temperament_count": {"min": 0, "max": 15}
}
```

### 6. **Security Hardening**

**Improvements:**

- **Secrets Management:**
  - AWS Secrets Manager or HashiCorp Vault
  - Never commit `.env` files (use `.gitignore`)
- **Database Security:**
  - Read-only user for dashboard queries
  - Row-level security policies
  - SSL/TLS for connections
- **API Rate Limiting:** Respect API quotas with rate limiter
- **Audit Logging:** Track who ran pipeline and when

### 7. **Cost Optimization**

**Current:** Free tier resources
**At Scale:**

- **Database:**
  - Use connection pooling (PgBouncer)
  - Archive old data to S3 (cheaper storage)
  - Implement data retention policies
- **Compute:**
  - Serverless functions (AWS Lambda) for infrequent runs
  - Spot instances for batch processing
- **API Costs:**
  - Cache API responses with TTL
  - Implement smart polling (only fetch changes)

### 8. **Testing Strategy**

**Improvements:**

- **Unit Tests:** Test each transformation function
- **Integration Tests:** Test full ETL flow with mock data
- **Data Quality Tests:** Validate output against expectations
- **Load Testing:** Ensure pipeline handles 10x data volume

**Example Test:**

```python
def test_calculate_avg_lifespan():
    assert transformer._calculate_avg_lifespan("10 - 12 years") == 11.0
    assert transformer._calculate_avg_lifespan("15 years") == 15.0
    assert transformer._calculate_avg_lifespan("Unknown") is None
```

## Project Structure

```
dog-breeds-pipeline/
├── extract.py           # API data extraction
├── transfom.py          # Data transformation logic
├── loader.py            # Database loading
├── etl.py              # Main pipeline orchestrator
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (not in git)
├── .gitignore          # Excluded files
└── README.md           # This file
```

## Troubleshooting

**Issue:** `RuntimeError: DATABASE_URL not set`

- **Solution:** Ensure `.env` file exists with valid `DATABASE_URL`

**Issue:** `requests.exceptions.Timeout`

- **Solution:** Check internet connection; API may be slow, retry will happen automatically

**Issue:** `psycopg2.OperationalError: could not connect`

- **Solution:** Verify PostgreSQL credentials and database is running

**Issue:** No data in dashboard

- **Solution:** Run `python etl.py` first to populate database

## License

MIT License - feel free to use this project for learning and portfolio purposes.

## Author

Created as part of a data engineering assignment. For questions or improvements, please open an issue on GitHub.

---

**Last Updated:** December 2024  
**Pipeline Version:** 1.0.0
