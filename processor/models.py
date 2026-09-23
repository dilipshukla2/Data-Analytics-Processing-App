from django.db import models

class FinalReport(models.Model):
    report_id = models.CharField(max_length=100, unique=True)
    processed_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.report_id