from django.urls import path
from . import views

urlpatterns = [
    path('step1/', views.Step1View.as_view(), name='step1'),
    path('step2/', views.Step2View.as_view(), name='step2'),
    path('step3/', views.Step3View.as_view(), name='step3'),
    path('step4/', views.Step4View.as_view(), name='step4'),
    
    # Master API for CI/CD
    path('run-pipeline/', views.MasterPipelineView.as_view(), name='master_pipeline'),
]