from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from app import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Unicode(200))
    sinthentic_content = db.Column(db.Unicode(5000))
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

    responsable = db.relationship("User", back_populate="responsable_courses")
    instructor = db.relationship("User", back_populate="instructor_courses")
