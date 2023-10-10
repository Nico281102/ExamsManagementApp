from flask import session
from sqlalchemy import select, text

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
    esami_non_passati = get_esami_non_passati(studente)  # lista di esami non passati
    prove_studente = []  # lista di prove di esami non passati
    for esame in esami_non_passati:
        prove_studente.append(esame.prove)  # aggiorno la lista di prove di esami non passati (è list di list)
    aux = []  # lista a una sola dimensione
    for i in prove_studente:  # trasformo la lista di liste in una lista a una sola dimensione
        for j in i:
            aux.append(j)
    prove_studente = aux  # lista di prove di esami non passati

    for appello in appelli:  # per ogni appello
        if appello.prove in prove_studente and appello not in studente.appelli:  # se l'appello ha una prova che lo studente non ha passato e non è già prenotato
            appelli_disponibili.append(appello)  # aggiungo l'appello alla lista di appelli disponibili
    return appelli_disponibili


def get_esami_non_passati(studente):
    studente_matricola = studente.matricola

    # Esegui una query per ottenere gli esami passati dallo studente
    esami_passati = Esami.query.join(formalizzazioneEsami).filter(
        formalizzazioneEsami.c.studente == studente_matricola,
        formalizzazioneEsami.c.passato == False
    ).all()

    return esami_passati


def set_voto(studente_matricola, voto, esame_cod):
    passato = False
    if voto >= 18:
        passato = True

    try:
        # Begin a transaction
        with db.engine.begin() as connection:
            # Execute the update statement
            connection.execute(
                formalizzazioneEsami
                .update()
                .where((formalizzazioneEsami.c.studente == studente_matricola) & (formalizzazioneEsami.c.esame == esame_cod))
                .values({'voto': voto, 'passato': passato})
            )

            # Fetch the updated row immediately after the update
            select_query = text(
                f"SELECT * FROM public.\"formalizzazioneEsami\" WHERE studente = {studente_matricola} AND esame = '{esame_cod}'"
            )
            updated_row = connection.execute(select_query).fetchone()

            # Check if the row is not None before attempting to convert to a dictionary
            if updated_row is not None:
                # Fetch the column names using result.keys()
                column_names = connection.execute(select_query).keys()

                # Convert the row to a dictionary
                row_dict = dict(zip(column_names, updated_row))
                print("Updated Row:", row_dict)
            else:
                print("No row found after update.")

            # Commit the changes to the database
            db.session.commit()

    except Exception as e:
        print(f"Error updating database: {e}")
        db.session.rollback()  # Rollback changes if an exception occurs






def set_voto_prova(studente_matricola, voto, prova_cod):
    voto = int(voto)
    isValid = False
    if voto >= 18 and voto <= 30 and voto != None:
        #controllare anche se la data in cui è stata svoltà la prova è antecedente alla data di scadenza
        isValid = True
    with db.engine.begin() as connection:
# Execute the update statement
        connection.execute(
            iscrizioni
            .update()
            .where((iscrizioni.c.studente == studente_matricola) & (iscrizioni.c.appello == prova_cod))
            .values({'voto': voto, 'isValid': isValid})
        )

        # Fetch the updated row immediately after the update
        select_query = text(
            f"SELECT * FROM public.\"iscrizioni\" WHERE studente = {studente_matricola} AND appello = '{prova_cod}'"
        )
        updated_row = connection.execute(select_query).fetchone()

        # Check if the row is not None before attempting to convert to a dictionary
        if updated_row is not None:
            # Fetch the column names using result.keys()
            column_names = connection.execute(select_query).keys()

            # Convert the row to a dictionary
            row_dict = dict(zip(column_names, updated_row))
            print("Updated Row:", row_dict)
        else:
            print("No row found after update.")

        # Commit the changes to the database
        db.session.commit()




def get_esame(codEsame):
    # Build the SQL query
    query = (
        select(
            Esami.cfu,
            Esami.name,
            Esami.cod,
            Esami.anno,
            Esami.docente
        )
        .where(Esami.cod == codEsame)
    )

    # Execute the query
    with db.engine.connect() as connection:
        result = connection.execute(query)

    return result.fetchone()

def get_esami_nonFormalizzati(studente_matricola):
    # Build the SQL query
    query = (
        select(
            formalizzazioneEsami.c.voto,
            formalizzazioneEsami.c.passato,
            formalizzazioneEsami.c.esame
        )
        .where((formalizzazioneEsami.c.studente == studente_matricola) & (formalizzazioneEsami.c.formalizzato == False) &
               (formalizzazioneEsami.c.voto != None))
    )

    # Execute the query
    with db.engine.connect() as connection:
        result = connection.execute(query)

    res = result.fetchall()

    for i in range(len(res)):
        res[i] = list(res[i])
        res[i][2] = (get_esame(res[i][2]).name, res[i][2])

    return res

def get_appelli_docente(teacher):
    appelli = Appelli.query.all()
    appelli_docente = []
    for appello in appelli:
        if appello.prove:
            prove = appello.prove
            if prove.docenti == teacher:
                appelli_docente.append(appello)

    return appelli_docente


