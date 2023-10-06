from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from App.checkFunctions import checkDocente
from App.db.models.database import Esami

teacher = Blueprint('teacher', __name__, url_prefix='/teacher', template_folder='templates')


@teacher.route('/')
@login_required
@checkDocente
def teacherPage():
    print("sono in teacherPage")
    return render_template('teacher/home.html', professore=current_user)


@teacher.route('/visualizzaCorsi')
@login_required
@checkDocente
def visualizzaCorsi():
    #visualizza l'elenco dei corsi tenuti dal professore e le relative prove
    print("sono in visualizzaEsami")
    print(current_user.esami)
    return render_template('teacher/corsi.html', user=current_user, esami=current_user.esami)


@teacher.route('/visualizzaCorsi/creaProve', methods=['POST', 'GET'])
@login_required
@checkDocente
def creaProve():
    #la somma dei pesi delle prove relative a un corso deve fare 1.
    #se il professore non ha ancora creato prove per un corso, deve poterlo fare
    #se il professore ha già creato prove per un corso, deve poterle modificare
    #se il professore ha già creato prove per un corso, deve poterle eliminare
    #non è possibile per problemi di progettazione creare le prove una alla volta, ma solo tutte insieme
    docente = current_user
    esame_id = request.form['esame']

    return render_template('teacher/creaProve.html', user=current_user)

@teacher.route('/visualizzaCorsi/eliminaProve', methods=['POST', 'GET'])
@login_required
@checkDocente
def eliminaProve():


    return redirect(url_for('teacher.visualizzaEsami'))



@teacher.route('/visualizzaCorsi/visualizzaProve', methods=['POST', 'GET'])
@login_required
@checkDocente
def visualizzaProve():

    esame_id = request.form['esame']
    esame = Esami.query.get(esame_id)
    prove = esame.prove
    print(prove)
    return render_template('teacher/visualizzaProve.html', user=current_user, prove=prove, esame=esame)


@teacher.route('/visualizzaCorsi/visualizzaProve/creaAppello', methods=['POST', 'GET'])
@login_required
@checkDocente
def creaAppello():


    return render_template('teacher/creaProve.html', user=current_user)
