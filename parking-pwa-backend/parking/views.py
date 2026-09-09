# parking/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ParkingSpot, ParkingSubmission
from .serializers import ParkingSpotSerializer, ParkingSubmissionSerializer
from django.contrib.auth.models import User

# GET /api/spots/ - Restituisce tutti i posteggi attivi
class ParkingSpotList(generics.ListAPIView):
    queryset = ParkingSpot.objects.filter(is_active=True)
    serializer_class = ParkingSpotSerializer

# POST /api/submissions/ - Permette di inviare una nuova segnalazione
class ParkingSubmissionCreate(generics.ListCreateAPIView):
    serializer_class = ParkingSubmissionSerializer
    permission_classes = [IsAuthenticated]

    # Aggiungiamo questa funzione per filtrare le segnalazioni
    def get_queryset(self):
        # Restituisce solo le segnalazioni dell'utente attualmente loggato
        return ParkingSubmission.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)