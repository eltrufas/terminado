from flask import Blueprint, redirect, render_template
from flask import request, url_for, current_app, abort, flash, send_file
from flask_user import current_user, login_required, roles_accepted
from app.util import send_email
from app import db
from app.models.course_models import (InformeForm,Retroalimentacion,RetroalimentacionForm,StartCourseRequestForm, Course,
                                      CourseStatus, DidacticInfoForm,
                                      LogisticInfoForm, ReviewDidacticInfoForm,
                                      Inscripcion, EvaluarListaAlumnosForm, EvaluarAlumnoForm)
from weasyprint import HTML
import tempfile

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

@curso_blueprint.route('/curso/<int:course_id>/info_informe',methods=["POST","GET"])
def info_informe(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.responsable != current_user:
        return abort(403)

    form = InformeForm()

    if form.validate_on_submit():
        form.populate_obj(course)

        db.session.commit()

        flash('Informacion guardada', 'success')
        return redirect(url_for('.course_details', course_id=course.id))

    return render_template('cursos/formulario_informe.html', form=form, curso=course)


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

@curso_blueprint.route('/curso/<int:course_id>/retroalimentacion', methods=['POST', 'GET'])
def retroalimentacion(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)
    form = RetroalimentacionForm()

    if form.validate_on_submit():
        retro = Retroalimentacion()
        form.populate_obj(retro)
        retro.curso = course

        db.session.add(retro)

        db.session.commit()
        return redirect(url_for('.course_details', course_id=course.id))

    return render_template("cursos/retroalimentacion.html",form=form,curso=course)


@curso_blueprint.route('/curso/<int:course_id>/constancias.zip')
def constancias(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    wp_carta = HTML(string=render_template('documents/carta_solicitud.html', curso=course))

    wp_registro = HTML(string=render_template('documents/registro_curso.html', curso=course))

    fp = tempfile.TemporaryFile()
    with zipfile.ZipFile(fp, mode='w') as zf:
        zf.writestr('carta_solicitud.pdf', wp_carta.write_pdf())
        zf.writestr('registro_curso.pdf', wp_registro.write_pdf())

        _, extension = splitext(course.curriculum_sintetico_filename)

        zf.write('files/{}'.format(course.curriculum_sintetico_filename),
            arcname='curriculum.{}'.format(extension))


    fp.seek(0)
    return send_file(fp, attachment_filename='documentos_{}.zip'.format(course.id))


@curso_blueprint.route('/curso/<int:course_id>/informe.pdf')
@roles_accepted('responsable')
def informe(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    wp = HTML(string=render_template('documents/informe_de_curso.html', curso=course))

    fp = tempfile.TemporaryFile()
    fp.write(wp.write_pdf())
    fp.seek(0)
    return send_file(fp, attachment_filename='informe.pdf'.format(course.id))


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
