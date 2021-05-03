from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Accounts.urls')),
    # path('oauth/', include('social_django.urls', namespace='social')),
    path('', include('Questions.urls')),

]

handler404 = 'Questions.views.error_404'
handler500 = 'Questions.views.error_500'

