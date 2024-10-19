from django.views import generic

class RegisterView(generic.TemplateView):
    template_name = "users/register.html"
