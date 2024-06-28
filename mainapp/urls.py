from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URL PUBLICOS
    path('', views.home, name='home'),
    path('nosotros/', views.nostros, name='nosotros'),
    path('detalle_critica/<int:pk>/', views.detalle_critica, name='detalle_critica'),
    path('peliculas/', views.peliculas, name='peliculas'),
    path('mas_y_mas_chismes/', views.mas_y_mas_chismes, name='mas_y_mas_chismes'),
    path('series/', views.series, name='series'),
    path('trailers/', views.trailers, name='trailers'),

    # URL PRIVADOS
    path('login/', views.login_view, name='login'),
    path('registro_usuario/', views.registro_usuario, name='registro_usuario'),
    path('editar_eliminar_usuario/', views.editar_eliminar_usuario, name='editar_eliminar_usuario'),
    path('actualizar_usuario/<str:correo>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('eliminar_usuario/<str:correo>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('detalle_usuario/<str:correo>/', views.detalle_usuario, name='detalle_usuario'),
    path('perfil/', views.perfil, name='perfil'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('admin_view/', views.admin_view, name='admin_view'),
    path('publicar_critica/', views.publicar_critica, name='publicar_critica'),
    path('critica/', views.critica, name='critica'),
    path('criticas_admin/', views.criticas_admin, name='criticas_admin'),
    path('search_movie/', views.search_movie_view, name='search_movie'),
    path('get_movie_details/', views.get_movie_details_view, name='get_movie_details'),
    path('mis_criticas/', views.mis_criticas, name='mis_criticas'),
    path('detalle_critica_admin/<int:pk>/', views.detalle_critica_admin, name='detalle_critica_admin'),
    path('eliminar_critica/<int:pk>/', views.eliminar_critica, name='eliminar_critica'),
    path('recuperar_password/', views.recuperar_password, name='recuperar_password'),
    path('logout/', views.logout_view, name='logout_view'),
    path('logout_and_redirect_home/', views.logout_and_redirect_home, name='logout_and_redirect_home'),

    # URL ADMINISTRADOR
    path('admin_view/', views.admin_view, name='admin_view'),
    path('no_permission/', views.no_permission, name='no_permission'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)