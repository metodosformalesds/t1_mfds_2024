from django.views import generic

class LandingPageView(generic.TemplateView):
    """
   Daniel Esqueda
    Vista para la página de aterrizaje del sitio.

    Esta vista es responsable de renderizar la página de inicio del sitio web para los visitantes.
    Utiliza el sistema de plantillas de Django para renderizar la plantilla correspondiente, 
    en este caso 'visitors/landing.html'.
    """
    template_name = "visitors/landing.html"
