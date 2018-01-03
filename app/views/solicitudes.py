from flask import Blueprint, redirect, render_template
from flask import request, url_for, current_app, abort
from flask_user import current_user, login_required, roles_accepted
from app.util import send_email


import uuid

from app import db
from app.models.user_models import UserProfileForm
from app.models.course_models import (StartCourseRequestForm, Course,
                                      CourseStatus, DidacticInfoForm)

main_blueprint = Blueprint('solicitudes', __name__, template_folder='templates')

@main_blueprint.route('/solicitud/iniciar', methods=['GET', 'POST'])
@roles_accepted('responsable')
def create_course_request():
    form = StartCourseRequestForm(request.form)

    if request.method == 'POST' and form.validate():
        course = Course()
        course.status = CourseStatus.awaiting_didactic_info
        course.responsable = current_user

        if form.other_instructor.data:

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


@main_blueprint.route('/solicitud/<int:course_id>/didactica', methods=['GET', 'POST'])
@login_required
def obtener_info_didactica(course_id):
    course = Course.query.get(course_id)
    if not course:
        return abort(404)

    if course.instructor != current_user:
        return abort(403)

    if course.status != CourseStatus.awaiting_didactic_info:
        return redirect()

    form = DidacticInfoForm()

    if request.method == 'POST' and form.validate():
        form.populate_obj(course)


    return render_template('solicitudes/obtener_info_didactica.html', form=form)
