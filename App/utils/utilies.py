from flask import session
from sqlalchemy import select

from App.db.models.database import *


def check_credentials(email, password):
    student = Studenti.query.filter_by(email=email).first()
    teacher = Docenti.query.filter_by(email=email).first()
    if student:
        if student.password == password:
            session['user_type'] = type(student).__name__
            return True, student
    elif teacher:
        if teacher.password == password:
            session['user_type'] = type(teacher).__name__
            return True, teacher
    return False, None


def appelli_disponibili(studente):
    appelli = Appelli.query.all()
    appelli_disponibili = []

    # Ottenere gli esami passati dallo studente
    esami_non_passati = get_esami_non_passati(studente) # lista di esami non passati
    prove_studente = [] # lista di prove di esami non passati
    for esame in esami_non_passati:
        prove_studente.append(esame.prove) # aggiorno la lista di prove di esami non passati (è list di list)
    aux = [] # lista a una sola dimensione
    for i in prove_studente: # trasformo la lista di liste in una lista a una sola dimensione
        for j in i:
            aux.append(j)
    prove_studente = aux # lista di prove di esami non passati

    for appello in appelli: # per ogni appello
        if appello.prove in prove_studente and appello not in studente.appelli: # se l'appello ha una prova che lo studente non ha passato e non è già prenotato
            appelli_disponibili.append(appello) # aggiungo l'appello alla lista di appelli disponibili
    return appelli_disponibili



def get_esami_non_passati(studente):
    studente_matricola = studente.matricola

    # Esegui una query per ottenere gli esami passati dallo studente
    esami_passati = Esami.query.join(formalizzazioneEsami).filter(
        formalizzazioneEsami.c.studente == studente_matricola,
        formalizzazioneEsami.c.passato == False
    ).all()

    return esami_passati
