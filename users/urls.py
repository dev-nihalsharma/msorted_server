from rest_framework.routers import SimpleRouter
from users.views import AccountingAPI, AuthAPI, UserAPI


router = SimpleRouter()

router.register("auth", AuthAPI, basename='auth')
router.register("user", UserAPI, basename='user')
router.register("accounting", AccountingAPI, basename='accounting')

urlpatterns = router.urls
