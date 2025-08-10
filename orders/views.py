import csv
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from Shop.permissions import IsVendor
from orders.filters import OrderFilter
from orders.models import Order
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from rest_framework import (serializers, viewsets,
                            generics, permissions, status)
from django.db.models import F

from Shop.models import Product
from campusprofile.models import Student, Vendor
from django.shortcuts import render

from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import (Cart, Wishlist, Order, Payment)
from .serializers import (
    CartSerializer, WishlistSerializer,
    OrderSerializer, OrderCreateSerializer,
    PaymentSerializer)

from Logistics.models import Sale, SaleLog, Stock

from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student = Student.objects.filter(user=self.request.user).first()
        print()
        print("REQUEST", self.request.data, self.request.query_params)
        print()
        return Wishlist.objects.filter(user=student)

    # def retrieve(self):
    #     print()
    #     print("REQUEST single object", self.request.data,
    #           self.request.query_params)
    #     print()

    #     student = Student.objects.filter(user=self.request.user).first()
    #     return Wishlist.objects.filter(user=student)

    def create(self, request, *args, **kwargs):

        student = Student.objects.filter(user=request.user).first()

        product_id = request.data.get('product')
        wishlist = Wishlist.objects.filter(
            user=student, product_id=product_id).first()

        if wishlist:
            wishlist.delete()
            return Response({
                "detail": "Removed from wishlist.",
                "action": "removed",
                "product": product_id
            }, status=status.HTTP_200_OK)

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({
                "detail": "Product not found.",
                "action": "error"
            }, status=status.HTTP_404_NOT_FOUND)

        wishlist = Wishlist.objects.create(user=student, product=product)
        serializer = self.get_serializer(wishlist)
        return Response({
            "detail": "Added to wishlist.",
            "action": "added",
            "product": product_id,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        student = Student.objects.filter(user=request.user).first()
        wishlist = Wishlist.objects.filter(
            user=student, product__id=pk).first()
        if wishlist:
            wishlist.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student = Student.objects.filter(user=self.request.user).first()
        # print()
        # print("get_queryset compromised", student)
        # print()

        return Cart.objects.filter(user=student)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        quantity = self.request.data.get('quantity', 1)

        product = Product.objects.filter(id=product_id).first()

        if not product:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        stock = Stock.objects.filter(product__id=product.id).first()
        print()
        print("stock", stock, product, product.id)
        print()

        if not stock or int(stock.count) < 1:
            # raise ValueError('Stock in lack')
            return Response({"detail": "Product out of stock."}, status=status.HTTP_204_NO_CONTENT)
            # return Response({"detail": "Product out of stock."}, status=status.HTTP_204_NO_CONTENT)

        student = Student.objects.filter(user=request.user).first()
        cart, created = Cart.objects.get_or_create(
            user=student, product=product, defaults={'quantity': 1})
        serializer = self.get_serializer(cart)
        # print()
        # print()
        # print("Created request", request, student,
        #       cart, cart.quantity, request.user, type(request.user), self.request.user, type(self.request.user))
        # print()
        # print()

        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart.quantity += int(quantity)
        cart.save()
        serialized_data = CartSerializer(cart, context={'request': request})
        print("serialized_data", serialized_data.data, cart)

        return Response(serialized_data.data)

    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        quantity = request.data.get('quantity')

        # print()
        # print()
        # print("Updated request", request, "quantity", quantity,
        #       cart_item, cart_item.quantity, "cart_item IDDD", cart_item.id)
        # print()
        # print()

        if quantity is not None:
            try:
                quantity = int(quantity)
                if quantity < 1:
                    return self.destroy(request, *args, **kwargs)
                cart_item.quantity = quantity
                cart_item.save()
                serializer = self.get_serializer(cart_item)
                return Response(serializer.data)
            except ValueError:
                return Response({"detail": "Invalid quantity."}, status=400)

        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        student = Student.objects.filter(user=request.user).first()
        Cart.objects.filter(user=student).delete()
        return Response({"detail": "Cart cleared."}, status=204)

    def destroy(self, request, pk=None):
        student = Student.objects.filter(user=request.user).first()
        cart = Cart.objects.filter(user=student, id=pk).first()
        # print()
        # print()
        # print("Delete request", request, pk, cart)
        # print()
        # print()
        # raise ValueError("no meaning in this")
        if cart:
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)


class OrderRetrieveView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure student only accesses their own orders
        student = Student.objects.filter(user=self.request.user).first()
        return Order.objects.filter(student=student)

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        try:
            return queryset.get(pk=pk)
        except Order.DoesNotExist:
            raise NotFound("Order not found.")

        # print()
        # print()
        # # print("USER", dir(user))
        # print("USER", user.vendor.exists(),
        #       user.vendor.instance, type(user.vendor.instance))
        # print("USER", user.student.exists(),
        #       user.student.instance, type(user.student.instance))
        # print()
        # print()


class OrderPagination(PageNumberPagination):
    page_size = 8
    # page_size_query_param = 'pagee3e'


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    pagination_class = OrderPagination
    queryset = Order.objects.all()

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "request": self.request}

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'student') and user.student.exists():
            # Student sees their placed orders
            student = Student.objects.filter(user=user).first()
            return Order.objects.filter(student=student).order_by('-ordered_at', '-delivery_date')

        elif hasattr(user, 'vendor') and user.vendor.exists():
            # Vendor sees orders placed to their store
            # store = getattr(user.vendor, 'store', None)
            store = Vendor.objects.filter(user=user).first().store
            if store:
                orders = Order.objects.filter(
                    store=store).order_by('-ordered_at')
                # new_orders = self.get_object().objects.filter(
                #     store=store).order_by('-ordered_at')
                print()
                print("All objs request", dir(self.request))
                print()
                print()
                print("query_params", self.request.query_params)
                print("data", self.request.data)
                print()
                print()
                # print("get_paginated_response",
                #       )
                print()
                print()
                # print('get_object', self.get_object())

                print()
                print("CHECK STRE orders", orders)
                print("orders len", len(orders))
                print()
                print()
                return orders
        return Order.objects.none()  # fallback


class SecondOrderPagination(PageNumberPagination):
    page_size = 3000
    # page_size_query_param = 'pagee3e'


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    pagination_class = SecondOrderPagination
    queryset = Order.objects.all()

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "request": self.request}

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'student') and user.student.exists():
            # Student sees their placed orders
            student = Student.objects.filter(user=user).first()
            return Order.objects.filter(student=student).order_by('-ordered_at', '-delivery_date')

        elif hasattr(user, 'vendor') and user.vendor.exists():
            # Vendor sees orders placed to their store
            # store = getattr(user.vendor, 'store', None)
            store = Vendor.objects.filter(user=user).first().store
            if store:
                return Order.objects.filter(store=store).order_by('-ordered_at')
        return Order.objects.none()  # fallback

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, 'student') or (hasattr(user, 'student') and not user.student.exists()):
            raise PermissionDenied(
                "Only students can place orders.")
        student = Student.objects.filter(user=user).first()

        order = serializer.save(student=student)
        if order.payment_status == 'paid':
            # Create Sale and Log for each item
            for item in order.items.all():
                sale = Sale.objects.create(
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.unit_price * item.quantity,
                    store=order.store
                )
                SaleLog.objects.create(
                    sale=sale,
                    action='created',
                    performed_by=user
                )

        # Compose Order Summary
        item_lines = [
            f"{item.product.product_name} × {item.quantity} = ₦{item.unit_price * item.quantity}"
            for item in order.items.all()
        ]

        body = "\n".join([
            f"Hello {order.student.first_name},",
            f"Your order #{order.id} has been received.",
            f"Scheduled Delivery: {order.delivery_date if order.delivery_date else 'Not specified'}",
            "",
            "Order Summary:",
            *item_lines,
            "",
            "Thank you for shopping with us!"
        ])

        send_mail(
            subject=f"Order Confirmation - #{order.id}",
            message=body,
            from_email=None,
            recipient_list=[order.student.email],
            fail_silently=True
        )

        # Notify Vendor
        store = order.store
        vendor_user = store.vendor.user

        vendor_message = "\n".join([
            f"Hello {store.vendor.first_name},",
            f"You have received a new order #{order.id} in your store: {store.store_name}.",
            f"Scheduled Delivery: {order.delivery_date if order.delivery_date else 'Not specified'}",
            "",
            "Order Summary:",
            *item_lines,
            "",
            "Please prepare the order for delivery.",
        ])

        send_mail(
            subject=f"New Order Alert - #{order.id}",
            message=vendor_message,
            from_email=None,
            recipient_list=[vendor_user.email],
            fail_silently=True
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user

        new_status = request.data.get('status')
        current_status = order.status

        # Disallow update if already delivered
        if current_status == 'delivered':
            print("Delivered orders cannot be updated.")
            raise PermissionDenied("Delivered orders cannot be updated.")

        # Only vendor can move from confirmed → delivered
        if current_status == 'confirmed' and new_status == 'delivered':
            print("Only vendor can mark as delivered.")
            if not hasattr(user, 'vendor') or not user.vendor.exists():
                raise PermissionDenied("Only vendor can mark as delivered.")

        # Only vendor can move from confirmed → delivered
        if current_status == 'confirmed' and new_status == 'cancelled':
            print("Only vendor can cancel confirmed orders.")
            if not hasattr(user, 'vendor') or not user.vendor.exists():
                raise PermissionDenied(
                    "Only vendor can cancel confirmed orders.")

        # Only vendor can mark as confirmed
        if current_status == 'pending' and new_status == 'confirmed':
            print("Only vendor can confirm an order.")
            if not hasattr(user, 'vendor') or not user.vendor.exists():
                raise PermissionDenied("Only vendor can confirm an order.")

        # both student and vendor can cancel if pending
        # if current_status == 'pending' and new_status == 'cancelled':
        #     print("Only student can cancel an order.")
        #     # if not hasattr(user, 'student') and user.vendor.exists():
        #     raise PermissionDenied("Only student can cancel an order.")

        # Disallow cancel after confirmation
        if current_status != 'pending' and new_status == 'cancelled':
            print("Order can only be cancelled if still pending.")
            raise PermissionDenied(
                "Order can only be cancelled if still pending.")

        if current_status == 'pending' and new_status == 'cancelled':
            order.payment_status = 'failed'
            order.save()

        if new_status == 'delivered':
            order.payment_status = 'paid'
            order.save()

        # if new_status == 'delivered':
        #     order.payment_status = 'paid'

        # if new_status == 'delivered':
        #     order.payment_status = 'paid'

        if order.payment_status == 'paid' or new_status == 'delivered':
            # Create Sale and Log for each item
            for item in order.items.all():
                sale = Sale.objects.create(
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.unit_price * item.quantity,
                    store=order.store
                )
                SaleLog.objects.create(
                    sale=sale,
                    action='created',
                    performed_by=user
                )
                # Stock.objects.filter(product=item.product).update(
                #     count=F('count') - item.quantity)

        return super().patch(request, *args, **kwargs)


class VendorOrderExportView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer  # Optional
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'vendor') or not request.user.vendor.exists():
            return HttpResponse("Unauthorized", status=401)

        vendor = Vendor.objects.filter(user=request.user).first()
        orders = Order.objects.filter(store__vendor=vendor)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vendor_orders.csv"'

        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Status', 'Buyer', 'Date'])

        for order in orders:
            writer.writerow([
                order.id,
                order.status,
                order.student.user.username,
                # order.created_atd.strftime('%Y-%m-%d')
            ])

        return response


class OrderBulkUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]

    def patch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'vendor'):
            return Response({"detail": "Unauthorized"}, status=401)

        vendor = Vendor.objects.filter(user=request.user).first()

        ids = request.data.get('ids', [])
        orders = Order.objects.filter(
            id__in=ids, store__vendor=vendor)

        for order in orders:
            if order.status in ['confirmed']:
                order.status = 'delivered'
                order.save()

        return Response({"updated": len(orders)})


class VendorCompletedOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # vendor = getattr(self.request.user, 'vendor', None)
        vendor = Vendor.objects.filter(user=self.request.user).first()
        if not vendor or not hasattr(vendor, 'store'):
            return Order.objects.none()

        return Order.objects.filter(store=vendor.store, status='delivered')


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# class CartListCreateView(generics.ListCreateAPIView):
#     serializer_class = CartSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.filter(student=self.request.user.student)

#     def perform_create(self, serializer):
#         student = self.request.user.student
#         product = Product.objects.filter(
#             id=self.request.data.get('product')).first()

#         if not product:
#             raise serializers.ValidationError("Product not found.")

#         serializer.save(student=student)


# class CartListCreateView(generics.ListCreateAPIView):
#     serializer_class = CartSerializer

#     def get_queryset(self):
#         # return Cart.objects.filter(user=self.request.user.student)
#         student = getattr(self.request.user, 'student', None)
#         if not student:
#             return Cart.objects.none()
#         student = Student.objects.filter(user=student.instance).first()
#         return Cart.objects.filter(user=student)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user.student)


# class WishlistListCreateView(generics.ListCreateAPIView):
#     serializer_class = WishlistSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Wishlist.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         product_id = self.request.data.get('product')
#         if Wishlist.objects.filter(user=self.request.user, product_id=product_id).exists():
#             raise serializers.ValidationError("Already in wishlist.")

#         serializer.save(user=self.request.user)

#     def destroy(self, request, *args, **kwargs):
#         product_id = request.query_params.get('product')
#         wishlist = Wishlist.objects.filter(
#             user=request.user, product_id=product_id).first()

#         if wishlist:
#             wishlist.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)


# class WishlistListCreateView(generics.ListCreateAPIView):
#     serializer_class = WishlistSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # return Wishlist.objects.filter(user=self.request.user.student)
#         student_user = getattr(self.request.user, 'student', None)

#         if not student_user:
#             return Wishlist.objects.none()
#         student = Student.objects.filter(
#             user=student_user.instance).first()
#         return Wishlist.objects.filter(user=student)

#     def perform_create(self, serializer):
#         student = Student.objects.filter(
#             user=self.request.user).first()

#         # Wishlist.objects.filter().exists()
#         product = Product.objects.filter(
#             id=self.request.data.get('product')).first()

#         # if product:

#         print()
#         print("student_user", self.request.user.student.instance,
#               type(self.request.user), self.request.data, product)
#         print()
#         serializer.save(user=self.request.user)
