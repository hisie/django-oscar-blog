from django.contrib.sitemaps import Sitemap

from oscar_blog.models import Post


class PostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Post.objects.published()

    def lastmod(self, post):
        return post.date_updated
