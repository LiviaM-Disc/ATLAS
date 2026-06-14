from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Sum
from .models import Usuario, Negocio, Receita, Despesa, Produto, Categoria, Precificacao

# ==============================================================================
# --- AUTENTICAÇÃO E SESSÃO ---
# ==============================================================================

def login_view(request):
    if 'usuario_id' in request.session:
        return redirect('index')

    if request.method == 'POST':
        email_post = request.POST.get('email')
        senha_post = request.POST.get('senha')

        usuario = Usuario.objects.filter(email=email_post).first()

        if usuario and check_password(senha_post, usuario.senha):
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nome'] = usuario.nome
            return redirect('index')
        else:
            messages.error(request, "E-mail ou senha inválidos.")
    
    return render(request, 'login.html')


def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado.")
        else:
            novo_usuario = Usuario(
                nome=nome,
                email=email,
                senha=make_password(senha)
            )
            novo_usuario.save()
            
            request.session['usuario_id'] = novo_usuario.id
            request.session['usuario_nome'] = novo_usuario.nome
            
            messages.success(request, "Cadastro realizado! Agora, vamos configurar sua empresa.")
            return redirect('cadastrar_negocio')
            
    return render(request, 'cadastro.html')


def cadastrar_negocio_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        nome_do_formulario = request.POST.get('nome_negocio')
        segmento_do_formulario = request.POST.get('segmento')
        meta_do_formulario = request.POST.get('meta_mensal') or 0.0
        capital_do_formulario = request.POST.get('capital_inicial') or 0.0

        if nome_do_formulario:
            usuario_id = request.session['usuario_id']
            usuario_instancia = get_object_or_404(Usuario, id=usuario_id)

            novo_negocio = Negocio(
                nome_negocio=nome_do_formulario,  
                usuario=usuario_instancia,
                segmento=segmento_do_formulario,
                meta_mensal=meta_do_formulario,
                capital_inicial=capital_do_formulario
            )
            novo_negocio.save()

            messages.success(request, "Empresa cadastrada com sucesso!")
            return redirect('index')
        else:
            messages.error(request, "O nome da empresa é obrigatório.")

    return render(request, 'negocio_form.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# ==============================================================================
# --- DASHBOARD PRINCIPAL ---
# ==============================================================================

def index_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    usuario_id = request.session['usuario_id']
    
    resultado_soma = Receita.objects.filter(negocio__usuario_id=usuario_id).aggregate(total=Sum('valor'))
    total_receitas = resultado_soma['total'] or 0.0
    
    meus_negocios = Negocio.objects.filter(usuario_id=usuario_id)
    
    context = {
        'nome': request.session.get('usuario_nome'),
        'total_receitas': total_receitas,
        'qtd_negocios': meus_negocios.count(),
        'negocios': meus_negocios,
    }
    return render(request, 'index.html', context)


# ==============================================================================
# --- MÓDULOS ESPECÍFICOS (VIEWS INDEPENDENTES) ---
# ==============================================================================

def listar_negocios(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
        
    usuario_id = request.session.get('usuario_id')
    negocios = Negocio.objects.filter(usuario_id=usuario_id)
    return render(request, 'negocios.html', {'negocios': negocios})


def lista_receitas(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
        
    receitas = Receita.objects.filter(negocio__usuario_id=request.session['usuario_id'])
    return render(request, 'receitas.html', {'receitas': receitas})


def precificacoes_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
        
    usuario_id = request.session['usuario_id']
    
    dados_precificacao = Precificacao.objects.filter(
        produto__negocio__usuario_id=usuario_id
    ) | Precificacao.objects.filter(
        servico__negocio__usuario_id=usuario_id
    )
    
    context = {
        'precificacoes': dados_precificacao.distinct()
    }
    return render(request, 'precificacoes.html', context)


def produtos_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
        
    usuario_id = request.session.get('usuario_id')
    negocio = Negocio.objects.filter(usuario_id=usuario_id).first()
    
    if not negocio:
        messages.warning(request, "Você precisa cadastrar um negócio antes de gerenciar produtos.")
        return redirect('cadastrar_negocio')

    if request.method == 'POST':
        nome_produto = request.POST.get('nome_produto')
        preco_venda = request.POST.get('preco_venda') or 0.0
        custo_producao = request.POST.get('custo_producao') or 0.0
        estoque = request.POST.get('estoque') or 0
        categoria_id = request.POST.get('categoria') 

        if nome_produto and categoria_id:
            categoria_instancia = get_object_or_404(Categoria, id=categoria_id)

            novo_produto = Produto(
                nome=nome_produto,
                preco_venda=preco_venda,
                custo=custo_producao,
                estoque=estoque,
                negocio=negocio,
                categoria=categoria_instancia 
            )
            novo_produto.save()
            messages.success(request, f"Produto '{nome_produto}' adicionado com sucesso!")
            return redirect('produtos')
        else:
            messages.error(request, "O nome do produto e a categoria são obrigatórios.")

    categorias = Categoria.objects.all()
    produtos = Produto.objects.filter(negocio=negocio)
    
    return render(request, 'produtos.html', {
        'produtos': produtos,
        'negocio': negocio,
        'categorias': categorias 
    })



# ==============================================================================
# --- NOVAS VIEWS ADICIONADAS PARA SUPORTE TOTAL ---
# ==============================================================================

def despesas_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    # Adicione a lógica de busca do banco se necessário, ex: Despesa.objects.all()
    return render(request, 'despesas.html')


def servicos_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'servicos.html')


def metas_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'metas.html')


def alertas_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'alertas.html')


def fechamentos_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'fechamentosMensais.html')


def indicadores_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'IndicadoresFinanceiros.html')


def notificacoes_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'notificacoes.html')


def relatorios_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'relatorios.html')


def usuarios_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'usuarios.html')


def categoria_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    # Se o formulário enviar dados para salvar uma nova categoria
    if request.method == 'POST':
        nome_categoria = request.POST.get('nome_categoria')
        if nome_categoria:
            from .models import Categoria  # Garanta que o seu modelo chama Categoria
            Categoria.objects.create(nome=nome_categoria)
            return redirect('categorias')

    # Busca as categorias para listar na tabela da página
    from .models import Categoria
    categorias = Categoria.objects.all()
    return render(request, 'categoria.html', {'categorias': categorias})