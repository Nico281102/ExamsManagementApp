from copy import copy

from flask import Blueprint, render_template, request, url_for, redirect, json
from flask_login import login_required, current_user

from App.checkFunctions import checkStudente
from App.db.models.database import Appelli, db, formalizzazioneEsami
from App.utils.utilies import appelli_disponibili, get_esami_nonFormalizzati

student = Blueprint('student', __name__, url_prefix='/student', template_folder='templates')


@student.route('/')
@login_required
@checkStudente
def studentPage():
    print("sono in studentPage")
    return render_template('student/home.html', student=current_user)


@student.route('/appelliDisponibili')
@login_required
@checkStudente
def appelliDisponibili():
    print("sono in prenotaAppello")
    appelli_disp = appelli_disponibili(current_user)
    print(appelli_disp)
    return render_template('student/appelliDisponibili.html', appelli_disponibili=appelli_disp)


@student.route('/prenota', methods=['POST', 'GET'])
@login_required
@checkStudente
def prenotaAppello():
    print("sono in prenotaAppello")
    appello_id = request.form['appello']
    appello = Appelli.query.get(appello_id)
    current_user.appelli.append(appello)
    db.session.commit()

    return redirect(url_for('student.appelliDisponibili'))


@student.route('/eliminaPrenotazione', methods=['POST', 'GET'])
@login_required
@checkStudente
def eliminaPrenotazioneAppello():
    print("sono in prenotaAppello")
    appello_id = request.form['appello']
    appello = Appelli.query.get(appello_id)
    if appello in current_user.appelli:
        current_user.appelli.remove(appello)

    db.session.commit()

    return redirect(url_for('student.prenotazioni'))


@student.route('/prenotazioni')
@login_required
@checkStudente
def prenotazioni():
    print("sono in prenotazioni")
    prenotazioni = current_user.appelli
    print(prenotazioni)
    return render_template('student/prenotazioni.html', prenotazioni=prenotazioni)


@student.route('/pianoDiStudi')
@login_required
@checkStudente
def pianoDiStudi():
    print("sono in EsamiFormalizzati")
    print(current_user.esami)
    #for each element in piano di studi, se formalizzato aggiungi il voto

    return render_template('student/pianoDiStudi.html', esami=current_user.esami)


@student.route('/bachecaEsiti')
@login_required
@checkStudente
def esiti():
    #renderizza la pagina di gestione della formalizzazione
    esami_non_form = get_esami_nonFormalizzati(current_user.matricola)
    print(esami_non_form)
    return render_template('student/esiti.html', esami=esami_non_form)


@student.route('/formalizza', methods=['POST'])
@login_required
@checkStudente
def formalizza():
    #effettua la formalizzazione vera e propria, conclude con un redirect a esiti.
    esame_cod = request.form['esame']
    # Begin a transaction
    with db.engine.begin() as connection:
        # Execute the update statement
        connection.execute(
            formalizzazioneEsami
            .update()
            .where(
                (formalizzazioneEsami.c.studente == current_user.matricola) & (formalizzazioneEsami.c.esame == esame_cod))
            .values({'formalizzato': True})
        )
    return redirect(url_for('student.esiti'))

@student.route('/rifiuta', methods=['POST'])
@login_required
@checkStudente
def rifiuta():
    #effettua la formalizzazione vera e propria, conclude con un redirect a esiti.
    esame_cod = request.form['esame']
    # Begin a transaction
    with db.engine.begin() as connection:
        # Execute the update statement
        connection.execute(
            formalizzazioneEsami
            .update()
            .where(
                (formalizzazioneEsami.c.studente == current_user.matricola) & (formalizzazioneEsami.c.esame == esame_cod))
            .values({'voto': None, 'formalizzato': False})
        )
    return redirect(url_for('student.esiti'))
