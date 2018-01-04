from flask_user import current_user
from app.models.user_models import Role
from flask import url_for

def init_nav(app):
    @app.context_processor
    def inject_nav():
        admin_role = Role.query.filter(Role.name == 'admin').one()
        responsable_role = Role.query.filter(Role.name == 'responsable').one()

        # cosas comunes
        navigation_bar = []

        if current_user.is_authenticated:

            # cosas del consejo
            if admin_role in current_user.roles:
                navigation_bar.extend([
                    ("Lista de solicitudes","lista_solicitudes",url_for('solicitudes.lista_consejo'),"list")
                ])

            # cosas del responsable
            if responsable_role in current_user.roles:
                navigation_bar.extend([
                    ("Solicitar curso", "solicitar_curso", url_for('solicitudes.create_course_request'),"assignment")
                ])

            # si es responsable o tiene algun curso
            if responsable_role in current_user.roles or current_user.instructor_courses:
                navigation_bar.extend([
                    ("Mis solicitudes", "mis_solicitudes", url_for('solicitudes.solicitud_list'),"list"),
                ])

        return dict(navigation_bar=navigation_bar)
