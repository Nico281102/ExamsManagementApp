from flask import Blueprint, render_template
from flask_login import current_user, login_required

from App.checkFunctions import checkDocente

teacher = Blueprint('teacher', __name__, url_prefix='/teacher', template_folder='templates')


@teacher.route('/')
@login_required
@checkDocente
def teacherPage():
    return render_template('teacher/home.html', professore=current_user)


@teacher.route('/lista_esami')
@login_required
@checkDocente
def visualizzaEsami():
    return render_template('teacher/appelli.html', user=current_user)


@teacher.route('/crea_esami')
@login_required
@checkDocente
def creaEsami():
    return render_template('teacher/esami.html', user=current_user)




