from django.urls import path, include

from user.views import ManageUserView, CreateUserView

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("me", ManageUserView.as_view(), name="manage")
]
