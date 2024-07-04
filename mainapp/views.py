from django.shortcuts import render,  redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth import logout as django_logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.views.decorators.http import require_GET
from .models import User, FotosPerfil, Critica, Tipo, Noticia, Actividad
from .forms import UserRegistrationForm, CriticaForm, PerfilForm, EditarCriticaForm, PerfilFormEditar, CriticaFilterForm, CriticaFilterFormWhitFilter, NoticiaForm, NoticiaFilterFormWhitFilter, EditarNoticiaForm, ActividadForm, EditarActividadForm
from .tmdb import search_movie, get_movie_details
from .decorators import admin_required
import os
import json
import datetime

''' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- '''

# VISTAS ADMINISTRADOR

# Vista de error de credenciales para no administradores
def no_permission(request):
    return render(request, 'mainapp/no_permission.html')

# Vista para el registro de usuario
@admin_required
def registro_usuario(request):
    fotos_perfil = FotosPerfil.objects.all()
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, fotos_perfil=fotos_perfil)
        if user_form.is_valid():
            usuario = user_form.save(commit=False)
            # Encriptar la contraseña antes de guardarla en la base de datos
            usuario.set_password(user_form.cleaned_data['password1'])
            usuario.save()
            messages.success(request, 'COLABORADOR REGISTRADO EXITOSAMENTE.')
            # En lugar de redirigir, renderizamos la misma página
            user_form = UserRegistrationForm(fotos_perfil=fotos_perfil)  # Reseteamos el formulario después del registro
        else:
            messages.error(request, 'ERROR AL REGISTRAR COLABORADOR. VERIFICA LOS DATOS INGRESADOS.\n SI LOS DATOS SON CORRECTOS TAL  VEZ EL COLABORADOR YA SE ENCUENTRA REGISTRADO.')
    else:
        user_form = UserRegistrationForm(fotos_perfil=fotos_perfil)
    
    context = {
        'user_form': user_form,
        'fotos_perfil': fotos_perfil,
    }
    return render(request, 'mainapp/registro_usuario.html', context)

@admin_required
def editar_eliminar_usuario(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        if correo:
            try:
                usuario = User.objects.get(correo=correo)
                if 'update' in request.POST:
                    form = PerfilFormEditar(request.POST, request.FILES, instance=usuario, fotos_perfil=FotosPerfil.objects.all())
                    if form.is_valid():
                        form.save()
                        messages.success(request, f'El usuario {usuario.nombre} ha sido actualizado correctamente.')
                    else:
                        messages.error(request, f'Error al actualizar el usuario {usuario.nombre}.')
                elif 'delete' in request.POST:
                    usuario.delete()
                    messages.success(request, f'El usuario {usuario.nombre} ha sido eliminado correctamente.')
            except User.DoesNotExist:
                messages.error(request, 'No se encontró el usuario especificado.')
        else:
            messages.error(request, 'No se proporcionó un correo válido.')
    
    usuarios = User.objects.all()
    forms = {}
    for usuario in usuarios:
        try:
            forms[usuario.correo] = PerfilFormEditar(instance=usuario, fotos_perfil=FotosPerfil.objects.all())
        except Exception as e:
            messages.error(request, f'Error al crear el formulario para {usuario.correo}: {e}')
    return render(request, 'mainapp/editar_eliminar_usuario.html', {'usuarios': usuarios, 'forms': forms})


@admin_required
def actualizar_usuario(request, correo):
    usuario = get_object_or_404(User, correo=correo)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Los cambios para {usuario.correo} han sido guardados.')
            return redirect('editar_eliminar_usuario')
    else:
        form = UserRegistrationForm(instance=usuario)
    return render(request, 'mainapp/actualizar_usuario.html', {'form': form, 'usuario': usuario})

@admin_required
def eliminar_usuario(request, correo):
    usuario = get_object_or_404(User, correo=correo)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, f'El usuario {usuario.correo} ha sido eliminado.')
        return redirect('editar_eliminar_usuario')
    return render(request, 'mainapp/eliminar_usuario.html', {'usuario': usuario})

@admin_required
def detalle_usuario(request):
    return render(request, 'mainapp/detalle_usuario.html')

User = get_user_model()

class DateTimeEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

@admin_required
def admin_view(request):
    # Recuperar la información del usuario
    nombre = request.session.get('nombre')
    # Indicador 1: Cantidad de usuarios registrados
    cantidad_usuarios = User.objects.count()

    # Indicador 2: Cantidad de críticas realizadas
    cantidad_criticas = Critica.objects.count()

    # Indicador 3: Cantidad de noticias realizadas
    cantidad_noticias = Noticia.objects.count()

    # Indicador 4: Cantidad de actividades realizadas
    cantidad_actividades = Actividad.objects.count()

    # Gráfica 1: Cantidad de críticas realizadas por usuario
    criticas_por_usuario = User.objects.annotate(num_criticas=Count('critica')).values('nombre', 'num_criticas')

    # Gráfica 2: Críticas realizadas tomando en cuenta las fechas y horas
    criticas_por_fecha = Critica.objects.extra(select={'date': 'date(datetime)'}).values('date').annotate(num_criticas=Count('id')).order_by('date')
    # Convertir las fechas a cadenas ISO
    criticas_por_fecha = [
        {
            'date': data['date'].isoformat(),
            'num_criticas': data['num_criticas']
        }
        for data in criticas_por_fecha
    ]

    # Gráfica 3: Cantidad de series, películas, chismes (gráfica de pastel)
    tipos = Critica.objects.values('tipo__descripcion').annotate(count=Count('tipo'))

    context = {
        'cantidad_usuarios': cantidad_usuarios,
        'cantidad_criticas': cantidad_criticas,
        'cantidad_noticias': cantidad_noticias,
        'cantidad_actividades': cantidad_actividades,
        'criticas_por_usuario': json.dumps(list(criticas_por_usuario)),
        'criticas_por_fecha': json.dumps(criticas_por_fecha),
        'tipos': json.dumps(list(tipos)),
        'nombre': nombre,
    }

    return render(request, 'mainapp/admin.html', context)

@admin_required
def criticas_admin(request):
    criticas = Critica.objects.all().order_by('-datetime')

    if request.method == 'GET':
        filter_form = CriticaFilterForm(request.GET)

        if filter_form.is_valid():
            calificacion_min = filter_form.cleaned_data.get('calificacion')
            tipo = filter_form.cleaned_data.get('tipo')
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if calificacion_min:
                criticas = criticas.filter(calificacion__gte=calificacion_min)

            if tipo:
                criticas = criticas.filter(tipo=tipo)

            if nombre:
                criticas = criticas.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                criticas = criticas.order_by('datetime')
            elif fecha_orden == 'desc':
                criticas = criticas.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'criticas': criticas,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/criticas_admin.html', context)

@admin_required
def noticias_admin(request):
    noticias = Noticia.objects.all().order_by('-datetime')

    if request.method == 'GET':
        filter_form = NoticiaFilterFormWhitFilter(request.GET)

        if filter_form.is_valid():
            tipo = filter_form.cleaned_data.get('tipo')
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if tipo:
                noticias = noticias.filter(tipo=tipo)

            if nombre:
                noticias = noticias.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                noticias = noticias.order_by('datetime')
            elif fecha_orden == 'desc':
                noticias = noticias.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'noticias': noticias,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/noticias_admin.html', context)

@admin_required
def calendario_admin(request):
    nombre = request.user.nombre
    actividades = Actividad.objects.all()

    if request.method == 'POST' and 'nueva_actividad' in request.POST:
        form = ActividadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Actividad registrada exitosamente.')
            return redirect('calendario_admin')
        else:
            messages.error(request, 'Error al registrar la actividad. Verifica los datos ingresados.')
    else:
        form = ActividadForm()

    context = {
        'actividades': actividades,
        'form': form,
        'nombre': nombre,
    }

    return render(request, 'mainapp/calendario_admin.html', context)


@login_required
def obtener_actividades(request):
    actividades = Actividad.objects.all()
    actividades_json = [
        {
            'title': actividad.descripcion,
            'start': actividad.datetime.strftime('%Y-%m-%d'),
            'url': reverse('editar_actividad', args=[actividad.pk])
        }
        for actividad in actividades
    ]
    return JsonResponse(actividades_json, safe=False)

@admin_required
def editar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    if request.method == 'POST':
        form = EditarActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            actividad = form.save(commit=False)

            actividad.save()
            messages.success(request, 'Actividad editada exitosamente.')
            return redirect('calendario_admin')
        else:
            messages.error(request, 'Error al editar la actividad. Verifica los datos ingresados.')
    else:
        form = EditarActividadForm(instance=actividad)

    return render(request, 'mainapp/editar_actividad.html', {'form': form})



''' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- '''

# VISTAS PUBLICAS

# Vista sobre la infromacion del sitio
def nostros(request):
    return render(request, 'mainapp/nosotros.html')

# Vista de la ventana inicial de la app
def home(request):
    criticas = Critica.objects.all().order_by('-datetime')

    if request.method == 'GET':
        filter_form = CriticaFilterForm(request.GET)

        if filter_form.is_valid():
            calificacion_min = filter_form.cleaned_data.get('calificacion')
            tipo = filter_form.cleaned_data.get('tipo')
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if calificacion_min:
                criticas = criticas.filter(calificacion__gte=calificacion_min)

            if tipo:
                criticas = criticas.filter(tipo=tipo)

            if nombre:
                criticas = criticas.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                criticas = criticas.order_by('datetime')
            elif fecha_orden == 'desc':
                criticas = criticas.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'criticas': criticas,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/main.html', context)


def peliculas(request):
    criticas = Critica.objects.filter(tipo='1').order_by('-datetime')

    if request.method == 'GET':
        filter_form = CriticaFilterFormWhitFilter(request.GET)

        if filter_form.is_valid():
            calificacion_min = filter_form.cleaned_data.get('calificacion')
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if calificacion_min:
                criticas = criticas.filter(calificacion__gte=calificacion_min)

            if nombre:
                criticas = criticas.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                criticas = criticas.order_by('datetime')
            elif fecha_orden == 'desc':
                criticas = criticas.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'criticas': criticas,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/peliculas.html', context)

def series(request):
    criticas = Critica.objects.filter(tipo='2').order_by('-datetime')

    if request.method == 'GET':
        filter_form = CriticaFilterFormWhitFilter(request.GET)

        if filter_form.is_valid():
            calificacion_min = filter_form.cleaned_data.get('calificacion')
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if calificacion_min:
                criticas = criticas.filter(calificacion__gte=calificacion_min)

            if nombre:
                criticas = criticas.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                criticas = criticas.order_by('datetime')
            elif fecha_orden == 'desc':
                criticas = criticas.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'criticas': criticas,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/series.html', context)



def mas_y_mas_chismes(request):
    criticas = Critica.objects.filter(tipo='3').order_by('-datetime')

    if request.method == 'GET':
        filter_form = CriticaFilterFormWhitFilter(request.GET)

        if filter_form.is_valid():
            calificacion_min = filter_form.cleaned_data.get('calificacion')
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if calificacion_min:
                criticas = criticas.filter(calificacion__gte=calificacion_min)

            if nombre:
                criticas = criticas.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                criticas = criticas.order_by('datetime')
            elif fecha_orden == 'desc':
                criticas = criticas.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'criticas': criticas,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/mas_y_mas_chismes.html', context)

def trailers(request):
    criticas = Critica.objects.filter(tipo='4').order_by('-datetime')

    if request.method == 'GET':
        filter_form = CriticaFilterFormWhitFilter(request.GET)

        if filter_form.is_valid():
            calificacion_min = filter_form.cleaned_data.get('calificacion')
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if calificacion_min:
                criticas = criticas.filter(calificacion__gte=calificacion_min)

            if nombre:
                criticas = criticas.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                criticas = criticas.order_by('datetime')
            elif fecha_orden == 'desc':
                criticas = criticas.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'criticas': criticas,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/trailers.html', context)

def noticias(request):
    noticias = Noticia.objects.all().order_by('-datetime')

    if request.method == 'GET':
        filter_form = NoticiaFilterFormWhitFilter(request.GET)

        if filter_form.is_valid():
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if nombre:
                noticias = noticias.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                noticias = noticias.order_by('datetime')
            elif fecha_orden == 'desc':
                noticias = noticias.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'noticias': noticias,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/noticias.html', context)

def publicar_critica(request):
    return render(request, 'mainapp/publicar_critica.html')


# Vista para el inisio de sesion de usuario
def login_view(request):
    if request.user.is_authenticated:
        user = request.user
        tipo_permiso = user.permisos_id
        request.session['tipo_permiso'] = tipo_permiso
        
        # Redirigir según el permiso del usuario
        if tipo_permiso == 1:
            return redirect('admin_view')
        else:
            return redirect('perfil')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(correo=email)
            if user.check_password(password):
                request.session['correo'] = user.correo
                request.session['nombre'] = user.nombre
                
                # Obtener el tipo de permiso del usuario
                tipo_permiso = user.permisos_id#user.permisos.tipo
                
                request.session['tipo_permiso'] = tipo_permiso

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Redirigir según el permiso del usuario
                if tipo_permiso == 1:
                    next_url = request.GET.get('next', 'admin_view')
                else:
                    next_url = request.GET.get('next', 'calendario')

                return redirect(next_url)
            else:
                messages.error(request, 'PASSWORD INCORRECTO.')
        except User.DoesNotExist:
            messages.error(request, 'CORREO INCORRECTO.')

    return render(request, 'mainapp/login.html')


def detalle_critica(request, pk):
    video = Critica.objects.first()  # Suponiendo que solo hay un video en la base de datos, puedes adaptar esto según tus necesidades
    critica = get_object_or_404(Critica, pk=pk)
    return render(request, 'mainapp/detalle_critica.html', {'critica': critica, 'video': video})



# ELIMINAR
def filtrar_criticas(request):
    filtro = request.GET.get('filtro')  # Obtener el criterio de filtro seleccionado

    # Filtrar las críticas según el criterio seleccionado
    if filtro == 'nombre':
        criticas = Critica.objects.order_by('nombre')
    elif filtro == 'calificacion':
        criticas = Critica.objects.order_by('-calificacion')
    else:
        criticas = Critica.objects.all()

    # Renderizar el template con las críticas filtradas
    return render(request, 'mainapp/filtrar_criticas.html', {'criticas': criticas})


''' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- '''


# VISTAS SOLO PARA COLABORADORES

def recuperar_password(request):
    return render(request, 'mainapp/recuperar_password.html')

# Vista para salir del sistema
def logout_view(request):
    # Limpia la sesión del usuario
    # logout(request)
    django_logout(request)
    return redirect('login')


# Vista/ funcion para salir del sistema automaticamente
def logout_and_redirect_home(request):
    logout(request)
    return redirect('login')  # 'home' es el nombre de la vista inicial

# Vista de perfil de usuario
@login_required
def perfil(request):
    usuario = request.user
    fotos_perfil = FotosPerfil.objects.all()
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=usuario, fotos_perfil=fotos_perfil)
        if form.is_valid():
            usuario = form.save(commit=False)
            
            # Obtener el ID de la foto de perfil seleccionada
            foto_perfil_pk = form.cleaned_data.get('foto_perfil', None)
            if foto_perfil_pk:
                usuario.foto_perfil_id = foto_perfil_pk  # Asignar el ID, no el objeto completo
            
            usuario.save()
            
            messages.success(request, 'PERFIL EDITADO EXITOSAMENTE.')
            return redirect('perfil')
        else:
            messages.error(request, 'ERROR AL EDITAR PERFIL. VERIFICA LOS DATOS INGRESADOS.')
    else:
        form = PerfilForm(instance=usuario, fotos_perfil=fotos_perfil)

    # Ocultar el campo permisos en el formulario para usuarios comunes
    form.fields.pop('permisos', None)

    return render(request, 'mainapp/perfil.html', {'usuario': usuario, 'form': form, 'fotos_perfil': fotos_perfil})
    

# Vista modifcar perfil de usuario
@login_required
def editar_perfil(request):
    usuario = request.user
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'PERFIL EDITADO EXITOSAMENTE.')
            print("Mensaje establecido correctamente")  # Agrega esta línea
            return redirect('perfil')  # Redirige al perfil después de guardar los cambios
        else:
            messages.error(request, 'ERROR AL EDITAR PERFIL. VERIFICA LOS DATOS INGRESADOS.')
    else:
        form = PerfilForm(instance=request.user)  # Crea una instancia del formulario con los datos del usuario actual

    return render(request, 'mainapp/editar_perfil.html', {'form': form})


# Vista que permite filtrar las peliculas
@login_required
def search_movie_view(request):
    movie_name = request.GET.get('name')
    if movie_name:
        search_results = search_movie(movie_name)
        if search_results:
            movie_id = search_results[0]['id']
            movie_details = get_movie_details(movie_id)
            return JsonResponse(movie_details)
    return JsonResponse({})

# Vista para realizar critica de pelicula
@login_required
def critica(request):
    correo = request.session.get('correo')
    nombre = request.session.get('nombre')
    if request.method == 'POST':
        form = CriticaForm(request.POST, request.FILES)
        if form.is_valid():
            critica = form.save(commit=False)
            critica.user = request.user  # Asigna el usuario logueado
            critica.datetime = timezone.now()  # Asigna la fecha y hora actual
            
            critica.save()
            messages.success(request, 'RESEÑA PUBLICADA EXITOSAMENTE')  # Mensaje de éxito
            return redirect('critica')
        else:
            messages.error(request, ' ERROR AL PUBLICAR RESEÑA. REVISA LOS DATOS INGRESADOS.')  # Mensaje de error
    else:
        form = CriticaForm()
    return render(request, 'mainapp/critica.html', {'form': form, 'correo': correo, 'nombre': nombre})

@login_required
def noticia(request):
    usuario = request.user.nombre  # Usar el nombre de usuario en lugar de first_name
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.user = request.user  # Asignar el usuario actual
            noticia.datetime = timezone.now()  # Asigna la fecha y hora actual
            noticia.save()
            messages.success(request, 'NOTICIA PUBLICADA EXITOSAMENTE')  # Mensaje de éxito
            return redirect('noticia')  # Redirigir usando el nombre de la URL
        else:
            messages.error(request, 'ERROR AL PUBLICAR NOTICIA. REVISA LOS DATOS INGRESADOS.')  # Mensaje de error
    else:
        form = NoticiaForm()
    
    context = {
        'form': form,
        'usuario': usuario,  # Cambiar a 'usuario' para coincidir con la plantilla
    }
    return render(request, 'mainapp/noticia.html', context)

@login_required
def get_movie_details_view(request):
    movie_id = request.GET.get('movie_id')
    movie_details = get_movie_details(movie_id)
    return JsonResponse(movie_details)

# Vista que muestras todas las criticas realizadas por el usuario
@login_required
def mis_criticas(request):
    # Obtener el usuario actual que ha iniciado sesión
    usuario = request.user
    # Filtrar las críticas del usuario actual
    criticas = Critica.objects.filter(user=usuario).order_by('-datetime')
    if request.method == 'GET':
        filter_form = CriticaFilterForm(request.GET)

        if filter_form.is_valid():
            calificacion_min = filter_form.cleaned_data.get('calificacion')
            tipo = filter_form.cleaned_data.get('tipo')
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if calificacion_min:
                criticas = criticas.filter(calificacion__gte=calificacion_min)

            if tipo:
                criticas = criticas.filter(tipo=tipo)

            if nombre:
                criticas = criticas.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                criticas = criticas.order_by('datetime')
            elif fecha_orden == 'desc':
                criticas = criticas.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'criticas': criticas,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/mis_criticas.html', context)


# Vista que muestras todas las criticas realizadas por el usuario
@login_required
def mis_noticias(request):
    # Obtener el usuario actual que ha iniciado sesión
    usuario = request.user
    # Filtrar las críticas del usuario actual
    noticias = Noticia.objects.filter(user=usuario).order_by('-datetime')
    if request.method == 'GET':
        filter_form = NoticiaFilterFormWhitFilter(request.GET)

        if filter_form.is_valid():
            nombre = filter_form.cleaned_data.get('nombre')
            fecha_orden = filter_form.cleaned_data.get('fecha_orden')

            if nombre:
                criticas = criticas.filter(nombre__icontains=nombre)

            if fecha_orden == 'asc':
                criticas = criticas.order_by('datetime')
            elif fecha_orden == 'desc':
                criticas = criticas.order_by('-datetime')

    else:
        filter_form = CriticaFilterForm()

    context = {
        'noticias': noticias,
        'filter_form': filter_form,
    }

    return render(request, 'mainapp/mis_noticias.html', context)

# Vista que muestra los detalles de la critica y pelicula
@login_required
def detalle_critica_admin(request, pk):
    critica = get_object_or_404(Critica, pk=pk)
    fotos_perfil = FotosPerfil.objects.all()

    if request.method == 'POST':
        form = EditarCriticaForm(request.POST, request.FILES, instance=critica)
        if form.is_valid():
            critica = form.save(commit=False)

            # Manejar la ruta de la foto de la crítica
            if 'ruta_foto_critica' in request.FILES:
                critica.ruta_foto_critica = request.FILES['ruta_foto_critica']

            critica.save()
            messages.success(request, 'Crítica editada exitosamente.')
            return redirect('detalle_critica_admin', pk=pk)
        else:
            messages.error(request, 'Error al editar crítica. Verifica los datos ingresados.')
    else:
        form = EditarCriticaForm(instance=critica)

    return render(request, 'mainapp/detalle_critica_admin.html', {'critica': critica, 'usuario': request.user, 'form': form, 'fotos_perfil': fotos_perfil})

@login_required
def detalle_noticia_admin(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    fotos_perfil = FotosPerfil.objects.all()

    if request.method == 'POST':
        form = EditarNoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            noticia = form.save(commit=False)

            # Manejar la ruta de la foto de la crítica
            if 'ruta_foto_critica' in request.FILES:
                noticia.ruta_foto_critica = request.FILES['ruta_foto_critica']

            noticia.save()
            messages.success(request, 'Noticia editada exitosamente.')
            return redirect('detalle_noticia_admin', pk=pk)
        else:
            messages.error(request, 'Error al editar noticia. Verifica los datos ingresados.')
    else:
        form = EditarNoticiaForm(instance=noticia)

    return render(request, 'mainapp/detalle_noticia_admin.html', {'noticia': noticia, 'usuario': request.user, 'form': form, 'fotos_perfil': fotos_perfil})


# Vista para eliminar critica
@login_required
def eliminar_critica(request, pk):
    critica = get_object_or_404(Critica, pk=pk)
    
    if request.method == 'POST':
        if 'eliminar' in request.POST:
            critica.delete()
            messages.success(request, 'Crítica eliminada exitosamente.')
            return redirect('mis_criticas')  # Cambia esto al nombre correcto de tu vista de lista de críticas
        
        form = EditarCriticaForm(request.POST, request.FILES, instance=critica)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cambios guardados exitosamente.')
            return redirect('detalle_critica_admin', pk=critica.pk)
    else:
        form = EditarCriticaForm(instance=critica)
    
    return render(request, 'mainapp/detalle_critica_admin.html', {'form': form, 'critica': critica})


# Vista para eliminar noticia
@login_required
def eliminar_noticia(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    
    if request.method == 'POST':
        if 'eliminar' in request.POST:
            noticia.delete()
            messages.success(request, 'Noticia eliminada exitosamente.')
            return redirect('mis_noticias')  # Cambia esto al nombre correcto de tu vista de lista de críticas
        
        form = EditarNoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cambios guardados exitosamente.')
            return redirect('detalle_noticia_admin', pk=noticia.pk)
    else:
        form = EditarNoticiaForm(instance=noticia)
    
    return render(request, 'mainapp/detalle_noticia_admin.html', {'form': form, 'noticia': noticia})


@login_required
def calendario(request):
    usuario = request.user.correo
    nombre = request.user.nombre
    colaborador = User.objects.get(correo=usuario)
    actividades = Actividad.objects.filter(user=colaborador)

    context = {
        'actividades': actividades,
        'usuario': usuario,
        'nombre': nombre,
    }

    return render(request, 'mainapp/calendario.html', context)

@login_required
def detalle_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)

    context = {
        'actividad': actividad
    }

    return render(request, 'mainapp/detalle_actividad.html', context)