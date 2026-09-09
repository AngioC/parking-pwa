# parking/urls.py
from django.urls import path
from .views import ParkingSpotList, ParkingSubmissionCreate

urlpatterns = [
    path('spots/', ParkingSpotList.as_view(), name='spot-list'),
    path('submissions/', ParkingSubmissionCreate.as_view(), name='submission-create'),
]