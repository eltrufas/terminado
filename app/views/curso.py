from flask import Blueprint, redirect, render_template
from flask import request, url_for, current_app, abort, flash, send_file
from flask_user import current_user, login_required, roles_accepted
from app.util import send_email
from app import db
from app.models.course_models import (StartCourseRequestForm, Course,
                                      CourseStatus, DidacticInfoForm,
                                      LogisticInfoForm, ReviewDidacticInfoForm,
                                      Inscripcion, EvaluarListaAlumnosForm, EvaluarAlumnoForm)

import re


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


@curso_blueprint.route('/curso/<int:course_id>/inscritos', methods=['POST', 'GET'])
def lista_inscritos(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    nombres = []
    ids = []

    form = None
    if course.status == CourseStatus.finalized:
        forms=[]
        for inscripcion in course.inscritos:
            f = EvaluarAlumnoForm(aprobado=False)
            f.user_id.data = inscripcion.asistente.id
            f.user_name.data = inscripcion.asistente.full_name()
            print(inscripcion.acreditado)
            f.aprobado.data = False
            print(f.aprobado.data)
            nombres.append(inscripcion.asistente.full_name())
            ids.append(inscripcion.asistente.id)
            forms.append(f)

        form = EvaluarListaAlumnosForm(alumnos=forms)

        if form.validate_on_submit():
            for i, alumno in enumerate(form.alumnos):
                user_id = ids[i]
                aprobado = alumno.aprobado.data
                ins = Inscripcion.query.filter(Inscripcion.curso_id==course.id, Inscripcion.asistente_id==user_id).one()

                ins.acreditado = aprobado

            course.calificado = True

            db.session.commit()

            flash('Evaluación exitosa')

            return redirect(url_for('.course_details', course_id=course.id))

    return render_template('cursos/inscritos.html', curso=course, form=form, nombres=nombres)
