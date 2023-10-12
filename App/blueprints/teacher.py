from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from App.checkFunctions import checkDocente
from App.db.models.database import Esami, Prove, db, Appelli
from App.utils.utilies import get_appelli_docente, set_voto_prova

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
    return render_template('teacher/visualizzaProve.html', user=current_user, prove=prove, esame=esame,
                           lista_prove_abilitate=current_user.prove)


@teacher.route('/visualizzaCorsi/visualizzaProve/definisciAppello', methods=['POST', 'GET'])
@login_required
@checkDocente
def definisciAppello():
    #crea un appello per una prova
    prova = request.form['prova']
    return render_template('teacher/definisciAppello.html', user=current_user, prove = current_user.prove)



@teacher.route('/visualizzaCorsi/visualizzaProve/definisciAppello/creaAppello', methods=['POST', 'GET'])
@login_required
@checkDocente
def creaAppello():
    print("sono in creaAppello")
    #crea un appello per una prova
    prova_id = request.form['prova']
    luogo = request.form['luogo']
    data = request.form['data']
    print("prima di creare l'appello")
    print(Appelli.query.all())
    new_appello = Appelli(data=data, luogo=luogo, prova=prova_id)
    db.session.add(new_appello)
    db.session.commit()
    print("dopo aver creato l'appello")
    print(Appelli.query.all())
    return redirect(url_for('teacher.teacherPage'))



#to do da implementare ancora def visualizzaAppelli.
@teacher.route('/visualizzaAppelli')
@login_required
@checkDocente
def visualizzaAppelli():
    print("sono in visualizzaAppelli")
    print(get_appelli_docente(current_user))
    return render_template('teacher/visualizzaAppelli.html', appelli=get_appelli_docente(current_user),
                           user=current_user)


@teacher.route('/visualizzaAppelli/studentiIscritti', methods=['POST'])
@login_required
@checkDocente
def visualizzaStudentiIscritti():
    codAppello = request.form['codAppello']
    studenti = Appelli.query.get(codAppello).studenti
    #gli studenti che hanno gia un voto devono comaparire con il voto settato.
    return render_template('teacher/visualizzaStudentiIscritti.html', studenti=studenti, codAppello=codAppello)


@teacher.route('/visualizzaAppelli/studentiIscritti/setVoto', methods=['POST'])
@login_required
@checkDocente
def setVoto():
    if request.method == 'POST':
        voto = request.form['voto']
        studente_id = request.form['studente_id']
        codAppello = request.form['codAppello']

        set_voto_prova(studente_id, voto, codAppello)

    return redirect(url_for('teacher.visualizzaStudentiIscritti'))


@teacher.route('/visualizzaAppelli/eliminaAppello', methods=['POST'])
@login_required
@checkDocente
def eliminaAppello():
    codAppello = request.form['codAppello']
    appello_to_delete = Appelli.query.get(codAppello)
    db.session.delete(appello_to_delete)
    db.session.commit()
    return redirect(url_for('teacher.visualizzaAppelli'))
