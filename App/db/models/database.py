from datetime import timedelta, datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Sequence
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy import select, and_

db = SQLAlchemy()

# nomeVariabile = db.relationship('NomeClasse', back_populates='nomeVariabile', lazy=True)

# M:M

iscrizioni = db.Table(
    'iscrizioni',
    db.metadata,
    db.Column('voto', db.Integer, nullable=True),
    db.Column('studente', db.Integer, db.ForeignKey('studenti.matricola'), primary_key=True),
    db.Column('appello', db.String(32), db.ForeignKey('appelli.codAppello'), primary_key=True),
    db.Column('isValid', db.Boolean, nullable=False, default=True),
    db.Column('DataScadenza', TIMESTAMP, nullable = False, default = func.now() + timedelta(12*365/12)), #dura 12 mesi default
    db.Column('created_at', TIMESTAMP, server_default=func.now()),
    db.Column('updated_at', TIMESTAMP, server_default=func.now(), onupdate=func.now())
)

formalizzazioneEsami = db.Table(
    'formalizzazioneEsami',
    db.metadata,
    db.Column('voto', db.Integer, nullable=True),
    db.Column('passato', db.Boolean, nullable=False, default=False),
    db.Column('studente', db.Integer, db.ForeignKey('studenti.matricola'), primary_key=True),
    db.Column('esame', db.String(32), db.ForeignKey('esami.cod'), primary_key=True),
    db.Column('formalizzato', db.Boolean , default=False),
    db.Column('created_at', TIMESTAMP, server_default=func.now()),
    db.Column('updated_at', TIMESTAMP, server_default=func.now(), onupdate=func.now())
)

gestiscono = db.Table(
    'gestiscono',
    db.metadata,
    db.Column('docente', db.Integer, db.ForeignKey('docenti.cod'), primary_key=True),
    db.Column('esame', db.String(32), db.ForeignKey('esami.cod'), primary_key=True),
    db.Column('created_at', TIMESTAMP, server_default=func.now()),
    db.Column('updated_at', TIMESTAMP, server_default=func.now(), onupdate=func.now())
)

# Ora `iscrizioni` può essere utilizzata per interagire direttamente con la tabella nel database.

class Studenti(db.Model, UserMixin):
    __tablename__ = 'studenti'
    name = db.Column(db.String(32), nullable=False)
    surname = db.Column(db.String(32), nullable=False)
    matricola = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    created_at = db.Column(TIMESTAMP, server_default=func.now())
    updated_at = db.Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 1:M
    appelli = db.relationship('Appelli', secondary=iscrizioni, back_populates='studenti', lazy=True)
    esami = db.relationship('Esami', secondary=formalizzazioneEsami, back_populates='studenti', lazy=True)

    def __init__(self, name, surname, matricola, password, phone):
        self.name = name
        self.surname = surname
        self.password = password
        self.matricola = matricola
        self.phone = phone
        self.email = self.generate_email()

    def get_id(self): # necessario per il login
        return self.matricola

    def generate_email(self):
        return f"{self.matricola}@stud.unive.it"

    def formalizzaEsame(self, codEsame):
        with db.engine.begin() as connection:
            # Execute the update statement
            connection.execute(
                formalizzazioneEsami
                .update()
                .where(
                    (formalizzazioneEsami.c.studente == self.matricola) & (
                                formalizzazioneEsami.c.esame == codEsame))
                .values({'formalizzato': True})
            )

    def rifiutaEsame(self, codEsame):
        with db.engine.begin() as connection:
            # Execute the update statement
            connection.execute(
                formalizzazioneEsami
                .update()
                .where(
                    (formalizzazioneEsami.c.studente == self.matricola) & (
                                formalizzazioneEsami.c.esame == codEsame))
                .values({'voto': None, 'formalizzato': False})
            )

    def getAppelliDisponibili(self):
        #Query to get the appelli disponibili
        #Invarianti:
        #   - Gli appelli disponibili sono quelli che non sono scaduti e che non sono già stati prenotati

        appelli = Appelli.query.all()
        appelli_disponibili = []


            # Get the list of tests the student has not passed
        esami_non_passati = self.getEsamiNonFormalizzati() # Perchè potenzialmente posso scegliere di rifare prove relative ad esami passati
        prove_studente = [prova for esame in esami_non_passati for prova in esame.prove]

        for appello in appelli:
            if appello.prove in prove_studente and appello not in self.appelli:
                appelli_disponibili.append(appello)

        current_time = datetime.now()
        appelli_disponibili_filtered = [appello for appello in appelli_disponibili if appello.data > current_time]

        return appelli_disponibili_filtered

    def getEsamiNonPassati(self):
        query = (
            select(
                formalizzazioneEsami.c.esame
            )
            .where((formalizzazioneEsami.c.studente == self.matricola) & (
                        formalizzazioneEsami.c.passato == False) )
        )

        with db.engine.connect() as connection:
            result = connection.execute(query)

        res = result.fetchall()

        esami = []
        for i in range(len(res)):
            esami.append(Esami.query.get(res[i][0]))

        return esami
    def getEsamiNonFormalizzati(self):
        #Query to get the esami non formalizzati
        #Invarianti:
        #   - Gli esami non formalizzati stati ancora formalizzati
        # Build the SQL query
        query = (
            select(
                formalizzazioneEsami.c.esame
            )
            .where((formalizzazioneEsami.c.studente == self.matricola) & (
                        formalizzazioneEsami.c.formalizzato == False)
                     )
        )

        # Execute the query
        with db.engine.connect() as connection:
            result = connection.execute(query)

        res = result.fetchall()

        esami = []
        for i in range(len(res)):
            esami.append(Esami.query.get(res[i][0]))

        return esami
    def getEsamiNonFormalizzatiandPassati(self):
        #Query to get the esami non formalizzati
        #Invarianti:
        #   - Gli esami non formalizzati sono quelli che sono stati passati e che non sono stati ancora formalizzati
        # Build the SQL query
        query = (
            select(
                formalizzazioneEsami.c.esame
            )
            .where((formalizzazioneEsami.c.studente == self.matricola) & (
                        formalizzazioneEsami.c.formalizzato == False) &
                   (formalizzazioneEsami.c.passato == True) &
                        (formalizzazioneEsami.c.voto != None))
        )

        # Execute the query
        with db.engine.connect() as connection:
            result = connection.execute(query)

        res = result.fetchall()

        esami = []
        for i in range(len(res)):
            esami.append(Esami.query.get(res[i][0]))

        print(res)
        print(esami)
        return esami

    def getEsamiFormalizzati(self):
#Query to get the esami formalizzati
        #Invarianti:
        #   - Gli esami formalizzati sono quelli che sono stati passati e che sono stati formalizzati
        # Build the SQL query
        query = (
            select(
                formalizzazioneEsami.c.esame
            )
            .where((formalizzazioneEsami.c.studente == self.matricola) & (
                        formalizzazioneEsami.c.formalizzato == True) &
                        (formalizzazioneEsami.c.voto != None))
        )

        # Execute the query
        with db.engine.connect() as connection:
            result = connection.execute(query)

        res = result.fetchall()

        esami = []
        for i in range(len(res)):
            esami.append(Esami.query.get(res[i][0]))

        return esami

    def getMean(self):
        #Query to get the mean of the voti
        #Invarianti:
        #   - La media è calcolata in base ai voti formalizzati
        # Build the SQL query
        query = (
            select(
                formalizzazioneEsami.c.voto
            )
            .where((formalizzazioneEsami.c.studente == self.matricola) & (
                        formalizzazioneEsami.c.formalizzato == True) &
                        (formalizzazioneEsami.c.voto != None))
        )
        with db.engine.connect() as connection:
            result = connection.execute(query)
        res = result.fetchall()

        for i in range(len(res)): #make the list of tuple a list of int
            res[i] = res[i][0]

        if res:
            return sum(res) / len(res)
        else:
            return None

    def getVotoEsame(self, codEsame):
        #Query to get the voto of the esame
        #Invarianti:
        #   - Il voto è calcolato in base ai voti formalizzati
        #   - l'esame può non essere formalizzato
        # Build the SQL query
        query = (
            select(
                formalizzazioneEsami.c.voto
            )
            .where((formalizzazioneEsami.c.studente == self.matricola) &
                        (formalizzazioneEsami.c.voto != None) &
                        (formalizzazioneEsami.c.esame == codEsame))
        )
        with db.engine.connect() as connection:
            result = connection.execute(query)
        res = result.fetchall()
        if res:
            print(res[0][0])
            return res[0][0]
        else:
            return None

    def getVotoProva(self, appello_cod):
        # Query to get the voto directly from the iscrizioni table
        # Invarianti:
        # - Prendo il voto dell'appello valido, assumendo che gli appelli passati siano stati invalidati durante la nuova iscrizione
        query = select(
            iscrizioni.c.voto).where(
            (iscrizioni.c.studente == self.matricola) &
            (iscrizioni.c.appello == appello_cod) &
            (iscrizioni.c.isValid == True)
        )
        with db.engine.connect() as connection:
            result = connection.execute(query)

        res = result.fetchall()
        if res:
            return res[0][0]
        else:
            return None

    def getAppelliNonValidi(self):
        # Query to get the appelli non validi
        # Invarianti:
        # - Prendo gli appelli non validi, assumendo che gli appelli passati siano stati invalidati durante la nuova iscrizione
        query = select(
            iscrizioni.c.appello).where(
            (iscrizioni.c.studente == self.matricola) &
            (iscrizioni.c.isValid == False)
        )
        with db.engine.connect() as connection:
            result = connection.execute(query)

        res = result.fetchall()
        out = []
        if res:
            for i in range(len(res)):
                res[i] = res[i][0]
            for codAppello in res:
                appello = Appelli.query.get(codAppello)
                out.append(appello)
            return out
        else:
            return []

    def computePassed(self):
        #da finire
        #Query to set passato
        #Considero ogni esame nel piano di studi dello studente
        #per ogni esame mi prendo l'insieme delle prove che lo compone che non sono Bonus
        #per ogni prova controllo se esiste un iscrizione VALIDA e con voto, relativa allo studente
        #settare il voto qui(?)
        passato = True
        insieme_iscrizioni_valide = []
        esami = self.esami
        for esame in esami:
            for prova in esame.prove and prova.bonus == 0:
                passato = prova in insieme_iscrizioni_valide and passato
            #metto passato all'esame nel caso passato sia true.
        return None


    def __repr__(self):
        return '<Studente %r>' % self.name


class Docenti(db.Model, UserMixin):
    __tablename__ = 'docenti'
    cod = db.Column(db.Integer, primary_key=True ,autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    surname = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(TIMESTAMP, server_default=func.now())
    updated_at = db.Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    prove = db.relationship('Prove', back_populates='docenti', lazy=True)
    esami = db.relationship('Esami', secondary=gestiscono, back_populates='docenti', lazy=True)

    def __init__(self, name, surname, password):
        self.name = name
        self.surname = surname
        self.password = password
        self.email = self.generate_email()

    def get_id(self): # necessario per il login
        return self.cod

    def generate_email(self):
        return f"{self.name.lower()}.{self.surname.lower()}@unive.it"

    def __repr__(self):
        return '<Docente %r>' % self.name


class Esami(db.Model):
    __tablename__ = 'esami'
    name = db.Column(db.String(32), nullable=False)
    cod = db.Column(db.String(32), nullable=False, primary_key=True)
    cfu = db.Column(db.Integer, nullable=False)
    anno = db.Column(db.Integer, nullable=False)
    created_at = db.Column(TIMESTAMP, server_default=func.now())
    updated_at = db.Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    studenti = db.relationship('Studenti', secondary=formalizzazioneEsami, back_populates='esami', lazy=True)
    docenti = db.relationship('Docenti', secondary=gestiscono, back_populates='esami', lazy=True)
    prove = db.relationship('Prove', back_populates='esami', lazy=True)

    def __repr__(self):
        return '[Esame: %r]' % self.name

    def getVoto(self, matricola):

        studente = Studenti.query.get(matricola)
        return studente.getVotoEsame(self.cod)



class Prove(db.Model):
    __tablename__ = 'prove'
    cod = db.Column(db.String(32), nullable=False, primary_key=True)
    idoneità = db.Column(db.Boolean, nullable=False, default=False)
    peso = db.Column(db.Float, nullable=False)
    Tipologia = db.Column(db.Enum('Orale', 'Scritto', 'Progetto', name='Tipologia'), nullable=False)
    Bonus = db.Column(db.Integer, nullable=False, default=0)
    esame = db.Column(db.String(32), db.ForeignKey('esami.cod'))
    docente = db.Column(db.Integer, db.ForeignKey('docenti.cod'))
    created_at = db.Column(TIMESTAMP, server_default=func.now())
    updated_at = db.Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    esami = db.relationship('Esami',  back_populates='prove', lazy=True)
    appelli = db.relationship('Appelli', back_populates='prove', lazy=True)
    docenti = db.relationship('Docenti', back_populates='prove', lazy=True)


   # __table_args__ = (
    #    db.CheckConstraint('(prove.Bonus = 0 OR peso = 0)', name='check_bonus_peso'),
    #)


    def __repr__(self):
        return '[Prova: %r]' % self.cod


    def getProveSuccessive(self, codProva):
        query = db.session.query(Superamento.provaSuccessiva).filter(Superamento.provaPrimaria == codProva)
        return query.all()


    def getProvePrecedenti(self, codProva):
        #Nota: Questa funzione tornerà sempre e solo una prova, per via della 1:M
        query = db.session.query(Superamento.provaPrimaria).filter(Superamento.provaSuccessiva == codProva)
        results = query.all()
        res = [result[0] for result in results]
        return res


class Superamento(db.Model):
    __tablename__ = 'superamento'
    provaSuccessiva = db.Column(db.String(32), db.ForeignKey('prove.cod'), primary_key=True)
    provaPrimaria = db.Column(db.String(32), db.ForeignKey('prove.cod'))
    created_at = db.Column(TIMESTAMP, server_default=func.now())
    updated_at = db.Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())





class Appelli(db.Model):
    __tablename__ = 'appelli'
    data = db.Column(TIMESTAMP, nullable=False)
    luogo = db.Column(db.String(32), nullable=False)
    codAppello = db.Column(db.String(32), Sequence('appelli_cod_seq'), nullable=False, primary_key=True)
    prova = db.Column(db.String(32), db.ForeignKey('prove.cod'))
    created_at = db.Column(TIMESTAMP, server_default=func.now())
    updated_at = db.Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    studenti = db.relationship('Studenti', secondary=iscrizioni, back_populates='appelli', lazy=True)
    prove = db.relationship('Prove', back_populates='appelli', lazy=True)

    def __repr__(self):
        return '<Appello %r>' % self.codAppello + '<Prova %r>' % self.prova



