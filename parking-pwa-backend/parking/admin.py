# parking/admin.py
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.contrib import messages
from .models import ParkingSpot, ParkingSubmission

# --- 1. DEFINIAMO LE AZIONI CUSTOM ---

@admin.action(description='✅ Approva le segnalazioni selezionate (Pubblica sulla mappa)')
def approve_submissions(modeladmin, request, queryset):
    submissions_to_approve = queryset.exclude(status='APPROVED')
    count = 0
    
    for sub in submissions_to_approve:
        ParkingSpot.objects.create(
            location=sub.location,
            description=sub.description,
            added_by=sub.user,
            is_active=True,
            photo=sub.photo  # <--- AGGIUNGI QUESTA RIGA PER COPIARE LA FOTO
        )
        sub.status = 'APPROVED'
        sub.save()
        count += 1
        
    modeladmin.message_user(request, f"{count} segnalazioni approvate e pubblicate con successo!", messages.SUCCESS)

@admin.action(description='❌ Rifiuta le segnalazioni selezionate')
def reject_submissions(modeladmin, request, queryset):
    # Aggiornamento massivo dello stato
    updated = queryset.update(status='REJECTED')
    modeladmin.message_user(request, f"{updated} segnalazioni sono state rifiutate.", messages.WARNING)


# --- 2. REGISTRIAMO I MODELLI ---

@admin.register(ParkingSpot)
class ParkingSpotAdmin(GISModelAdmin):
    # Abbiamo aggiunto 'photo_link' alla lista
    list_display = ('id', 'location', 'is_active', 'added_by', 'created_at', 'photo_link')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('photo_link',)
    
    gis_widget_kwargs = {
        'attrs': {
            'default_lon': 12.49, 
            'default_lat': 41.90, 
            'default_zoom': 5,
        }
    }

    # Funzione per mostrare il link cliccabile nell'admin
    def photo_link(self, obj):
        if obj.photo:
            return f'<a href="{obj.photo.url}" target="_blank">Vedi Foto</a>'
        return "Nessuna foto"
    
    photo_link.allow_tags = True
    photo_link.short_description = "Foto"

@admin.register(ParkingSubmission)
class ParkingSubmissionAdmin(GISModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('media_url_link',)
    
    # COLLEGHIAMO LE AZIONI AL PANNELLO!
    actions = [approve_submissions, reject_submissions]

    gis_widget_kwargs = {
        'attrs': {
            'default_lon': 12.49, 
            'default_lat': 41.90, 
            'default_zoom': 5,
        }
    }

    def media_url_link(self, obj):
        if obj.photo:
            return f'<a href="{obj.photo.url}" target="_blank">Vedi Foto Prova</a>'
        return "Nessuna foto"
    
    media_url_link.allow_tags = True
    media_url_link.short_description = "Foto Prova"