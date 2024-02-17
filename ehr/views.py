from django.shortcuts import render
from django.http import JsonResponse

from zeep import Client

from ehr.forms.forms import StringForm
from users.decorators import requires_scopes
from django_project.permissions import GlobalPermissions as gb

gPAS_domain_name = 'TurboChainsaw'

@requires_scopes(gb.EHR_PSEUDO_RWX)
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

@requires_scopes(gb.EHR_PSEUDO_RWX)
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

