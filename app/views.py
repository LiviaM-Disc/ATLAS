from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Usuario, Negocio, Receita, Despesa, Produto, Categoria

# --- NAVEGAÇÃO E LOGIN ---
from django.contrib.auth.hashers import make_password # Importante!

def index_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    usuario_id = request.session['usuario_id']
    
    # Buscando dados reais para os Cards
    total_receitas = Receita.objects.filter(usuario_id=usuario_id).sum('valor') # Lógica simplificada
    meus_negocios = Negocio.objects.filter(usuario_id=usuario_id)
    
    context = {
        'nome': request.session.get('usuario_nome'),
        'total_receitas': total_receitas,
        'qtd_negocios': meus_negocios.count(),
    }
    return render(request, 'index.html', context)

def listar_negocios(request):
    usuario_id = request.session.get('usuario_id')
    negocios = Negocio.objects.filter(usuario_id=usuario_id)
    return render(request, 'negocios.html', {'negocios': negocios})

def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        # Verifica se o email já existe para não dar erro
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado.")
        else:
            # CRIANDO O USUÁRIO COM SENHA CRIPTOGRAFADA
            novo_usuario = Usuario(
                nome=nome,
                email=email,
                senha=make_password(senha) # A MÁGICA ACONTECE AQUI
            )
            novo_usuario.save()
            messages.success(request, "Cadastro realizado! Faça login.")
            return redirect('login')
            
    return render(request, 'cadastro.html')

def login_view(request):
    # Se já estiver logado na sessão, vai para a index
    if 'usuario_id' in request.session:
        return redirect('index')

    if request.method == 'POST':
        email_post = request.POST.get('email')
        senha_post = request.POST.get('senha')

        # Busca o usuário pelo email
        usuario = Usuario.objects.filter(email=email_post).first()

        # Verifica se o usuário existe e se a senha criptografada bate
        if usuario and check_password(senha_post, usuario.senha):
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nome'] = usuario.nome
            return redirect('index')
        else:
            messages.error(request, "E-mail ou senha inválidos.")
    
    return render(request, 'login.html')

def index_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'index.html', {'nome': request.session.get('usuario_nome')})

def logout_view(request):
    request.session.flush()
    return redirect('login')

def index_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    usuario_id = request.session['usuario_id']
    negocios = Negocio.objects.filter(usuario_id=usuario_id)
    
    context = {
        'nome': request.session.get('usuario_nome'),
        'negocios': negocios,
    }
    return render(request, 'index.html', context)

# --- LÓGICA DE NEGÓCIO (EXEMPLO PARA RECEITAS) ---

def lista_receitas(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
        
    # Busca receitas apenas dos negócios deste usuário
    receitas = Receita.objects.filter(negocio__usuario_id=request.session['usuario_id'])
    return render(request, 'receitas.html', {'receitas': receitas})