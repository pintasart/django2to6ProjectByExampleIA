from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views import View
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count # Count aggregation function
#from django.contrib.postgres.search import SearchVector # pesquisa
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm
# Create your views here.

class PostListView(View):
    def get(self, request, tag_slug=None):
        object_list = Post.published.select_related('author').prefetch_related('tags')
        tag = None
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            object_list = object_list.filter(tags__in=[tag])

        paginator = Paginator(object_list, 3)  # 3 posts in each page
        page = request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            posts = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            posts = paginator.page(paginator.num_pages)

        return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})






class PostDetailView(View):
    def get_post(self, year, month, day, post):
        return get_object_or_404(
            Post.objects.select_related('author'),
            slug=post,
            status='published',
            publish__year=year,
            publish__month=month,
            publish__day=day,
        )

    def get_context_data(self, post, comment_form, new_comment=None):
        # List of active comments for this post
        comments = post.comments.filter(active=True)

        # List of similar posts
        #retrieve a Python list of IDs for the tags of the current post
        post_tags_ids = post.tags.values_list('id', flat=True)
        #excluding the current post itself
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        # contains the number of tags shared with all the tags queried
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

        return {
            'post': post,
            'comments': comments,
            'new_comment': new_comment,
            'comment_form': comment_form,
            'similar_posts': similar_posts,
        }

    def get(self, request, year, month, day, post):
        post_obj = self.get_post(year, month, day, post)
        comment_form = CommentForm()
        context = self.get_context_data(post_obj, comment_form)
        return render(request, 'blog/post/detail.html', context)

    def post(self, request, year, month, day, post):
        post_obj = self.get_post(year, month, day, post)
        new_comment = None
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post_obj
            # Save the comment to the database
            new_comment.save()
        context = self.get_context_data(post_obj, comment_form, new_comment)
        return render(request, 'blog/post/detail.html', context)






def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                                          post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    
    return render(request, 'blog/post/share.html', {'post': post, 'form': form,'sent': sent})



class PostSearchView(View):
    def get(self, request):
        form = SearchForm()
        query = None
        results = []
        if 'query' in request.GET:
            form = SearchForm(request.GET)
            if form.is_valid():
                query = form.cleaned_data['query']
                results = Post.objects.annotate(
                    similarity=TrigramSimilarity('title', query),
                ).filter(similarity__gt=0.3).order_by('-similarity')
        return render(
            request,
            'blog/post/search.html',
            {
                'form': form,
                'query': query,
                'results': results,
            },
        )
