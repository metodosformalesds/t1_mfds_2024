from django.views import generic

class LandingPageView(generic.TemplateView):
    template_name = "visitors/landing.html"
