from app import db
from app.models.course_models import Course, CourseStatus
from datetime import date


def actualizar_cursos():
    today = date.today()
    for course in Course.query:
        if course.in_process():
            if course.fecha_inicio <= today <= course.fecha_fin:
                course.status = CourseStatus.in_process
                course.inscripciones_abiertas = False
            if course.fecha_fin < today:
                course.status = CourseStatus.finalized

    db.session.commit()
