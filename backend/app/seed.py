from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Incident
from app.hindsight_service import hindsight_service

SEED_INCIDENTS = [
    {
        "id": "INC-101",
        "service": "Payment API",
        "error": "Database connection timeout",
        "symptoms": "High HTTP 504 Gateway Timeouts on /v1/charge endpoint, elevated API latency",
        "severity": "high",
        "root_cause": "Connection pool exhaustion due to leaked unclosed DB sessions during traffic surge",
        "resolution": "Increased connection pool size from 20 to 100 and deployed hotfix for session leak",
        "post_mortem": "Connection pool configuration was insufficient for observed traffic surges. Added automated connection pool utilization alerting at 80% capacity.",
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
        "post_mortem": "NTP service daemon configuration lacked drift limits across nodes. Added chrony status monitoring to cluster health checks.",
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
        "post_mortem": "Expired Redis keys lacked TTL eviction policy. Updated Redis queue configuration to volatile-lru and enforced key TTL checks.",
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
        "post_mortem": "Data node storage allocation threshold was unmonitored. Added auto-expanding EBS volumes and disk space alarms at 85%.",
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
        "post_mortem": "Unindexed query on transaction_logs caused full table scans. Enforced index requirement checks in CI/CD migration pipeline.",
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
        "post_mortem": "Worker processes failed to clean up idle connection pools upon crashes. Added PgBouncer connection limits and process crash recovery hooks.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 26, 9, 15, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 26, 10, 0, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-107",
        "service": "Kubernetes Ingress Gateway",
        "error": "HTTP 502 Bad Gateway across API endpoints",
        "symptoms": "Spike in 502 error rates on ingress controller; upstream pods failing readiness probes",
        "severity": "high",
        "root_cause": "Uncapped pod memory limits resulting in Linux OOMKilled crashes during batch request processing",
        "resolution": "Increased container memory request/limit ratio and enabled Horizontal Pod Autoscaler (HPA)",
        "post_mortem": "Inadequate container memory limits caused unexpected OOM Kills. Implemented resource request/limit standard guidelines in Kubernetes manifests.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 28, 14, 20, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 28, 15, 0, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-108",
        "service": "Event Streaming Pipeline",
        "error": "Kafka Consumer Group Rebalance Storm",
        "symptoms": "Consumer lag spiking to >100k messages; stream processing latency exceeded 10 minutes",
        "severity": "critical",
        "root_cause": "Max poll interval timeout exceeded by heavy synchronous database batch processing in stream loop",
        "resolution": "Offloaded DB writes to asynchronous worker pools and adjusted max.poll.interval.ms to 600,000ms",
        "post_mortem": "Synchronous DB writes blocked Kafka consumer message polling loop. Migrated stream event handlers to async worker queues.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 3, 30, 8, 45, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 3, 30, 9, 40, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-109",
        "service": "Media Storage Service",
        "error": "AWS S3 AccessDenied Exception during file upload",
        "symptoms": "HTTP 403 Forbidden on avatar and attachment uploads across web and mobile clients",
        "severity": "medium",
        "root_cause": "Stale IAM role session policy attached to EKS service account missing s3:PutObjectAcl permission",
        "resolution": "Updated IAM policy JSON with s3:PutObjectAcl and recycled EKS worker service account pods",
        "post_mortem": "Service account IAM policy lacked explicit PutObjectAcl action. Added automated IAM policy linting in Terraform pipeline.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 4, 1, 12, 10, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 4, 1, 12, 50, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-110",
        "service": "Service Mesh Proxy",
        "error": "TLS Certificate Expiration on Internal gRPC Endpoints",
        "symptoms": "transport: authentication handshake failed: x509: certificate expired",
        "severity": "critical",
        "root_cause": "Cert-manager webhook renewal pipeline stalled due to failed Let's Encrypt ACME challenge retry",
        "resolution": "Manually re-issued cert-manager ClusterIssuer resource and triggered secret rotation across Istio proxies",
        "post_mortem": "Cert-manager webhook renewal failed silently. Added expiration monitoring alerts for internal gRPC TLS certificates 7 days in advance.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 4, 3, 16, 0, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 4, 3, 16, 30, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-111",
        "service": "CoreDNS Resolver Cluster",
        "error": "Cluster internal DNS resolution timeout",
        "symptoms": "i/o timeout errors resolving *.cluster.local service names across all microservice namespaces",
        "severity": "high",
        "root_cause": "UDP packet loss in CoreDNS pods due to socket buffer exhaustion during DNS query spike",
        "resolution": "Autoscaled CoreDNS deployment to 10 replicas and enabled autopath plugin for search domain optimization",
        "post_mortem": "CoreDNS query spikes led to UDP socket buffer packet drops. Configured HPA for CoreDNS deployment and autopath DNS optimization.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 4, 5, 11, 20, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-112",
        "service": "RabbitMQ Task Broker",
        "error": "RabbitMQ memory alarm triggered & publisher channel blockage",
        "symptoms": "Publishers receiving channel block warnings; high memory alarm threshold reached (4GB limit)",
        "severity": "high",
        "root_cause": "Dead letter exchange queue filled up without consumer handling expired payload retries",
        "resolution": "Purged dead-letter queue backlog, set x-max-length policy, and increased cluster memory high watermark",
        "post_mortem": "RabbitMQ dead-letter exchange backlog accumulated unhandled expired messages. Implemented queue length alarms and auto-purging dead letter policy.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 4, 7, 9, 30, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 4, 7, 10, 15, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-113",
        "service": "Central Logging Aggregator",
        "error": "Logstash ingestion pipeline backpressure stalling Filebeat",
        "symptoms": "Log latency in Kibana >2 hours behind real time; Kubernetes nodes dropping log buffers",
        "severity": "medium",
        "root_cause": "Elasticsearch cluster reached flood_stage disk watermark (95% usage), blocking index writes",
        "resolution": "Applied ILM policy to delete index snapshots older than 30 days and reset index.blocks.read_only_allow_delete",
        "post_mortem": "Elasticsearch disk usage reached read-only flood stage threshold. Automated snapshot ILM cleanup policy for indices older than 30 days.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 4, 9, 15, 10, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 4, 9, 16, 0, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-114",
        "service": "HashiCorp Vault Service",
        "error": "Vault Dynamic Secret Lease Expiration causing Auth Crashes",
        "symptoms": "PostgreSQL database login errors: role 'v-token-xyz' does not exist",
        "severity": "critical",
        "root_cause": "Vault renewal sidecar container failed due to expired Vault token permission policy",
        "resolution": "Renewed root Vault token, updated sidecar policy TTL to 24 hours, and restarted auth pods",
        "post_mortem": "Sidecar container Vault renewal token expired without retry alert. Updated Vault token renewal policy TTL to 24 hours and added health probes.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 4, 11, 10, 0, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 4, 11, 10, 45, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-115",
        "service": "Cloudflare CDN Edge",
        "error": "CDN Edge Cache Stale Data & Cache Invalidation Failure",
        "symptoms": "Users seeing outdated UI web assets and stale API response payloads after blue/green deployment",
        "severity": "low",
        "root_cause": "Cache-Control header configured with s-maxage=86400 without Cache-Tag header for targeted purge",
        "resolution": "Triggered full CDN cache purge and updated Cache-Control header to no-cache, must-revalidate for dynamic routes",
        "post_mortem": "CDN Cache-Control headers lacked Cache-Tag tags for targeted invalidation. Configured revalidation headers for dynamic asset routes.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 4, 13, 14, 0, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 4, 13, 14, 25, 0, tzinfo=timezone.utc),
    },
    {
        "id": "INC-116",
        "service": "Prometheus Monitoring Service",
        "error": "Prometheus TSDB Write Ahead Log (WAL) Corruption",
        "symptoms": "Prometheus server pod stuck in CrashLoopBackOff with 'err=corrupted WAL segment'",
        "severity": "high",
        "root_cause": "Hard node shutdown during cloud provider maintenance without clean SIGTERM shutdown",
        "resolution": "Removed corrupted WAL segment files from TSDB storage directory and restarted Prometheus instance",
        "post_mortem": "Unclean host node shutdown corrupted TSDB WAL segment. Configured graceful termination grace period on monitoring pods.",
        "outcome": "Resolved",
        "created_at": datetime(2026, 4, 15, 7, 50, 0, tzinfo=timezone.utc),
        "resolved_at": datetime(2026, 4, 15, 8, 30, 0, tzinfo=timezone.utc),
    }
]

async def aseed_incidents(db: Session) -> None:
    for data in SEED_INCIDENTS:
        existing = db.query(Incident).filter(Incident.id == data["id"]).first()
        if not existing:
            incident = Incident(
                id=data["id"],
                service=data["service"],
                error=data["error"],
                symptoms=data["symptoms"],
                severity=data["severity"],
                root_cause=data.get("root_cause"),
                resolution=data.get("resolution"),
                post_mortem=data.get("post_mortem"),
                outcome=data.get("outcome", "Resolved"),
                created_at=data["created_at"],
                resolved_at=data.get("resolved_at"),
                memory_retained=False,
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
        else:
            if data.get("post_mortem") and not existing.post_mortem:
                existing.post_mortem = data.get("post_mortem")
                db.commit()
            incident = existing

        if incident.outcome.lower() == "resolved" and (incident.root_cause or incident.resolution) and not incident.memory_retained:
            retain_res = await hindsight_service.aretain_incident(
                incident_id=incident.id,
                service=incident.service,
                error=incident.error,
                symptoms=incident.symptoms,
                severity=incident.severity,
                root_cause=incident.root_cause,
                resolution=incident.resolution,
                post_mortem=incident.post_mortem,
                outcome=incident.outcome,
            )
            if retain_res.get("success"):
                incident.memory_retained = True
                db.commit()

def seed_incidents(db: Session) -> None:
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(aseed_incidents(db))
    else:
        asyncio.run(aseed_incidents(db))
