from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post


class LatestPostsFeed(Feed):
    title = 'My blog'
    link = '/blog/'
    description = 'New posts of my blog.'
    
    #retrieves the objects to be included in the feed
    def items(self):
        return Post.published.all()[:5]
    #receive each object returned by items() and return the title 
    def item_title(self, item):
        return item.title
    #receive each object returned by items() and return the description for each item
    def item_description(self, item):
        return truncatewords(item.body, 30)