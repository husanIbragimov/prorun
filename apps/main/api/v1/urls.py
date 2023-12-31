from django.urls import path
from .views import NewsDefaultBannerListView, NewsRetrieveAPIView, NewsListView, PartnerListView

urlpatterns = [
    path('banner/', NewsDefaultBannerListView.as_view()),
    path('news/', NewsListView.as_view()),
    path('news/<int:pk>/', NewsRetrieveAPIView.as_view()),

    path('partners/', PartnerListView.as_view()),
]
