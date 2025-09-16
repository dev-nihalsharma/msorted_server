from rest_framework.routers import SimpleRouter
from .views import SavingsAPI


router = SimpleRouter()

router.register("savings", SavingsAPI, basename='savings')

urlpatterns = router.urls
