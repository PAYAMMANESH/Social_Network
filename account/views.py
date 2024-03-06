from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from . import forms
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import \
    LoginRequiredMixin  # use for check that user is logged in or not when you use Log out and if user not logged in got to the url that you add in url_login in setting
from home.models import Post
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import Relation, Profile


# Create your views here.

class UserRegisterView(View):
    form_class = forms.UserRegisterForm
    template_name = 'account/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = forms.UserRegisterForm()
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'], cd['email'], cd['password1'])
            messages.success(request, "you registered successfully", "success")
            return redirect('home:home')
        return render(request, self.template_name, context={'form': form})


class UserLoginView(View):
    form_class = forms.UserLoginForm
    template_name = 'account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get(
            'next')  # برای تعیین ادرس برگشت کاربرد دارد مثلا .قتی قصد دیدن یک پست را داریم ولی لاگین نکردیم با لاگین کردن وارد همان صفحه پست مدنظر میشویم
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, "you are logged in", "success")
                if self.next:
                    return redirect(self.next)
                return redirect("home:home")
            messages.error(request, "you are not logged in", "warning")
        return render(request, self.template_name, context={"form": form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, "you are logged out", "success")
        return redirect("home:home")


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        # user = User.objects.get(pk=user_id)
        is_following = False
        user = get_object_or_404(User, id=user_id)
        # posts = Post.objects.filter(user_id=user_id)
        # posts = Post.objects.filter(user=user)  # get back list of object from db
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user=request.user, to_user=user).exists()
        if relation:
            is_following = True
        return render(request, "account/profile.html",
                      context={"user": user, 'posts': posts, 'is_following': is_following})


class UserPasswordRestView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'  # get user email
    success_url = reverse_lazy('account:password_reset_done')  # show message to user that we send you email
    email_template_name = 'account/password_reset_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'  # we sent you email


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'  # open this page after click on link that sent
    success_url = reverse_lazy('account:password_reset_complete')


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user).exists()
        if relation:
            messages.warning(request, "you are already following this user", "danger")
        else:
            Relation.objects.create(from_user=request.user, to_user=user)
            messages.success(request, "you followed this user", 'success')
        return redirect('account:user_profile', user.id)


class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation:
            relation.delete()
            messages.success(request, "you unfollowed this user", 'success')
        else:
            messages.warning(request, "you are not following this user", 'danger')
        return redirect('account:user_profile', user.id)


class EditUserView(LoginRequiredMixin, View):
    form_class = forms.EditUserForm

    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={'email': request.user.email})
        return render(request, 'account/edit_profile.html', context={'form': form})

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'profile updated', 'success')
            return redirect('account:user_profile', request.user.id)
