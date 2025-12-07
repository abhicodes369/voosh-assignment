# Dog Breeds ETL (Short Readme)

**Overview:** A small ETL pipeline that fetches dog-breed data from an external API, transforms and stores it in PostgreSQL, and provides basic monitoring and display.

**API used & why**

- **Used:** The Dog API (`https://thedogapi.com/`).
- **Why:** Free, well-documented, and returns structured breed data (weights, heights, temperament) suitable for quick ETL work.

**Run locally**

- Requirements: Python 3.8+, `pip`.
- Set environment variables: `DOG_API_KEY` and `DATABASE_URL` (Postgres URI).
- Install and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python etl.py
```

**Pipeline (fetch → transform → store → monitor → display)**

- **Fetch (extract.py):** Calls The Dog API, with retries and timeouts, returning raw JSON.
- **Transform (transfom.py):** Cleans fields, flattens nested metrics, computes small derived fields (e.g., avg lifespan).
- **Store (loader.py):** Upserts records into a PostgreSQL `dog_breeds` table and writes run status to `pipeline_logs`.
- **Monitor (etl.py / DB):** Logs run results to `pipeline_logs` and console for health checks and basic alerting.
- **Display:** Data can be viewed with any BI tool (the original project used a Retool dashboard) or by querying the database.

**How I would improve / scale for production**

- Make API calls concurrent (`asyncio`/`aiohttp`) and add batching for large datasets.
- Containerize (`Docker`) and run with an orchestrator (Kubernetes / ECS) or schedule with a workflow engine (Airflow).
- Add observability: centralized logs (ELK/Datadog), metrics (Prometheus/Grafana), and alerts (PagerDuty/Slack).
- Harden reliability: circuit breakers, DLQ for bad records, idempotent upserts, and automated retries with backoff.
