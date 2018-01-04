from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, validators, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired
from app import db
import enum


class CourseStatus(enum.Enum):
    new = 'Nuevo'
    awaiting_didactic_info = 'Esperando información didactica'
    awaiting_didactic_review = 'Esperando revisión de información didactica'
    awaiting_didactic_info_correction = 'Esperando corrección de información didactica'
    awaiting_logistic_info = 'Esperando información logistica'
    awaiting_submission = 'Esperando entrega de documentos'
    awaiting_review = 'Esperando revisión por Consejo Divisional'
    approved = 'Aprobado'
    rejected = 'Rechazado'



class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.Enum(CourseStatus))
    reason = db.Column(db.Unicode(500))

    nombre = db.Column(db.Unicode(200))
    contenido_sintetico = db.Column(db.Unicode(5000))
    modalidades_aprendizaje =  db.Column(db.Unicode(5000))
    modalidades_evaluacion = db.Column(db.Unicode(5000))
    bibliografia = db.Column(db.Unicode(5000))
    perfil_academico = db.Column(db.Unicode(5000))
    curriculum_sintetico_filename = db.Column(db.Unicode(5000))
    antecedentes = db.Column(db.Unicode(5000))
    duracion = db.Column(db.Integer)

    abierto = db.Column(db.Boolean)
    cupo_min = db.Column(db.Integer)
    cupo_max = db.Column(db.Integer)
    apoyo_econ = db.Column(db.Unicode(5000))
    apoyo_admin = db.Column(db.Unicode(5000))
    apoyo_servicio = db.Column(db.Unicode(5000))

    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)

    instructor_email = db.Column(db.String(50))

    responsable_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responsable = db.relationship("User", foreign_keys=[responsable_id],
                                  backref="responsable_courses")

    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    instructor = db.relationship("User", foreign_keys=[instructor_id],
                                 backref='instructor_courses')

    def has_didactic_info(self):
        return self.nombre is not None

    def has_logistic_info(self):
        return self.apoyo_econ is not None

    def instructor_name_or_email(self):
        return self.instructor.full_name() if self.instructor else instructor_email


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
        RequiredIf('other_instructor','Es necesario especificar el correo del instructor', negate=True)])

    submit = SubmitField("Crear solicitud")


class DidacticInfoForm(FlaskForm):
    nombre = StringField('Nombre del curso', validators=[
        DataRequired('El campo de contenido sintetico es obligatorio')
    ])
    contenido_sintetico = TextAreaField('Contenido sintetico', validators=[
        DataRequired('El campo de contenido sintetico es obligatorio')
    ])
    modalidades_aprendizaje =  TextAreaField('Modalidades o formas de conducción de los procesos de enseñanza y aprendizajes', validators=[
        DataRequired('El campo Modalidades o formas de conducción de los procesos de enseñanza y aprendizajes es requerido')
    ])
    modalidades_evaluacion = TextAreaField('Las modalidades y requisitos de evaluación y acreditación', validators=[
        DataRequired('Las modalidades y requisitos de evaluación y acreditación')
    ])
    perfil_academico = TextAreaField("Perfil academico del instructor", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    bibliografia = TextAreaField('Bibliografía, documentación y materiales de apoyo', validators=[
        DataRequired('El campo de Bibliografía, documentación y materiales de apoyo es obligatorio')
    ])
    curriculum_sintetico = FileField('Curriculum sintético de el instructor', validators=[])
    antecedentes = TextAreaField('Antecedentes o habilidades necesarios de los alumnos', validators=[
        DataRequired('El campo de Antecedentes o habilidades necesarios de los alumnos es obligatorio')
    ])
    duracion = IntegerField('Duración en horas del programa', validators=[
        DataRequired('El campo de Duración en horas del programa es obligatorio')
    ])

    submit = SubmitField("Enviar info")


class ReviewDidacticInfoForm(FlaskForm):
    approved = BooleanField('Aprobado')
    rejection_reason = StringField('Razon de rechazo', validators=[
        RequiredIf('approved', 'El campo de Razon de rechazo es requerido.', negate=True)
    ])

    submit = SubmitField("Enviar revisión")


class LogisticInfoForm(FlaskForm):
    abierto = BooleanField("Abierto para el publico", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    cupo_min = IntegerField("Cupo minimo", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    cupo_max = IntegerField("Cupo maximo", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    apoyo_econ = TextAreaField("Apoyo economico", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    apoyo_admin = TextAreaField("Apoyo administrativo", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    apoyo_servicio = TextAreaField("Apoyos de servicio existentes y solicitado", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    fecha_inicio = DateField("Fecha de inicio", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    fecha_fin = DateField("Fecha de finalización", validators=[
        DataRequired('El campo de Perfil academico del responsable es obligatorio')
    ])
    submit = SubmitField("Enviar info")

class ReviewCourseForm(FlaskForm):
    approved = BooleanField('Aprobado')
    rejection_reason = StringField('Razon de rechazo', validators=[
        RequiredIf('approved', 'El campo de Razon de rechazo es requerido.', negate=True)
    ])

    submit = SubmitField("Enviar revisión")
