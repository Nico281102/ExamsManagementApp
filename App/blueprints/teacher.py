from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from App.checkFunctions import checkDocente
from App.db.models.database import Esami, Prove, db, Appelli, Docenti
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


@teacher.route('/visualizzaCorsi/visualizzaDocenti/<codEsame>', methods=['GET'])
@login_required
@checkDocente
def visualizzaDocenti(codEsame):
    # Ottieni l'elenco dei docenti relativi all'esame con il codice fornito
    print("sono in visualizzaDocenti")
    print(codEsame)
    docenti = Esami.query.get(codEsame).docenti
    print(docenti)
    # Passa l'elenco dei docenti al template HTML
    return render_template('teacher/visualizzaDocenti.html', docenti=docenti, codEsame=codEsame)


@teacher.route('/visualizzaCorsi/visualizzaDocenti/<codEsame>/ricercaDocente', methods=['GET'])
@login_required
@checkDocente
def ricercaDocente(codEsame):
    # Ottieni l'elenco dei docenti relativi all'esame con il codice fornito
    print("sono in ricercaDocente")
    docenti = Docenti.query.all()
    esame = Esami.query.get(codEsame)
    docenti_relativi_esame = esame.docenti

    return render_template('teacher/ricercaDocente.html', docenti= set(set(docenti) - set(docenti_relativi_esame)), codEsame=codEsame)


@teacher.route('/visualizzaCorsi/visualizzaDocenti/<codEsame>/ricercaDocente/aggiungiDocente/<codDocente>', methods=['POST', 'GET'])
@login_required
@checkDocente
def aggiungiDocente(codEsame, codDocente):
    # Ottieni l'elenco dei docenti relativi all'esame con il codice fornito
    esame = Esami.query.get(codEsame)
    docente = Docenti.query.get(codDocente)
    esame.docenti.append(docente)
    db.session.commit()
    docenti = Esami.query.get(codEsame).docenti

    return redirect(url_for('teacher.visualizzaDocenti', docenti = docenti, codEsame=codEsame))


@teacher.route('/visualizzaCorsi/definisciProve', methods=['POST', 'GET'])
@login_required
@checkDocente
def definisciProve():
    #la somma dei pesi delle prove relative a un corso deve fare 1.
    #se il professore non ha ancora creato prove per un corso, deve poterlo fare
    #se il professore ha già creato prove per un corso, deve poterle modificare
    #se il professore ha già creato prove per un corso, deve poterle eliminare
    #non è possibile per problemi di progettazione creare le prove una alla volta, ma solo tutte insieme
    docente = current_user
    esame_id = request.form['esame']
    esame = Esami.query.get(esame_id)
    prove = esame.prove
    return render_template('teacher/definisciProve.html', user=current_user, prove=prove)


@teacher.route('/visualizzaCorsi/definisciProve/creaProva', methods=['POST', 'GET'])
@login_required
@checkDocente
def creaProve():
    codProva = request.form['prova']
    tipologia = request.form['tipologia']
    peso = request.form['peso']
    dataScadenza = request.form['dataScadenza']
    add_prova = Prove(cod=codProva, tipologia=tipologia, peso=peso, dataScadenza=dataScadenza)
    db.session.add(add_prova)
    db.session.commit()

    #richiede il superamento della prova....

    #controllare le invariatni....

    return redirect(url_for('teacher.visualizzaEsami'))


@teacher.route('/visualizzaCorsi/eliminaProve', methods=['POST', 'GET'])
@login_required
@checkDocente
def eliminaProve():

    return redirect(url_for('teacher.visualizzaEsami'))


@teacher.route('/visualizzaCorsi/visualizzaProve/<codEsame>', methods=['POST', 'GET'])
@login_required
@checkDocente
def visualizzaProve(codEsame):
    #visualizza le prove relative ad un corso
    esame = Esami.query.get(codEsame)
    prove = esame.prove
    print(prove)
    #potrei passare anche un booleano che mi dice se si può creare la prova oppure no
    return render_template('teacher/visualizzaProve.html', user=current_user, prove=prove, esame=esame,
                           lista_prove_abilitate=current_user.prove, codEsame=codEsame)


@teacher.route('/visualizzaCorsi/visualizzaProve/<codEsame>/eliminaProva/<codProva>', methods=['POST', 'GET'])
@login_required
@checkDocente
def eliminaProva(codEsame,codProva):
    docente = current_user
    prova_to_delete = Prove.query.get(codProva)
    owner_prova = prova_to_delete.docente
    if owner_prova == docente:
        db.session.delete(prova_to_delete)
        db.session.commit()
    else:
        print("non puoi eliminare questa prova")
    return redirect(url_for('teacher.visualizzaProve', codEsame=codEsame))


@teacher.route('/visualizzaCorsi/visualizzaProve/definisciAppello/<codProva>', methods=['POST', 'GET'])
@login_required
@checkDocente
def definisciAppello(codProva):
    print("sono in definisciAppello")
    isAbilitata = False   #una prova è abilitata quando la somma dei pesi delle prove abilitate per un corso è 1
    prova = Prove.query.get(codProva)
    esame = prova.esami
    pesoTot = 0
    for prova in esame.prove:
        pesoTot = pesoTot + prova.peso
    if pesoTot == 1:
        isAbilitata = True

    if isAbilitata:
        # crea un appello per una prova
        return render_template('teacher/definisciAppello.html', user=current_user, prove=current_user.prove)
    else:
        return redirect(url_for('teacher.visualizzaProve'))


@teacher.route('/visualizzaCorsi/visualizzaProve/definisciAppello/creaAppello', methods=['POST', 'GET'])
@login_required
@checkDocente
def creaAppello():
    print("sono in creaAppello")
    #crea un appello per una prova
    #impedire la creazione di un appello per una prova il quale appello è definito per una certa distanza di data ?
    #bisognerebbe implementare delle politiche interne.
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


@teacher.route('/visualizzaAppelli/studentiIscritti/<codAppello>', methods=['GET'])
@login_required
@checkDocente
def visualizzaStudentiIscritti(codAppello):
        studenti = Appelli.query.get(codAppello).studenti
        #gli studenti che hanno gia un voto devono comaparire con il voto settato.
        print("sono in visualizzaStudentiIscritti")
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

    return redirect(url_for('teacher.visualizzaStudentiIscritti', codAppello=codAppello))


@teacher.route('/visualizzaAppelli/eliminaAppello', methods=['POST'])
@login_required
@checkDocente
def eliminaAppello():
    codAppello = request.form['codAppello']
    appello_to_delete = Appelli.query.get(codAppello)
    db.session.delete(appello_to_delete)
    db.session.commit()
    return redirect(url_for('teacher.visualizzaAppelli'))


@teacher.route('/visualizzaProveGestite')
@login_required
@checkDocente
def visualizzaProveGestite():
    print("sono in visualizzaProveGestite")
    print(current_user.prove)
    return render_template('teacher/visualizzaProveGestite.html', user=current_user, prove=current_user.prove,
                           esami=current_user.esami)

