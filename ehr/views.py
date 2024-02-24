from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from zeep import Client

from ehr.forms.forms import StringForm
from ehr.models import Patient
from users.decorators import requires_scopes
from users.models import User
from django_project.permissions import GlobalsScopes as gs

from users.decorators import uma_protected_resource
from users.uma_policy_management import grant_resource_permission

gPAS_domain_name = 'TurboChainsaw'

@login_required
def index(request):
    keycloak_id = None
    pk = None
    patient_profile = None

    if not request.user.is_anonymous:
        keycloak_id = request.user.keycloak_id

    try:
        patient_profile = Patient.objects.get(user__keycloak_id=keycloak_id)
        pk = patient_profile.pk
    except Patient.DoesNotExist:
        patient_profile = None

    return render(request, 'ehr/index.html', {'pk': pk})

@login_required
@uma_protected_resource(gs.PATIENT_PROFILE_READ)
def patient_profile(request, pk=None):
    """ Takes Patient pk which is same as identifier without 'P' """

    if request.method == 'POST' and 'grant_access' in request.POST:
        grant_resource_permission(request)

    if pk:
        patient = Patient.objects.get(pk=pk)
        user = User.objects.get(patient=patient)
    else:
        return Http404("This User has no Patient Profile.")

    ctx = {
        "user": user,
        "patient": patient
    }

    return render(request, 'ehr/patient_profile.html', ctx)


@login_required
@requires_scopes(gs.EHR_READ, gs.EHR_WRITE)
def pseudonymize_data(request):
    # Ensure this is a POST request with necessary data
    pseudonymized_data = ''
    if request.method == "POST":
        form = StringForm(request.POST)
        if form.is_valid():
            string = form.cleaned_data['string']

            # Either use IP in docker network or its container name
            wsdl_url = 'http://gpas-wildfly:8080/gpas/gpasService?wsdl'

            try:
                client = Client(wsdl_url)
                response = client.service.getOrCreatePseudonymFor(value=string, domainName=gPAS_domain_name)
                pseudonymized_data = response  # Adapt based on actual response structure

            except Exception as e:
                print(e)
                # Handle any errors that occur during the SOAP request
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
    else:
        form = StringForm()

    return render(request, 'ehr/pseudonymize.html', {'form': form, 'pseudonymized_data': pseudonymized_data})

@login_required
@requires_scopes(gs.EHR_READ, gs.EHR_WRITE)
def de_pseudonymize_data(request):
    de_pseudonymized_data = ''
    if request.method == "POST":
        form = StringForm(request.POST)
        if form.is_valid():
            pseudonymized_string = form.cleaned_data['string']

            # Either use IP in docker network or its container name
            wsdl_url = 'http://gpas-wildfly:8080/gpas/gpasService?wsdl'

            try:
                client = Client(wsdl_url)
                response = client.service.getValueFor(psn=pseudonymized_string, domainName=gPAS_domain_name)
                de_pseudonymized_data = response  # Adapt based on actual response structure

            except Exception as e:
                print(e)
                # Handle any errors that occur during the SOAP request
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
    else:
        form = StringForm()

    return render(request, 'ehr/de_pseudonymize.html', {'form': form, 'de_pseudonymized_data': de_pseudonymized_data})

