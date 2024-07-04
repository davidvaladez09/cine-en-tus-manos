from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

# Create your models here.
class FotosPerfil(models.Model):
    id = models.AutoField(primary_key=True)
    # direccion = models.CharField(max_length=100)
    direccion = models.ImageField(upload_to='profiles/')
    nombre = models.CharField(max_length=50)
    
class Tipo(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

class CategoriaGenero(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

class DondeVer(models.Model):
    id = models.AutoField(primary_key=True)
    plataforma = models.CharField(max_length=50) 

class Permisos(models.Model):
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=100)

class UserManager(BaseUserManager):
    def create_user(self, correo, nombre, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo debe ser proporcionado')
        email = self.normalize_email(correo)
        user = self.model(correo=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(correo, nombre, password, **extra_fields)

class User(AbstractBaseUser):
    correo = models.EmailField(primary_key=True)
    nombre = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    descripcion = models.CharField(max_length=280)
    foto_perfil = models.ForeignKey(FotosPerfil, on_delete=models.CASCADE)
    #permisos = models.CharField(max_length=50)
    permisos = models.ForeignKey(Permisos, on_delete=models.CASCADE)

    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class Critica(models.Model):
    id = models.AutoField(primary_key=True)
    ruta_foto_critica = models.ImageField(upload_to='review/')
    #ruta_foto_critica = models.ImageField(upload_to='review/', default='path/to/default/image.jpg')
    
    nombre = models.CharField(max_length=255)
    sipnosis = models.TextField()
    director = models.CharField(max_length=255)
    escritor = models.CharField(max_length=255)
    reparto = models.CharField(max_length=255)
    ano = models.CharField(max_length=4)
    pais = models.CharField(max_length=100)
    categoria_genero = models.CharField(max_length=255, blank=True, null=True)

    link_trailer = models.CharField(max_length=255, blank=True, null=True)
    nombre_espanol = models.CharField(max_length=255, blank=True, null=True)
    no_capitulos = models.IntegerField(blank=True, null=True)
    critica = models.TextField()
    donde_ver = models.CharField(max_length=255)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE, related_name='criticas')

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Cambiado de user_id a user
    datetime = models.DateTimeField(default=timezone.now)

    calificacion = models.FloatField(blank=True, null=True)


class FotosCritica(models.Model):
    id = models.AutoField(primary_key=True)
    direccion = models.CharField(max_length=100)
    critica = models.ForeignKey(Critica, on_delete=models.CASCADE)


class Noticia(models.Model):
    id = models.AutoField(primary_key=True)
    ruta_foto_critica = models.ImageField(upload_to='review/')
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Cambiado de id_user a user
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nombre

class Actividad(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.TextField()
    datetime = models.DateField()
    estado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.descripcion} - {self.user.username}"