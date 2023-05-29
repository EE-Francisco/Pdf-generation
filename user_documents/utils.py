import pdfkit
import os
import zipfile
import tempfile
import pyodbc
import pandas as pd
from datetime import datetime
from typing import Type, Dict
from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Q, Model
from django.contrib import messages


def download_pdfs(template_paths, context):
    """
    Download PDF files generated from HTML templates as a ZIP file.

    Args:
        template_paths (list): List of file paths that contain HTML templates.
        context (dict): Dictionary containing context data for rendering the templates.

    Returns:
        An HTTP response containing a ZIP file containing the generated PDFs.
    """
    print(template_paths)
    zip_name = 'pdfs.zip'
    zip_file = zipfile.ZipFile(zip_name, 'w')

    with tempfile.TemporaryDirectory() as temp_dir:

        for template_path in template_paths:
            template = get_template(template_path)
            html = template.render(context)
            options = {
                'enable-local-file-access': None,
                'page-size': 'B4',
                'encoding': 'UTF-8',
                'margin-top': '0',
                'margin-bottom': '0',
            }
            pdf = pdfkit.from_string(html, False, options=options)
            template_name = os.path.splitext(template_path)[0] + ".pdf"

            with open(os.path.join(temp_dir, template_name), "wb") as f:
                f.write(pdf)

        with zip_file as zip_file:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, f"{file}")

    with open(zip_name, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_name}'

    os.remove(zip_name)

    return response


def get_queryset(query, model):
    """
    Filter a queryset using a search query.

    This function takes a search query and a Django model and returns a
    queryset of objects that match the query.

    Args:
        query (str): The search query as a text string.
        model (Model): The Django model in which to search for objects.

    Returns:
        QuerySet: A QuerySet of filtered objects that match the query.

    """
    keywords = query.split()
    keywords = [p.rstrip(".,") for p in keywords]
    filters = []
    filters_list = [
        ('name__icontains', 'string'),
        ('cc__icontains', 'string'),
        ('patientrecord__date__year', 'year'),
        ('patientrecord__date__month', 'month'),
        ('patientrecord__date__day', 'day')
    ]
    MONTHS = [('Jan', 'January', 'jan'), ('Feb', 'February', 'feb'), ('Mar', 'March', 'mar'), ('Apr', 'April', 'apr'), ('May', 'May', 'may'), ('Jun', 'June', 'jun'),
              ('Jul', 'July', 'jul'), ('Aug', 'August', 'aug'), ('Sep', 'Sept', 'September', 'sep', 'sept'), ('Oct', 'October', 'oct'), ('Nov', 'November', 'nov'), ('Dec', 'December', 'dec')]
    for word in keywords:
        for field, field_type in filters_list:
            try:
                if field_type == 'year':
                    value = datetime.strptime(word, '%Y').year
                elif field_type == 'month':
                    for i, months in enumerate(MONTHS):
                        if word in months:
                            value = i+1
                            break
                    if not isinstance(value, int) or value > 12:
                        value = datetime.strptime(word, '%m').month
                elif field_type == 'day':
                    value = datetime.strptime(word, '%d').day
                elif field_type == 'string':
                    value = word
                else:
                    continue
            except:
                continue
            filters.append(Q(**{field: value}))
    consultation = Q()
    for filter in filters:
        consultation |= filter
    object_list = model.objects.filter(consultation).distinct()
    return object_list


def migrate_csv(folder_path: str, model: Type[Model], field_mapping: Dict[str, str], delimiter: str = ';', encoding: str = 'latin-1') -> None:
    """
        Moves data from a set of CSV files to a database using the specified model.

        Args:
            folder_path (str): Path of the folder that contains the CSV files to migrate.
            model (Type[Model]): The Django model class to use to store the migrated data.
            field_mapping (Dict[str, str]): Mapping the column names of the CSV file to the field names of the Django model.
            delimiter (str, optional): Delimiter used in CSV files. Default, ';'.
            encoding (str, optional): Encoding used in CSV files. Default 'utf-8'.

        Raises:
            Exception: Thrown if an error occurs during the migration of a CSV file.

        Returns:
            None: This function does not return anything. Saves the migrated data to the database using the specified model.
    """
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            data = pd.read_csv(file_path, sep=delimiter,
                               encoding=encoding).dropna(how='all')
            print(data)
            instances = []
            for _, row in data.iterrows():
                instance = model()
                print(row)
                for attribute_name, field_name in field_mapping.items():
                    print(field_name, "----------------")
                    value = row[field_name]
                    if not pd.isna(value):
                        if attribute_name == 'invoice_number':
                            value = int(value)
                        elif attribute_name == 'value':
                            value = value.replace(',', '')
                        setattr(instance, attribute_name, value)
                instances.append(instance)
            model.objects.bulk_create(instances)
        except Exception as e:
            print(f'Error al migrar el archivo {file_name}: {str(e)}')
            raise


def get_materials(request, patient, model):
    """
    Returns a list of materials for a given patient, based on the last record in their history and the date of purchase
    of the material. The function receives as arguments an `HttpRequest` object (request), a `Patient` object (patient) and a model.
    (model) that represents the materials that you want to obtain.

    Args:
        request: `HttpRequest` object representing the received HTTP request.
        patient: `Patient` object that represents the patient for whom you want to obtain the materials.
        model: model that represents the materials to be obtained.

    Raises:
        If no previous date is found for the product in question, an error message is displayed.

    Returns:
        materials: List of objects in the specified model that represent the materials to be supplied to the patient.
    """
    raw_materials = patient.product_name.raw_materials.all()
    date = patient.patientrecord_set.latest('date').date
    materials = []

    for raw_material in raw_materials:
        try:
            material = model.objects.filter(supplies=raw_material, purchase_date__lt=date).order_by(
                '-purchase_date').latest('purchase_date')
            materials.append(material)
        except model.DoesNotExist:
            messages.error(
                request, f'No se encontró ninguna fecha previa para el producto {raw_material}.')

    return materials


def query_msaccess(database_path, query):
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={database_path};"
    )
    conn = pyodbc.connect(conn_str)
    conn.setdecoding(pyodbc.SQL_WCHAR, encoding='latin-1')
    df = pd.read_sql(query, conn)
    # cursor = conn.cursor()
    # cursor.execute(query)
    # description = cursor.description
    # rows = cursor.fetchall()
    # cursor.close()
    conn.close()
    return df


def migrate_msaccess(database_path, query, patient_model, product_model, field_mapping):
    data = query_msaccess(database_path, query)
    instances = []
    for _, row in data.iterrows():
        product_name = row[field_mapping['product_name']]
        product_instance = product_model.objects.get(product_name=product_name)
        patient_instance = patient_model()
        for attribute_name, field_name in field_mapping.items():
            if not attribute_name == 'product_name':
                value = row[field_name]
                setattr(patient_instance, attribute_name, value)
        patient_instance.product_name = product_instance
        instances.append(patient_instance)
    patient_model.objects.bulk_create(instances)


def migrate_excel(file_path, sheet_name, patient_model):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df_left = df.iloc[:, :7]
    df_right = df.iloc[:, 9:]
    df_left['Unnamed: 2'].replace(['PACIENTE', 'FESTIVO'], inplace=True)
    df_left.dropna(subset=['Unnamed: 2'], inplace=True)
    df_right['Unnamed: 10'].replace(['PACIENTE', 'FESTIVO'], inplace=True)
    df_right.dropna(subset=['Unnamed: 10'], inplace=True)
    patient_names = df_left["Unnamed: 2"]
    for patient_name in patient_names:
        patient = patient_model.objects.filter(name__icontains=patient_name)
        print(patient)
    # print(patient_names)
    # patient = patient_model.objects.filter(name=patient_name)
    return df_left, df_right, patient_names


# from apps.user_documents.utils import migrate_csv
# from apps.user_documents.models import Traceability
# field_mapping = {
#     'invoice_number': 'FACTURA',
#     'purchase_date': 'FECHA',
#     'supplies': 'DETALLE',
#     'amount': 'CANTIDAD',
#     'supplier': 'PROVEEDOR',
#     'batch_number': 'LOTE',
#     'invima_registry': 'REGISTRO INVIMA',
#     'expiration_date': 'FECHA DE CADUCIDAD',
#     'value': 'VALOR',
# }
# migrate_csv('traceability/2023/', Traceability, field_mapping=field_mapping)
# df = pd.read_csv('traceability/Abril.csv', sep=';', encoding='latin-1').dropna(how='all')
