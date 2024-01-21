from django.urls import path #vai procurar no url do study_app
from . import views  #o ponto significa mesma pasta

 #rota da url e função chamada no file views
urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logar/', views.logar, name='login'),
    path('logout/', views.logout, name='logout'),
]