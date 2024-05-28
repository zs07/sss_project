from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError, transaction
from django.contrib import messages
from .models import *
from .forms import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q, F, Sum


def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            Cart.objects.create(user=user)
            login(request, user)
            return redirect("index")
        except IntegrityError:
            return render(request, "signup.html", {"message": "Username or email is already taken."})

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "login.html", {"message": "Invalid username or password."})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def index(request):
    category = request.GET.get('category')
    if category:
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    categories = Product.objects.values_list('category', flat=True).distinct()

    if request.user.is_staff:
        return render(request, 'admin_dashboard.html', {'products': products, 'categories': categories})
    else:
        total_quantity = sum(cart_item.quantity for cart_item in request.user.cart.cartitem_set.all())
        return render(request, 'customer_dashboard.html', {'products': products, 'total_quantity': total_quantity, 'categories': categories, 'selected_category': category})


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user.customer)
    for order in orders:
        order.total_items = order.orderitem_set.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    return render(request, 'my_orders.html', {'orders': orders})


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    subtotal = cart_items.aggregate(total_price=Sum(F('product__price') * F('quantity')))['total_price'] or 0

    return render(request, "cart.html", {'cart_items': cart_items, 'subtotal': subtotal})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if product.stock < 1:
        return JsonResponse({'message': 'Product is out of stock'}, status=400)

    cart, _ = Cart.objects.get_or_create(user=request.user)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)

    cart_item.save()
    request.session['cart'] = cart.id

    total_cart_items = CartItem.objects.filter(cart=cart).aggregate(total_items=Sum('quantity'))['total_items']
    cart_item_count = total_cart_items if total_cart_items else 0

    return JsonResponse({'message': 'Product added to cart successfully', 'cart_item_count': cart_item_count}, status=200)


@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance, name=instance.username)


@login_required
@transaction.atomic
def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            street = form.cleaned_data['street']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            postcode = form.cleaned_data['postcode']
            credit_card_number = form.cleaned_data['credit_card_number']
            expiration_date = form.cleaned_data['expiration_date']
            cvv = form.cleaned_data['cvv']

            cart = Cart.objects.get(user=request.user)

            for cart_item in cart.cartitem_set.all():
                product = cart_item.product
                if product.stock < cart_item.quantity:
                    messages.error(request, f'Insufficient stock for {product.name}')
                    return render(request, 'checkout.html', {'form': form})

            total_price = sum(item.product.price * item.quantity for item in cart.cartitem_set.all())

            shipping_address = Address.objects.create(street=street, city=city, state=state, postcode=postcode)

            order = Order.objects.create(customer=cart.user.customer, shipping_address=shipping_address,
                                         total_price=total_price)

            for cart_item in cart.cartitem_set.all():
                OrderItem.objects.create(order=order, product=cart_item.product, price=cart_item.product.price,
                                         quantity=cart_item.quantity)

            billing_address = Address.objects.create(street=street, city=city, state=state, postcode=postcode)

            OrderPayment.objects.create(card_number=credit_card_number, txnid='', order=order,
                                        billing_address=billing_address)

            for cart_item in cart.cartitem_set.all():
                product = cart_item.product
                if product.stock >= cart_item.quantity:
                    product.stock -= cart_item.quantity
                    product.save()
                else:
                    messages.error(request, f'Insufficient stock for {product.name}')
                    return render(request, 'checkout.html', {'form': form})

            cart.cartitem_set.all().delete()

            return redirect('my_orders')
        else:
            messages.error(request, 'Error processing order. Please check your information.')
            return render(request, 'checkout.html', {'form': form})
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {'form': form})


@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user.is_authenticated and (request.user.is_staff or order.customer.user == request.user):
        order_items = OrderItem.objects.filter(order=order)
        total_quantity = sum(order_item.quantity for order_item in order_items)

        for order_item in order_items:
            order_item.subtotal = order_item.product.price * order_item.quantity

        context = {
            'order': order,
            'order_items': order_items,
            'total_quantity': total_quantity,
        }

        return render(request, 'order_details.html', context)
    else:
        return HttpResponseForbidden('You do not have permission to view this order.')


@staff_member_required
@transaction.atomic
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            product.save()
            messages.success(request, 'Product created successfully')
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
            return redirect('index')
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Product updated successfully'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = ProductForm(instance=product)
        return render(request, 'edit_product.html', {'form': form, 'product': product})


@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return JsonResponse({'message': 'Product deleted successfully'}, status=200)


@login_required
def update_quantity(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        action = request.POST.get('action')

        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        if action == 'increment':
            cart_item.quantity += 1
        elif action == 'decrement':
            cart_item.quantity -= 1 if cart_item.quantity > 0 else 0
        cart_item.save()

        subtotal = cart_item.product.price * cart_item.quantity
        return JsonResponse({'quantity': cart_item.quantity, 'subtotal': subtotal})


@login_required
def remove_from_cart(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')

        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.delete()

        return JsonResponse({'success': True})


@login_required
def cart_quantity(request):
    if request.user.is_authenticated:
        cart_item_count = request.user.cart.cartitem_set.count() if hasattr(request.user, 'cart') else 0
        return JsonResponse({'total_quantity': cart_item_count})
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=403)


@staff_member_required
def admin_all_orders(request):
    if request.user.is_superuser:
        orders = Order.objects.all()
        return render(request, 'admin_all_orders.html', {'orders': orders})
    else:
        return HttpResponse("Unauthorized", status=401)
