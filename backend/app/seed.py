from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Incident

SEED_INCIDENTS = [
    {
        "id": "INC-101",
        "service": "Payment API",
        "error": "Database connection timeout",
        "symptoms": "High HTTP 504 Gateway Timeouts on /v1/charge endpoint, elevated API latency",
        "severity": "high",
        "root_cause": "Connection pool exhaustion due to leaked unclosed DB sessions during traffic surge",
        "resolution": "Increased connection pool size from 20 to 100 and deployed hotfix for session leak",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 15, 10, 30, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 15, 11, 15, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-102",
        "service": "Auth Service",
        "error": "JWT validation failure on token refresh",
        "symptoms": "Users unexpectedly logged out; spike in 401 Unauthorized error rate",
        "severity": "critical",
        "root_cause": "Clock skew across auth cluster instances after NTP service restart",
        "resolution": "Resynchronized NTP daemon across all nodes and rotated auth signing keys",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 18, 14, 0, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 18, 14, 45, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-103",
        "service": "Notification Worker",
        "error": "Redis OOM command not allowed",
        "symptoms": "Background push notifications failing to send, queue backlog building up",
        "severity": "medium",
        "root_cause": "Expired notification payload keys missing TTL config causing memory leak",
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
    }
]

def seed_incidents(db: Session) -> None:
    for data in SEED_INCIDENTS:
        existing = db.query(Incident).filter(Incident.id == data["id"]).first()
        if not existing:
            incident = Incident(**data)
            db.add(incident)
    db.commit()
