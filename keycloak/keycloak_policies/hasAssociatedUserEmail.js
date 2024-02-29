var userEmail = $evaluation.getContext().getIdentity().getAttributes().getValue('email').asString(0)
var resourceAttributeEmail = $evaluation.getPermission().getResource().getSingleAttribute('associated_user_email')

if (resourceAttributeEmail === userEmail)
$evaluation.grant()