from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
# after create model we should register it in admin.py

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='posts')  # each user have many post but each post just for one user
    # اگر خواستیم از روی پست کاربر ار بدست بیاریم که کار خاصی نیار نیست بکنیم ولی اگر از روی کاربر خواستیم پست ها رو بگیریم کافی است که :
    # user.related name(posts).all استفاده کنیم
    body = models.TextField()
    slug = models.SlugField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:  # its work like order_by but every time that use this models this class run and show data by order of created
        ordering = ('created',)

    def __str__(self):  # for show in admin pannel
        return self.slug

    def get_absolute_url(self):
        return reverse('home:post_detail', args=[self.id, self.slug])

    def likes_count(self):
        return self.pvote.count()

    def user_can_like(self, user):
        user_like = user.uvote.filter(post=self)
        if user_like.exists():
            return True
        return False


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ucomment')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pcomment')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='rcomment', blank=True,
                              null=True)  # use blank and null to set empty this field
    is_reply = models.BooleanField(default=False)
    body = models.TextField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.body[:30]}"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uvote')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pvote')

    def __str__(self):
        return f'{self.user} liked {self.post}'
