from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, validators
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired
from app import db
import enum

class CourseStatus(enum.Enum):
    new = 0
    awaiting_didactic_info = 1
    awaiting_didactic_review = 2
    awaiting_didactic_info_correction = 3
    awaiting_logistic_info = 4
    awaiting_submission = 5
    awaiting_review = 6
    approved = 7
    rejected = 8


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.Enum(CourseStatus))

    nombre = db.Column(db.Unicode(200))
    contenido_sintetico = db.Column(db.Unicode(5000))
    modalidades_aprendizaje =  db.Column(db.Unicode(5000))
    modalidades_evaluacion = db.Column(db.Unicode(5000))
    bibliografia = db.Column(db.Unicode(5000))
    perfil_academico = db.Column(db.Unicode(5000))
    curriculum_sintetico = db.Column(db.Unicode(5000))
    antecedentes = db.Column(db.Unicode(5000))
    duracion = db.Column(db.Integer)

    abierto = db.Column(db.Boolean)
    cupo_min = db.Column(db.Integer)
    cupo_max = db.Column(db.Integer)
    apoyo_econ = db.Column(db.Unicode(5000))
    apoyo_admin = db.Column(db.Unicode(5000))
    apoyo_servicio = db.Column(db.Unicode(5000))

    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)

    instructor_email = db.Column(db.String(50))

    responsable_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsable = db.relationship("User", foreign_keys=[responsable_id],
                                  backref="responsable_courses")

    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    instructor = db.relationship("User", foreign_keys=[instructor_id],
                                 backref='instructor_courses')


class RequiredIf(validators.DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

    """
    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None, negate=False, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message
        self.negate = negate

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if self.negate != bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)


class StartCourseRequestForm(FlaskForm):
    other_instructor = BooleanField('Otro usuario será instructor de este curso')
    instructor_email = StringField('Correo del instructor', validators=[
        RequiredIf('other_instructor','Es necesario especificar el correo del instructor')])

    submit = SubmitField("Crear solicitud")


class DidacticInfoForm(FlaskForm):
    nombre = StringField('Nombre del curso', validators=[
        DataRequired('El campo de contenido sintetico es obligatorio')
    ])
    contenido_sintetico = StringField('Contenido sintetico', validators=[
        DataRequired('El campo de contenido sintetico es obligatorio')
    ])
    modalidades_aprendizaje =  StringField('Modalidades o formas de conducción de los procesos de enseñanza y aprendizajes', validators=[
        DataRequired('El campo Modalidades o formas de conducción de los procesos de enseñanza y aprendizajes es requerido')
    ])
    modalidades_evaluacion = StringField('Las modalidades y requisitos de evaluación y acreditación', validators=[
        DataRequired('Las modalidades y requisitos de evaluación y acreditación')
    ])
    bibliografia = StringField('Bibliografía, documentación y materiales de apoyo', validators=[
        DataRequired('El campo de Bibliografía, documentación y materiales de apoyo es obligatorio')
    ])
    perfil_academico = StringField('Perfil academico del instructor', validators=[
        DataRequired('El campo de Perfil academico del instructor es obligatorio')
    ])
    curriculum_sintetico = FileField('Curriculum sintético de el instructor', validators=[
        FileRequired('El campo de Curriculum sintético de el instructor es obligatorio')
    ])
    antecedentes = StringField('Antecedentes o habilidades necesarios de los alumnos', validators=[
        DataRequired('El campo de Antecedentes o habilidades necesarios de los alumnos es obligatorio')
    ])
    duracion = StringField('Duración en horas del programa', validators=[
        DataRequired('El campo de Duración en horas del programa es obligatorio')
    ])

    submit = SubmitField("Enviar info")


class ReviewDidacticInfoForm(FlaskForm):
    approved = BooleanField('Aprobado')
    rejection_reason = BooleanField()
