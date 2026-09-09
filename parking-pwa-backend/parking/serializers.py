# parking/serializers.py
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import ParkingSpot, ParkingSubmission

class ParkingSpotSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = ParkingSpot
        # Indichiamo quale campo contiene la geometria (per generare il GeoJSON)
        geo_field = "location"
        fields = ['id', 'description', 'photo', 'is_active', 'created_at']

class ParkingSubmissionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = ParkingSubmission
        geo_field = "location"
        fields = ['id', 'description', 'photo', 'status', 'created_at']
        read_only_fields = ['status', 'created_at'] # L'utente non può inviare lo stato