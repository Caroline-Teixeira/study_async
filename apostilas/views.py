from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Apostila, ViewApostila
from django.contrib.messages import constants
from django.contrib import messages

# Create your views here.

#Adicionar apostilas
def adicionar_apostilas(request):
    # Proíbe usuários não autenticados de acessarem a página
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')


    if request.method == "GET":
        apostilas = Apostila.objects.filter(user=request.user)
        # !! criar as tags !!
        views_totais = ViewApostila.objects.filter(apostila__user=request.user).count()
        return render(request, 'adicionar_apostilas.html', {'apostilas': apostilas, 'views_totais': views_totais})

    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        arquivo = request.FILES['arquivo']

        apostila = Apostila(user=request.user, titulo=titulo, arquivo=arquivo)
        apostila.save()

        messages.add_message(
            request, constants.SUCCESS, 'Apostila adicionada com sucesso.')
        return redirect('/apostilas/adicionar_apostilas/')

#APOSTILAS/Visualização
def apostila(request, id):
    # Proíbe usuários não autenticados de acessarem a página
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')


    apostila = Apostila.objects.get(id=id)
    views_totais = ViewApostila.objects.filter(apostila=apostila).count()
    views_unicas = ViewApostila.objects.filter(apostila=apostila).values('ip').distinct().count()

    view = ViewApostila(
        ip=request.META['REMOTE_ADDR'],
        apostila=apostila
    )
    view.save()


    return render(request, 'apostila.html', {'apostila': apostila, 'views_totais': views_totais})