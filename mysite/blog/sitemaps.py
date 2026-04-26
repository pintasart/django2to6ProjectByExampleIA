from django.contrib.sitemaps import Sitemap
from .models import Post


#create a custom sitemap by inheriting the Sitemap class 
class PostSitemap(Sitemap):
    #changefreq and priority attributes indicate the change frequency of your post pages and their relevance in your website
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Post.published.all()
    
    #receives each object returned by items() and returns the last time the object was modified
    def lastmod(self, obj):
        return obj.updated