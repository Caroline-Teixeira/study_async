from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.http import HttpResponse, Http404
from django.contrib.messages import constants
from django.contrib import messages, auth
from django.contrib.auth.models import User

# Create your views here.
#request = requesição do usuario
#get = request via navegador
#categoria = Categoria.objects.all() - traz as categorias dentro do banco de dados
#flashcards = Flashcard.objects.filter() -  retorna para o usuario seus respectivos flashcards



#Para criar flashcards
def novo_flashcard(request):
    # Proíbe usuários não autenticados de acessarem a página
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')

    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards = Flashcard.objects.filter(user=request.user)

        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')

        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar)

        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)

        return render(request, 'novo_flashcard.html', {'categorias': categorias,
                                                       'dificuldades': dificuldades,
                                                       'flashcards': flashcards})

    elif request.method == "POST":
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        #Não deixa o usuário cadastrar espaços vazios
        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR, "Por favor, preencha os campos de pergunta e resposta adequadamente")
            return redirect('/flashcard/novo_flashcard/')

        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade,
        )
        # salva os dados no banco
        flashcard.save()

        messages.add_message(request, constants.SUCCESS, "Flashcard cadastrado com sucesso!")
        return redirect('/flashcard/novo_flashcard/')

#Para deletar flashcards
def deletar_flashcard(request, id):

    # Validação de segurança !!
    flashcard = Flashcard.objects.get(id=id)
    if flashcard.user == request.user:
        flashcard.delete()
        messages.add_message(request, constants.SUCCESS, "Flashcard deletado com sucesso!")
    else:
        messages.add_message(request, constants.WARNING, "Acesso negado!")
    return redirect('/flashcard/novo_flashcard/')

#Para iniciar desafios - !! faltar checar um item !!
def iniciar_desafio(request):
    # Proíbe usuários não autenticados de acessarem a página
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')

    if request.method == "GET":
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(request, 'iniciar_desafio.html', {'categorias': categorias,
                                                        'dificuldades': dificuldades})
    elif request.method == "POST":
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade
        )

        desafio.save()

        for categoria in categorias:
            desafio.categoria.add(categoria)

        flashcards = (
            Flashcard.objects.filter(user=request.user)
            .filter(dificuldade=dificuldade)
            .filter(categoria_id__in=categorias)
            .order_by('?')
        )

        # order_by('?') - random no django

        if flashcards.count() < int(qtd_perguntas):
            return redirect('/flashcard/iniciar_desafio/')
        #TRATAR PARA ESCOLHER DEPOIS
        # !! Se tiver menos flashcards do que o qtd_perguntas vai dar erro !!

        flashcards = flashcards[: int(qtd_perguntas)]  #0 até a qtd de perguntas que o usuário inseriu

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=f,
            )
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()
        return redirect('/flashcard/listar_desafio/')
        #return HttpResponse("Teste")

#Na página de desafios
def listar_desafio(request):
    # Proíbe usuários não autenticados de acessarem a página
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')


    desafios = Desafio.objects.filter(user=request.user)
    # !! Desenvolver os status !!


    #Filtros
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES


        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')
        #flashcards = Flashcard.objects.filter(user=request.user)

        if categoria_filtrar:
            desafios = desafios.filter(categoria__id=categoria_filtrar)

        if dificuldade_filtrar:
            desafios = desafios.filter(dificuldade=dificuldade_filtrar)




    return render(request, 'listar_desafio.html', {'desafios': desafios, 'categorias': categorias,
                                                   'dificuldades': dificuldades,})

def desafio(request, id):
    #Validação de segurança
    desafio = Desafio.objects.get(id=id)
    if not desafio.user == request.user:
        raise Http404()

    #Status do desafio
    respondidas = desafio.flashcards.filter(respondido=True).count()

    if respondidas == 0:
        desafio.status=desafio.STATUS_CHOICES[0]

    elif desafio.quantidade_perguntas == respondidas:
        desafio.status=desafio.STATUS_CHOICES[2]

    else: desafio.status=desafio.STATUS_CHOICES[1]

    #numero de acertos e erros
    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
        erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()
        return render(request, 'desafio.html', {'desafio': desafio, 'acertos': acertos, 'erros': erros, 'faltantes': faltantes}, )

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()

    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == '1' else False
    flashcard_desafio.save()
    return redirect(f'/flashcard/desafio/{desafio_id}/')

#RELATÓRIOS
def relatorio(request, id):
    desafio = Desafio.objects.get(id=id)

    acertos = desafio.flashcards.filter(acertou=True).count()
    erros = desafio.flashcards.filter(acertou=False).count()
    dados = [acertos, erros]


    #grafico de radar
    categorias = desafio.categoria.all()
    name_categoria = []
    for i in categorias:
        name_categoria.append(i.nome)

    dados2 = []
    for categoria in categorias:
        dados2.append(desafio.flashcards.filter(flashcard__categoria=categoria).filter(acertou=True).count())

    #fazer o ranking the melhores e piores matérias
    return render(request, 'relatorio.html', {'desafio': desafio, 'dados': dados,'categorias': name_categoria, 'dados2': dados2}, )

