from flask import Blueprint, redirect, render_template
from flask import request, url_for, current_app, abort, flash, send_file
from flask_user import current_user, login_required, roles_accepted
from app.util import send_email

from app.models.course_models import (StartCourseRequestForm, Course,
                                      CourseStatus, DidacticInfoForm,
                                      LogisticInfoForm, ReviewDidacticInfoForm)


curso_blueprint = Blueprint('curso', __name__, template_folder='templates')

@curso_blueprint.route('/curso/<int:curso_id>')
@login_required
def course_details(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    return render_template('cursos/details/base.html', curso=course)


@curso_blueprint.route('/mis_cursos')
@login_required
def mis_cursos():
    cursos_inscritos = []
    cursos_responsable = []
    cursos_instructor = []

    return render_template('cursos/mis_cursos.html', cursos_inscritos=cursos_inscritos,
        cursos_responsable=cursos_responsable,
        cursos_instructor=cursos_instructor)


@curso_blueprint.route('/curso/<int:curso_id>/inscritos')
def lista_inscritos(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    return render_template('cursos/inscritos.html', curso=course)
