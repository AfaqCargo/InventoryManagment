from django.urls import path
from . import views
from .views import CustomerSearchView, ItemSearchView

urlpatterns = [
    # Customer URLs
    path('', views.home, name='home'),

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Employee URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # Item URLs
    path('items/', views.item_list, name='item_list'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:pk>/delete/', views.item_delete, name='item_delete'),

    # Order URLs
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/edit/', views.order_update, name='order_update'),
    path('orders/<int:order_id>/delete/', views.order_delete, name='order_delete'),
    
    # Chart URLs
    path('sales-chart-data/', views.sales_chart_data, name='sales_chart_data'),
    path('activity-chart-data/', views.activity_chart_data, name='activity_chart_data'),

    # Print URLs
    path('print/<int:order_id>/', views.print_order, name='print_order'),

    # Color URLs
    path('colors/', views.color_list, name='color_list'),
    path('color/add/', views.add_color, name='add_color'),
    path('colors/<int:pk>/', views.color_detail, name='color_detail'),

    
    # # API endpoints for dynamic form handling
    # path('api/get-column-form/<int:column_number>/', views.get_column_form, name='get_column_form'),
    path('validate-field/', views.validate_field, name='validate_field'),


    path('collect-static/', views.collect_static, name="collect"),
    path('run-migrations/', views.run_migrations, name='run_migrations'),
    
]
