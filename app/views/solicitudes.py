from flask import Blueprint, redirect, render_template
from flask import request, url_for, current_app, abort
from flask_user import current_user, login_required, roles_accepted
from app.util import send_email

from os.path import splitext
import uuid

from app import db
from app.models.user_models import UserProfileForm
from app.models.course_models import (StartCourseRequestForm, Course,
                                      CourseStatus, DidacticInfoForm,
                                      LogisticInfoForm)

main_blueprint = Blueprint('solicitudes', __name__, template_folder='templates')



@main_blueprint.route('/solicitud/iniciar', methods=['GET', 'POST'])
@roles_accepted('responsable')
def create_course_request():
    form = StartCourseRequestForm(request.form)

    if form.validate_on_submit():
        course = Course()
        course.status = CourseStatus.awaiting_didactic_info
        course.responsable = current_user

        print(form.other_instructor.data)
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

            return render_template('solicitudes/iniciar_solicitud_success.html')

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
    return filename


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
            return render_template('solicitudes/didactic_info_success.html')

    return render_template('solicitudes/obtener_info_didactica.html', form=form)


@main_blueprint.route('/solicitud/<int:course_id>/revisar_didactica')
@login_required
def revisar_info_didactica(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.responsable != current_user:
        return abort(403)

    if course.status != CourseStatus.awaiting_didactic_review:
        return redirect('/')

    if form.validate_on_submit():
        if form.approved:
            course.status = CourseStatus.awaiting_logistic_info
            return redirect(url_for('.obtener_info_logistica', curso_id=curso.id))
        else:
            return render_template('solicitudes/didactic_info_success.html', curso=curso)


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
        return redirect(url_for(''))

    return render_template('solicitudes/obtener_info_logistica.html', form=form)


@main_blueprint.route('/solicitud/<int:course_id>/documentos.zip', methods=['GET', 'POST'])
@login_required
def obtener_documentos(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.responsable != current_user:
        return abort(403)

    if course.status != CourseStatus.awaiting_submission:
        return redirect('/')

    wp = HTML(string=render_template(''))
