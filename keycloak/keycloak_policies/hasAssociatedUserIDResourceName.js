var userId = $evaluation.getContext().getIdentity().getId()
var resourceName = $evaluation.getPermission().getResource().getName()

if (resourceName.contains(userId))
$evaluation.grant()