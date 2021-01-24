from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page,
        'paginator': paginator
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:10]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page,
        'paginator': paginator
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author__username=username)
    # post_count = user_posts.count()
    # if post_count == 0:
    #     main_post = ''
    # else:
    #     main_post = user_posts[0]
    followers_count = Follow.objects.filter(author__username=user).count()
    following_count = Follow.objects.filter(user__username=user).count()
    following = Follow.objects.filter(user__username=request.user.username,
                                      author__username=user).exists()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'author': user,
        'user_posts': user_posts,
        # 'post_count': post_count,
        'page': page,
        'paginator': paginator,
        # 'main_post': main_post,
        'followers_count': followers_count,
        'following_count': following_count,
        'following': following
    })


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    post_count = Post.objects.filter(author__username=username).count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    followers_count = Follow.objects.filter(author__username=user).count()
    following_count = Follow.objects.filter(user__username=user).count()
    following = Follow.objects.filter(user__username=request.user.username,
                                      author__username=user).exists()
    return render(request, 'post.html', {
        'author': user,
        'post': post,
        'post_count': post_count,
        'comments': comments,
        'form': form,
        'followers_count': followers_count,
        'following_count': following_count,
        'following': following
    })


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.user != user:
        return redirect(reverse('post', kwargs={
            'username': username,
            'post_id': post_id
        }))
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect(reverse('post', kwargs={
            'username': username,
            'post_id': post_id
        }))
    return render(request, 'posts/new.html', {
        'form': form,
        'is_edit': True,
        'post': post
    })


def page_not_found(request, exception=None):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
        return redirect('post', username, post_id)
    return redirect('post', username, post_id)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(user=request.user,
                          author__username=username).delete()
    return redirect('profile', username=username)


@login_required
def follow_index(request):
    following_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
        'page': page,
        'paginator': paginator
    })
