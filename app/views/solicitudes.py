from flask import Blueprint, redirect, render_template
from flask import request, url_for, current_app, abort, flash, send_file
from flask_user import current_user, login_required, roles_accepted
from app.util import send_email
import tempfile
from flask_user.signals import user_registered

from os.path import splitext
import uuid
from weasyprint import HTML
import zipfile

from app import db
from app.models.user_models import UserProfileForm, Role
from app.models.course_models import (StartCourseRequestForm, Course,
                                      CourseStatus, DidacticInfoForm,
                                      LogisticInfoForm, ReviewDidacticInfoForm)

main_blueprint = Blueprint('solicitudes', __name__, template_folder='templates')

@main_blueprint.route('/solicitud/iniciar', methods=['GET', 'POST'])
@roles_accepted('responsable', 'admin')
def create_course_request():
    form = StartCourseRequestForm(request.form)

    if form.validate_on_submit():
        course = Course()
        course.status = CourseStatus.awaiting_didactic_info
        course.responsable = current_user

        if not form.other_instructor.data:

            email = form.instructor_email.data
            instructor, _ = current_app.user_manager.find_user_by_email(email)
            if instructor:
                course.instructor = instructor
            course.instructor_email = email

            db.session.add(course)
            db.session.commit()

            send_email(email,
                'Solicitud de datos didacticos',
                render_template('email/solicitar_info_didactica.html', course=course),
                'jaja')

            flash('Solicitud enviada exitosamente.', 'success')
            return redirect(url_for('.solicitud_list'))

        else:
            course.instructor = current_user

            db.session.add(course)
            db.session.commit()

            return redirect(url_for('.obtener_info_didactica', course_id=course.id))

    return render_template('solicitudes/iniciar_solicitud.html', form=form)


@main_blueprint.route('/solicitudes')
@login_required
def solicitud_list():
    return render_template('solicitudes/lista.html',
                           instructor_courses = current_user.instructor_courses,
                           responsable_courses = current_user.responsable_courses)


def upload_helper(file):
    id = uuid.uuid4().hex
    _, extension = splitext(file.filename)
    filename = 'files/' + id + extension
    file.save(filename)
    return id + extension


@main_blueprint.route('/solicitud/<int:course_id>/didactica', methods=['GET', 'POST'])
@login_required
def obtener_info_didactica(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.instructor != current_user:
        return abort(403)

    if course.status != CourseStatus.awaiting_didactic_info:
        return redirect('/')

    form = DidacticInfoForm()

    print(form.curriculum_sintetico.data)

    if form.validate_on_submit():
        form.populate_obj(course)
        curriculum_filename = upload_helper(form.curriculum_sintetico.data)
        course.curriculum_sintetico_filename = curriculum_filename

        if course.instructor == course.responsable:
            course.status = CourseStatus.awaiting_logistic_info
            db.session.commit()
            return redirect(url_for('.obtener_info_logistica', course_id=course.id))
        else:
            course.status = CourseStatus.awaiting_didactic_review
            db.session.commit()

            flash('Informacion didactica enviada exitosamente.', 'success')

            send_email(email,
                'Datos diácticos enviados',
                render_template('email/notificacion_didactica_enviada.html', course=course),
                'jaja')

            return redirect(url_for('.solicitud_list'))

    return render_template('solicitudes/obtener_info_didactica.html', form=form, course=course)


@main_blueprint.route('/solicitud/<int:course_id>/revisar_didactica', methods=['GET', 'POST'])
@login_required
def revisar_info_didactica(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.responsable != current_user:
        return abort(403)

    if course.status != CourseStatus.awaiting_didactic_review:
        return redirect('/')

    form = ReviewDidacticInfoForm()

    if form.validate_on_submit():

        flash('Revisión enviada exitosamente', 'success')
        send_email(email,
            'Revisión de datos didácticos',
            render_template('email/revision_info_didactica.html', course=course),
            'jaja')
        if form.approved:
            course.status = CourseStatus.awaiting_logistic_info
            db.session.commit()
            return redirect(url_for('.obtener_info_logistica', course_id=course.id))
        else:
            course.status = CourseStatus.awaiting_didactic_info_correction
            course.reason = form.rejection_reason
            db.session.commit()
            return redirect(url_for('.solicitud_list'))

    return render_template('solicitudes/revisar_info_didactica.html', form=form)


@main_blueprint.route('/solicitud/<int:course_id>/didactica', methods=['GET', 'POST'])
@login_required
def corregir_info_didactica(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.instructor != current_user:
        return abort(403)

    if course.status != CourseStatus.awaiting_didactic_info_correction:
        return redirect('/')

    form = DidacticInfoForm(requert.form, course)

    print(form.curriculum_sintetico.data)

    if form.validate_on_submit():
        form.populate_obj(course)
        curriculum_filename = upload_helper(form.curriculum_sintetico.data)
        course.curriculum_sintetico_filename = curriculum_filename

        course.status = CourseStatus.awaiting_didactic_review
        db.session.commit()

        flash('Informacion didactica enviada exitosamente.', 'success')

        send_email(email,
            'Datos didacticos actualizados',
            render_template('email/notificacion_didactica_enviada.html', course=course),
            'jaja')

        return redirect(url_for('.solicitud_details', course_id=course.id))

    return render_template('solicitudes/obtener_info_didactica.html', form=form, course=course)


@main_blueprint.route('/solicitud/<int:course_id>/logistica', methods=['GET', 'POST'])
@login_required
def obtener_info_logistica(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.responsable != current_user:
        return abort(403)

    if course.status != CourseStatus.awaiting_logistic_info:
        return redirect('/')

    form = LogisticInfoForm()

    if form.validate_on_submit():
        form.populate_obj(course)

        course.status = CourseStatus.awaiting_submission
        db.session.commit()
        return redirect(url_for('.solicitud_details', course_id=course.id))

    return render_template('solicitudes/obtener_info_logistica.html', form=form)


@main_blueprint.route('/solicitud/<int:course_id>/documentos.zip')
@login_required
def obtener_documentos(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.responsable != current_user:
        return abort(403)

    if course.status != CourseStatus.awaiting_submission:
        return redirect('/')

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


@main_blueprint.route('/solicitudes_consejo')
@roles_accepted('admin')
def lista_consejo():
    pending_courses = Course.query.filter(Course.status.in_([
        CourseStatus.awaiting_submission,
        CourseStatus.awaiting_review])).all()

    return render_template('solicitudes/lista_consejo.html', solicitudes=pending_courses)


@main_blueprint.route('/solicitud/<int:course_id>/receive_docs')
@roles_accepted('admin')
def receive_docs(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.status != CourseStatus.awaiting_submission:
        return redirect('/')

    course.status = CourseStatus.awaiting_review

    send_email(email,
        'Documentos de solicitud recibidos',
        render_template('email/solicitud_documentos_recibidos.html', course=course),
        'jaja')

    flash("Documentos marcados como recibidos", "success")

    db.session.commit()

    return redirect(url_for('.solicitud_details', course_id=course.id))


@main_blueprint.route('/solicitud/<int:course_id>/revisar', methods=['POST'])
@roles_accepted('admin')
def revisar_solicitud(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.status != CourseStatus.awaiting_review:
        return redirect('/')

    form = ReviewDidacticInfoForm()

    if form.validate_on_submit():

        flash('Revisión enviada exitosamente', 'success')

        send_email(email,
            'Solicitud de curso revisada',
            render_template('email/solicitud_curso_revisado.html', course=course),
            'jaja')

        if form.approved:
            course.status = CourseStatus.approved
        else:
            course.status = CourseStatus.rejected
            course.reason = form.rejection_reason
        db.session.commit()

    return redirect(url_for('.solicitud_details', course_id=course.id))


@main_blueprint.route('/solicitud/<int:course_id>')
def solicitud_details(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    admin_role = Role.query.filter(Role.name == 'admin').one()

    if course.status == CourseStatus.awaiting_didactic_info and current_user == course.instructor:
        return render_template('solicitudes/detalles/didactic.html', curso=course)
    elif course.status == CourseStatus.awaiting_didactic_review and current_user == course.responsable:
        form = ReviewDidacticInfoForm()
        return render_template('solicitudes/detalles/review_didactic.html', curso=course, form=form)
    elif course.status == CourseStatus.awaiting_didactic_info_correction and current_user == course.instructor:
        return render_template('solicitudes/detalles/didactic_correction.html')
    elif course.status == CourseStatus.awaiting_logistic_info and current_user == course.responsable:
        return render_template('solicitudes/detalles/logistic.html', curso=course)
    elif course.status == CourseStatus.awaiting_submission:
        if current_user == course.responsable:
            return render_template('solicitudes/detalles/documents.html', curso=course)
        if admin_role in current_user.roles:
            return render_template('solicitudes/detalles/receive_docs.html', curso=course)
    elif course.status == CourseStatus.awaiting_review and admin_role in current_user.roles:
        form = ReviewDidacticInfoForm()

        return render_template('solicitudes/detalles/review.html', curso=course, form=form)

    if course.solicitud_aprobada():
        return redirect(url_for('curso.course_details', course_id=course.id))

    return render_template('solicitudes/detalles/detalles_publicos.html', curso=course)
