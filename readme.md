# 🐕 Dog Breeds Data Pipeline

A production-ready ETL pipeline that extracts dog breed data from The Dog API, transforms it with calculated metrics, stores it in PostgreSQL, and provides monitoring capabilities through a live dashboard.

---

## 🎯 Overview

This ETL pipeline demonstrates:

- Robust data extraction with retry logic and error handling
- Data transformation with calculated metrics
- Idempotent database operations (no duplicates on reruns)
- Basic monitoring and logging
- Live data visualization

**Tech Stack**: Python 3.8+, SQLAlchemy, PostgreSQL, Retool

---

## 🔌 API Selection

**API Used:** [The Dog API](https://thedogapi.com/)

**Why this API?**

1. **Free & Reliable**: No rate limits for basic usage, well-maintained
2. **Rich Data**: Provides structured breed data (temperament, lifespan, physical metrics)
3. **Good Documentation**: Clear API endpoints and response formats
4. **Real-world Applicability**: Demonstrates handling nested JSON, missing fields, and data quality issues

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  The Dog    │─────▶│   Extract    │─────▶│  Transform  │─────▶│   Load       │
│     API     │      │  (extract.py)│      │(transform.py)│      │ (loader.py)  │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                            │                                           │
                            │                                           ▼
                            │                                  ┌──────────────────┐
                            │                                  │   PostgreSQL     │
                            │                                  │  ┌────────────┐  │
                            │                                  │  │dog_breeds  │  │
                            ▼                                  │  └────────────┘  │
                     ┌──────────────┐                         │  ┌────────────┐  │
                     │ Error Logs   │                         │  │pipeline_logs│ │
                     └──────────────┘                         │  └────────────┘  │
                                                              └──────────────────┘
                                                                       │
                                                                       ▼
                                                              ┌──────────────────┐
                                                              │ Retool Dashboard │
                                                              └──────────────────┘
```

**Pipeline Flow:**

1. **Extract** → Fetch data from API with retries and timeout handling
2. **Transform** → Clean, normalize, and enrich data with calculated fields
3. **Load** → Upsert into PostgreSQL (prevents duplicates)
4. **Monitor** → Log success/failure to `pipeline_logs` table
5. **Display** → Visualize metrics in Retool dashboard

---

## 📦 Prerequisites

- **Python**: 3.8 or higher
- **PostgreSQL**: 12+ (local or hosted on Render/Neon/Supabase)
- **pip**: Package installer for Python
- **Git**: For cloning the repository

---

## 🚀 Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/dog-breeds-etl.git
cd dog-breeds-etl
```

### 2. Create Virtual Environment

**On Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate
```

**On macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required: PostgreSQL connection string
DATABASE_URL=postgresql://username:password@hostname:5432/database_name

# Optional: The Dog API key (increases rate limits)
DOG_API_KEY=your_api_key_here
```

**Example DATABASE_URL formats:**

```env
# Local PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/dog_breeds_db

# Neon.tech (free tier)
DATABASE_URL=postgresql://user:pass@ep-xxxxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# Supabase
DATABASE_URL=postgresql://postgres:pass@db.xxxxx.supabase.co:5432/postgres
```

**Getting a Dog API Key (Optional):**

1. Visit [https://thedogapi.com/signup](https://thedogapi.com/signup)
2. Sign up for a free account
3. Copy your API key from the dashboard

## 🗄️ Database Schema

### `dog_breeds` Table

Stores transformed dog breed information.

```sql
CREATE TABLE dog_breeds (
    breed_id INTEGER PRIMARY KEY,
    breed_name TEXT NOT NULL,
    breed_group TEXT,
    bred_for TEXT,
    life_span TEXT,
    temperament TEXT,
    origin TEXT,
    weight_kg TEXT,
    height_cm TEXT,
    temperament_count INTEGER,           -- Calculated: number of temperament traits
    avg_lifespan_years REAL,             -- Calculated: average lifespan from range
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for query performance
CREATE INDEX idx_breed_name ON dog_breeds(breed_name);
CREATE INDEX idx_breed_group ON dog_breeds(breed_group);
CREATE INDEX idx_origin ON dog_breeds(origin);
```

## ▶️ Running the Pipeline

### Manual Execution

```bash
python etl.py
```

**Expected Output:**

```
🚀 Starting ETL pipeline...
2025-12-08 10:30:15 - INFO - Attempting to fetch data (attempt 1/3)
2025-12-08 10:30:16 - INFO - Successfully extracted 172 dog breeds
2025-12-08 10:30:16 - INFO - Transformed 172 records successfully
✅ Table created/verified
✅ Successfully processed 172 records into dog_breeds table
✅ ETL pipeline completed!
```

### Using Docker + Cron (Recommended for Production)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Setup cron job
RUN echo "0 6 * * * cd /app && python etl.py >> /var/log/cron.log 2>&1" > /etc/cron.d/etl-cron
RUN chmod 0644 /etc/cron.d/etl-cron
RUN crontab /etc/cron.d/etl-cron

CMD ["cron", "-f"]
```

Build and run:

```bash
docker build -t dog-etl .
docker run -d --env-file .env dog-etl
```

### Verify Cron is Working

```bash
# Check cron logs
tail -f /var/log/cron.log

# Check pipeline logs in database
psql $DATABASE_URL -c "SELECT * FROM pipeline_logs ORDER BY run_time DESC LIMIT 5;"
```

---

## 🔍 Monitoring & Logging

### Application Logs

All components use Python's `logging` module:

```python
# Logs appear in console and can be redirected to files
2025-12-08 10:30:15 - INFO - Attempting to fetch data (attempt 1/3)
2025-12-08 10:30:16 - INFO - Successfully extracted 172 dog breeds
2025-12-08 10:30:16 - WARNING - Skipping record with missing critical data
2025-12-08 10:30:16 - ERROR - HTTP error occurred: 500 Server Error
```

### Database Monitoring

Query pipeline health:

```sql
-- Check last 10 runs
SELECT run_time, status, records_processed, error_message
FROM pipeline_logs
ORDER BY run_time DESC
LIMIT 10;

-- Success rate over last 30 days
SELECT
    COUNT(*) FILTER (WHERE status = 'SUCCESS') * 100.0 / COUNT(*) as success_rate,
    COUNT(*) FILTER (WHERE status = 'FAILED') as failures
FROM pipeline_logs
WHERE run_time > NOW() - INTERVAL '30 days';
```

### Error Handling Features

1. **Retry Logic**: 3 attempts with exponential backoff for API calls
2. **Timeout Protection**: 10-second timeout prevents hanging
3. **Graceful Degradation**: Skips invalid records, continues processing
4. **Transaction Safety**: Database operations wrapped in transactions
5. **Detailed Logging**: All errors captured with context

---

## 🚀 Production Improvements

### 1. Infrastructure & Deployment

**Containerization**

- **Dockerize the application** for consistent environments across dev/staging/prod
- **Multi-stage builds** to minimize image size (builder stage + runtime stage)
- **Health check endpoints** in container for orchestrator monitoring
- Store images in **container registry** (Docker Hub, AWS ECR, Google GCR)

**Orchestration & Scheduling**

- **Kubernetes CronJob** for cloud-native scheduling with auto-restart on failure
- **AWS ECS Scheduled Tasks** with EventBridge for AWS-native deployments
- **Apache Airflow** for complex workflows with task dependencies, retries, and monitoring UI
- **GitHub Actions / GitLab CI** with scheduled workflows for simple automation
- **Temporal.io** for durable workflow execution with built-in retries

**Example Kubernetes CronJob:**

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: dog-breeds-etl
spec:
  schedule: "0 6 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: etl
              image: your-registry/dog-etl:latest
              envFrom:
                - secretRef:
                    name: etl-secrets
          restartPolicy: OnFailure
```

### 2. Observability & Monitoring

**Centralized Logging**

- **ELK Stack** (Elasticsearch, Logstash, Kibana) for log aggregation and search
- **Datadog** or **New Relic** for unified logs, metrics, and traces
- **CloudWatch Logs** (AWS) or **Cloud Logging** (GCP) for cloud-native solutions
- **Structured logging** with JSON format for better parsing and filtering

**Metrics & Alerting**

- **Prometheus + Grafana** for time-series metrics and custom dashboards
  - Track: pipeline duration, record count, API latency, error rates
- **StatsD/Telegraf** for application-level metrics collection
- **Dead Letter Queue (DLQ)** for failed records with retry mechanism
- **Custom metrics** exported via StatsD or Prometheus client:

```python
  from prometheus_client import Counter, Histogram

  records_processed = Counter('etl_records_processed', 'Total records processed')
  pipeline_duration = Histogram('etl_duration_seconds', 'Pipeline execution time')
```

**Alerting Channels**

- **PagerDuty** for critical production incidents with on-call rotation
- **Slack webhooks** for team notifications on failures/degradation
- **Email alerts** via **SendGrid** or **AWS SES** for daily summaries
- **SMS alerts** via **Twilio** for high-severity issues

**Example Slack Alert:**

```python
import requests

def send_slack_alert(message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    payload = {
        'text': f'🚨 ETL Pipeline Alert: {message}',
        'username': 'Dog ETL Bot'
    }
    requests.post(webhook_url, json=payload)

# In etl.py error handling
except Exception as e:
    send_slack_alert(f'Pipeline failed: {str(e)}')
    raise
```
