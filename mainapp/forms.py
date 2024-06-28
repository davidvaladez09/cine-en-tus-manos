from django import forms
from . models import User, FotosPerfil, Permisos, Critica, Tipo

# Form de registrp de usuario
class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    foto_perfil = forms.ModelChoiceField(queryset=None, empty_label="SELECCIONA UNA FOTO DE PERFIL")
    permisos = forms.ModelChoiceField(queryset=Permisos.objects.all(), empty_label="SELECCIONA EL ROL DEL NUEVO COLABORADOR")
    
    def __init__(self, *args, **kwargs):
        fotos_perfil = kwargs.pop('fotos_perfil', None)
        super().__init__(*args, **kwargs)
        if fotos_perfil:
            self.fields['foto_perfil'].queryset = fotos_perfil
            self.fields['foto_perfil'].label_from_instance = lambda obj: obj.nombre
            self.fields['permisos'].label_from_instance = lambda obj: obj.tipo

            # Asignar choices para mostrar correctamente las opciones en el formulario
            self.fields['foto_perfil'].choices = [(foto.pk, foto.nombre) for foto in fotos_perfil]
            self.fields['foto_perfil'].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = User
        fields = ['correo', 'nombre', 'password1', 'password2', 'foto_perfil', 'permisos', 'descripcion']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("LAS CONTRASEÑAS INGRESADAS NO COINCIDEN.")
        

# Form para subir archivo multimedia
class UploadPhotoForm(forms.ModelForm):
    class Meta:
        model = FotosPerfil
        fields = ['direccion']

# Form para realizar reseña
class CriticaForm(forms.ModelForm):
    tipo = forms.ModelChoiceField(queryset=Tipo.objects.all(), empty_label="SELECCIONA EL TIPO")
    trailer_file = forms.FileField(label='Selecciona el archivo del tráiler', required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].label_from_instance = lambda obj: obj.descripcion
    
    class Meta:
        model = Critica
        fields = ['nombre', 'sipnosis', 'director', 'escritor', 'reparto', 'ano', 'pais', 'categoria_genero',
                  'link_trailer', 'nombre_espanol', 'no_capitulos', 'critica', 'donde_ver', 'ruta_foto_critica', 'tipo', 'calificacion']
        widgets = {
            'ruta_foto_critica': forms.ClearableFileInput(attrs={'required': True}),
            'link_trailer': forms.ClearableFileInput(attrs={'required': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        trailer_file = cleaned_data.get("trailer_file")
        if not trailer_file:
            raise forms.ValidationError("Debe seleccionar un archivo de tráiler")
        return cleaned_data

# Form perfil de usuario
class PerfilForm(forms.ModelForm):
    foto_perfil = forms.ModelChoiceField(queryset=None, empty_label="SELECCIONA UNA FOTO DE PERFIL", required=False)

    class Meta:
        model = User
        fields = ['nombre', 'descripcion', 'foto_perfil']

    def __init__(self, *args, **kwargs):
        fotos_perfil = kwargs.pop('fotos_perfil', None)
        super().__init__(*args, **kwargs)
        
        # Configurar opciones del dropdown para las fotos de perfil disponibles
        if fotos_perfil:
            self.fields['foto_perfil'].queryset = fotos_perfil
            self.fields['foto_perfil'].label_from_instance = lambda obj: obj.nombre
            
            # Asignar choices para mostrar correctamente las opciones en el formulario
            choices = [(foto.pk, foto.nombre) for foto in fotos_perfil]
            self.fields['foto_perfil'].choices = choices
            
            # Obtener la foto de perfil actual del usuario
            current_photo = getattr(self.instance, 'foto_perfil', None)
            
            # Si hay una foto actualmente seleccionada, establecerla como seleccionada por defecto
            if current_photo:
                self.initial['foto_perfil'] = current_photo.pk

        # Actualizar atributos del widget
        self.fields['foto_perfil'].widget.attrs.update({
            'class': 'form-control'
        })

    
class PerfilFormEditar(forms.ModelForm):
    foto_perfil = forms.ModelChoiceField(queryset=FotosPerfil.objects.none(), empty_label="SELECCIONA UNA FOTO DE PERFIL")
    permisos = forms.ModelChoiceField(queryset=Permisos.objects.all(), empty_label="SELECCIONA EL ROL DEL COLABORADOR")

    class Meta:
        model = User
        fields = ['nombre', 'descripcion', 'foto_perfil', 'permisos']

    def __init__(self, *args, **kwargs):
        fotos_perfil = kwargs.pop('fotos_perfil', None)
        super().__init__(*args, **kwargs)
        if fotos_perfil is not None:
            self.fields['foto_perfil'].queryset = fotos_perfil
            self.fields['foto_perfil'].label_from_instance = lambda obj: obj.nombre
            self.fields['permisos'].label_from_instance = lambda obj: obj.tipo

        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'style': 'height: 4rem;'})
        self.fields['descripcion'].widget.attrs.update({'class': 'form-control', 'style': 'height: 4rem;'})
        self.fields['foto_perfil'].widget.attrs.update({'class': 'form-control'})
        self.fields['permisos'].widget.attrs.update({'class': 'form-control'})

# Form para editar critica 
class EditarCriticaForm(forms.ModelForm):
    tipo = forms.ModelChoiceField(queryset=Tipo.objects.all(), empty_label="SELECCIONA EL TIPO")
    ruta_foto_critica = forms.FileField(label='Selecciona la foto de la crítica', required=False)
    trailer_file = forms.FileField(label='Selecciona el archivo del tráiler', required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].label_from_instance = lambda obj: obj.descripcion

    class Meta:
        model = Critica
        fields = ['nombre', 'sipnosis', 'director', 'escritor', 'reparto', 'ano', 'pais', 'categoria_genero',
                  'link_trailer', 'nombre_espanol', 'no_capitulos', 'critica', 'donde_ver', 'ruta_foto_critica', 'tipo', 'calificacion']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class TipoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.descripcion  # Cambia 'nombre' por el campo correcto que quieres mostrar

class CriticaFilterForm(forms.Form):
    calificacion = forms.FloatField(required=False, label='Calificación mínima')
    tipo = TipoModelChoiceField(queryset=Tipo.objects.all(), required=False, label='Tipo')
    nombre = forms.CharField(max_length=255, required=False, label='Nombre')
    fecha_orden_choices = [
        ('', 'Ordenar por fecha'),
        ('asc', 'Fecha ascendente'),
        ('desc', 'Fecha descendente'),
    ]
    fecha_orden = forms.ChoiceField(choices=fecha_orden_choices, required=False, label='Orden de fecha')

class CriticaFilterFormWhitFilter(forms.Form):
    calificacion = forms.FloatField(required=False, label='Calificación mínima')
    nombre = forms.CharField(max_length=255, required=False, label='Nombre')
    fecha_orden_choices = [
        ('', 'Ordenar por fecha'),
        ('asc', 'Fecha ascendente'),
        ('desc', 'Fecha descendente'),
    ]
    fecha_orden = forms.ChoiceField(choices=fecha_orden_choices, required=False, label='Orden de fecha')