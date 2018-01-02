from flask import Blueprint, redirect, render_template
from flask import request, url_for
from flask_user import current_user, login_required, roles_accepted

from app import db
from app.models.user_models import UserProfileForm

main_blueprint = Blueprint('main', __name__, template_folder='templates')

@main_blueprint.route('/solcitud/crear_solicitud')
def create_course_request():
    return render_template('')
