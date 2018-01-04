# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime

from datetime import date

from flask import current_app
from flask_script import Command

from app import db
from app.models.user_models import User, Role
from app.models.course_models import Course, CourseStatus, Inscripcion

class InitDbCommand(Command):
    """ Initialize the database."""

    def run(self):
        init_db()


def init_db():
    """ Initialize the database."""
    db.drop_all()
    db.create_all()
    create_users()


def create_users():
    """ Create users """

    # Create all tables
    db.create_all()

    # Adding roles
    admin_role = find_or_create_role('admin', u'Admin')
    responsable_role = find_or_create_role('responsable', u'Responsable')

    # Add users
    # admins
    user = find_or_create_user(u'Enrique', u'Pe;a Nieto', u'Persona existente', u'admin@example.com', 'Password1', admin_role)

    #responsables
    res1 = find_or_create_user(u'Antonio', u'Lopez Santana', u'Persona existente', u'responsable1@example.com', 'Password1', responsable_role)
    res2 = find_or_create_user(u'Plutarco', u'Elias Calles', u'Persona existente', u'responsable2@example.com', 'Password1', responsable_role)


    #usuarios
    victoria = find_or_create_user(u'Guadalupe', u'Victoria', u'Persona existente', u'member1@example.com', 'Password1')
    villa = find_or_create_user(u'Francisco', u'Villa', u'Persona existente', u'member2@example.com', 'Password1')
    carranza = find_or_create_user(u'Venustiano', u'Carranza', u'Persona existente', u'member3@example.com', 'Password1')
    juarez = find_or_create_user(u'Benito', u'Juarez', u'Persona existente', u'member4@example.com', 'Password1')

    c = Course(
        nombre='Programación no lineal',
        objetivo_general='Enseñar sobre programanción no lineal',
        objetivos_especificos='Enseñarles a programar en python',
        contenido_sintetico='Algebra lineal y otras cosas',
        modalidades_aprendizaje='Competencias',
        bibliografia='Libros y mas libros',
        perfil_academico='Una vez dio una clase',
        curriculum_sintetico_filename='wero_curriculum.pdf',
        antecedentes='Saber programar dos tres',
        duracion=9,

        abierto=True,
        cupo_min=3,
        cupo_max=15,
        apoyo_econ='Ninguno',
        apoyo_admin='Un aula con mesas y sillas disponible.',
        apoyo_servicio='Ninguno',
        fecha_inicio=date(2017, 11, 27),
        fecha_fin=date(2017, 12, 15),

        instructor=villa,
        responsable=res1,
        instructor_email=villa.email,

        status=CourseStatus.finalized
    )

    inscribir(c, victoria)
    inscribir(c, carranza)
    inscribir(c, juarez)

    # Save to DB
    db.session.commit()


def inscribir(curso, usuario):
    ins = Inscripcion(asistente=usuario, curso=curso)

    db.session.add(ins)


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(first_name, last_name, cargo, email, password, role=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    first_name=first_name,
                    last_name=last_name,
                    cargo=cargo,
                    password=current_app.user_manager.hash_password(password),
                    active=True,
                    confirmed_at=datetime.datetime.utcnow())
        if role:
            user.roles.append(role)
        db.session.add(user)
    return user
