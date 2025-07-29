import os
import logging
import requests
import firebase_admin

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from fastapi import HTTPException
from firebase_admin import credentials, auth as firebase_auth
from dotenv import load_dotenv

from models.users import User
from models.login import Login

from utils.security import create_jwt_token


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
URI = os.getenv("URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

cred = credentials.Certificate("secrets/futurafree-secrets.json")
firebase_admin.initialize_app(cred)


def get_collection(uri, col):
    client = MongoClient(
        uri,
        server_api=ServerApi("1"),
        tls=True,
        tlsAllowInvalidCertificates=True,
    )
    client.admin.command("ping")  # Para probar conexión
    return client[MONGO_DB_NAME][col]


async def create_user(user: User) -> User:
    user_record = {}
    try: 
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )
    except Exception as e:
        logger.warning(e)
        raise HTTPException(
            status_code=400,
            detail="Error al registrar al usuario en Firebase"
        )

    try:
        coll = get_collection(URI, "users")
        user_dict = user.model_dump(exclude={"id", "password"})
        inserted = coll.insert_one(user_dict)
        user.id = str(inserted.inserted_id)
        return user
    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        logger.error(f"Error creando usuario en MongoDB: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el usuario")


async def login(user: Login) -> dict:
    api_key = os.getenv("FIREBASE_API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    response_data = response.json()

    if "error" in response_data:
        raise HTTPException(
            status_code=400,
            detail="Error al autenticar usuario"
        )

    # Aquí corregimos pasando URI y nombre de colección
    coll = get_collection(URI, "users")
    user_info = coll.find_one({"email": user.email})

    if not user_info:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado en la base de datos"
        )

    return {
        "message": "Usuario Autenticado correctamente",
        "idToken": create_jwt_token(
            user_info["name"],
            user_info["lastname"],
            user_info["email"],
            user_info["active"],
            user_info["admin"],
            str(user_info["_id"])
        )
    }