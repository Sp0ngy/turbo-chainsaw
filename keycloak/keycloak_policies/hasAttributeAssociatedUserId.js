var userId = $evaluation.getContext().getIdentity().getId()
var resourceAttributeEmail = $evaluation.getPermission().getResource().getSingleAttribute('associated_user_id')

if (resourceAttributeEmail === userId)
$evaluation.grant()