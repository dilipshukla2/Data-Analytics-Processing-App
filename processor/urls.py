# processor/urls.py
from django.urls import path
from . import views

app_name = "processor"

urlpatterns = [
    # Master pipeline trigger
    path("v1/pipeline/trigger/", views.TriggerPipelineView.as_view(), name="trigger_pipeline"),
    
    # Individual step demos
    path("v1/pipeline/step1/", views.Step1View.as_view(), name="step1"),
    path("v1/pipeline/step2-3/", views.Step2And3View.as_view(), name="step2_3"),
    
    # Result fetching
    path("v1/pipeline/<uuid:job_id>/result/", views.GetResultView.as_view(), name="get_result"),
    
    # Instant RAM/CPU bomb demo
    path("v1/pipeline/ram-bomb/", views.RamBombView.as_view(), name="ram_bomb"),
]