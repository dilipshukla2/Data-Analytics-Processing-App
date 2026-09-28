# locustfile.py
from locust import HttpUser, task


class SingleShotPipelineUser(HttpUser):
    """
    Each virtual user sends exactly ONE request, then stops.
    This ensures exactly N requests are queued, and all of them 
    will eventually complete without infinite looping.
    """

    @task
    def trigger_pipeline_once(self):
        self.client.post(
            "/api/v1/pipeline/trigger/",
            json={},
            name="POST /api/v1/pipeline/trigger/",
            timeout=None,  # Wait indefinitely in the queue, do not drop the connection
        )
        # Stop this virtual user immediately after sending the request
        self.stop(force=True)