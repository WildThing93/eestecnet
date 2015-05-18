# Create your views here.
from django.views.generic import DetailView, UpdateView, CreateView, ListView

from apps.pages.views import Protected
from apps.wiki.forms import WikiForm
from apps.wiki.models import WikiPage


class PageLatest(Protected, ListView):
    model = WikiPage
    template_name = 'wiki/latest.html'

    def get_queryset(self):
        return WikiPage.objects.order_by('-last_modified')[:5]


class PageRandom(Protected, DetailView):
    model = WikiPage

    def get_object(self, queryset=None):
        return WikiPage.objects.order_by('?')[0]


class WikiHome(Protected, DetailView):
    model = WikiPage

    def get_object(self, queryset=None):
        page, created = WikiPage.objects.get_or_create(name="home")
        return page


class PageDetail(Protected, DetailView):
    model = WikiPage

    def get_object(self, queryset=None):
        page, created = WikiPage.objects.get_or_create(slug=self.kwargs['slug'])
        if created:
            page.name = page.slug
            page.save()
        return page


class PageUpdate(Protected, UpdateView):
    model = WikiPage
    form_class = WikiForm

    def form_valid(self, form):
        form.instance.username = self.request.user
        return super(PageUpdate, self).form_valid(form)


class PageCreate(Protected, CreateView):
    model = WikiPage
    form_class = WikiForm

    def form_valid(self, form):
        form.instance.username = self.request.user
        return super(PageCreate, self).form_valid(form)
