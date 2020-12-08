from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from posts.models import User, Group, Post, Follow
from posts.forms import PostForm, CommentForm


@cache_page(20, key_prefix='index_page')
def index(request):
    """Render the homepage."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_list(request):
    """Render the page with a list of groups."""
    groups = Group.objects.order_by('-title')
    return render(request, 'group_list.html', {'groups': groups})


def group_posts(request, slug):
    """Render the page with a list of group's posts."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    """Render the page with a form of creating a new post."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """Render the profile page."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = bool(request.user.follower.filter(author=author))
    return render(
        request, 'profile.html',
        {'author': author, 'page': page,
         'paginator': paginator, 'following': following}
    )


def post_view(request, username, post_id):
    """Render the page containing one specific post with comments."""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request, 'post.html',
        {'author': post.author, 'post': post,
         'comments': comments, 'form': form}
    )


@login_required
def post_edit(request, username, post_id):
    """Render the page with a post-editting form.

    Check if the user is logged in and has a permission to edit the post.
    """
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user == post.author:
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
        return render(
            request, 'edit_post.html',
            {'author': post.author, 'post': post, 'form': form}
        )
    return redirect('post', username=username, post_id=post_id)


@login_required
def add_comment(request, username, post_id):
    """Render the comment page."""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = post.author
        comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    """Render the page with followed's latest posts."""
    post_list = Post.objects.select_related('author').filter(
        author__in=request.user.follower.all().values('author')
    )
    message = len(post_list) == 0
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, "follow.html",
        {'page': page, 'paginator': paginator, 'message': message}
    )


@login_required
def profile_follow(request, username):
    """Allow the user to subscribe if the user is not subscribed already
    and don't allow self-subscription.
    """
    author = get_object_or_404(User, username=username)
    if (not request.user.follower.filter(author=author) and
       request.user != author):
        follow = Follow(user=request.user, author=author)
        follow.save()
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Allow the user to unsubscribe."""
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow, user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception=None):
    return render(
        request, 'misc/404.html',
        {'path': request.path}, status=404
    )


def server_error(request, exception=None):
    return render(request, 'misc/500.html', status=500)
