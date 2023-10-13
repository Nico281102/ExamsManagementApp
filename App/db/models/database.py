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
    db.Column('isValid', db.Boolean, nullable=False, default=False),
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


    def getVotoProva(self, appello_cod):
        # Query to get the voto directly from the iscrizioni table
        query = select(iscrizioni.c.voto).where((iscrizioni.c.studente == self.matricola) & (iscrizioni.c.appello == appello_cod)
        )
        with db.engine.connect() as connection:
            result = connection.execute(query)

        res = result.fetchall()
        if res:
            return res[0][0]
        else:
            return None



    def getVotoEsame(self, esame_cod):
        for esame in self.esami:
            if esame.cod == esame_cod:
                #query per ottenere il voto dell'esame dalle prove
                return 0
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
        return '<Esame %r>' % self.name


class Prove(db.Model):
    __tablename__ = 'prove'
    cod = db.Column(db.String(32), nullable=False, primary_key=True)
    dataScadenza = db.Column(TIMESTAMP, nullable=False)
    idoneità = db.Column(db.Boolean, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    isValid = db.Column(db.Boolean, nullable=False)
    Tipologia = db.Column(db.Enum('Orale', 'Scritto', 'Progetto', name='Tipologia'), nullable=False)
    Bonus = db.Column(db.Integer, nullable=False)
    esame = db.Column(db.String(32), db.ForeignKey('esami.cod'))
    docente = db.Column(db.Integer, db.ForeignKey('docenti.cod'))
    created_at = db.Column(TIMESTAMP, server_default=func.now())
    updated_at = db.Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    esami = db.relationship('Esami',  back_populates='prove', lazy=True)
    appelli = db.relationship('Appelli', back_populates='prove', lazy=True)
    docenti = db.relationship('Docenti', back_populates='prove', lazy=True)

    superamenti_secondari = db.relationship('Superamento', back_populates='prova_secondaria', lazy=True,
                                            foreign_keys='Superamento.provaSecondaria')

    def __repr__(self):
        return '<Prova %r>' % self.cod


class Superamento(db.Model):
    __tablename__ = 'superamento'
    provaPrincipale = db.Column(db.String(32), db.ForeignKey('prove.cod'))
    provaSecondaria = db.Column(db.String(32), db.ForeignKey('prove.cod'), primary_key=True)
    created_at = db.Column(TIMESTAMP, server_default=func.now())
    updated_at = db.Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    prova_secondaria = db.relationship('Prove', back_populates='superamenti_secondari', foreign_keys=[provaSecondaria],
                                       lazy=True)




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



