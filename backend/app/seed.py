from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Incident
from app.hindsight_service import hindsight_service

SEED_INCIDENTS = [
    {
        "id": "INC-101",
        "service": "Payment API",
        "error": "Database connection timeout",
        "symptoms": "High HTTP 504 Gateway Timeouts on /v1/charge endpoint, elevated checkout latency",
        "severity": "high",
        "root_cause": "Connection pool exhaustion due to leaked unclosed DB sessions during traffic surge",
        "resolution": "Increased connection pool size from 20 to 100 and deployed hotfix patching session leaks",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 15, 10, 30, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 15, 11, 15, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-102",
        "service": "Auth Service",
        "error": "Authentication service failure & token refresh errors",
        "symptoms": "Users unexpectedly logged out; HTTP 401 Unauthorized spike across login endpoints",
        "severity": "critical",
        "root_cause": "Clock skew across auth cluster instances after NTP service restart causing invalid token signatures",
        "resolution": "Resynchronized NTP daemon across all nodes and rotated auth signing keys",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 18, 14, 0, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 18, 14, 45, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-103",
        "service": "Notification Worker",
        "error": "Notification service failure due to Redis queue OOM",
        "symptoms": "Background push notifications and SMS alerts failing to send, queue backlog exceeding 50,000 tasks",
        "severity": "medium",
        "root_cause": "Expired notification payload keys missing TTL config causing memory exhaustion in Redis buffer",
        "resolution": "Applied volatile-lru eviction policy and backfilled TTLs for queued tasks",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 20, 8, 10, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 20, 9, 30, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-104",
        "service": "Search Indexer",
        "error": "Elasticsearch cluster yellow state",
        "symptoms": "Search results lagging behind database updates by >15 minutes",
        "severity": "low",
        "root_cause": "Unassigned replica shards due to insufficient disk space on data node 2",
        "resolution": "Expanded volume capacity and triggered shard allocation rebalance",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 22, 16, 0, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 22, 17, 20, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-105",
        "service": "Checkout Gateway",
        "error": "API latency and response degradation",
        "symptoms": "P99 response time jumped from 120ms to 4800ms; downstream payment webhooks timing out",
        "severity": "high",
        "root_cause": "Unindexed full-table scan on transaction_logs during high-volume query execution",
        "resolution": "Created composite index on (created_at, account_id) and enabled query caching in Redis",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 24, 11, 0, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 24, 12, 10, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-106",
        "service": "Customer Relational Database",
        "error": "Database connection problems & client pool refusal",
        "symptoms": "FATAL: remaining connection slots are reserved for non-replication superuser connections",
        "severity": "critical",
        "root_cause": "Zombie ORM worker connections staying open after unexpected microservice crashes",
        "resolution": "Configured idle connection timeout setting in PgBouncer and restarted orphaned backend instances",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 26, 9, 15, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 26, 10, 0, 0, tzinfo=timezone.utc),
    }
]

def seed_incidents(db: Session) -> None:
    for data in SEED_INCIDENTS:
        existing = db.query(Incident).filter(Incident.id == data["id"]).first()
        if not existing:
            incident = Incident(**data)
            db.add(incident)
            db.commit()
            db.refresh(incident)

        # Retain seed incidents into Hindsight for semantic recall
        hindsight_service.retain_incident(
            incident_id=data["id"],
            service=data["service"],
            error=data["error"],
            symptoms=data["symptoms"],
            severity=data["severity"],
            root_cause=data.get("root_cause"),
            resolution=data.get("resolution"),
            outcome=data.get("outcome", "Resolved"),
        )
