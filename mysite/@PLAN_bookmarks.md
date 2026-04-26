---
  Plano de Arquitectura — Bookmarks no Blog

  ---
  1. Alterações ao Modelo

  Decisão: modelo intermédio explícito Bookmark, não campo M2M directo em Post.

  # blog/models.py

  class Bookmark(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='bookmarks')
      post = models.ForeignKey(Post, on_delete=models.CASCADE,
                               related_name='bookmarked_by')
      created = models.DateTimeField(auto_now_add=True)

      class Meta:
          ordering = ['-created']
          constraints = [
              models.UniqueConstraint(fields=['user', 'post'],
                                      name='unique_bookmark')
          ]
      def __str__(self):
          return f'{self.user} → {self.post}'

  Porquê modelo intermédio e não Post.bookmarks = ManyToManyField(User)?

  ┌───────────────────────┬─────────────────────────┬───────────────────────────────────┐
  │       Critério        │       M2M directo       │          Modelo Bookmark          │
  ├───────────────────────┼─────────────────────────┼───────────────────────────────────┤
  │ created (quando       │ ✗ impossível sem        │ ✓ nativo                          │
  │ guardou)              │ through                 │                                   │
  ├───────────────────────┼─────────────────────────┼───────────────────────────────────┤
  │ Query "bookmarks      │ ✗ não ordenável por     │ ✓ order_by('-created')            │
  │ recentes"             │ data                    │                                   │
  ├───────────────────────┼─────────────────────────┼───────────────────────────────────┤
  │ Extensível (notas,    │ ✗ requer reescrita da   │ ✓ adiciona campos                 │
  │ tags)                 │ migração                │                                   │
  ├───────────────────────┼─────────────────────────┼───────────────────────────────────┤
  │ Coerência com o livro │ —                       │ ✓ segue padrão de bookmarks app   │
  │                       │                         │ do livro                          │
  ├───────────────────────┼─────────────────────────┼───────────────────────────────────┤
  │ Simplicidade imediata │ ✓ menos código          │ ligeiramente mais código          │
  └───────────────────────┴─────────────────────────┴───────────────────────────────────┘

  A única vantagem real do M2M directo é menos código inicial. Não justifica, porque
  Bookmark.created vai ser necessário logo na listagem ("guardado há 3 dias").

  O contador de favoritos por post é derivado via annotate, sem campo desnormalizado — segue
   exactamente o padrão que o livro usa para total_comments em get_most_commented_posts.

  ---
  2. Migração

  python manage.py makemigrations blog --name="add_bookmark_model"
  python manage.py migrate

  A migração cria a tabela blog_bookmark com unique_together (user, post) via
  UniqueConstraint. Não altera a tabela blog_post — zero risco de regressão.

  Risco mitigado: o UniqueConstraint ao nível da BD é a única garantia real contra duplos
  bookmarks em requests concorrentes. Não confiar apenas em lógica Python.

  ---
  3. Views

  Toggle: FBV. Listagem: CBV (LoginRequiredMixin + ListView). Porquê esta mistura?

  O toggle é uma operação com efeitos secundários (POST → lógica condicional →
  JsonResponse). Um CBV não simplifica isto — post() num View base é literalmente um FBV com
   overhead de classe. O livro usa FBV para todas as operações de acção (post_share,
  post_search); seguir a convenção.

  A listagem é exactamente o caso para o qual ListView existe: queryset + paginação +
  template. O livro já introduz ListView (está comentado em urls.py com PostListView). Usar
  aqui é consistente e elimina o boilerplate de Paginator manual.

  # blog/views.py (acrescentar)

  from django.contrib.auth.decorators import login_required
  from django.http import JsonResponse
  from django.views.generic import ListView
  from django.contrib.auth.mixins import LoginRequiredMixin
  from django.db.models import Count, Exists, OuterRef
  from .models import Post, Comment, Bookmark

  @login_required
  def post_bookmark(request, post_id):
      """Toggle bookmark. Devolve JSON: {bookmarked: bool, count: int}"""
      if request.method != 'POST':
          return JsonResponse({'error': 'method not allowed'}, status=405)

      post = get_object_or_404(Post, id=post_id, status='published')
      bookmark, created = Bookmark.objects.get_or_create(
          user=request.user, post=post
      )
      if not created:
          bookmark.delete()

      count = post.bookmarked_by.count()
      return JsonResponse({'bookmarked': created, 'count': count})


  class BookmarkedPostsView(LoginRequiredMixin, ListView):
      template_name = 'blog/post/bookmarks.html'
      context_object_name = 'bookmarks'
      paginate_by = 5

      def get_queryset(self):
          return (Bookmark.objects
                  .filter(user=self.request.user)
                  .select_related('post', 'post__author')
                  .order_by('-created'))

  Nota sobre get_or_create: é atómico ao nível da BD (usa SELECT + INSERT com constraint).
  Resolve a race condition de dois requests simultâneos do mesmo utilizador.

  select_related('post', 'post__author'): evita N+1 queries na listagem. O livro não
  menciona isto explicitamente, mas é crítico — sem ele, cada item da lista faz 2 queries
  adicionais.

  ---
  4. URLs a Adicionar

  # blog/urls.py (acrescentar a urlpatterns)

  path('<int:post_id>/bookmark/', views.post_bookmark, name='post_bookmark'),
  path('bookmarks/', views.BookmarkedPostsView.as_view(), name='post_bookmarks'),

  O post_bookmark usa post_id (inteiro) em vez do slug com data, porque é uma operação de
  acção — não uma URL pública/indexável. Segue o mesmo padrão de post_share já existente.

  ---
  5. Template Changes

  blog/post/detail.html — acrescentar antes dos "Similar posts":

  {% if request.user.is_authenticated %}
  <div id="bookmark-section">
      <button id="bookmark-btn"
              data-post-id="{{ post.id }}"
              data-bookmarked="{{ is_bookmarked|yesno:'true,false' }}">
          {% if is_bookmarked %}★ Guardado{% else %}☆ Guardar{% endif %}
      </button>
      <span id="bookmark-count">{{ bookmark_count }}</span> favorito{{
  bookmark_count|pluralize:"s" }}
  </div>

  <script>
  document.getElementById('bookmark-btn').addEventListener('click', function() {
      const btn = this;
      const postId = btn.dataset.postId;
      fetch("{% url 'blog:post_bookmark' post.id %}", {
          method: 'POST',
          headers: {
              'X-CSRFToken': '{{ csrf_token }}',
              'Content-Type': 'application/json',
          },
      })
      .then(r => r.json())
      .then(data => {
          btn.dataset.bookmarked = data.bookmarked;
          btn.textContent = data.bookmarked ? '★ Guardado' : '☆ Guardar';
          document.getElementById('bookmark-count').textContent = data.count;
      });
  });
  </script>
  {% endif %}

  O JS é inline e sem dependências externas — o mysite não tem jQuery nem nenhum bundler.
  Vanilla fetch é suficiente e é o padrão actual.

  blog/post/bookmarks.html — novo template:

  {% extends "blog/base.html" %}
  {% block title %}Os meus favoritos{% endblock %}
  {% block content %}
  <h1>Os meus favoritos</h1>
  {% for bookmark in bookmarks %}
      <h2><a href="{{ bookmark.post.get_absolute_url }}">{{ bookmark.post.title }}</a></h2>
      <p class="date">Guardado {{ bookmark.created }} · por {{ bookmark.post.author }}</p>
  {% empty %}
      <p>Ainda não guardaste nenhum post.</p>
  {% endfor %}
  {% include "pagination.html" with page=page_obj %}
  {% endblock %}

  views.py — actualizar post_detail para injectar is_bookmarked e bookmark_count:

  # Dentro de post_detail, acrescentar ao context:
  is_bookmarked = (request.user.is_authenticated and
                   Bookmark.objects.filter(user=request.user, post=post).exists())
  bookmark_count = post.bookmarked_by.count()

  blog_tags.py — sidebar "mais guardados" (opcional, segue padrão do
  get_most_commented_posts):

  @register.simple_tag
  def get_most_bookmarked_posts(count=5):
      return (Post.published
              .annotate(total_bookmarks=Count('bookmarked_by'))
              .order_by('-total_bookmarks')[:count])

  ---
  6. Trade-offs e Riscos

  Autenticação no mysite: o projecto não tem URLs de login configuradas (ao contrário do
  bookmarks). O @login_required vai redirigir para /accounts/login/ que não existe. É
  necessário adicionar ao mysite/urls.py:

  path('accounts/', include('django.contrib.auth.urls')),

  ...ou definir LOGIN_URL nos settings e criar o template registration/login.html.

  Contador em post_detail — 1 query extra: post.bookmarked_by.count() é uma query separada.
  Para um blog com pouco tráfego é aceitável. Se escalar, a alternativa é um campo
  desnormalizado bookmark_count em Post actualizado por signal — mas introduz complexidade
  de consistência que não vale para este projecto.

  is_bookmarked em post_list: se quiseres mostrar o estado de bookmark na listagem, seriam N
   queries (uma por post). Usar Exists(OuterRef) com annotate resolve em 1 query total:

  # Em post_list, se o utilizador estiver autenticado:
  object_list = object_list.annotate(
      is_bookmarked=Exists(
          Bookmark.objects.filter(user=request.user, post=OuterRef('pk'))
      )
  )

  Admin: registar Bookmark no admin para poder inspeccionar dados durante desenvolvimento.

  @admin.register(Bookmark)
  class BookmarkAdmin(admin.ModelAdmin):
      list_display = ('user', 'post', 'created')
      list_filter = ('created',)
      raw_id_fields = ('user', 'post')

  ---
  7. Passos de Implementação Ordenados

  1. models.py      — adicionar classe Bookmark
  2. admin.py       — registar BookmarkAdmin
  3. makemigrations + migrate
  4. views.py       — post_bookmark (FBV) + BookmarkedPostsView (CBV)
                      + actualizar post_detail para injectar is_bookmarked/bookmark_count
  5. urls.py        — 2 novas paths
  6. detail.html    — botão + JS AJAX
  7. bookmarks.html — novo template de listagem
  8. mysite/urls.py — adicionar django.contrib.auth.urls (se não existir)
  9. (opcional) blog_tags.py  — get_most_bookmarked_posts
  10.(opcional) list.html     — mostrar estado bookmark com annotate+Exists

  A ordem é crítica: migração antes das views (caso contrário, o servidor não arranca com a
  model importada), e o template de detalhe só depois de a view injectar o contexto.

  ---
  Resumo das decisões arquitecturais:

  ┌──────────────┬─────────────────────────────┬────────────────────────────────────────┐
  │   Decisão    │           Escolha           │            Razão principal             │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ Modelo       │ Bookmark intermédio         │ created + extensibilidade              │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ Contador     │ annotate em query           │ Consistente com padrão do livro        │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ Toggle view  │ FBV                         │ Convenção do projecto; CBV não         │
  │              │                             │ simplifica                             │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ Listagem     │ ListView CBV                │ Paginação + LoginRequiredMixin sem     │
  │ view         │                             │ boilerplate                            │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ AJAX         │ Vanilla fetch               │ Sem jQuery no projecto                 │
  ├──────────────┼─────────────────────────────┼────────────────────────────────────────┤
  │ Race         │ get_or_create +             │ Atomicidade na BD                      │
  │ condition    │ UniqueConstraint            │                                        │
  └──────────────┴─────────────────────────────┴────────────────────────────────────────┘

