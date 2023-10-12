from App.db.create_db import create_formalizzato_2, create_formalizzato
from App.db.models.database import Studenti, db
from App.utils.utilies import set_voto
from main import app





with app.app_context():

    create_formalizzato()
    print("Formalizzato creato")

    print("DB initialized")