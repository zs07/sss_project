from django.contrib import admin
from django.urls import path
from sss_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('accounts/signup/', views.signup_view, name="signup"),
    path('accounts/login/', views.login_view, name="login"),
    path('accounts/logout/', views.logout_view, name="logout"),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name="checkout"),
    path('my_orders/', views.my_orders, name="my_orders"),
    path('cart/', views.cart, name="cart"),
    path('create_product/', views.create_product, name="create_product"),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/quantity/', views.cart_quantity, name='cart_quantity'),
    path('orders/<int:order_id>/', views.order_details, name='order_details'),
    path('admin_all_orders/', views.admin_all_orders, name='admin_all_orders'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
