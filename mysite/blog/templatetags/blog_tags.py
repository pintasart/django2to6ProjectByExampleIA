from django import template
from ..models import Post
from django.db.models import Count

#custom template filters
from django.utils.safestring import mark_safe
import markdown





register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()


#register the template tag using @register.inclusion_tag and specify the template that has to be rendered
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}



@register.simple_tag
def get_most_commented_posts(count=5):
    #annotate() function to aggregate the total number of comments for each post
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]



@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))