from flask import Blueprint, redirect, render_template
from flask import request, url_for, current_app, abort, flash, send_file
from flask_user import current_user, login_required, roles_accepted
from app.util import send_email
from app import db
from app.models.course_models import (StartCourseRequestForm, Course,
                                      CourseStatus, DidacticInfoForm,
                                      LogisticInfoForm, ReviewDidacticInfoForm,
                                      Inscripcion)


curso_blueprint = Blueprint('curso', __name__, template_folder='templates')

@curso_blueprint.route('/curso/<int:course_id>')
@login_required
def course_details(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    return render_template('cursos/detalles/base.html', curso=course)


@curso_blueprint.route('/curso/<int:course_id>/toggle_inscripcion')
@roles_accepted('responsable')
def toggle_inscripcion(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.responsable != current_user:
        return abort(403)

    course.inscripciones_abiertas = not course.inscripciones_abiertas
    db.session.commit()

    return redirect(url_for('.course_details', course_id=course.id))


@curso_blueprint.route('/curso/<int:course_id>/inscribirse')
@login_required
def inscribirse(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if not Inscripcion.query.filter(Inscripcion.curso == course,
        Inscripcion.asistente == current_user).first():

        inscripcion = Inscripcion(asistente_id=current_user.id, curso_id=course.id)

        db.session.add(inscripcion)

        db.session.commit()

    return redirect(url_for('.course_details', course_id=course.id))


@curso_blueprint.route('/mis_cursos')
@login_required
def mis_cursos():
    cursos_inscritos = [i.curso for i in current_user.inscriptions]
    cursos_responsable = [course for course in current_user.responsable_courses
        if course.solicitud_aprobada()]
    cursos_instructor = [course for course in current_user.instructor_courses
        if course.solicitud_aprobada()]

    return render_template('cursos/mis_cursos.html', cursos_inscritos=cursos_inscritos,
        cursos_responsable=cursos_responsable,
        cursos_instructor=cursos_instructor)


@curso_blueprint.route('/curso/<int:course_id>/inscritos')
def lista_inscritos(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    return render_template('cursos/inscritos.html', curso=course)
