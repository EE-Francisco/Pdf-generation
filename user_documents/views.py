"""
View for rendering the index page of the web application.

This view displays a search box for finding patient records and allows the user to select one or more records for further processing. The selected records can be downloaded as a PDF document by clicking a button.

Attributes:
    template_name (str): the name of the HTML template to be rendered.

Methods:
    get_context_data(**kwargs): generates the context data dictionary for the template rendering. The method retrieves the search query from the GET parameters and retrieves or generates the relevant data objects from the database. The context data includes the request object, the search query, the list of matching patients, the selected patient (if any), the follow-up and traceability checkboxes, the materials associated with the selected patient (if traceability is checked), and the indices of the selected records (if any).
    get(request, *args, **kwargs): handles GET requests. If the "Generar pdf" button was clicked, the method generates a PDF document based on the selected records and returns it as a response. Otherwise, the method simply renders the template with the context data.

Usage:
    The view is associated with the 'index' URL pattern in the website's URLs file. When a user accesses this URL, the view searches for patients whose names match the search criteria provided in the 'q' parameter of the GET request. The search results are displayed in a table on the index page, along with links to view more detailed information about each patient.
    If the user clicks on the "Generar pdf" button on the page, the view generates a PDF document that includes additional information about the selected patient(s), such as traceability data for the raw materials used in their products, or a detailed record of their medical history. The PDF document is created by combining multiple HTML templates (defined in separate files) using the `download_pdfs` utility function, and then returning the resulting PDF file to the user's browser.
    The view also stores the search criteria in the user's session, so that it can be retrieved and used again if the user navigates away from the index page and then returns to it later.
"""


from .models import Patient, Traceability
from .utils import download_pdfs, get_queryset, get_materials
from django.views.generic import TemplateView
from django.core.paginator import Paginator


class IndexPageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Generates the context data dictionary for the template rendering.

        Args:
            **kwargs: optional keyword arguments.

        Returns:
            A dictionary of context data for the template rendering.

        Raises:
            None.

        Description:
            This method retrieves the search query from the GET parameters and retrieves or generates the relevant data objects from the database. The context data includes the following keys:
            - 'request': the current request object.
            - 'q': the search query, if any.
            - 'patient_list': a list of Patient objects matching the search query, if any.
            - 'selected_patient': the selected Patient object, if any.
            - 'follow-up': a boolean indicating whether the 'follow-up' checkbox was checked.
            - 'traceability': a boolean indicating whether the 'traceability' checkbox was checked.
            - 'materials': a list of Traceability objects associated with the selected Patient, if traceability is checked.
            - 'indices': a list of integers representing the indices of the selected records, if any.

            If no search query is provided, the method returns an empty list of Patient objects.

            If a selected Patient is found, the method populates the 'follow-up' and 'traceability' keys in the context data based on the corresponding GET parameters. If traceability is checked, the method also retrieves the associated Traceability objects from the database.

            The 'indices' key is populated based on the remaining GET parameters, which represent the indices of the selected records.
        """
        context = super().get_context_data(**kwargs)

        request = self.request
        context["request"] = request

        if "q" in request.GET:
            query = request.GET["q"]
            request.session['q'] = query
        elif request.GET:
            query = request.session.get('q', '')
        else:
            query = ""

        patient_list = get_queryset(query, Patient)
        context["patient_list"] = patient_list

        # Pagination
        paginator = Paginator(patient_list, 25)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        context["paginator"] = paginator

        if request.GET:
            first_key = list(request.GET.keys())[0]
            selected_patient = patient_list.filter(name=first_key)

            if selected_patient.exists():
                patient_name = first_key
                parameters = request.GET.getlist(patient_name)
                patient = selected_patient.first()
                context["selected_patient"] = patient

                if "follow_up" in parameters:
                    context["follow_up"] = parameters.pop(-2)

                if "traceability" in parameters:
                    context["traceability"] = parameters.pop(-2)

                    context["materials"] = get_materials(
                        request, patient, Traceability)

                context["indices"] = list(map(int, parameters[:-1]))

            # Temporary

                prosthesis = ["DESARTICULADO DE HOMBRO",
                              "DESARTICULADA DE CADERA",
                              "TRANSTIBIAL",
                              "TRANSRADIAL",
                              "TRANSHUMERAL",
                              "TRANSFEMORAL"]

                if patient.product_name.product_name in prosthesis:
                    context["prothesis"] = True

        return context

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to the index page view.

        Args:
            request: the current request object.
            *args: optional positional arguments.
            **kwargs: optional keyword arguments.

        Returns:
            A response object containing the rendered template or a PDF download, depending on the presence of the 'Generar pdf' button in the GET parameters.

        Raises:
            None.

        Description:
            This method calls the 'get_context_data' method to generate the context data dictionary for the template rendering. If the 'Generar pdf' button is present in the GET parameters, the method generates a PDF file by rendering one or more HTML templates specified by the 'follow-up', 'traceability', and 'indices' keys in the context data dictionary. The resulting PDF file is returned as a download response.

            If the 'Generar pdf' button is not present in the GET parameters, the method renders the 'index.html' template using the context data dictionary and returns the resulting response object.
        """
        context = self.get_context_data(**kwargs)
        if "Generar pdf" in request.GET.values():
            template_paths = []
            if context.get("follow_up"):
                template_paths.append("follow-up.html")
            if context.get("traceability"):
                template_paths.append("traceability.html")
            if context.get("indices"):
                template_paths.append("patient_record.html")
            pdf = download_pdfs(template_paths, context)
            return pdf
        return self.render_to_response(context)
