from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
# from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow

from .utils import paginator_context


COUNT_POST = 10


# @cache_page(20 * 15)
def index(request):
    """Главная страница."""
    posts = Post.objects.select_related('author', 'group')
    paginator = Paginator(posts, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница списка групп постов."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Cписок постов пользователя, информация о пользователе.
    Проверка: подписан ли текущий пользователь на автора, страницу
    которого он просматривает; результат проверки переменной following."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author').all()
    page_obj = paginator_context(request, posts)
    following = True
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
        context = {
            'author': author,
            'page_obj': page_obj,
            'following': following,
        }
        return render(request, 'posts/profile.html', context)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница поста пользоввателя и общее количество постов."""
    post = get_object_or_404(Post, id=post_id)
    post_number = Post.objects.filter(author=post.author).count()
    post_comment = post.text
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'post_number': post_number,
        'post_comment': post_comment,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Добавление нового поста."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
    title = 'Создание нового поста'
    context = {
        'title': title,
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Cтраница редактирования постов"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    title = 'Редактирование поста'
    context = {
        'post': post,
        'form': form,
        'title': title,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    # Получите пост и сохраните его в переменную post.
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(reverse('posts:post_detail',
                        kwargs={'post_id': post_id}))
    return render(request, 'posts/post_detail.html',
                  {'form': form, 'post': post})


@login_required
def follow_index(request):
    """Информация о текущем пользователе доступна в переменной request.user."""
    list_posts = Post.objects.select_related('author', 'group').filter(
        author__following__user=request.user
    )
    page_obj = paginator_context(request, list_posts)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)
# args=[self.author.username]


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка.
    Проверка is_follower существует, то удаляем подписку."""
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)
