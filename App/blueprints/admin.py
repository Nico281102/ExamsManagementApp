from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from App.checkFunctions import checkAdmin
from App.db.models.database import db, Studenti, Docenti, Esami

admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

@admin.route('/')
@login_required
@checkAdmin
def adminPage():
    return render_template('admin/home.html', professore = current_user)


@admin.route('/creaStudente')
@login_required
@checkAdmin
def creaStudente():
    return render_template('admin/creaStudente.html')


@admin.route('/creaStudente/inserisciStudente', methods=['POST'])
@login_required
@checkAdmin
def inserisciStudente():
    nome = request.form['name']
    cognome = request.form['surname']
    matricola = request.form['matricola']
    password = request.form['password']
    phone = request.form['phone']

    db.session.add(Studenti(matricola=matricola, name=nome, surname=cognome, password=password, phone=phone))
    db.session.commit()

    return redirect(url_for('admin.adminPage'))

@admin.route('/creaDocente')
@login_required
@checkAdmin
def creaDocente():
    return render_template('admin/creaDocente.html')

@admin.route('creaDocente/inserisciDocente', methods=['POST'])
@login_required
@checkAdmin
def inserisciDocente():
    nome = request.form['name']
    cognome = request.form['surname']
    password = request.form['password']

    db.session.add(Docenti(name=nome, surname=cognome, password=password))
    db.session.commit()

    return redirect(url_for('admin.adminPage'))



@admin.route('/creaEsame')
@login_required
@checkAdmin
def creaEsame():
    docenti = Docenti.query.all()
    return render_template('admin/creaEsame.html', docenti=docenti)


@admin.route('/creaEsame/inserisciEsame', methods=['POST'])
@login_required
@checkAdmin
def inserisciEsame():
    nome = request.form['name']
    codice = request.form['codice']
    cfu = request.form['cfu']
    anno = request.form['anno']
    docente_cod = request.form['docente']

    db.session.add(Esami(name=nome, codice=codice, cfu=cfu, anno=anno))
    db.session.commit()

    #docente_Cod è listea?
    docente = Docenti.query.get(docente_cod)
    docente.esami.append(Esami.query.get(codice))
    db.session.commit()

    return redirect(url_for('admin.adminPage'))


@admin.route('/visualizzaStudenti')
@login_required
@checkAdmin
def visualizzaStudenti():
    studenti = Studenti.query.all()
    return render_template('admin/visualizzaStudenti.html', studenti=studenti)


@admin.route('/visualizzaDocenti')
@login_required
@checkAdmin
def visualizzaDocenti():
    docenti = Docenti.query.all()
    return render_template('admin/visualizzaDocenti.html', docenti=docenti)
