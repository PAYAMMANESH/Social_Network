from django.contrib import admin
from .models import Post, Comment, Vote


# Register your models here.

# @admin.register(Post)
class PostAdmin(admin.ModelAdmin):  # for change admin panel
    list_display = ('user', 'slug', 'updated')  # for each Post in admin panel show usr slug updated
    search_fields = ('slug',)  # in admin panel search with slug
    list_filter = ('updated',)  # filter post in admin panel with updated
    prepopulated_fields = {'slug': ('body',)}  # auto fill slug
    raw_id_fields = ('user',)  # use id instead of username when you want to create new post


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created', 'is_reply')
    raw_id_fields = ('user', 'post', 'reply')


admin.site.register(Post, PostAdmin)
admin.site.register(Vote)
