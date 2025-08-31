# ...existing code...

import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from crm.models import Product

class Query(graphene.ObjectType):
    ping = graphene.String(default_value="pong")
    hello = graphene.String(default_value="Hello, GraphQL!")
    all_customers = DjangoFilterConnectionField(lambda: CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(graphene.String))
    all_products = DjangoFilterConnectionField(lambda: ProductType, filterset_class=ProductFilter, order_by=graphene.List(graphene.String))
    all_orders = DjangoFilterConnectionField(lambda: OrderType, filterset_class=OrderFilter, order_by=graphene.List(graphene.String))
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils import timezone

# Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

# Mutations
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(message="Email already exists")
        if phone:
            validator = RegexValidator(regex=r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$')
            try:
                validator(phone)
            except Exception:
                return CreateCustomer(message="Invalid phone format")
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        customers = []
        errors = []
        for idx, data in enumerate(input):
            name = data.name
            email = data.email
            phone = data.phone
            if not name or not email:
                errors.append(f"Row {idx+1}: Name and email required")
                continue
            if Customer.objects.filter(email=email).exists():
                errors.append(f"Row {idx+1}: Email already exists")
                continue
            if phone:
                validator = RegexValidator(regex=r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$')
                try:
                    validator(phone)
                except Exception:
                    errors.append(f"Row {idx+1}: Invalid phone format")
                    continue
            customer = Customer(name=name, email=email, phone=phone)
            customer.save()
            customers.append(customer)
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)
    message = graphene.String()

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            return CreateProduct(message="Price must be positive")
        if stock is not None and stock < 0:
            return CreateProduct(message="Stock cannot be negative")
        product = Product(name=name, price=price, stock=stock or 0)
        product.save()
        return CreateProduct(product=product, message="Product created successfully")

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)
    message = graphene.String()

    @transaction.atomic
    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(message="Invalid customer ID")
        if not product_ids:
            return CreateOrder(message="At least one product must be selected")
        products = list(Product.objects.filter(pk__in=product_ids))
        if len(products) != len(product_ids):
            return CreateOrder(message="One or more product IDs are invalid")
        order = Order(customer=customer, order_date=order_date or timezone.now())
        order.save()
        order.products.set(products)
        total = sum([p.price for p in products])
        order.total_amount = total
        order.save()
        return CreateOrder(order=order, message="Order created successfully")

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    # Return fields
    updated_products = graphene.List(ProductType)
    message = graphene.String()
    count = graphene.Int()

    def mutate(self, info):
        try:
            # Query products with stock < 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            
            updated_products = []
            for product in low_stock_products:
                # Increment stock by 10 (simulating restocking)
                product.stock += 10
                product.save()
                updated_products.append(product)
            
            count = len(updated_products)
            message = f"Successfully updated {count} low-stock products"
            
            return UpdateLowStockProducts(
                updated_products=updated_products,
                message=message,
                count=count
            )
        except Exception as e:
            return UpdateLowStockProducts(
                updated_products=[],
                message=f"Error updating low-stock products: {str(e)}",
                count=0
            )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
