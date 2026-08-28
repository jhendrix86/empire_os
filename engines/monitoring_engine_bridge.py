import httpx
from typing import Any, Dict
from empire_os.operators.all_operators import DriftMonitor

class MonitoringEngineBridge:
    def __init__(self, monitoring_engine_url: str):
        self.url = monitoring_engine_url.rstrip("/")
        self.client = httpx.Client(timeout=10.0)

    def fetch_metrics(self) -> Dict[str, Any]:
        """Fetch real performance metrics from the monitoring-engine."""
        try:
            response = self.client.get(f"{self.url}/performance/summary")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Honest failure, log and continue. Do not crash.
            print(f"Shadow Integration Error: Could not fetch metrics from {self.url}: {e}")
            return {}

    def analyze_drift(self, current_metrics: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Pass real metrics through the DriftMonitor operator."""
        state = {
            "current_metrics": current_metrics,
            "baseline_metrics": baseline
        }
        operator = DriftMonitor()
        return operator.execute(state)
