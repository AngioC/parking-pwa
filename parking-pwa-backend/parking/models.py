# parking/models.py
from django.contrib.gis.db import models
from django.contrib.auth.models import User

class ParkingSpot(models.Model):
    # Il PointField salva Latitudine e Longitudine. 
    # SRID 4326 è lo standard WGS84 (quello del GPS e di Google Maps/Leaflet)
    location = models.PointField(srid=4326, verbose_name="Coordinate GPS")
    description = models.TextField(blank=True, null=True, verbose_name="Descrizione/Note")
    is_active = models.BooleanField(default=True, verbose_name="Attivo")
    photo = models.ImageField(upload_to='spots/', blank=True, null=True, verbose_name="Foto Posteggio")
    
    # Utente che lo ha aggiunto (o di cui è stata approvata la segnalazione)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Posteggio #{self.id} - {self.location.y}, {self.location.x}"

class ParkingSubmission(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'In attesa'),
        ('APPROVED', 'Approvato'),
        ('REJECTED', 'Rifiutato'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utente Segnalatore")
    location = models.PointField(srid=4326, verbose_name="Posizione Segnalata")
    description = models.TextField(blank=True, null=True, verbose_name="Dettagli aggiuntivi")
    
    # Salveremo solo l'URL della foto (che caricheremo su Supabase Storage o S3)
    photo = models.ImageField(upload_to='submissions/', blank=True, null=True, verbose_name="Foto Prova")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Note Admin (Motivo rifiuto)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Segnalazione {self.id} da {self.user.username} - {self.get_status_display()}"