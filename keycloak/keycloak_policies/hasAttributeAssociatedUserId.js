var userId = $evaluation.getContext().getIdentity().getId()
var resourceAttributeUserId = $evaluation.getPermission().getResource().getSingleAttribute('associated_user_id')

if (resourceAttributeUserId === userId)
$evaluation.grant()