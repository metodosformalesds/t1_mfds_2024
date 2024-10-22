from django.urls import path
from .views import ToolFormView, ToolListView

urlpatterns = [
    path("", ToolListView.as_view(), name="list_tool"),
    path("agregar/", ToolFormView.as_view(), name="add_tool"),
]
