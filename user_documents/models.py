"""
Module: models.py
Description: This module defines the database models for the application.

Classes:
- Patient: Represents a patient record in the database.
- PatientRecord: Represents a record of a patient's appointment in the database.
"""

from django.db import models
from django.utils import timezone

YES = 'SI'
NO = 'NO'
YES_NO_CHOICES = [
    (YES, 'SI'),
    (NO, 'NO'),
]

SUBCATEGORY_CHOICES = [
    ('', '---------'),  # opción vacía
    ('Resortada', 'Resortada'),
    ('Reaccion a piso', 'Reaccion a piso'),
    ('Sarmiento corto', 'Sarmiento corto'),
    ('Sarmiento articulado', 'Sarmiento articulado'),
    ('Plantillas termoformadas', 'Termoformadas'),
    ('Plantillas Cuero', 'Cuero'),
    ('Plantillas UCBL', 'UCBL'),
]


class RawMaterial(models.Model):
    raw_material_name = models.CharField(max_length=50)

    def __str__(self):
        return self.raw_material_name


class Product(models.Model):
    product_name = models.CharField(max_length=50)
    raw_materials = models.ManyToManyField(
        RawMaterial, through='RawMaterialQuantity')
    subcategory = models.CharField(
        max_length=50, choices=SUBCATEGORY_CHOICES, blank=True, null=True)

    def __str__(self):
        if self.subcategory:
            return f"{self.product_name} - {self.subcategory}"
        else:
            return self.product_name


class RawMaterialQuantity(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.quantity} {self.raw_material.raw_material_name} needed for {self.product.product_name}"


class Patient(models.Model):
    """
    Represents a patient record in the database.

    Fields:
    - EPS: a constant representing the patient's EPS entity.
    - ARL: a constant representing the patient's ARL entity.
    - IPS: a constant representing the patient's IPS entity.
    - PARTICULAR: a constant representing a particular healthcare entity.
    - OTTOBOCK: a constant representing the Otterbock entity.
    - ENTITY_CHOICES: a list of tuples representing the possible choices for the entity field.
    - YES: a constant representing a "Yes" choice.
    - NO: a constant representing a "No" choice.
    - YES_NO_CHOICES: a list of tuples representing the possible choices for fields that have a "Yes" or "No" value.
    - SATISFACTORIO: a constant representing a satisfactory activity value.
    - name: a string representing the patient's name.
    - cc: a string representing the patient's CC number.
    - entity: a string representing the patient's healthcare entity.
    - entity_name: a string representing the name of the patient's healthcare entity.
    - companion_required: a string representing whether a companion is required for the appointment.
    - activity: a string representing the activity the patient is attending.
    - reported_drawbacks: a string representing whether the patient has reported any drawbacks.
    - drawbacks_description: a string representing the description of the patient's reported drawbacks.
    - technosurveillance: a string representing whether the patient is under technosurveillance.
    - technosurveillance_id: an integer representing the patient's technosurveillance ID.
    - technosurveillance_date: a date representing the date of the patient's technosurveillance.

    Methods:
    - __str__: returns the patient's name as a string.
    """
    EPS = 'EPS'
    ARL = 'ARL'
    IPS = 'IPS'
    PARTICULAR = 'PARTICULAR'
    OTTOBOCK = 'OTTOBOCK'
    GRADUATE = 'GR'
    ENTITY_CHOICES = [
        (EPS, 'EPS'),
        (ARL, 'ARL'),
        (IPS, 'IPS'),
        (PARTICULAR, 'Particular')
    ]

    name = models.CharField(max_length=100)
    cc = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10)
    city = models.CharField(max_length=30)
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE)
    entity = models.CharField(
        max_length=10, choices=ENTITY_CHOICES, default=IPS)
    entity_name = models.CharField(max_length=30, default=OTTOBOCK)
    companion_required = models.CharField(
        max_length=2, choices=YES_NO_CHOICES, default=NO)
    signature = models.ImageField(upload_to='signatures', null=True)

    def __str__(self):
        return self.name


class PatientRecord(models.Model):
    """
    A model to represent a record of a patient's appointment.

    Fields:
    - patient (ForeignKey): the patient associated with the record
    - date (DateTimeField): the date and time of the appointment
    - client (CharField): whether the patient is a new or existing client
    - requirement (CharField): the reason for the appointment, chosen from a list of pre-defined options
    - description (CharField): a brief description of the appointment
    - new_appointment (CharField): whether a new appointment needs to be scheduled, chosen from a list of yes/no options
    - new_appointment_date (DateTimeField): the date and time of the next appointment, if applicable

    Methods:
    - __str__(): returns a string representation of the appointment date in the format "DD/MM/YYYY"
    """
    ENTRENAMIENTO = 'ENTRENAMIENTO'
    GARANTIA = 'GARANTIA'
    MANTENIMIENTO = 'MANTENIMIENTO'
    REPARACION = 'REPARACION'
    VALORACION = 'VALORACION'
    TOMA_MEDIDAS = 'TOMA DE MEDIDAS'
    PRUEBA_DISPOSITIVO = 'PRUEBA DE DISPOSITIVO'
    PRUEBA_Y_ENTREGA_DE_DISPOSITIVO = 'PRUEBA Y ENTREGA DE DISPOSITIVO'
    REQUIREMENT_CHOICES = [
        (ENTRENAMIENTO, 'ENTRENAMIENTO'),
        (GARANTIA, 'GARANTIA'),
        (MANTENIMIENTO, 'MANTENIMIENTO'),
        (REPARACION, 'REPARACION'),
        (VALORACION, 'VALORACION'),
        (TOMA_MEDIDAS, 'TOMA DE MEDIDAS'),
        (PRUEBA_DISPOSITIVO, 'PRUEBA DE DISPOSITIVO'),
        (PRUEBA_Y_ENTREGA_DE_DISPOSITIVO, 'PRUEBA Y ENTREGA DE DISPOSITIVO')
    ]
    description_message = 'Usuario asiste para toma de medidas'
    NEW = 'Nuevo'
    EXISTING = 'Existente'
    CLIENT_CHOICES = [
        (NEW, 'New'),
        (EXISTING, 'Existing')
    ]
    SATISFACTORIO = 'SATISFACTORIO'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    client = models.CharField(
        max_length=9, choices=CLIENT_CHOICES, default=NEW)
    requirement = models.CharField(
        max_length=35, choices=REQUIREMENT_CHOICES, default=TOMA_MEDIDAS)
    description = models.CharField(max_length=100, default=description_message)
    activity = models.CharField(max_length=30, default=SATISFACTORIO)
    reported_drawbacks = models.CharField(
        max_length=2, choices=YES_NO_CHOICES, default=NO)
    drawbacks_description = models.CharField(max_length=100, blank=True)
    technosurveillance = models.CharField(
        max_length=2, choices=YES_NO_CHOICES, default=NO)
    technosurveillance_id = models.IntegerField(blank=True, null=True)
    technosurveillance_date = models.DateField(blank=True, null=True)
    new_appointment = models.CharField(
        max_length=2, choices=YES_NO_CHOICES, default=YES)
    new_appointment_date = models.DateTimeField(
        default=timezone.now, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.date.strftime('%d/%m/%Y'))


class Traceability(models.Model):
    invoice_number = models.CharField(max_length=10)
    purchase_date = models.DateField()
    supplies = models.CharField(max_length=50)
    amount = models.FloatField()
    supplier = models.CharField(max_length=60)
    batch_number = models.CharField(max_length=30, blank=True)
    invima_registry = models.CharField(max_length=30, blank=True)
    expiration_date = models.DateField(blank=True, null=True)
    value = models.IntegerField(null=True)

    def __str__(self):
        return str(self.invoice_number)
