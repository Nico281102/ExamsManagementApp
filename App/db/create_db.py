from flask_sqlalchemy.session import Session
from sqlalchemy import text

from App.utils.utilies import set_voto, set_voto_2
from main import app
from App.db.models.database import Studenti, Docenti, Esami, db, Prove, Appelli, iscrizioni, Superamento, \
    formalizzazioneEsami

query = Session(db)

def add(obj):
    db.session.add(obj)
    db.session.commit()


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



def create_exam_and_test(dict_docenti):
    ferrara_cod = dict_docenti['pietro.ferrara@unive.it']
    calzavara_cod = dict_docenti['stefano.calzavara@unive.it']
    focardi_cod = dict_docenti['riccardo.focardi@unive.it']
    marin_cod = dict_docenti['andrea.marin@unive.it']
    raffaeta_cod = dict_docenti['alessandra.raffaeta@unive.it']
    spano_cod = dict_docenti['alvise.spano@unive.it']
    balsamo_cod = dict_docenti['simonetta.balsamo@unive.it']
    pelillo_cod = dict_docenti['marcello.pelillo@unive.it']
    lucchese_cod = dict_docenti['claudio.lucchese@unive.it']

    add(Esami(name='Programmazione ad Oggetti', cod='01QWERTY', cfu=6, anno=1, docente=ferrara_cod))  # creo un esame
    add(Esami(name='Basi di dati', cod='02QWERTY', cfu=6, anno=2, docente=calzavara_cod)) # creo un esame
    add(Esami(name='Sistemi operativi', cod='03QWERTY', cfu=12, anno=2, docente=focardi_cod)) # creo un esame
    add(Esami(name='Programmazione e Laboratorio', cod='04QWERTY', cfu=12, anno=1, docente=marin_cod)) # creo un esame
    add(Esami(name='Algoritmi e Strutture Dati', cod='05QWERTY', cfu=12, anno=2, docente=raffaeta_cod)) # creo un esame
    add(Esami(name='Reti di Calcolatori', cod='06QWERTY', cfu=12, anno=2, docente=balsamo_cod)) # creo un esame
    add(Esami(name='Introduzione alla programmazione', cod='07QWERTY', cfu=6, anno=1, docente=lucchese_cod))

    add(Prove(esame='01QWERTY', docente=ferrara_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='PO1',
              idoneità=False, Tipologia='Scritto', Bonus=0))
    add(Prove(esame='01QWERTY', docente=spano_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='PO2',
              idoneità=False, Tipologia='Scritto', Bonus=0))

    add(Prove(esame='02QWERTY', docente=raffaeta_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='BD1',
              idoneità=False, Tipologia='Scritto', Bonus=0))
    add(Prove(esame='02QWERTY', docente=calzavara_cod, dataScadenza='2024-01-01', peso=0.3, isValid=True, cod='BD2',
              idoneità=False, Tipologia='Scritto', Bonus=0))
    add(Prove(esame='02QWERTY', docente=calzavara_cod, dataScadenza='2024-01-01', peso=0.2, isValid=True,
              cod='BDProject', idoneità=False, Tipologia='Progetto', Bonus=0))

    add(Prove(esame='03QWERTY', docente=balsamo_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='SO1',
                idoneità=False, Tipologia='Scritto', Bonus=0))
    add(Prove(esame='03QWERTY', docente=focardi_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='SO2',
                idoneità=False, Tipologia='Scritto', Bonus=0))

    add(Prove(esame='04QWERTY', docente=marin_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='PL1',
                idoneità=False, Tipologia='Scritto', Bonus=0))
    add(Prove(esame='04QWERTY', docente=marin_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='PL2',
                idoneità=False, Tipologia='Orale', Bonus=0))

    add(Prove(esame='05QWERTY', docente=raffaeta_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='ASD1',
                idoneità=False, Tipologia='Scritto', Bonus=0))
    add(Prove(esame='05QWERTY', docente=pelillo_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='ASD2',
                idoneità=False, Tipologia='Scritto', Bonus=0))

    add(Prove(esame='06QWERTY', docente=balsamo_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='RC1',
                idoneità=False, Tipologia='Scritto', Bonus=0))

    add(Prove(esame='07QWERTY', docente=lucchese_cod, dataScadenza='2024-01-01', peso=0.5, isValid=True, cod='IAP',
                idoneità=False, Tipologia='Scritto', Bonus=0))


def create_appelli():

    add(Appelli(data='2024-01-01', luogo='Aula1', codAppello='1', prova='PO1'))
    add(Appelli(data='2024-01-01', luogo='Aula2', codAppello='2', prova='PO2'))

    add(Appelli(data='2024-01-05', luogo='Aula1', codAppello='3', prova='BD1'))
    add(Appelli(data='2024-01-05', luogo='Aula2', codAppello='4', prova='BD2'))

    add(Appelli(data='2024-01-10', luogo='Aula1', codAppello='5', prova='SO1'))
    add(Appelli(data='2024-01-10', luogo='Aula2', codAppello='6', prova='SO2'))

    add(Appelli(data='2024-01-15', luogo='Aula1', codAppello='7', prova='PL1'))
    add(Appelli(data='2024-01-15', luogo='Aula2', codAppello='8', prova='PL2'))

    add(Appelli(data='2024-01-20', luogo='Aula1', codAppello='9', prova='ASD1'))
    add(Appelli(data='2024-01-20', luogo='Aula2', codAppello='10', prova='ASD2'))

    add(Appelli(data='2024-01-25', luogo='Aula1', codAppello='11', prova='RC1'))

    add(Appelli(data='2024-01-19', luogo='Aula1', codAppello='12', prova='IAP'))



def create_superamento():
    add(Superamento(provaPrincipale='PO1', provaSecondaria='PO2'))
    add(Superamento(provaPrincipale='BD1', provaSecondaria='BD2'))
    add(Superamento(provaPrincipale='SO1', provaSecondaria='SO2'))
    add(Superamento(provaPrincipale='PL1', provaSecondaria='PL2'))
    add(Superamento(provaPrincipale='ASD1', provaSecondaria='ASD2'))


def create_iscrizioni():
    studenti = db.session.query(Studenti).filter().all()
    appello = db.session.get(Appelli, '1')
    for studente in studenti:
        studente.appelli.append(appello)
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

def create_formalizzato_2():
    list_studenti = db.session.query(Studenti).filter().all()
    studente = list_studenti[0]
    set_voto_2(studente.matricola, 18, '01QWERTY')
    set_voto_2(studente.matricola, 29, '02QWERTY')
    set_voto_2(studente.matricola, 26, '03QWERTY')
    studente = list_studenti[1]
    set_voto_2(studente.matricola, 18, '01QWERTY')
    set_voto_2(studente.matricola, 29, '02QWERTY')
    set_voto_2(studente.matricola, 26, '03QWERTY')

    set_voto_2(892075, 18, '04QWERTY')
    set_voto_2(892075, 25, '05QWERTY')



def init_db():
    db.create_all()
    print("DB created")

    list_docenti = create_teacher()
    print("Docenti creati")
    create_exam_and_test(list_docenti)
    print("Esami  e prove creati")
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


def delete_db():
    db.drop_all()
    db.session.commit()


    print("DB deleted")

with app.app_context():
    delete_db()
    init_db()
    print("DB created")

