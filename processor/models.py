# processor/models.py
import uuid
from django.db import models
from django.utils import timezone

class Merchant(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    risk_tier = models.CharField(max_length=20, default='standard') # 'standard', 'high', 'critical'

class Customer(models.Model):
    email_hash = models.CharField(max_length=100, db_index=True)
    account_age_days = models.IntegerField()

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.CharField(max_length=100, db_index=True)

class Transaction(models.Model):
    """The Heavyweight: 10 Million Records"""
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    
    amount = models.FloatField()
    status = models.CharField(max_length=20, db_index=True) # 'completed', 'flagged'
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

class ProcessingJob(models.Model):
    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, default='pending')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    peak_memory_mb = models.FloatField(default=0.0) # We will simulate tracking this

class FraudAnalysisResult(models.Model):
    job = models.ForeignKey(ProcessingJob, on_delete=models.CASCADE, related_name='results')
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    total_suspicious_amount = models.FloatField()
    transaction_count = models.IntegerField()
    complex_risk_hash = models.CharField(max_length=100) # To store heavy string output