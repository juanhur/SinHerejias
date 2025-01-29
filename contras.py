import streamlit as st
from PIL import Image
import streamlit as st
import streamlit_authenticator as stauth
# Diccionario con credenciales de usuario en texto plano
credentials = {
    "usernames": {
        "usuario1": {
            "name": "pruebas",
            "password": "pruebas"
        },
        "usuario2": {
            "name": "Ana López",
            "password": "otra_contraseña_segura"
        }
    }
}
hashed_passwords = stauth.Hasher.hash_passwords(credentials)
print(hashed_passwords)