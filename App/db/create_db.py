from flask_sqlalchemy.session import Session
from sqlalchemy import text

from App.utils.utilies import set_voto
from main import app
from App.db.models.database import Studenti, Docenti, Esami, db, Prove, Appelli, iscrizioni, Superamenti, \
    formalizzazioneEsami

query = Session(db)

def add(obj):
    db.session.add(obj)
    db.session.commit()


def create_trigger():
    # Comando SQL per creare il trigger PostgreSQL
    create_trigger_sql = """
        CREATE TRIGGER invalidate_trial 
        BEFORE INSERT ON Iscrizioni 
        FOR EACH ROW 
        EXECUTE FUNCTION invalidate_trial_function(); 
    """

    # Comando SQL per creare la funzione PostgreSQL
    create_function_sql = """
        CREATE OR REPLACE FUNCTION invalidate_trial_function() RETURNS TRIGGER AS $$ 
        BEGIN
            UPDATE Iscrizioni 
            SET "isValid" = FALSE 
            WHERE studente = new.studente 
            AND appello IN (
                SELECT Appelli."codAppello"
                FROM Appelli JOIN Iscrizioni ON  Appelli."codAppello" = appello
                WHERE Iscrizioni."isValid" = TRUE 
                AND Iscrizioni."voto" >= 18 
                AND prova IN (
                    SELECT prova 
                    FROM Appelli 
                    WHERE Appelli."codAppello" = new.appello
                )
            );
            RETURN NEW;
        END; 
        $$ LANGUAGE plpgsql;"""

    create_trigger_sql2= """
        CREATE TRIGGER invalidate_exam_cascade
        BEFORE UPDATE ON Iscrizioni 
        FOR EACH ROW 
        WHEN (new."isValid" = FALSE)
        EXECUTE FUNCTION invalidate_exam_cascade_function(); """

    create_function_sql2 = """
        CREATE OR REPLACE FUNCTION invalidate_exam_cascade_function() RETURNS TRIGGER AS $$ 
        BEGIN
            -- Rimozione dell'esame che era formalizzabile, in quanto una prova che lo costituiva non è più valida
            UPDATE "formalizzazioneEsami"	
            SET "passato" = FALSE 		 
            WHERE studente = new.studente 
            AND passato = TRUE 
            AND "formalizzazioneEsami".esame IN (
                SELECT esame 
                FROM appelli JOIN prove ON  appelli."prova" = prove."cod"
                WHERE appelli."codAppello" = new.appello
            ); 

            -- Gestione invalida prove che richiedevano una prova che è stata invalidata, produce ricorsione di chiamate 
            UPDATE Iscrizioni
            SET "isValid" = FALSE
            WHERE studente = new.studente AND "isValid" = TRUE 
            AND appello IN (
                SELECT appelli."codAppello"
                FROM Appelli 
                WHERE prova IN (
                    SELECT superamenti."provaSuccessiva"
                    FROM Superamenti JOIN Appelli ON prova = superamenti."provaPrimaria"
                    WHERE appelli."codAppello" = NEW.appello
                )
            );	 
            RETURN NEW; 
        END; 
        $$ LANGUAGE plpgsql;
    """

    # Esegui i comandi SQL per creare il trigger e la funzione

    with db.engine.connect() as conn:
        # Ottieni una connessione al database
        conn = db.session.connection()

        # Esegui i comandi SQL per creare il trigger e la funzione
        conn.execute(text(create_function_sql))
        conn.execute(text(create_function_sql2))
        conn.execute(text(create_trigger_sql))
        conn.execute(text(create_trigger_sql2))



    db.session.commit()

        # Chiamata alla funzione per creare il trigger e la funzione


def creates_students():
    domenico_sosta = Studenti(name='Domenico', surname='Sosta', matricola=892075, password='1', phone='3479145154')
    add(domenico_sosta)
    luca_bianchi = Studenti(name='Luca', surname='Bianchi', matricola=892076, password='1', phone='3479145152')
    add(luca_bianchi)
    mario_rossi = Studenti(name='Mario', surname='Rossi', matricola=892077, password='1', phone='3479145153')
    add(mario_rossi)
    giusy_verdi = Studenti(name='Giusy', surname='Verdi', matricola=892078, password='1', phone='3479145155')
    add(giusy_verdi)

    return domenico_sosta, luca_bianchi, mario_rossi, giusy_verdi


def create_teacher():
    pietro_ferrara = Docenti(name='Pietro', surname='Ferrara', password='1')
    alvis_spano = Docenti(name='Alvise', surname='Spano', password='1')
    stefano_calzavara = Docenti(name='Stefano', surname='Calzavara', password='1')
    alessandra_raffaeta = Docenti(name='Alessandra', surname='Raffaeta', password='1')
    claudio_lucchese = Docenti(name='Claudio', surname='Lucchese', password='1')
    andrea_marin = Docenti(name='Andrea', surname='Marin', password='1')
    riccardo_focardi = Docenti(name='Riccardo', surname='Focardi', password='1')
    simonetta_balsamo = Docenti(name='Simonetta', surname='Balsamo', password='1')
    marcello_pelillo = Docenti(name='Marcello', surname='Pelillo', password='1')
    add(pietro_ferrara)
    add(alvis_spano)
    add(stefano_calzavara)
    add(alessandra_raffaeta)
    add(claudio_lucchese)
    add(andrea_marin)
    add(riccardo_focardi)
    add(simonetta_balsamo)
    add(marcello_pelillo)
    obj = {}
    for docente in Docenti.query.all():
        obj[docente.email] = docente.cod
    return obj

def creat_exam_and_teacher():
    pietro_ferrara = Docenti(name='Pietro', surname='Ferrara', password='1')
    alvise_spano = Docenti(name='Alvise', surname='Spano', password='1')
    stefano_calzavara = Docenti(name='Stefano', surname='Calzavara', password='1')
    alessandra_raffaeta = Docenti(name='Alessandra', surname='Raffaeta', password='1')
    claudio_lucchese = Docenti(name='Claudio', surname='Lucchese', password='1')
    andrea_marin = Docenti(name='Andrea', surname='Marin', password='1')
    riccardo_focardi = Docenti(name='Riccardo', surname='Focardi', password='1')
    simonetta_balsamo = Docenti(name='Simonetta', surname='Balsamo', password='1')
    marcello_pelillo = Docenti(name='Marcello', surname='Pelillo', password='1')
    simeoni_marta = Docenti(name='Marta', surname='Simeoni', password='1')
    bergamasco_filippo = Docenti(name='Filippo', surname='Bergamasco', password='1')


    PO = Esami(name='Programmazione ad Oggetti', cod='01QWERTY', cfu=12, anno=2)
    add(PO)
    add(pietro_ferrara)
    add(alvise_spano)
    pietro_ferrara.esami.append(PO)
    alvise_spano.esami.append(PO)
    BD = Esami(name='Basi di dati', cod='02QWERTY', cfu=12, anno=2)
    add(BD)
    add(stefano_calzavara)
    stefano_calzavara.esami.append(BD)
    SO = Esami(name='Sistemi operativi', cod='03QWERTY', cfu=12, anno=2)
    add(SO)
    add(simonetta_balsamo)
    add(riccardo_focardi)
    simonetta_balsamo.esami.append(SO)
    riccardo_focardi.esami.append(SO)
    PL = Esami(name='Programmazione e Laboratorio', cod='04QWERTY', cfu=12, anno=1)
    add(PL)
    add(andrea_marin)
    andrea_marin.esami.append(PL)
    ASD = Esami(name='Algoritmi e Strutture Dati', cod='05QWERTY', cfu=12, anno=2)
    add(ASD)
    add(alessandra_raffaeta)
    add(marcello_pelillo)
    alessandra_raffaeta.esami.append(ASD)
    marcello_pelillo.esami.append(ASD)
    RC = Esami(name='Reti di Calcolatori', cod='06QWERTY', cfu=12, anno=3)
    add(RC)
    add(simonetta_balsamo)
    simonetta_balsamo.esami.append(RC)
    IAP = Esami(name='Introduzione alla programmazione', cod='07QWERTY', cfu=6, anno=1)
    DWM = Esami(name='Data and Web Mining', cod='08QWERTY', cfu=6, anno=3)
    add(IAP)
    add(DWM)
    add(claudio_lucchese)
    claudio_lucchese.esami.append(IAP)
    claudio_lucchese.esami.append(DWM)
    ADE = Esami(name='Architettura degli Elaboratori', cod='09QWERTY', cfu=12, anno=1)
    add(ADE)
    add(simeoni_marta)
    simeoni_marta.esami.append(ADE)

    add(bergamasco_filippo)

    obj = {}
    for docente in Docenti.query.all():
        obj[docente.email] = docente.cod
    return obj



def create_test(dict_docenti):
    ferrara_cod = dict_docenti['pietro.ferrara@unive.it']
    calzavara_cod = dict_docenti['stefano.calzavara@unive.it']
    focardi_cod = dict_docenti['riccardo.focardi@unive.it']
    marin_cod = dict_docenti['andrea.marin@unive.it']
    raffaeta_cod = dict_docenti['alessandra.raffaeta@unive.it']
    spano_cod = dict_docenti['alvise.spano@unive.it']
    balsamo_cod = dict_docenti['simonetta.balsamo@unive.it']
    pelillo_cod = dict_docenti['marcello.pelillo@unive.it']
    lucchese_cod = dict_docenti['claudio.lucchese@unive.it']

    add(Prove(esame='01QWERTY', docente=ferrara_cod, peso=0.5, cod='PO1',  Tipologia='Scritto'))
    add(Prove(esame='01QWERTY', docente=spano_cod, peso=0.5, cod='PO2',Tipologia='Scritto'))

    add(Prove(esame='02QWERTY', docente=raffaeta_cod, peso=0.5, cod='BD1', Tipologia='Scritto'))
    add(Prove(esame='02QWERTY', docente=calzavara_cod, peso=0.3, cod='BD2', Tipologia='Scritto'))
    add(Prove(esame='02QWERTY', docente=calzavara_cod, peso=0.2,  cod='BDProject', Tipologia='Progetto'))

    add(Prove(esame='03QWERTY', docente=balsamo_cod, peso=0.5,  cod='SO1', Tipologia='Scritto'))
    add(Prove(esame='03QWERTY', docente=focardi_cod, peso=0.5,  cod='SO2', Tipologia='Scritto'))

    add(Prove(esame='04QWERTY', docente=marin_cod, peso=0.5,  cod='PL1', Tipologia='Scritto'))
    add(Prove(esame='04QWERTY', docente=marin_cod, peso=0.5, cod='PL2', Tipologia='Orale'))

    add(Prove(esame='05QWERTY', docente=raffaeta_cod, peso=0.5, cod='ASD1', Tipologia='Scritto'))
    add(Prove(esame='05QWERTY', docente=pelillo_cod, peso=0.5, cod='ASD2', Tipologia='Scritto'))

    add(Prove(esame='06QWERTY', docente=balsamo_cod, peso=1.0, cod='RC1', Tipologia='Scritto'))

    add(Prove(esame='07QWERTY', docente=lucchese_cod, peso=1.0, cod='IAP', Tipologia='Scritto'))


def create_appelli():

    add(Appelli(data='2023-01-10 12:00:00', luogo='Aula1', prova='PO1'))
    add(Appelli(data='2023-01-10', luogo='Aula2', prova='PO2'))

    add(Appelli(data='2023-01-15', luogo='Aula1', prova='BD1'))
    add(Appelli(data='2023-01-15', luogo='Aula2', prova='BD2'))

    add(Appelli(data='2023-01-20', luogo='Aula1', prova='SO1'))
    add(Appelli(data='2023-01-20', luogo='Aula2', prova='SO2'))

    add(Appelli(data='2023-01-25', luogo='Aula1', prova='PL1'))
    add(Appelli(data='2023-01-25', luogo='Aula2', prova='PL2'))

    add(Appelli(data='2023-01-30', luogo='Aula1', prova='ASD1'))
    add(Appelli(data='2023-01-30', luogo='Aula2', prova='ASD2'))


    add(Appelli(data='2024-01-01', luogo='Aula1', prova='PO1'))
    add(Appelli(data='2024-01-01', luogo='Aula2', prova='PO2'))

    add(Appelli(data='2024-01-05', luogo='Aula1', prova='BD1'))
    add(Appelli(data='2024-01-05', luogo='Aula2', prova='BD2'))

    add(Appelli(data='2024-01-10', luogo='Aula1', prova='SO1'))
    add(Appelli(data='2024-01-10', luogo='Aula2', prova='SO2'))

    add(Appelli(data='2024-01-15', luogo='Aula1', prova='PL1'))
    add(Appelli(data='2024-01-15', luogo='Aula2', prova='PL2'))

    add(Appelli(data='2024-01-20', luogo='Aula1', prova='ASD1'))
    add(Appelli(data='2024-01-20', luogo='Aula2', prova='ASD2'))

    add(Appelli(data='2024-01-25', luogo='Aula1', prova='RC1'))

    add(Appelli(data='2024-01-19', luogo='Aula1', prova='IAP'))



def create_superamento():
    add(Superamenti(provaPrimaria='PO1', provaSuccessiva='PO2'))
    add(Superamenti(provaPrimaria='BD1', provaSuccessiva='BD2'))
    add(Superamenti(provaPrimaria='BD2', provaSuccessiva='BDProject'))
    add(Superamenti(provaPrimaria='SO1', provaSuccessiva='SO2'))
    add(Superamenti(provaPrimaria='PL1', provaSuccessiva='PL2'))
    add(Superamenti(provaPrimaria='ASD1', provaSuccessiva='ASD2'))


def create_iscrizioni():
    studenti = db.session.query(Studenti).filter().all()
    appello1 = db.session.get(Appelli, '1')
    appello11 = db.session.get(Appelli,'11')
    for studente in studenti:
        studente.appelli.append(appello1)
    db.session.commit()


def create_piano_studi():
    studenti = db.session.query(Studenti).filter().all()
    esami = db.session.query(Esami).filter().all()
    for studente in studenti:
        for esame in esami:
            studente.esami.append(esame)
    db.session.commit()

def create_formalizzato():
    #attenzione!!! prima di aggiungere il voto ad una esame bisognerebbe calcolarlo in base alle prove relative a tale esame!!
    #Questa funzione serviva per testare la funzione di formalizzazione
    list_studenti = db.session.query(Studenti).filter().all()
    studente = list_studenti[0]
    set_voto(studente.matricola, 18, '01QWERTY')
    set_voto(studente.matricola, 29, '02QWERTY')
    set_voto(studente.matricola, 26, '03QWERTY')
    studente = list_studenti[1]
    set_voto(studente.matricola, 18, '01QWERTY')
    set_voto(studente.matricola, 29, '02QWERTY')
    set_voto(studente.matricola, 26, '03QWERTY')

    set_voto(892075, 18, '04QWERTY')
    set_voto(892075, 25, '05QWERTY')




def init_db():
    db.create_all()

    print("DB created")


    create_trigger()
    print("Trigger creati")

    list_docenti = creat_exam_and_teacher()
    print("Docenti ed esami creati")
    create_test(list_docenti)
    print("prove create")
    create_superamento()
    print("Superamenti creati")
    creates_students()
    print("Studenti creati")
    create_appelli()
    print("Appelli creati")
    create_iscrizioni()
    print("Iscrizioni create")
    create_piano_studi()
    print("Piano di studi creato")
    create_formalizzato()
    print("Formalizzato creato")


    db.session.commit()

def delete_db():
    db.drop_all()
    db.session.commit()

    print("DB deleted")

with app.app_context():
    delete_db()
    init_db()
    print("DB created")

