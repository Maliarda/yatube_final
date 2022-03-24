from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

LIMIT_POSTS = 10


def get_pagination(queryset, request):
    paginator = Paginator(queryset, LIMIT_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {
        "paginator": paginator,
        "page_number": page_number,
        "page_obj": page_obj,
    }


def index(request):
    """Главная страница."""
    page_obj = Post.objects.all()
    context = {
        "page_obj": page_obj,
    }
    context.update(get_pagination(page_obj, request))
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    """Страница со списком постов."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        "group": group,
        "posts": posts,
    }
    context.update(get_pagination(posts, request))
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    """Страница с профайлом пользователя"""
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated and request.user != author:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        "author": author,
        "following": following,
    }
    context.update(get_pagination(author.posts.all(), request))
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    """Страница просмотра поста"""
    post = get_object_or_404(Post, id=post_id)
    group = post.group
    author = post.author
    form = CommentForm()
    comments = post.comments.all()
    context = {
        "post": post,
        "group": group,
        "author": author,
        "form": form,
        "comments": comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    """Создание новой записи"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect("posts:profile", request.user.username)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    """Редактирование записи для автора"""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)
    return render(
        request,
        "posts/create_post.html",
        {"form": form, "post": post, "is_edit": True},
    )


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    """Вывод постов авторов, на которых подписан текущий юзер"""
    page_obj = Post.objects.filter(author__following__user=request.user)
    context = {"page_obj": page_obj}
    context.update(get_pagination(page_obj, request))
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    user = request.user
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect(reverse("posts:profile", args=[username]))


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect("posts:profile", username=author)
