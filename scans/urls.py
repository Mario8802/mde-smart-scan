from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("scan/", views.scan_capture, name="scan-capture"),
    path("scan/<int:pk>/", views.scan_review, name="scan-review"),
    path("scan/<int:pk>/prepare-label/", views.prepare_label, name="prepare-label"),
    path("scan/<int:pk>/label/", views.scan_label, name="scan-label"),
    path("api/v1/scans/", views.scans_api, name="scans-api"),
    path("api/v1/impact/", views.impact_api, name="impact-api"),
    path("health/", views.health, name="health"),
]
