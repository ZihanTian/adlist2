from django.shortcuts import render
from ads.utils import dump_queries
from django.db.models import Q
# Create your views here.
from ads.models import Ad, Comment, Fav
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.views import View
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from ads.forms import CreateForm
from ads.forms import CommentForm
from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse

from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
class AdListView(OwnerListView):
    model = Ad
    template_name = "ads/Ad_list.html"
   # def get(self, request) :
   #     ad_list = Ad.objects.all()
   #     favorites = list()
   #     if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
   #         rows = request.user.favorite_ads.values('id')
            # favorites = [2, 4, ...] using list comprehension
   #         favorites = [ row['id'] for row in rows ]
   #     ctx = {'ad_list' : ad_list, 'favorites': favorites}
   #     return render(request, self.template_name, ctx)
    def get(self, request) :
        favorites = list()
        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            query = Q(title__contains=strval)
            query.add(Q(text__contains=strval), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 posts and watch the queries that happen
            ad_list = Ad.objects.all().order_by('-updated_at')[:10]
            # objects = Post.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in ad_list:
            obj.natural_updated = naturaltime(obj.updated_at)
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_ads.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
            ctx = {'ad_list' : ad_list, 'search': strval, 'favorites': favorites }
        else:
            ctx = {'ad_list' : ad_list, 'search': strval}
        retval = render(request, self.template_name, ctx)

        dump_queries()
        return retval
class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/Ad_detail.html"
    def get(self, request, pk) :
        ad = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=ad).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'ad' : ad, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk])) 
class AdCreateView(LoginRequiredMixin, View):
    model = Ad
    fields = ['title', 'text', 'price']
    template = "ads/Ad_form.html"
   # template = 'pics/form.html'  #need to be changed later
    success_url = reverse_lazy('ads:ads')
    def get(self, request, pk=None) :
        form = CreateForm()
        ctx = { 'form': form }
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)
class AdUpdateView(LoginRequiredMixin, View):
    model = Ad
    fields = ['title', 'text']
    template = "ads/Ad_form.html"
   # template = 'pics/form.html'
    success_url = reverse_lazy('ads:ads')
    def get(self, request, pk) :
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = { 'form': form }
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        pic = form.save(commit=False)
        pic.save()

        return redirect(self.success_url)

class AdDeleteView(OwnerDeleteView):
    model = Ad
    template_name = "ads/Ad_delete.html"
class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/Ad_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        comment = self.object.ad
        return reverse('ads:ad_detail', args=[comment.id])

def stream_file(request, pk) :
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response
