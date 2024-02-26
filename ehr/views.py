from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required

from zeep import Client

from ehr.forms.forms import StringForm
from ehr.models import Patient
from users.models import User, Resource
from django_project.permissions import GlobalsScopes as gs

from users.decorators import protected_user_resource, requires_scope
from users.uma_policy_management import grant_resource_permission

gPAS_domain_name = 'TurboChainsaw'

@login_required
def index(request):
    try:
        patient_resource = request.user.resource_set.get(type=Resource.ResourceTypes.PATIENT_PROFILE)
        if patient_resource:
            patient_resource_id = patient_resource.keycloak_resource_id
        else:
            patient_resource_id = None
    except Resource.DoesNotExist:
        patient_resource_id = None

    return render(request, 'ehr/index.html', {'patient_resource_id': patient_resource_id})

@login_required
@protected_user_resource(gs.PATIENT_PROFILE_READ, gs.PATIENT_PROFILE_WRITE)
def patient_profile(request, keycloak_resource_id=None):
    """ Takes Patient pk which is same as identifier without 'P' """

    if request.method == 'POST' and 'grant_access' in request.POST:
        grant_resource_permission(request)

    if keycloak_resource_id:
        # Find the resource and then the user
        resource = get_object_or_404(Resource, keycloak_resource_id=keycloak_resource_id)
        user = get_object_or_404(User, pk=resource.user.pk)
        patient = get_object_or_404(Patient, user=user)
    else:
        return Http404("This User has no Patient Profile.")

    ctx = {
        "user": user,
        "patient": patient
    }

    return render(request, 'ehr/patient_profile.html', ctx)


@login_required
@requires_scope(gs.STAFF_PORTAL_READ, gs.STAFF_PORTAL_WRITE)
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
@requires_scope(gs.STAFF_PORTAL_READ, gs.STAFF_PORTAL_WRITE)
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

