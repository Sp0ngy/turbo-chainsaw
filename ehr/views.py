import zeep
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from zeep import Client

from ehr.forms.forms import StringForm
from ehr.models import Patient
from users.models import Resource
from django_project.permissions import GlobalsScopes as gs

from users.auth_utils import has_protected_user_resource_scope, has_required_scope

gPAS_domain_name = 'TurboChainsaw'

@login_required
def index(request):
    return render(request, 'ehr/index.html', {})

@login_required
def patient_profile(request):
    user = request.user
    try:
        resource = get_object_or_404(Resource, user=user, type=Resource.ResourceTypes.PATIENT_PROFILE)
        patient = get_object_or_404(Patient, user=user)
        keycloak_resource_id = resource.keycloak_resource_id
    except Resource.DoesNotExist:
        raise Http404("This User has no Patient Profile.")

    is_authorized, message = has_protected_user_resource_scope(request, [gs.PATIENT_PROFILE_READ, gs.PATIENT_PROFILE_WRITE], keycloak_resource_id)
    if not is_authorized:
        return HttpResponseForbidden(message)

    ctx = {
        "user": user,
        "patient": patient
    }

    return render(request, 'ehr/patient_profile.html', ctx)


@login_required
def pseudonymize_data(request):
    is_authorized, message = has_required_scope(request,[gs.STAFF_PORTAL_READ, gs.STAFF_PORTAL_WRITE])
    if not is_authorized:
        return HttpResponseForbidden(message)

    # Ensure this is a POST request with necessary data
    pseudonymized_data = ''
    if request.method == "POST":
        form = StringForm(request.POST)
        if form.is_valid():
            string = form.cleaned_data['string']

            # Either use IP in docker network or its container name
            access_token = request.session.get('oidc_access_token')
            wsdl_url = 'http://gpas-wildfly:8080/gpas/gpasService?wsdl'
            settings = zeep.Settings(extra_http_headers={'Authorization': f'Bearer {access_token}'})

            try:
                client = Client(wsdl_url, settings=settings)
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
def de_pseudonymize_data(request):
    is_authorized, message = has_required_scope(request,[gs.STAFF_PORTAL_READ, gs.STAFF_PORTAL_WRITE])
    if not is_authorized:
        return HttpResponseForbidden(message)

    de_pseudonymized_data = ''
    if request.method == "POST":
        form = StringForm(request.POST)
        if form.is_valid():
            pseudonymized_string = form.cleaned_data['string']

            access_token = request.session.get('oidc_access_token')
            wsdl_url = 'http://gpas-wildfly:8080/gpas/gpasService?wsdl'
            settings = zeep.Settings(extra_http_headers={'Authorization': f'Bearer {access_token}'})

            try:
                client = Client(wsdl_url, settings=settings)
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

