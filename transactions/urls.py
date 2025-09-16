from rest_framework.routers import SimpleRouter
from .views import TransactionsAPI


router = SimpleRouter()

router.register("transactions", TransactionsAPI, basename='transactions')

urlpatterns = router.urls
