from django.contrib import admin
from users.models import User, Resource, Address

admin.site.register(User)
admin.site.register(Resource)
admin.site.register(Address)
