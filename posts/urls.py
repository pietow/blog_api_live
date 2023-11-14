from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import PostList, PostDetail, UserViewSet

urlpatterns = [
    path("<int:pk>/", PostDetail.as_view(), name="post_detail"),
    path("", PostList.as_view(), name="post_list"),
    # path('users/', UserList.as_view(), name='user_list'),
    # path('users/<int:pk>', UserDetail.as_view(), name='user_detail'),
]

router = SimpleRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns += router.urls


