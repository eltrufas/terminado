from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, validators, IntegerField, DateField, TextAreaField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired
from app import db
import enum

class RetroOptions(enum.Enum):
    malo = 'Malo'
    regular = 'Regular'
    bueno = "Bueno"
    excelente = "Excelente"


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
    in_process = 'En proceso'
    finalized = 'Finalizado'



class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.Enum(CourseStatus))
    reason = db.Column(db.Unicode(500))

    nombre = db.Column(db.Unicode(200))
    objetivo_general = db.Column(db.Unicode(200))
    objetivos_especificos = db.Column(db.Unicode(200))
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

    calificado = db.Column(db.Boolean, default=False)

    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)

    inscripciones_abiertas = db.Column(db.Boolean, nullable=False, default=False)

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
        return self.instructor.full_name() if self.instructor else self.instructor_email

    def solicitud_aprobada(self):
        return self.status not in [CourseStatus.new, CourseStatus.awaiting_didactic_info,
            CourseStatus.awaiting_didactic_review, CourseStatus.awaiting_didactic_info_correction,
            CourseStatus.awaiting_logistic_info, CourseStatus.awaiting_submission, CourseStatus.rejected]

    def allow_inscription_toggle(self):
        return self.status == CourseStatus.approved

    def esta_inscrito(self, user):
        return any(i.asistente == user for i in self.inscritos)

    def is_in_process(self):
        return self.status in [CourseStatus.approved, CourseStatus.in_process, CourseStatus.finalized]

class Retroalimentacion(db.Model):
    expectativas = db.Column(db.Unicode(20))
    pertinencia = db.Column(db.Unicode(20))
    topicos= db.Column(db.Unicode(20))
    tiempos= db.Column(db.Unicode(20))
    logro_objetivos= db.Column(db.Unicode(20))
    materiales_apoyo= db.Column(db.Unicode(20))
    aplicacion= db.Column(db.Unicode(20))
    medios_tecnologicos= db.Column(db.Unicode(20))
    cantidad_info= db.Column(db.Unicode(20))
    general_curso= db.Column(db.Unicode(20))

    sugerencias_curso = db.Column(db.Unicode(5000))

    dominio_tema = db.Column(db.Unicode(20))
    presentacion= db.Column(db.Unicode(20))
    interaccion= db.Column(db.Unicode(20))
    uso_recursos= db.Column(db.Unicode(20))
    comunicacion= db.Column(db.Unicode(20))
    tutoria= db.Column(db.Unicode(20))
    extension_info= db.Column(db.Unicode(20))
    estrategias= db.Column(db.Unicode(20))
    general_instructor= db.Column(db.Unicode(20))

    sugerencias_instructor = db.Column(db.Unicode(5000))

    curso_id = db.Column(db.Integer, db.ForeignKey=('courses.id'))
    curso = db.relationship('Curso', backref='retroalimentaciones')


class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'
    __table_args__ = (
        db.PrimaryKeyConstraint('asistente_id', 'curso_id'),
    )
    asistente_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    curso_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    acreditado = db.Column(db.Boolean, nullable=True)

    asistente = db.relationship('User', backref='inscriptions')
    curso = db.relationship('Course', backref='inscritos')



class RequiredIf(validators.DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value.

    Sources:    acreditado = db.Column(db.Boolean, nullable=True)
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
    objetivo_general = TextAreaField('Objectivo general', validators=[
        DataRequired('El campo de objetivo general es obligatorio')
    ])
    objetivos_especificos = TextAreaField('Ojetivos_especificos', validators=[
        DataRequired('El campo de objetivos especificos es obligatorio')
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
    curriculum_sintetico = FileField('Curriculum sintético de el instructor', validators=[
        FileRequired("Se requiere que subas un archivo conteniendo el curriculum sintetico del instructor")
    ])
    antecedentes = TextAreaField('Antecedentes o habilidades necesarios de los alumnos', validators=[
        DataRequired('El campo de Antecedentes o habilidades necesarios de los alumnos es obligatorio')
    ])
    duracion = IntegerField('Duración en horas del programa', validators=[
        DataRequired('El campo de Duración en horas del programa es obligatorio'),
        validators.NumberRange(1, message="El curso debe durar al menos una hora")
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
        DataRequired('El campo de abierto para el publico es obligatorio')
    ])
    cupo_min = IntegerField("Cupo minimo", validators=[
        DataRequired('El campo de cupo minimo es obligatorio'),
        validators.NumberRange(1, message="El cupo debe ser positivo")
    ])
    cupo_max = IntegerField("Cupo maximo", validators=[
        DataRequired('El campo de cupo maximo es obligatorio'),
        validators.NumberRange(1, message="El cupo debe ser positivo")
    ])
    apoyo_econ = TextAreaField("Apoyo economico", validators=[
        DataRequired('El campo de apoyo economico es obligatorio')
    ])
    apoyo_admin = TextAreaField("Apoyo administrativo", validators=[
        DataRequired('El campo de apoyo administrativo es obligatorio')
    ])
    apoyo_servicio = TextAreaField("Apoyos de servicio existentes y solicitado", validators=[
        DataRequired('El campo de apoyos de servicio existentes y solicitado es obligatorio')
    ])
    fecha_inicio = DateField("Fecha de inicio", validators=[
        DataRequired('El campo de fecha de inicio es obligatorio')
    ])
    fecha_fin = DateField("Fecha de finalización", validators=[
        DataRequired('El campo de fecha de finalización es obligatorio')
    ])
    submit = SubmitField("Enviar info")


class RetroalimentacionForm(FlaskForm):
    expectativas = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )

    pertinencia = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    topicos = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    tiempos = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    logro_objetivos = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    materiales_apoyo = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    aplicacion = SelectFie = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )ld(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    medios_tecnologicos = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    cantidad_info = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    general_curso = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )

    sugerencias_curso = TextAreaField('Sugerencias sobre el curso', validators=[
        DataRequired('El campo de sugerencias sobre el curso es obligatorio')
    ])

    dominio_tema = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    presentacion = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    interaccion = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    uso_recursos = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    comunicacion = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    tutoria = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    extension_info = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    estrategias = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )
    general_instructor = SelectField(
        'Programming Language',
        choices=[('malo', 'Malo'), ('regular', 'Regular'), ('bueno', 'Bueno'), ('excelente', 'Excelente')]
    )

    sugerencias_instructor = TextAreaField('Sugerencias al instructor', validators=[
        DataRequired('El campo de objetivo general es obligatorio')
    ])

class ReviewCourseForm(FlaskForm):
    approved = BooleanField('Aprobado')
    rejection_reason = StringField('Razon de rechazo', validators=[
        RequiredIf('approved', 'El campo de Razon de rechazo es requerido.', negate=True)
    ])

    submit = SubmitField("Enviar revisión")


class EvaluarAlumnoForm(FlaskForm):
    user_id = HiddenField()
    user_name = HiddenField()
    aprobado = BooleanField("Aprobado", default=False)


class EvaluarListaAlumnosForm(FlaskForm):
    alumnos = FieldList(FormField(EvaluarAlumnoForm))
    submit = SubmitField("Enviar evaluación")
