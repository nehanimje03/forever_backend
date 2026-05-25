from django.urls import path
from products.APIs.Carts.cart import *
from products.APIs.Carts.clear_cart import *
from products.APIs.Carts.recently_viewed import *
from products.APIs.Product.all_product import *
from products.APIs.Product.related_product_details import *
from products.APIs.Wishlist.wishlish import *

urlpatterns = [
    # product details & related product
    path('products-detail/', PublicProductDetailAPIView.as_view()),
    path('related-products/', PublicProductDetailAPIView.as_view()),

    # all products (latest, bestseller, all)
    path('all-products/', PublicProductsAPIView.as_view()),
    path('latest-products/', PublicProductsAPIView.as_view()),
    path('bestseller-products/', PublicProductsAPIView.as_view()),

    # Recent Products Viewed
    path('recent-product-track/', TrackRecentProductAPIView.as_view()),
    path('recent-product/', RecentProductsAPIView.as_view()),
    # path('recent/clear/', ClearRecentProductsAPIView.as_view()),

    # cart 
    path('add-to-cart/', CartAPIView.as_view()),
    path('get-items-from-cart/',CartAPIView.as_view()),
    path('update-cart-item-details/',CartAPIView.as_view()),
    path('remove-items-from-cart/',CartAPIView.as_view()),
    path('increase-product-quantity/', CartAPIView.as_view()),
    path('decrease-product-quantity/', CartAPIView.as_view()),



    # path('cart-clear/', CartClearAPIView.as_view()),

    # wishlist
    path('add-to-wishlist/', WishlistApiView.as_view()),
    path('get-items-from-wishlist/', WishlistApiView.as_view()),
    path('remove-item-from-wishlist/', WishlistApiView.as_view()),


]