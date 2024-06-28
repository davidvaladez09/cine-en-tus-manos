from django.contrib import admin
from .models import FotosPerfil, User, CategoriaGenero, DondeVer, Tipo, FotosCritica, Critica

# Register your models here.
admin.site.register(FotosPerfil)
admin.site.register(User)
admin.site.register(CategoriaGenero)
admin.site.register(DondeVer)
admin.site.register(Tipo)
admin.site.register(FotosCritica)
admin.site.register(Critica)