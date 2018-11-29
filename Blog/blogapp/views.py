from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from .models import author, category, article, comment
from django.contrib.auth import authenticate,login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import createForm,SignUpForm,createAuthor,categoryForm, commentForm
from django.contrib import messages

# Create your views here.
def index(request):
    post=article.objects.get_queryset().order_by('id')
    search=request.GET.get('q')
    if search:
        post=post.filter(
            Q(title__icontains=search)|
            Q(body__icontains=search)
        )
    paginator = Paginator(post,4)  # Show 25 contacts per page

    page = request.GET.get('page')
    total_article = paginator.get_page(page)

    context={
        "post":total_article
    }
    return render(request,"index.html",context)

def getauthor(request,name):
    post_author=get_object_or_404(User,username=name)
    auth=get_object_or_404(author,name=post_author.id)
    post=article.objects.filter(article_author=auth.id)
    ok={
        "post":post,
        "auth":auth,
        "post_author":post_author
    }
    return render(request,"profile.html",ok)


def getsingle(request, id):
      post = get_object_or_404(article, pk=id)
      first = article.objects.first()
      last = article.objects.last()
      getComment = comment.objects.filter(post=id)
      related = article.objects.filter(category=post.category).exclude(id=id)[:4]
      form = commentForm(request.POST or None)
      if form.is_valid():
         instance = form.save(commit=False)
         instance.post = post
         instance.save()
      context = {
            "post": post,
            "first": first,
            "last": last,
            "related": related,
            "form": form,
            "comment": getComment
       }
      return render(request, "single.html", context)


def getTopic(request,name):
    cat=get_object_or_404(category,name=name)
    post=article.objects.filter(category=cat.id)
    context={
        "post":post,
        "cat":cat
    }
    return render(request,"category.html",context)

def getLogin(request):

    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == "POST":
            user = request.POST.get('user')
            password = request.POST.get('pass')
            auth = authenticate(request, username=user, password=password)
            if auth is not None:
                login(request, auth)
                return redirect('index')
            else:
                messages.add_message(request, messages.ERROR, 'Username or Password incorrect')
                return render(request,'login.html')


        return render(request, "login.html")


def signup(request):

        form = SignUpForm(request.POST or None)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            messages.success(request,'Registration Succesfully completed')
            return redirect('login')

        return render(request, 'signup.html',{"form":form} )


def getLogout(request):
    logout (request)
    return redirect('index')

def getCreate(request):

    if request.user.is_authenticated:
        u=get_object_or_404(author,name=request.user.id)
        form=createForm(request.POST or None, request.FILES or None)
        contex = {"form": form}
        if form.is_valid():
            instance=form.save(commit=False)
            instance.article_author=u
            instance.save()
            return redirect('index')

        return render(request,"create.html",contex)
    else:
           return redirect('login')



def getUpdate(request,pid):

    if request.user.is_authenticated:
        u=get_object_or_404(author,name=request.user.id)
        post=get_object_or_404(article,id=pid)
        form=createForm(request.POST or None, request.FILES or None,instance=post)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.article_author=u
            instance.save()
            messages.success(request,'Post Updated succesfully')
            return redirect('profile')


        return render(request,"create.html", {"form": form})
    else:
           return redirect('login')

def getDelete(request,pid):

    if request.user.is_authenticated:
        post=get_object_or_404(article,id=pid)
        post.delete()
        messages.warning(request, 'Post Deleted succesfully ')
        return redirect('profile')
    else:
           return redirect('login')



def getProfile(request):
    if request.user.is_authenticated:
        user=get_object_or_404(User, id=request.user.id)
        author_profile=author.objects.filter(name=user.id)
        if author_profile:
            authorUser=get_object_or_404(author,name=request.user.id)
            post=article.objects.filter(article_author=authorUser.id)
            context={
               "post":post,
               "user":user
              }
            return render(request,'logged_in_profile.html',context)
        else:
            form=createAuthor(request.POST or None , request.files or None)
            if form.is_valid():
                instance=form.save(commit=False)
                instance.save()
                return redirect('profile')
            return render(request,'createauthor.html',{"form":form})


    else:
        return redirect('login')

