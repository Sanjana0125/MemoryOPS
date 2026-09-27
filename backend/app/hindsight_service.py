import logging
from typing import Any, Dict, List, Optional
from hindsight_client import Hindsight
from app.config import settings

logger = logging.getLogger("incidentiq.hindsight")

class HindsightService:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        bank_id: Optional[str] = None,
    ):
        self.base_url = base_url or settings.HINDSIGHT_API_URL
        self.api_key = api_key or settings.HINDSIGHT_API_KEY
        self.bank_id = bank_id or settings.HINDSIGHT_BANK_ID
        self._client: Optional[Hindsight] = None

    @property
    def client(self) -> Hindsight:
        if self._client is None:
            self._client = Hindsight(base_url=self.base_url, api_key=self.api_key)
        return self._client

    async def aretain_incident(
        self,
        incident_id: str,
        service: str,
        error: str,
        symptoms: str,
        severity: str,
        root_cause: Optional[str] = None,
        resolution: Optional[str] = None,
        outcome: str = "Resolved",
    ) -> Dict[str, Any]:
        """
        RETAIN (Async): Store a resolved incident and its investigation experience into Hindsight memory.
        """
        content_lines = [
            f"Incident ID: {incident_id}",
            f"Service: {service}",
            f"Error: {error}",
            f"Symptoms: {symptoms}",
            f"Severity: {severity}",
            f"Outcome: {outcome}",
        ]
        if root_cause:
            content_lines.append(f"Root Cause: {root_cause}")
        if resolution:
            content_lines.append(f"Resolution: {resolution}")

        content_text = "\n".join(content_lines)

        metadata = {
            "incident_id": incident_id,
            "service": service,
            "severity": severity,
            "outcome": outcome,
        }

        try:
            response = await self.client.aretain(
                bank_id=self.bank_id,
                content=content_text,
                metadata=metadata,
                document_id=incident_id,
                tags=[service, severity, outcome],
            )
            logger.info(f"Retained incident {incident_id} in Hindsight bank '{self.bank_id}'")
            return {
                "success": True,
                "incident_id": incident_id,
                "bank_id": self.bank_id,
                "response": str(response),
            }
        except Exception as e:
            logger.warning(f"Failed to retain incident {incident_id} in Hindsight: {e}")
            return {
                "success": False,
                "incident_id": incident_id,
                "bank_id": self.bank_id,
                "error": str(e),
            }

    async def arecall_memories(
        self,
        query: str,
        budget: str = "mid",
        max_tokens: int = 4096,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        RECALL (Async): Retrieve similar historical incidents/memories from Hindsight based on an incident query.
        """
        try:
            response = await self.client.arecall(
                bank_id=self.bank_id,
                query=query,
                budget=budget,
                max_tokens=max_tokens,
                tags=tags,
            )
            return {
                "success": True,
                "query": query,
                "bank_id": self.bank_id,
                "results": response,
            }
        except Exception as e:
            logger.warning(f"Failed to recall memories from Hindsight: {e}")
            return {
                "success": False,
                "query": query,
                "bank_id": self.bank_id,
                "error": str(e),
                "results": None,
            }

    async def areflect_patterns(
        self,
        query: str,
        budget: str = "low",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        REFLECT (Async): Synthesize overall patterns, recurring issues, or cross-incident takeaways from Hindsight.
        """
        try:
            response = await self.client.areflect(
                bank_id=self.bank_id,
                query=query,
                budget=budget,
                context=context,
            )
            return {
                "success": True,
                "query": query,
                "bank_id": self.bank_id,
                "results": response,
            }
        except Exception as e:
            logger.warning(f"Failed to reflect patterns from Hindsight: {e}")
            return {
                "success": False,
                "query": query,
                "bank_id": self.bank_id,
                "error": str(e),
                "results": None,
            }

    # Backward-compatibility sync aliases for non-async contexts (e.g. initial startup seeding)
    def retain_incident(self, *args, **kwargs) -> Dict[str, Any]:
        content_lines = [
            f"Incident ID: {kwargs.get('incident_id', '')}",
            f"Service: {kwargs.get('service', '')}",
            f"Error: {kwargs.get('error', '')}",
            f"Symptoms: {kwargs.get('symptoms', '')}",
            f"Severity: {kwargs.get('severity', '')}",
            f"Outcome: {kwargs.get('outcome', 'Resolved')}",
        ]
        if kwargs.get("root_cause"):
            content_lines.append(f"Root Cause: {kwargs.get('root_cause')}")
        if kwargs.get("resolution"):
            content_lines.append(f"Resolution: {kwargs.get('resolution')}")

        try:
            # When called in sync, gracefully attempt or catch if no loop
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Schedule task on existing event loop
                loop.create_task(self.aretain_incident(*args, **kwargs))
                return {"success": True, "status": "scheduled"}
            else:
                return asyncio.run(self.aretain_incident(*args, **kwargs))
        except Exception as e:
            logger.warning(f"Sync retain fallback exception: {e}")
            return {"success": False, "error": str(e)}

    def recall_memories(self, *args, **kwargs) -> Dict[str, Any]:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            logger.warning("recall_memories called synchronously inside running event loop. Use arecall_memories instead.")
            return {"success": False, "error": "Synchronous recall inside running loop. Use arecall_memories."}
        else:
            return asyncio.run(self.arecall_memories(*args, **kwargs))

    def reflect_patterns(self, *args, **kwargs) -> Dict[str, Any]:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            logger.warning("reflect_patterns called synchronously inside running event loop. Use areflect_patterns instead.")
            return {"success": False, "error": "Synchronous reflect inside running loop. Use areflect_patterns."}
        else:
            return asyncio.run(self.areflect_patterns(*args, **kwargs))

hindsight_service = HindsightService()
