# parking/authentication.py
import requests
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

class SupabaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None 

        token = auth_header.split(' ')[1]
        
        # Facciamo una chiamata GET a Supabase per verificare l'utente
        user_url = f"{settings.SUPABASE_URL}/auth/v1/user"
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        
        try:
            response = requests.get(user_url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Errore di connessione a Supabase: {e}")
            raise exceptions.AuthenticationFailed('Impossibile contattare Supabase.')
        
        # Se Supabase risponde con un errore (es. token scaduto o modificato)
        if response.status_code != 200:
            print(f"Token rifiutato da Supabase. Dettagli: {response.text}")
            raise exceptions.AuthenticationFailed('Token non valido o scaduto.')
            
        # Token valido! Supabase ci restituisce i dati dell'utente
        user_data = response.json()
        email = user_data.get('email')
        
        if not email:
            raise exceptions.AuthenticationFailed('Email mancante nel profilo utente.')

        # Troviamo o creiamo l'utente nel database di Django
        user, created = User.objects.get_or_create(
            username=email, 
            defaults={'email': email}
        )

        return (user, token)