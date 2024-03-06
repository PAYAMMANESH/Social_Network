from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from .models import Post, Comment, Vote
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import PostCreateUpdateForm, CommentCreateForm, CommentReplyForms, SearchPostForm
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class HomeView(View):
    form_class = SearchPostForm

    def get(self, request):
        posts = Post.objects.all()
        # posts = Post.objects.order_by('created')   #show data by order that you want and if you use - before attribute that you want work reverse
        if request.GET.get('search'):
            posts = posts.filter(body__contains=request.GET['search'])
        return render(request, 'home/index.html', context={'posts': posts, 'form': self.form_class})


class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForms

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # post = Post.objects.get(pk=post_id, slug=post_slug)
        can_like = False
        if request.user.is_authenticated and self.post_instance.user_can_like(request.user):
            can_like = True
        comments = self.post_instance.pcomment.filter(post=self.post_instance, is_reply=False)
        return render(request, 'home/detail.html',
                      context={'post': self.post_instance, 'comments': comments, 'form': self.form_class,
                               'reply_form': self.form_class_reply, 'can_like': can_like})

    @method_decorator(login_required)  # this decorators limited this function just for login user
    def post(self, request, *args, **kwargs):
        post = self.form_class(request.POST)
        if post.is_valid():
            comment = post.save(commit=False)
            comment.user = request.user
            comment.post = self.post_instance
            comment.save()
            messages.success(request, "your comment added successfully", 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        # post = Post.objects.get(pk=post_id)
        post = get_object_or_404(Post, pk=post_id)
        if post.user.id == request.user.id:
            post.delete()
            messages.success(request, 'your post has been deleted!', "success")
            return redirect("account:user_profile", user_id=request.user.id)
        else:
            messages.error(request, 'you can not delete this post', "warning")
            return redirect("home:home")


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):  # وقتی چند بار نیاز داریم به دیتابیس وصل بشیم یکبار ان را در ستاپ نوشته
        # self.post_instance = Post.objects.get(pk=kwargs['post_id'])
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if request.user.id != post.user.id:
            messages.error(request, "you can not update this post", "warning")
            return redirect("home:home")
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request, post_id):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/update.html', context={"form": form})

    def post(self, request, post_id):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.slug = slugify(form.cleaned_data['body'][:30])
            updated_post.save()
            messages.success(request, "your post updated", "success")
            return redirect("home:post_detail", post_id, post.slug)


class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'home/create.html', context={'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            created_post = form.save(commit=False)
            created_post.slug = slugify(form.cleaned_data['body'][:30])
            created_post.user = request.user
            created_post.save()
            messages.success(request, "you post created", "success")
            return redirect('home:post_detail', created_post.id, created_post.slug)


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForms

    def post(self, request, post_id, comment_id):
        post = get_object_or_404(Post, pk=post_id)
        comment = get_object_or_404(Comment, pk=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid:
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            reply.is_reply = True
            reply.save()
            messages.success(request, "your reply successfully added", "success")
        return redirect('home:post_detail', post_id, post.slug)


class PostLikeView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        like = Vote.objects.filter(user=request.user, post=post)
        if not like.exists():
            Vote.objects.create(user=request.user, post=post)
            messages.success(request, 'your vote has been added', 'success')
        else:
            messages.error(request, 'your vote has been already', 'warning')
        return redirect('home:post_detail', post_id, post.slug)
