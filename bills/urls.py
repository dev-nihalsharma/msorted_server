
from rest_framework.routers import SimpleRouter
from bills.views import BillsAPI


router = SimpleRouter()

router.register("bills", BillsAPI, basename='bills')

urlpatterns = router.urls
