# Plano de Integração: Claude Pro + Cursor Pro (V4 — Django 2 By Example)
### Guia Completo para o Projeto do Livro de Antonio Melé

---

## Sobre este guia

Este plano foi adaptado especificamente para o projeto **Django 2 By Example** de Antonio Melé.
O livro cobre quatro projetos progressivos que serão usados como exemplos práticos ao longo de todos os exercícios:

| Projeto | App Django | Tecnologias extras |
|---|---|---|
| **Blog** | `blog` | Django ORM, RSS, Sitemap, Search |
| **Rede Social (Bookmarks)** | `account`, `images`, `actions` | Redis, Many-to-Many, AJAX |
| **Loja Online** | `shop`, `orders`, `payment`, `coupons` | Celery, Redis, Braintree |
| **E-learning** | `courses`, `students` | Cache framework, REST API |

O modelo mental e o workflow mantêm-se iguais ao V4 original. O que muda são os comandos, os templates `.mdc` e os exemplos de código — todos adaptados para Django 2 e Python.

---

## Índice

1. [Modelo Mental](#modelo-mental)
2. [Setup Inicial](#setup-inicial)
3. [Dia 1 — Indexação e Leitura do Projeto](#dia-1)
4. [Dia 2 — Arquitetura, Regras e Plan Mode](#dia-2)
5. [Dia 3 — Refatoração Global com Agent Mode](#dia-3)
6. [Dia 4 — Revisão Sénior e Loop de Feedback](#dia-4)
7. [Dia 5 — Workflow Completo e Git](#dia-5)
8. [Templates `.mdc` para Django](#templates-mdc)
9. [Gestão de Contexto e Tokens](#gestao-contexto)
10. [Estratégia de Testes](#estrategia-testes)
11. [Projetos Legados — Django 2 especificamente](#projetos-legados)
12. [Claude fora do Cursor](#claude-fora-cursor)
13. [Prompts de Ponte — Tabela Completa](#prompts-ponte)
14. [Troubleshooting — Problemas Frequentes](#troubleshooting)
15. [Critérios de Decisão](#criterios-decisao)
16. [Indicadores de Evolução](#indicadores)

---

## Modelo Mental {#modelo-mental}

```
Claude (Arquiteto Sénior)
        ↓
Documentação Técnica / Regras .mdc (Single Source of Truth)
        ↓
Cursor Composer + Agent Mode (Operário Qualificado)
        ↓
Terminal: manage.py + pytest + flake8 (Realidade)
        ↓
Tu (Orquestrador e Decisor Final)
```

**Regras de ouro — nunca quebrar:**

- Nunca deixes o Cursor decidir arquitetura Django sozinho (estrutura de apps, relações de models, etc.).
- Nunca uses o Claude para escrever views ou models um a um.
- Usa sempre **Plan Mode** (Shift + Tab) antes de qualquer tarefa com mais de 1 passo.
- Se o Cursor falhar duas vezes na mesma tarefa, para. Volta ao Claude.
- Faz sempre `git commit` antes de uma sessão agentic.

---

## Setup Inicial — Antes de Começar {#setup-inicial}

### 1. Instalar e configurar o ambiente

```bash
# Clonar o repositório do livro (se disponível) ou abrir a tua cópia
cursor /caminho/para/django2byexample

# Confirmar o ambiente virtual ativo
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Verificar a versão do Django
python -m django --version  # deve mostrar 2.x

# Instalar dependências
pip install -r requirements.txt
```

### 2. Ligar o Claude ao Cursor

1. No Cursor, vai a **Settings → Models**.
2. Seleciona `claude-sonnet-4-5` como modelo padrão (uso geral).
3. Reserva `claude-opus-4-5` para arquitetura complexa e revisão profunda.
4. Confirma que a indexação está ativa: **Settings → Features → Codebase Indexing → Enable**.

### 3. Verificar a indexação

```
# No chat do Cursor, após a indexação:
@Codebase Quantas apps Django existem neste projeto? Lista-as.
```

Se responder corretamente com `blog`, `account`, `images`, etc., está funcional.

### 4. Criar a estrutura de regras

```bash
# Na raiz do projeto Django
mkdir -p .cursor/rules
touch .cursor/rules/core.mdc
touch .cursor/rules/django.mdc
touch .cursor/rules/testing.mdc
```

### 5. Confirmar ferramentas essenciais

```bash
# Verificar que tudo funciona antes de começar
python manage.py check               # verifica configuração Django
python manage.py migrate             # aplica migrações pendentes
python manage.py test                # corre os testes (pode estar vazio inicialmente)
flake8 .                             # lint (instalar com: pip install flake8)
pytest                               # se preferires pytest (pip install pytest-django)
```

Se `python manage.py check` passar sem erros, o ambiente está pronto.

### 6. Criar `.cursorignore` para excluir ficheiros irrelevantes

```
# .cursorignore
venv/
__pycache__/
*.pyc
*.pyo
.env
db.sqlite3
media/
staticfiles/
node_modules/
.git/
```

---

## Dia 1 — Indexação e Leitura do Projeto {#dia-1}

**Objetivo:** Compreender a estrutura do projeto Django antes de alterar uma única linha.

### Exercício 1.1 — Leitura estrutural com o Cursor

No **Chat do Cursor** (Ctrl/Cmd + L):

```
@Codebase Resume a arquitetura deste projeto Django:
- Quantas apps existem e qual é a responsabilidade de cada uma?
- Como estão organizadas as urls (urls.py raiz vs apps)?
- Que modelos de dados existem e quais as relações entre eles?
- Que views são class-based vs function-based?
- Onde está o maior technical debt?
```

Depois, aprofunda por app:

```
@blog/ Explica a arquitetura desta app:
- Modelos e as suas relações
- Views e o que cada uma faz
- Template tags personalizadas (se existirem)
- Pontos de melhoria óbvios
```

```
@shop/ Explica como o fluxo de compra está implementado:
- Que modelos representam o carrinho, encomenda e pagamento?
- Como está implementado o sistema de cupões?
- Onde está a integração com Celery?
```

### Exercício 1.2 — Análise arquitetural com o Claude

Copia os ficheiros `models.py` das principais apps e envia ao Claude:

```
Atua como arquiteto sénior Django. Vou partilhar os models.py das apps 
deste projeto (Django 2 By Example de Antonio Melé).

Analisa e diz-me:
1. As relações entre modelos estão bem definidas? Há redundâncias?
2. Que campos deveriam ter índices de base de dados e não têm?
3. Há problemas potenciais de N+1 queries nas relações ForeignKey/M2M?
4. Os Meta classes estão bem configurados (ordering, verbose_name)?
5. O que melhorarias com prioridade, mesmo sendo Django 2?

[Cola aqui o conteúdo dos models.py]
```

**Exemplo específico para o projeto do livro:**

```
# Pergunta focada no blog
Olhando para o modelo Post do blog, com campos como status, publish, 
author (FK para User) e tags (M2M via django-taggit):

1. O manager personalizado PublishedManager está a ser usado corretamente?
2. Como otimizarias as queries na ListView do blog para evitar N+1?
3. Faz sentido o campo slug ter unique_for_date=True? Que problema resolve?
```

### Exercício 1.3 — Criar o `core.mdc`

Pede ao Claude para gerar o ficheiro de regras base:

```
Com base na análise do projeto Django 2 By Example, gera um core.mdc para o Cursor com:
- Stack e versões exatas
- Estrutura de apps do projeto
- Comandos Django essenciais
- Convenções de código observadas no livro
- O que nunca fazer neste projeto Django

Formato frontmatter .mdc do Cursor.
```

**Resultado esperado ao fim do Dia 1:**
- Mapa claro de todas as apps e as suas responsabilidades
- `core.mdc` criado com regras reais do projeto
- Lista das 3–5 melhorias mais impactantes identificadas

---

## Dia 2 — Arquitetura, Regras e Plan Mode {#dia-2}

**Objetivo:** Definir a "lei" do projeto antes de tocar no código.

### Exercício 2.1 — Planear uma melhoria real com o Claude

Escolhe uma das seguintes melhorias concretas do projeto do livro:

**Opção A — Blog: adicionar sistema de bookmarks/favoritos nos posts**
```
Atua como arquiteto sénior Django. O projeto tem uma app `blog` com o modelo Post (título, corpo, autor, status, slug, publish).

Quero adicionar a funcionalidade de um utilizador poder guardar posts como favoritos (bookmark), com:
- Relação M2M entre User e Post
- View para toggle de favorito (AJAX)
- Listagem de posts favoritos do utilizador
- Contador de favoritos por post

Cria um plano detalhado com:
1. Alterações ao modelo (nova tabela ou campo M2M em Post?)
2. Migração necessária
3. Views necessárias (function-based ou class-based? Porquê?)
4. URLs a adicionar
5. Template changes
6. Trade-offs e riscos
7. Passos de implementação ordenados
```

**Opção B — Shop: adicionar histórico de preços dos produtos**
```
Atua como arquiteto sénior Django. O projeto tem uma app `shop` 
com o modelo Product (name, slug, image, description, price, available).

Quero registar o histórico de alterações de preço de cada produto, com:
- Novo modelo PriceHistory com FK para Product, preço, data
- Signal para registar automaticamente quando o preço muda
- View no admin para ver o histórico
- API endpoint simples para consultar o histórico

Cria o plano completo com trade-offs.
```

### Exercício 2.2 — Gerar regras `.mdc` específicas

```
Com base neste plano, gera um ficheiro feature.mdc para o Cursor que force as boas práticas Django nesta  implementação:
- Quando usar select_related vs prefetch_related nas views
- Padrão de resposta para views AJAX (JsonResponse format)
- Como estruturar signals Django neste projeto
- Regras de naming para URLs, views e templates desta feature
- O que nunca fazer (ex: lógica de negócio nos templates)
```

### Exercício 2.3 — Plan Mode no Cursor

No **Composer** (Ctrl/Cmd + Shift + I):

1. Ativa **Plan Mode** (Shift + Tab).
2. Cola o plano:

```
@PLAN_bookmarks.md

Em Plan Mode:
Analisa o plano e cria apenas a estrutura para o Passo 1:
- Alteração ao models.py da app blog
- Ficheiro de migração

Não implementes as views ainda.
Respeita as convenções Django em .cursor/rules/
Mostra o plano de execução antes de editar qualquer ficheiro.
```

3. Revê o plano antes de aprovar.

**Resultado esperado ao fim do Dia 2:**
- Feature planeada com contratos claros
- Regras `.mdc` específicas criadas
- Migração e model gerados pelo Cursor com consistência

---

## Dia 3 — Refatoração Global com Agent Mode {#dia-3}

**Objetivo:** Executar mudanças estruturais em múltiplos ficheiros de forma consistente.

### Preparação obrigatória — Git primeiro

```bash
git add -A
git commit -m "chore: snapshot antes de refatoração agentic"
git checkout -b refactor/[nome-da-tarefa]
git checkout -b refactor/refactor_all
```

### Exercício 3.1 — Padronizar views para Class-Based Views

O projeto do livro mistura function-based e class-based views. Este é um exercício de refatoração real:

No **Composer em Agent Mode**:

```
@blog/views.py @blog/urls.py

Refatora as function-based views do blog para class-based views onde faz sentido:
- PostListView (já existe) — verifica se está completa
- PostDetailView — converte a view de detalhe
- PostSearchView — converte a view de pesquisa
- Mantém EXATAMENTE o mesmo comportamento — não alteres a lógica
- Atualiza as urls.py para usar .as_view()
- Não convertes views AJAX — essas ficam como function-based

Após cada conversão, verifica que o servidor não dá erros com:
python manage.py check
```

### Exercício 3.2 — Adicionar select_related onde falta

Um problema comum no projeto do livro são as queries N+1. Refatora:

```
@Codebase

Identifica todas as views que fazem queries com ForeignKey ou M2M sem usar select_related ou prefetch_related.

Para cada caso encontrado:
1. Mostra a query atual
2. Explica o problema (quantas queries adicionais gera)
3. Aplica a correção com select_related ou prefetch_related conforme adequado

Começa pelas apps blog e shop que têm mais views de listagem.
```

### Exercício 3.3 — Loop de erros Django

Após cada mudança, corre:

```bash
python manage.py check
python manage.py test
flake8 . --max-line-length=120
```

Se houver erros, copia o output completo para o Cursor:

```
Após a refatoração das views, tenho estes erros:

[cola o output do terminal]

Corrige todos os erros. 
Não alteres a lógica de negócio — apenas corrige os problemas estruturais.
```

### Exercício 3.4 — Rever o diff com o Claude

```bash
git diff main...HEAD > diff_refactor.txt
```

```git 
Revê este diff de uma refatoração Django que fiz com o Cursor.

[cola o conteúdo]

Diz-me:
1. Alguma view perdeu funcionalidade após a conversão para CBV?
2. Os mixins estão a ser usados corretamente?
3. As permissões (login_required, etc.) estão aplicadas?
4. Há algum caso edge nos templates que possa quebrar?
```

**Resultado esperado ao fim do Dia 3:**
- Views padronizadas com CBV onde faz sentido
- Queries N+1 eliminadas nas principais listagens
- Zero regressões verificadas pelo Claude

---

## Dia 4 — Revisão Sénior e Loop de Feedback {#dia-4}

**Objetivo:** Usar o Claude como revisor de alto nível.

### Exercício 4.1 — Revisão profunda de um módulo

Escolhe a app `orders` (a mais complexa do livro) e pede ao Claude:

```
Atua como revisor sénior Django. Vou partilhar a app orders do projeto Django 2 By Example.

Faz uma revisão profunda com foco em:
1. Performance — há queries lentas? O processo de checkout é eficiente?
2. Segurança — validação de dados do formulário de encomenda, exposição de dados?
3. Design — as responsabilidades estão bem separadas entre models/views/forms?
4. Celery — a task de envio de email está bem implementada?
5. Technical debt — o que causará problemas se o volume de encomendas crescer?

Para cada problema: severidade (crítico/importante/cosmético) + solução concreta.

[Cola models.py, views.py, forms.py, tasks.py da app orders]
```

### Exercício 4.2 — Loop de erros por tipo

| Tipo de erro | Onde resolver | Como |
|---|---|---|
| `SyntaxError` / `IndentationError` | Cursor | "Corrige este erro de sintaxe: [cola]" |
| `ImportError` / `ModuleNotFoundError` | Cursor | "Resolve este import em todos os ficheiros afetados" |
| `django.core.exceptions` | Claude primeiro | "Este erro Django significa o quê? Como corrijo?" |
| Query incorreta / resultado errado | Claude primeiro | "Esta query não retorna o esperado — onde está a falha?" |
| Migração com conflito | Claude primeiro | "Como resolvo este conflito de migrações Django?" |
| Template tag a falhar | Cursor | "Corrige este erro no template tag: [cola]" |

### Exercício 4.3 — Debugging de problemas Django complexos

Para problemas difíceis, usa este prompt no Claude:

```
Tenho um problema no projeto Django 2 By Example.

App afetada: [nome da app]
Comportamento esperado: [descreve]
Comportamento atual: [descreve]
Erro no terminal: [cola o traceback completo]

Código relevante:
[cola apenas os ficheiros relevantes: model, view, form, url]

Raciocina passo-a-passo sobre cada possível causa antes de sugerir 
a correção. Considera as particularidades do Django 2 (não Django 3+).
```

**Nota Django 2 específica:** O Claude conhece bem as diferenças entre Django 2 e versões mais recentes. Quando pedires ajuda, menciona sempre "Django 2" para evitar sugestões de `path()` com sintaxe mais nova ou outras features que não existem nesta versão.

---

## Dia 5 — Workflow Completo e Git {#dia-5}

**Objetivo:** Executar o ciclo completo de forma fluida.

### Fluxo de trabalho Django (V4)

```
1. IDEIA / MELHORIA
   └─→ Claude: plano + migrações necessárias + trade-offs

2. SETUP
   └─→ git commit (snapshot)
   └─→ Atualiza .cursor/rules/ se necessário
   └─→ Plan Mode ativo no Cursor

3. IMPLEMENTAÇÃO (por esta ordem em Django)
   └─→ Models → Migração → Forms → Views → URLs → Templates

4. VALIDAÇÃO
   └─→ python manage.py check
   └─→ python manage.py test
   └─→ flake8 .
   └─→ Testa manualmente no browser (python manage.py runserver)

5. REVISÃO
   └─→ git diff → Claude revê
   └─→ Cursor aplica correções menores

6. COMMIT
   └─→ git add -A && git commit -m "feat: [descrição]"
```

### Ciclo prático por tipo de tarefa Django

**Nova feature (ex: comentários no blog):**
```
Claude planeia modelo + views + forms → .mdc atualizado 
→ Cursor cria modelo e migração → Cursor cria forms e views 
→ Cursor atualiza URLs e templates → testes passam → Claude revê diff → commit
```

**Bug de query Django:**
```
Claude identifica se é N+1, query errada ou problema de ORM 
→ Cursor aplica correção com select_related/prefetch_related 
→ verifica com python manage.py shell → teste unitário criado → commit
```

**Migração complexa (ex: mudar tipo de campo):**
```
Claude cria estratégia segura em 2 fases (adicionar novo campo → migrar dados → remover antigo) 
→ Cursor implementa fase 1 → testa em dev → fase 2 → testa → fase 3
```

**Adicionar nova app ao projeto:**
```
Claude define responsabilidades e relações com apps existentes 
→ Cursor cria estrutura com django-admin startapp 
→ Cursor cria models, views, urls conforme o plano → regista em INSTALLED_APPS
```

### Convenção Git para trabalho agentic Django

```bash
# Antes de sessão agentic
git stash
git checkout -b feat/[nome-da-feature]

# Commits atómicos por camada Django
git add blog/models.py && git commit -m "feat(blog): add Bookmark model with M2M to Post"
git add blog/migrations/ && git commit -m "feat(blog): migration for Bookmark model"
git add blog/views.py && git commit -m "feat(blog): add toggle_bookmark AJAX view"
git add blog/urls.py blog/templates/ && git commit -m "feat(blog): add bookmark URLs and templates"

# Se o Cursor destruir migrações (acontece!)
git checkout -- blog/migrations/    # reverte apenas as migrações
python manage.py migrate            # recria estado limpo

# Nunca fazer reset a migrações após aplicadas em BD
# Se precisares, usa: python manage.py migrate blog 0005  (volta à migração anterior)
```

---

## Templates `.mdc` para Django {#templates-mdc}

### `core.mdc` — Global

```markdown
---
description: Regras globais do projeto Django 2 By Example
globs: **/*
alwaysApply: true
---

## Stack
- Python 3.6+
- Django 2.x (NÃO usar features do Django 3+)
- Base de dados: SQLite (dev) / PostgreSQL (prod)
- Cache: Redis (via django-redis)
- Tasks assíncronas: Celery com Redis como broker
- Pagamentos: Braintree
- Tags: django-taggit
- Testes: Django TestCase (ou pytest-django)

## Estrutura de apps
- `blog` — aplicação de blog com posts, comentários, tags, RSS
- `account` — autenticação, perfil de utilizador, follows
- `images` — bookmarking de imagens, AJAX likes
- `actions` — sistema de activity stream
- `shop` — catálogo de produtos, carrinho de compras
- `orders` — processamento de encomendas, email via Celery
- `payment` — integração Braintree
- `coupons` — sistema de cupões de desconto
- `courses` — plataforma e-learning, conteúdos por módulos
- `students` — inscrições em cursos

## Comandos essenciais
- Dev server: `python manage.py runserver`
- Migrações: `python manage.py makemigrations && python manage.py migrate`
- Testes: `python manage.py test` ou `pytest`
- Check: `python manage.py check`
- Shell: `python manage.py shell`
- Lint: `flake8 . --max-line-length=120`
- Celery worker: `celery -A [projeto] worker -l info`

## Convenções de código
- Views simples → function-based; views com herança/mixins → class-based
- Forms sempre em `forms.py` separado, nunca inline nas views
- Lógica de negócio nos models ou services, nunca nos templates
- URLs com nomes (name='...') sempre — nunca URLs hardcoded nos templates
- Usar `{% url 'nome' %}` nos templates, nunca strings diretas
- Modelos com `__str__` sempre definido
- `get_absolute_url()` em todos os modelos com página de detalhe

## Proibições absolutas
- Nunca lógica de negócio nos templates Django
- Nunca queries na camada de template (via property que faz query)
- Nunca usar features do Django 3+ (path converters avançados, etc.)
- Nunca hardcoded IDs ou PKs no código — usar sempre slugs ou lookups
- Nunca `SELECT *` implícito em queries com M2M sem prefetch
```

### `django_models.mdc` — Models e ORM

```markdown
---
description: Regras para models Django e queries ORM
globs: **/models.py
alwaysApply: false
---

## Estrutura obrigatória de models

```python
# CORRETO — estrutura completa
class Post(models.Model):
    # Campos
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'  # sempre definir related_name
    )
    
    # Managers personalizados primeiro
    objects = models.Manager()       # manager padrão sempre primeiro
    published = PublishedManager()   # manager personalizado depois
    
    class Meta:
        ordering = ('-publish',)
        verbose_name = 'post'
        verbose_name_plural = 'posts'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[...])
```

## Queries — obrigatório

```python
# ERRADO — N+1 query
posts = Post.published.all()
for post in posts:
    print(post.author.username)  # query por cada post!

# CORRETO — select_related para ForeignKey
posts = Post.published.select_related('author').all()

# CORRETO — prefetch_related para M2M e reverse FK
posts = Post.published.prefetch_related('tags').all()
posts = Post.published.prefetch_related('comments').all()

# CORRETO — ambos quando necessário
posts = Post.published.select_related('author').prefetch_related('tags')
```

## Signals — quando usar

```python
# Usar signals para lógica desacoplada entre apps
# Ficheiro: blog/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Post)
def post_published_notification(sender, instance, created, **kwargs):
    if instance.status == 'published' and not created:
        # notifica subscritores
        pass

# Registar em blog/apps.py:
class BlogConfig(AppConfig):
    def ready(self):
        import blog.signals
```

## Proibições
- Nunca `null=True` em campos CharField/TextField — usa `blank=True` e string vazia
- Nunca ForeignKey sem `on_delete` explícito
- Nunca `related_name` omitido em ForeignKey para o mesmo modelo
- Nunca queries dentro de propriedades de modelo (caching se necessário)
```

### `django_views.mdc` — Views

```markdown
---
description: Regras para views Django (function-based e class-based)
globs: **/views.py
alwaysApply: false
---

## Quando usar function-based vs class-based

```python
# Function-based: simples, AJAX, ações pontuais
@login_required
def toggle_bookmark(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        # lógica
        return JsonResponse({'status': 'ok'})
    return HttpResponseNotAllowed(['POST'])

# Class-based: listagens, detalhe, CRUD com herança
class PostListView(ListView):
    queryset = Post.published.select_related('author').prefetch_related('tags')
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
```

## Respostas AJAX — formato obrigatório

```python
# SEMPRE este formato para respostas AJAX
from django.http import JsonResponse

# Sucesso
return JsonResponse({'status': 'ok', 'data': {...}})

# Erro
return JsonResponse({'status': 'error', 'message': 'Descrição do erro'}, status=400)

# Verificar se é AJAX (Django 2)
if request.is_ajax():
    ...
```

## Paginação — padrão

```python
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def post_list(request):
    posts = Post.published.select_related('author')
    paginator = Paginator(posts, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts})
```

## Proibições
- Nunca lógica de negócio diretamente nas views — delegar para models ou services
- Nunca queries sem select_related/prefetch_related em listagens
- Nunca retornar 200 para erros em respostas AJAX
- Nunca acesso direto a `request.POST` sem validação de form
```

### `django_testing.mdc` — Testes

```markdown
---
description: Regras para testes Django
globs: **/tests*.py
alwaysApply: false
---

## Estrutura obrigatória

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post

class PostModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Dados que não mudam entre testes — mais eficiente
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=cls.user,
            body='Test body content',
            status='published'
        )
    
    def test_post_str(self):
        self.assertEqual(str(self.post), 'Test Post')
    
    def test_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertIn('test-post', url)


class PostViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user', password='pass')
        self.post = Post.objects.create(
            title='Test', slug='test', author=self.user,
            body='Body', status='published'
        )
    
    def test_post_list_view(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test')
        self.assertTemplateUsed(response, 'blog/post/list.html')
    
    def test_post_list_requires_published_status(self):
        draft = Post.objects.create(
            title='Draft', slug='draft', author=self.user,
            body='Draft body', status='draft'
        )
        response = self.client.get(reverse('blog:post_list'))
        self.assertNotContains(response, 'Draft')
```

## O que sempre testar em Django
- `__str__` de todos os models
- `get_absolute_url()` de todos os models com página
- Status codes das views principais (200, 302, 404)
- Views que requerem login → redireccionam se não autenticado
- Forms válidos → guardam corretamente
- Forms inválidos → não guardam e mostram erros
- Managers personalizados → filtram corretamente

## Fixtures vs setUpTestData
- `setUpTestData` para dados de leitura (mais rápido — cria uma vez por classe)
- `setUp` para dados que os testes modificam (recria antes de cada teste)
- Fixtures apenas para dados muito complexos — prefere criar programaticamente

## Proibições
- Nunca testes que dependem de ordem de execução
- Nunca aceder à BD de produção nos testes
- Nunca `time.sleep()` em testes — usa mock para Celery tasks
```

---

## Gestão de Contexto e Tokens {#gestao-contexto}

### Quanto código Django enviar ao Claude de uma vez

| Situação | O que enviar |
|---|---|
| Planear nova feature | Apenas o `models.py` relevante + descrição em texto |
| Debug de view | A view + o form + o template (se relevante) |
| Problema de query | A query + o modelo com as suas relações |
| Revisão de app completa | `models.py` + `views.py` + `forms.py` (sem templates) |
| Problema de migração | O ficheiro de migração + o modelo atual |
| Celery task a falhar | A task + o traceback completo |

**Regra Django específica:** Os `templates/` raramente precisam de ir ao Claude — são a camada menos crítica. Foca o contexto em models, views e forms.

### Como estruturar prompts para Django

```
[CONTEXTO — o que é a app]
App `orders` do Django 2 By Example — gere encomendas de uma loja online.
Modelos: Order, OrderItem. Integração com Celery para envio de emails.

[PROBLEMA — específico]
A task `order_created` do Celery não está a enviar o email quando 
uma encomenda é criada. O worker está a correr e não há erros no log.

[CÓDIGO — apenas o necessário]
# tasks.py
[cola apenas a task em questão]

# views.py — apenas a view que cria a encomenda
[cola apenas essa view]

[PERGUNTA — uma só]
Qual é a causa mais provável e como depuro este problema?
```

### Gerir sessões longas com Django

Quando uma sessão longa perde contexto, usa este resumo:

```
Nova sessão — contexto do projeto:
- Projeto: Django 2 By Example (Antonio Melé)
- Apps ativas: blog, account, images, shop, orders, payment
- Django 2.x, Python 3.6+, SQLite (dev), Redis, Celery
- Regras ativas: [cola o core.mdc]
- O que já fiz hoje: [descreve as mudanças]
- Tarefa atual: [descreve onde estás]
```

---

## Estratégia de Testes {#estrategia-testes}

### Quem gera os testes e quando

**Antes de implementar (TDD) — usa Claude:**

```
Vou implementar a funcionalidade de "posts relacionados" no blog.
A lógica: dado um post, encontrar os 4 posts com mais tags em comum.

Antes de implementar, gera os testes Django (TestCase) para esta função:
- Teste com post sem tags — deve retornar lista vazia ou posts aleatórios?
- Teste com tags em comum — verifica ordenação por número de tags partilhadas
- Teste com posts sem publicar — não devem aparecer nos relacionados
- Teste de performance — não deve fazer mais de 2 queries

Usa Django TestCase com setUpTestData.
```

**Depois de implementar — usa Cursor:**

```
@blog/views.py @blog/models.py

Gera testes Django completos para todos os models e views nestes ficheiros:
- Testa __str__ e get_absolute_url de cada model
- Testa status codes de cada view (200, 302, 404 conforme apropriado)
- Testa views com login_required — verifica redireccionar se não autenticado
- Testa o manager PublishedManager — só retorna posts published
- Usa setUpTestData para dados partilhados
```

### Loop de testes no workflow Django

```bash
# Corre apenas os testes da app que estás a modificar
python manage.py test blog
python manage.py test shop.tests.TestOrderView

# Com verbosidade para ver o que passa/falha
python manage.py test blog -v 2

# Para ver o tempo de cada teste (identificar testes lentos)
python manage.py test blog --timing
```

Se os testes falharem após uma mudança do Cursor:

```
Após a refatoração, estes testes Django falharam:

[cola o output com FAIL e o traceback]

Código atual:
[cola o ficheiro relevante]

Há uma regressão lógica? Ou o teste precisa de ser atualizado 
porque o comportamento mudou intencionalmente?
Explica antes de propor a correção.
```

---

## Projetos Legados — Django 2 Especificamente {#projetos-legados}

### Compatibilidade Django 2 — o que o Claude pode confundir

O Claude conhece bem Django mas pode sugerir patterns de Django 3+ sem querer. Previne com este aviso nos prompts:

```
IMPORTANTE: Este projeto usa Django 2.x. NÃO uses:
- path converters do tipo <int:pk> com sintaxe nova (verifica compatibilidade)
- DATABASES['default']['OPTIONS'] com opções do Django 3+
- django.utils.timezone.now() em vez de datetime.now() (verifica o contexto)
- AsyncToSync ou qualquer feature assíncrona
- Novos lookups de ORM introduzidos após Django 2.2
```

### Migrações Django 2 — cuidados especiais

Migrações são a área de maior risco em projetos Django legados:

```bash
# Antes de qualquer mudança em models.py
git add -A && git commit -m "chore: snapshot antes de alterar models"

# Após alterar models.py
python manage.py makemigrations [nome_da_app]

# SEMPRE verificar o ficheiro de migração gerado antes de aplicar
# Abre o ficheiro em migrations/000X_auto_...py e lê o que vai fazer

# Apenas depois de confirmar:
python manage.py migrate

# Se a migração correr mal
python manage.py migrate [app] [numero_migracao_anterior]
# Ex: python manage.py migrate blog 0005
```

**Prompt para ajuda com migrações:**

```
Vou alterar o modelo Post no Django 2 para adicionar um campo `updated`.

Modelo atual:
[cola o modelo]

Mudança desejada: adicionar `updated = models.DateTimeField(auto_now=True)`

Qual é o risco desta migração? Há dados existentes que podem ser afetados?
Preciso de uma migração de dados (data migration) ou é seguro fazer direto?
```

### Atualização gradual de Django 2 para versões mais recentes

Se no futuro quiseres atualizar o projeto do livro para Django 3+:

```
Atua como especialista em migrações Django.

Tenho o projeto Django 2 By Example e quero fazer um upgrade gradual 
para Django 3.2 LTS (não saltar direto para versões mais recentes).

Diz-me:
1. Que deprecations do Django 2 tenho de corrigir primeiro?
2. Que mudanças de breaking change existem de 2.x para 3.2?
3. Qual a ordem segura para fazer o upgrade?
4. Como testo que nada quebrou em cada passo?

Foca nos projetos do livro: blog, bookmarks, shop, e-learning.
```

---

## Claude fora do Cursor {#claude-fora-cursor}

### Quando usar claude.ai para o projeto Django

| Tarefa | Porquê fora do Cursor |
|---|---|
| Desenhar a arquitetura de uma nova app | Conversa exploratória sem código |
| Analisar requisitos do livro e planear melhorias | Upload do capítulo em PDF |
| Comparar abordagens (CBV vs FBV, signals vs override save) | Discussão conceptual |
| Gerar documentação da API REST (app courses) | Texto longo sem código |
| Entender um conceito Django que não está claro | Explicação sem pressão de implementar |

**Exemplo — analisar um capítulo do livro:**

```
[Anexa o PDF do capítulo ou cola o texto]

Acabei de ler este capítulo sobre o sistema de pagamentos com Braintree.

Diz-me:
1. O que o livro não explica mas é importante saber sobre esta integração?
2. Que problemas de segurança existem na implementação apresentada?
3. Como modernizarias esta abordagem mantendo Django 2?
4. Que testes de integração devo escrever para o fluxo de pagamento?
```

### Quando usar o terminal com Claude Code

```bash
# Instalar Claude Code
pip install claude-code   # ou via npm

# Tarefas úteis para o projeto do livro
claude "Analisa os ficheiros de migração do projeto e diz-me se há alguma inconsistência"
claude "Corre os testes e explica os que falharam em linguagem simples"
claude "Lista todas as views que não têm testes escritos"
claude "Gera um relatório de todas as queries N+1 potenciais no projeto"
```

---

## Prompts de Ponte — Tabela Completa {#prompts-ponte}

### Estrutura recomendada para prompts Django

```
[ROLE] + [VERSÃO DJANGO] + [APP AFETADA] + [SPECS] + [CONSTRAINTS] + [OUTPUT]
```

**Exemplo:**
```
Atua como arquiteto sénior Django.
Projeto: Django 2.x, app `blog` do livro Django 2 By Example.

Preciso adicionar um sistema de newsletters onde utilizadores se subscrevem 
e recebem um email quando um novo post é publicado.

Constraints:
- Usar Celery (já configurado no projeto)
- Não usar bibliotecas externas de email marketing
- Compatível com Django 2 — sem features do Django 3+
- Manter a estrutura de apps do livro

Output: plano com modelos, signals, tasks Celery e views necessárias.
```

### Tabela de prompts por situação Django

| Situação | Claude (Estratégia) | Cursor (Execução) |
|---|---|---|
| **Nova app Django** | "Define a estrutura da app, modelos, relações com apps existentes e trade-offs. Django 2." | "Em Plan Mode: Cria a estrutura da app [nome] com models.py, views.py, urls.py, admin.py conforme @PLAN.md" |
| **Novo modelo** | "Que campos, relações e Meta preciso? Há risco de migração de dados existentes?" | "Adiciona o modelo ao models.py da app [X] e cria a migração. Não apliques ainda." |
| **View com bug** | "Analisa este traceback + view. Qual é a causa conceptual? Considera Django 2." | "Aplica a correção. Adiciona um teste que reproduz o bug antes e passa depois." |
| **Otimização de queries** | "Identifica os N+1 nesta view e qual a melhor estratégia: select_related ou prefetch_related?" | "Aplica select_related/prefetch_related conforme sugerido. Mantém o comportamento." |
| **Nova migração** | "Que risco tem esta alteração ao modelo? Preciso de data migration?" | "Cria a migração para [mudança]. Não apliques. Mostra o ficheiro gerado." |
| **Task Celery** | "Esta task está correta? Há risco de duplicação se correr duas vezes?" | "Cria a task em tasks.py e adiciona o signal/view que a dispara." |
| **Formulário Django** | "Que validação falta neste form? Há dados que devem ser sanitizados?" | "Adiciona as validações sugeridas ao forms.py. Inclui testes para inputs inválidos." |
| **Admin Django** | "Como devo configurar o admin para esta app? Que list_display, filters e actions fazem sentido?" | "Configura o admin.py conforme o plano. Usa list_select_related para evitar N+1 no admin." |

---

## Troubleshooting — Problemas Frequentes {#troubleshooting}

### Problemas Django específicos

| Problema | Causa provável | Solução |
|---|---|---|
| **`No module named 'X'`** | Package não instalado ou venv errado | `pip install X` e verifica que o venv está ativo |
| **`django.db.utils.OperationalError: no such table`** | Migração não aplicada | `python manage.py migrate` |
| **`django.db.migrations.exceptions.InconsistentMigrationHistory`** | Migrações fora de ordem | Pede ao Claude a estratégia de resolução com o histórico |
| **Migração gerada mas parece errada** | Model incompleto ou campo mal definido | Revê o model antes de aplicar. Usa `python manage.py sqlmigrate app 000X` para ver o SQL |
| **Template tag não encontrado** | `{% load %}` em falta ou tag não registada | Verifica `templatetags/` e o `{% load nome_do_modulo %}` no template |
| **View retorna 403** | `@login_required` ou permissão em falta | Verifica decoradores e `LoginRequiredMixin` |
| **Celery task não executa** | Worker parado ou broker não configurado | `celery -A [projeto] worker -l info` e verifica CELERY_BROKER_URL |
| **Admin não mostra os dados esperados** | Manager personalizado aplicado no admin | O admin usa o manager `objects` por padrão — verifica `get_queryset` |
| **`RelatedObjectDoesNotExist`** | FK para objeto que não existe | Usa `select_related` e `get_object_or_404` nas views |
| **Formulário sempre inválido** | Token CSRF em falta no template | Adiciona `{% csrf_token %}` dentro do `<form>` |

### Problemas com o Cursor no contexto Django

| Problema | Causa provável | Solução |
|---|---|---|
| **Cursor gera Django 3+ syntax** | Não conhece a versão | Adiciona ao prompt: "Django 2.x — não usar features do Django 3+" |
| **Cursor cria migração e aplica automaticamente** | Agent Mode sem restrição | Especifica: "Cria a migração mas NÃO a apliques" |
| **Cursor ignora a estrutura de apps** | Contexto insuficiente | Usa `@Codebase` ou `@[app]/` para dar contexto da estrutura |
| **Cursor coloca lógica nos templates** | Regras `.mdc` insuficientes | Adiciona ao `django.mdc`: "Nunca colocar lógica de negócio em templates" |
| **Regras `.mdc` ignoradas** | Frontmatter inválido | Verifica se os `---` de abertura e fecho estão corretos |

### Problemas gerais do workflow

| Problema | Causa provável | Solução |
|---|---|---|
| **Cursor falha 2x na mesma task Django** | Plano vago ou contexto em falta | Para. Volta ao Claude com o erro específico e o código relevante |
| **Claude sugere solução incompatível com Django 2** | Não mencionaste a versão | Sempre inclui "Django 2.x" e "sem features do Django 3+" nos prompts |
| **Refatoração criou migrations inconsistentes** | Agent Mode alterou models sem estratégia | `git reset` nas migrations. Planeia a migração com Claude antes de refatorar |

---

## Critérios de Decisão {#criterios-decisao}

### Qual modelo usar

| Tarefa Django | Modelo recomendado |
|---|---|
| Implementar view simples, form, template | `claude-sonnet-4-5` |
| Arquitetura de nova app com relações complexas | `claude-opus-4-5` |
| Debug de bug difícil (N+1, migração, Celery) | `claude-sonnet-4-5` (rápido) |
| Estratégia de migração Django 2 → 3 | `claude-opus-4-5` |
| Revisão de segurança (views de pagamento) | `claude-opus-4-5` |
| Gerar testes unitários | `claude-sonnet-4-5` |

### Quando usar Agent Mode vs Plan Mode em Django

| Usa Agent Mode quando... | Usa Plan Mode quando... |
|---|---|
| Refatoração de views em múltiplos ficheiros | Criar nova app com estrutura definida |
| Adicionar select_related a todas as listagens | Implementar nova feature passo a passo |
| Padronizar admin.py de todas as apps | Criar modelo com relações complexas |
| Atualizar imports após rename de módulo | Migração com risco de perda de dados |

### Ordem certa para implementar em Django

Nunca deixes o Cursor saltar etapas nesta ordem:

```
1. Models (e relações)
2. Migrações (makemigrations — VERIFICA antes de migrate)
3. Forms (validação antes das views)
4. Views (usa os forms criados)
5. URLs (regista as views)
6. Templates (última camada — mais fácil de corrigir)
7. Admin (opcional mas útil para testar)
8. Testes (idealmente escritos antes das views)
```

---

## Indicadores de Evolução {#indicadores}

### Semana 1 — Básico funcional

- [ ] Cursor indexado e a responder correctamente sobre as apps do livro
- [ ] `core.mdc` e `django.mdc` criados com regras reais
- [ ] Primeiro plano gerado pelo Claude para uma melhoria real do projeto
- [ ] Plan Mode usado pelo menos uma vez para criar um modelo e migração
- [ ] Loop `manage.py check` + `test` + `flake8` integrado no workflow

### Semana 2 — Fluidez operacional

- [ ] Escreves menos de 30% do código Django manualmente
- [ ] Regras `.mdc` específicas para pelo menos 2 apps
- [ ] Git com commits atómicos por camada (model → migration → view → url → template)
- [ ] Consegues classificar erros Django (ORM → Claude, sintaxe → Cursor)
- [ ] Pelo menos uma refatoração de views com Agent Mode

### Semana 3 — Eficiência avançada

- [ ] Menos de 10–15% do código escrito manualmente
- [ ] Taxa de sucesso no primeiro try > 70%
- [ ] Testes escritos antes ou durante a implementação (não depois)
- [ ] Ciclo completo (model → migration → view → test) em < 1 hora para features simples
- [ ] Claude usado para rever diffs de todas as migrações antes de aplicar

### Sinais de que algo está errado

- Estás a editar muitos templates manualmente → normal, templates são mais rápidos à mão
- O Cursor cria migrações e aplica automaticamente → adiciona "NÃO apliques a migração" ao prompt
- O Claude sugere Django 3+ syntax → adiciona "Django 2.x" ao início de todos os prompts
- As sessions Django perdem dados → provavelmente problema de configuração, não de código — pede ao Claude para rever o `settings.py`

---

## Regra Final

> Se o Cursor gera código Django 3+ num projeto Django 2, **o problema é o teu prompt** — não mencionaste a versão.
>
> Se o Cursor cria migrações incorretas, **o problema está no model** que não estava bem definido — volta ao Claude antes de gerar migrações.
>
> Se estás a editar manualmente muitas views parecidas, **estás a subutilizar o Agent Mode** — diz ao Cursor para aplicar o padrão a todas as views de uma vez.

---

*Plano V4 Django Edition — Claude Pro + Cursor Pro*
*Adaptado especificamente para Django 2 By Example (Antonio Melé)*
*Baseado no V4 original com templates .mdc Django, exemplos das 4 apps do livro,*
*gestão de migrações, compatibilidade Django 2, e troubleshooting específico.*
