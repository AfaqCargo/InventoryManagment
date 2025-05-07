from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from .forms import *
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import timezone, datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, TruncWeek
import random
from django.views import View
from django.db import transaction
from decimal import Decimal, getcontext

# Home/Dashboard view
def home(request):
    customer_count = Customer.objects.count()
    color_count = ColorRecord.objects.count()
    item_count = Item.objects.count()
    orders = Orders.objects.all().order_by('-date')
    logs = ActivityLog.objects.all().order_by('-timestamp')[:5]

    # Get filter parameters from the request
    customer = request.GET.get('customer')
    code = request.GET.get('code')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    label_name = request.GET.get('label_name')
    status = request.GET.get('status')

    # Apply filters conditionally
    if customer:
        orders = orders.filter(customer_data__name__icontains=customer)
    if code:
        orders = orders.filter(item_data__code__icontains=code)
    if start_date:
        orders = orders.filter(date__gte=start_date)
    if end_date:
        orders = orders.filter(date__lte=end_date)
    if label_name:
        orders = orders.filter(item_data__label_name__icontains=label_name)
    if status:
        orders = orders.filter(status=status)

    # Generate random colors for each log entry
    colors = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in logs]

    # Pass logs and colors to the template
    context = {
        
    }
    context = {
        'customer_count': customer_count,
        'color_count': color_count,
        'item_count': item_count,
        'orders': orders,
        'request': request,
        'activity_logs': logs,
        'colors': colors,
    }
    return render(request, 'home.html', context)

# --------------------- Customer Views ---------------------

def customer_list(request):
    # Start with all customers
    customers = Customer.objects.all()
    
    # Get filter parameters
    name = request.GET.get('name', '').strip()
    phone = request.GET.get('phone', '').strip()
    email = request.GET.get('email', '').strip()
    city = request.GET.get('city', '').strip()
    
    # Apply filters if any parameters are provided
    if name or phone or email or city:
        # Create a query that matches any of the provided filters
        # Use Q objects to create complex OR queries
        query = Q()
        
        if name:
            query |= Q(name__icontains=name)
        
        if phone:
            query |= Q(phone__icontains=phone)
        
        if email:
            query |= Q(email__icontains=email)
        
        if city:
            query |= Q(city__icontains=city)
        
        # Filter the queryset
        customers = customers.filter(query)
    
    # Pagination
    paginator = Paginator(customers, 10)  # Show 10 customers per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Prepare context
    context = {
        'customers': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.paginator.num_pages > 1
    }
    
    return render(request, 'customers/customer_list.html', context)


def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    item = Item.objects.filter(customer=customer).order_by('-date')
    order = Orders.objects.filter(customer_data = customer)
    # item = get_object_or_404(items)

    return render(request, 'customers/customer_detail.html', {'customer': customer, 'items':item, 'orders':order})

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'Customer created successfully.')
            # Log the activity
            ActivityLog.objects.create(
                action='Created',
                description=f'Customer "{customer.name}" is added.'
            )
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    return render(request, 'customers/customer_form.html', {
        'form': form,
        'title': 'Add New Customer',
        'submit_text': 'Create Customer'
    })

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            frm = form.save()
            # Log the activity
            ActivityLog.objects.create(
                action='update',
                description=f'Customer "{frm.name}" is updated.'
            )
            messages.success(request, 'Customer updated successfully.')
            return redirect('customer_detail', pk=customer.pk)
        
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customers/customer_form.html', {
        'form': form,
        'customer': customer,
        'title': 'Edit Customer',
        'submit_text': 'Update Customer'
    })

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.delete()
        # Log the activity
        ActivityLog.objects.create(
            action='Deleted',
            description=f'Customer "{customer.name}" is Deleted.'
        )
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer_list')
    
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})

# --------------------- Employee Views ---------------------

def employee_list(request):
    # Base queryset
    queryset = Employee.objects.all()

    # Search filters
    search_query = request.GET.get('search', '').strip()

    # Filter by search (name or employee ID)
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) 
        )

    # Order the results
    queryset = queryset.order_by('name')

    # Pagination
    paginator = Paginator(queryset, 10)  # 10 employees per page
    page = request.GET.get('page', 1)

    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        employees = paginator.page(1)
    except EmptyPage:
        employees = paginator.page(paginator.num_pages)

    # Context for template
    context = {
        'employees': employees,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': employees,
    }
    return render(request, 'employees/employee_list.html', context)

def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_detail.html', {'employee': employee})

def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        
        if form.is_valid():
            employee = form.save()
            # Log the activity
            ActivityLog.objects.create(
                action='Created',
                description=f'Employee "{employee.name}" is added.'
            )
            messages.success(request, 'Employee created successfully.')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Add New Employee',
        'submit_text': 'Create Employee'
    })

def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            frm = form.save()
            # Log the activity
            ActivityLog.objects.create(
                action='update',
                description=f'Employee "{frm.name}" is update.'
            )
            messages.success(request, 'Employee updated successfully.')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'employee': employee,
        'title': 'Edit Employee',
        'submit_text': 'Update Employee'
    })

def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        # Log the activity
        ActivityLog.objects.create(
            action='Deleted',
            description=f'Employee "{employee.name}" is Deleted.'
        )
        employee.delete()
        messages.success(request, 'Employee deleted successfully.')
        return redirect('employee_list')
    
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})

# --------------------- Item Views ---------------------


def calculate_thread_weight(color_pick, denier, quantity):
    """
    Calculates thread weight in kg using formula:
    (Color Pick × Denier × Quantity) ÷ 761,682,243
    """
    try:
        return (
            Decimal(str(color_pick)) * 
            Decimal(str(denier)) * 
            Decimal(str(quantity)) 
        ) / Decimal('761682243')
    except Exception:
        return Decimal('0.000')

# # Example usage:
# color_pick = 326
# denier = 100
# quantity = 5000
# result = calculate_thread_weight(color_pick, denier, quantity)
# print(f"Thread Weight: {result} kg")  # Output: Thread Weight: 0.214 kg

def item_list(request):
    # Base queryset
    items = Item.objects.all().order_by('-date')
    
    # Filtering
    label_name = request.GET.get('label_name', '').strip()
    code = request.GET.get('code', '').strip()
    machine = request.GET.get('machine', '').strip()
    date_str = request.GET.get('date', '').strip()
    
    # Apply filters if provided
    if label_name:
        items = items.filter(label_name__icontains=label_name)
    
    if code:
        items = items.filter(code__icontains=code)
    
    if machine:
        items = items.filter(machine__icontains=machine)
    
    # Date filtering
    if date_str:
        try:
            # Convert date string to datetime object
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            items = items.filter(date=filter_date)
        except ValueError:
            # If date parsing fails, skip date filtering
            pass
    
    # Pagination
    paginator = Paginator(items, 10)  # Show 10 items per page
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'items': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'items/item_list.html',context)

def item_detail(request, pk):
    item = get_object_or_404(Item.objects.prefetch_related('columns__rows'), pk=pk)
    orders = Orders.objects.filter(item_data = item)
    # Get all related colors (from ItemColumnRow where row_type = 'color_name')
    colors = []
    for column in item.columns.all():
        color_name = column.rows.filter(row_type='color_name').first()
        if color_name:
            colors.append(color_name.value)
        color_dtex = column.rows.filter(row_type='dtex').first()
        if color_dtex:
            colors.append(color_dtex.value)
        color_number = column.rows.filter(row_type='color_number').first()
        if color_number:
            colors.append(color_number.value)
        rack_no = column.rows.filter(row_type='rack_no').first()
        if rack_no:
            colors.append(rack_no.value)
        stock_kg = column.rows.filter(row_type='stock_kg').first()
        if stock_kg:
            colors.append(stock_kg.value)

    return render(request, 'items/item_detail.html', {'item': item,'colors': colors, 'odr': orders})


def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            column_count = int(request.POST.get('column_count', 0))

            try:
                with transaction.atomic():
                    for col_index in range(column_count):
                        column_name = request.POST.get(
                            f'column_{col_index}', 
                            f'Column {col_index + 1}'
                        )
                        column = ItemColumn.objects.create(
                            item=item,
                            column_name=column_name,
                            column_order=col_index
                        )

                        # Step 1: Collect all row values for this column
                        row_values = []
                        for row_index in range(4):
                            row_value = request.POST.get(
                                f'column_{col_index}_row_{row_index}-value', ''
                            )
                            row_values.append(row_value)

                        # Step 2: Process row data
                        for row_index in range(4):
                            row_value = row_values[row_index]
                            if row_index == 3:
                                if row_value:
                                    column.color_pick = row_value
                                    column.save()
                            else:
                                if row_value:
                                    ItemColumnRow.objects.create(
                                        column=column,
                                        value=row_value,
                                        row_type=[
                                            'color_name',    # Row 0
                                            'dtex',          # Row 1
                                            'color_number'   # Row 2
                                        ][row_index],
                                        row_order=row_index
                                    )

                        # Step 3: Extract relevant fields
                        color_name = row_values[0].strip()
                        color_pick_str = row_values[3].strip()

                        if color_name and color_pick_str:
                            try:
                                color_record = ColorRecord.objects.get(color_name=color_name)
                            except ColorRecord.DoesNotExist:
                                raise Exception(f"Color record not found: {color_name}")

                            try:
                                color_pick = int(color_pick_str)
                                denier = item.density
                                quantity = item.quantity
                                thread_weight = calculate_thread_weight(color_pick, denier, quantity)
                            except ValueError:
                                raise Exception("Invalid input for thread calculation.")

                            if thread_weight <= 0:
                                raise Exception("Invalid thread weight: must be greater than 0.")

                            # Convert float to Decimal before subtraction
                            thread_weight_decimal = Decimal(str(thread_weight))

                            if color_record.stock_kg < thread_weight_decimal:
                                raise Exception(f"Insufficient stock for {color_name}: required={thread_weight_decimal}, available={color_record.stock_kg}")

                            # Now both are Decimal, so subtraction is safe
                            color_record.stock_kg -= thread_weight_decimal
                            color_record.save()

                    # Step 5: Log and redirect
                    ActivityLog.objects.create(
                        action='Created',
                        description=f'Label "{item.label_name}" is added.'
                    )
                    messages.success(request, 'Item created successfully!')
                    return redirect('item_list')

            except Exception as e:
                # Rollback everything if any part fails
                item.delete()
                messages.error(request, f'Error creating item: {str(e)}')
                return render(request, 'items/item_form.html', {'form': form})

    else:
        form = ItemForm()

    # Context for rendering form
    context = {
        'form': form,
        'columns': []
    }

    if request.method == 'POST':
        column_count = int(request.POST.get('column_count', 0))
        context['columns'] = [
            {
                'column_form': ItemColumnForm(
                    prefix=f'column_{i}',
                    initial={'column_name': f'Column {i+1}'},
                    data=request.POST if request.POST else None
                ),
                'rows': [
                    ItemColumnRowForm(
                        prefix=f'column_{i}_row_{j}',
                        data=request.POST if request.POST else None
                    ) for j in range(4)
                ]
            } for i in range(column_count)
        ]

    return render(request, 'items/item_form.html', context)

def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            frm = form.save()
            # Log the activity
            ActivityLog.objects.create(
                action='update',
                description=f'Label "{frm.label_name}" is update.'
            )
            messages.success(request, 'Item updated successfully.')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'items/item_form.html', {
        'form': form,
        'item': item,
        'title': 'Edit Item',
        'submit_text': 'Update Item'
    })

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        # Log the activity
        ActivityLog.objects.create(
            action='update',
            description=f'Label "{item.label_name}" is Deleted.'
        )
        item.delete()

        messages.success(request, 'Item deleted successfully.')
        return redirect('item_list')
    
    return render(request, 'items/item_confirm_delete.html', {'item': item})



# --------------------- Validation Views ---------------------

def validate_field(request):
    field_name = request.POST.get('field_name')
    field_value = request.POST.get('field_value')
    item_id = request.POST.get('item_id')
    
    if field_name == 'code':
        # Check if code already exists
        if item_id:
            # For update case - check if code exists excluding current item
            exists = Item.objects.filter(code=field_value).exclude(pk=item_id).exists()
        else:
            # For create case - check if code exists
            exists = Item.objects.filter(code=field_value).exists()
        
        return JsonResponse({
            'valid': not exists,
            'error': 'This code is already in use' if exists else ''
        })
    else:
        # Add validation for other fields if needed
        return JsonResponse({
            'valid': True,
            'error': ''
        })
    

# --------------------- Orders Views ---------------------

def order_create(request):
    """View function to create a new order."""
    if request.method == 'POST':
        form = OrdersForm(request.POST)
        try:
            if form.is_valid():
                order = form.save()
                # Log the activity
                ActivityLog.objects.create(
                    action='Created',
                    description=f'New Order for {order.item_data} was created.'
                )
                messages.success(request, 'Order successfully created.')
                return redirect('home')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        form = OrdersForm()
    
    context = {
        'form': form,
        'action': 'Create',
        'button_text': 'Create Order',
        'form_action': reverse('order_create')
    }
    
    return render(request, 'orders/order_form.html', context)

def order_update(request, order_id):
    """View function to update an existing order."""
    order = get_object_or_404(Orders, pk=order_id)
    customers = Customer.objects.all()
    items = Item.objects.all()
    
    if request.method == 'POST':
        form = OrdersForm(request.POST, instance=order)
        try:
            if form.is_valid():
                updated_order = form.save()
                ActivityLog.objects.create(
                    action='Updated',
                    description=f'Order for {updated_order.item_data} is Updated.'
                )
                messages.success(request, 'Order successfully updated.')
                return redirect('home')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Please correct the errors below. {str(e)}')
    else:
        form = OrdersForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
        'action': reverse('order_update', args=[order_id]),
        'customers': customers,
        'items': items,
        'button_text': 'Update Order'
    }
    
    return render(request, 'orders/order_form.html', context)

def order_delete(request, order_id):
    """View function to delete an order."""
    order = get_object_or_404(Orders, id=order_id)
    ActivityLog.objects.create(
        action='Deleted',
        description=f'Order for {order.item_data.label_name} is Delete.'
    )
    # Delete the order and show success message
    order.delete()
    messages.success(request, 'Order successfully deleted.')
    return redirect('home')
 
 # --------------------- Charts Views ---------------------
def sales_chart_data(request):
    # Get the selected time period from the query parameters
    time_period = request.GET.get('time_period', 'month')  # Default to 'month'

    # Calculate the date range based on the selected time period
    end_date = now()
    if time_period == 'year':
        start_date = end_date - timedelta(days=365)
        trunc_func = TruncYear
    elif time_period == '6_months':
        start_date = end_date - timedelta(days=180)
        trunc_func = TruncMonth
    elif time_period == 'month':
        start_date = end_date - timedelta(days=30)
        trunc_func = TruncMonth
    elif time_period == 'week':
        start_date = end_date - timedelta(days=7)
        trunc_func = TruncWeek
    elif time_period == 'day':
        start_date = end_date - timedelta(days=1)
        trunc_func = TruncDate
    else:
        start_date = end_date - timedelta(days=30)  # Default to 1 month
        trunc_func = TruncMonth

    # Query the database for orders within the date range
    orders = (
        Orders.objects.filter(date__range=(start_date, end_date))
        .annotate(date_group=trunc_func('date'))  # Apply truncation function
        .values('date_group')
        .annotate(order_count=Count('id'))
        .order_by('date_group')
    )

      # Log the query results
    print("Query Results:", list(orders))

    # Format the data for the chart
    labels = [item['date_group'].strftime('%Y-%m-%d') for item in orders]
    data = [item['order_count'] for item in orders]

    # Return the data as JSON
    return JsonResponse({
        'labels': labels,
        'data': data,
    })

def activity_chart_data(request):
    # Fetch all activity logs ordered by timestamp
    logs = ActivityLog.objects.all().order_by('-timestamp')[:10]  # Limit to 50 recent logs

    # Format the data for the chart
    labels = [log.timestamp.strftime('%Y-%m-%d %H:%M') for log in logs]
    descriptions = [log.description for log in logs]

    # Generate random colors for each point
    import random
    colors = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in logs]

    # Return the data as JSON
    return JsonResponse({
        'labels': labels,
        'descriptions': descriptions,
        'colors': colors,
    })

# --------------------- PRINT Views ---------------------


def print_order(request, order_id):
    # Fetch the order and related item
    order = get_object_or_404(Orders, id=order_id)
    item = order.item_data
    customer = order.customer_data
    # Fetch columns and rows for the item
    columns = ItemColumn.objects.filter(item=item).prefetch_related('rows')

    # Preprocess rows into a structured format
    rows_data = []
    max_rows = max(column.rows.count() for column in columns) if columns else 0

    for row_order in range(max_rows):
        row_values = []
        for column in columns:
            try:
                value = column.rows.get(row_order=row_order).value
            except ItemColumnRow.DoesNotExist:
                value = ''  # Empty value if no row exists for this column
            row_values.append(value)
        rows_data.append(row_values)

    # Prepare context data
    context = {
        'order': order,
        'item': item,
        'customer': customer,
        'columns': columns,
        'rows_data': rows_data,
    }

    return render(request, 'extra/print.html', context)



class CustomerSearchView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        results = Customer.objects.filter(
            Q(name__icontains=q) | Q(email__icontains=q)
        )[:5]
        return JsonResponse({
            'results': [{'id': c.id, 'name': c.name, 'email': c.email} for c in results]
        })

class ItemSearchView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        results = Item.objects.filter(
            Q(label_name__icontains=q) | Q(code__icontains=q)
        )[:5]
        return JsonResponse({
            'results': [{'id': i.id, 'label_name': i.label_name, 'code': i.code} for i in results]
        })
    


def add_color(request):
    if request.method == 'POST':
        form = ColorRecordForm(request.POST)
        if form.is_valid():
            color_record = form.save()
            
            # Log the activity
            ActivityLog.objects.create(
                action='Created',
                description=f'New Color Record for {color_record.color_name} ({color_record.color_number}) was added.'
            )
            
            messages.success(request, 'Color record successfully created.')
            return redirect('color_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ColorRecordForm()
    
    return render(request, 'colors/add_color.html', {'form': form})

def color_list(request):
    # Get filter parameters from GET request
    color_name = request.GET.get('color_name', '')
    color_number = request.GET.get('color_number', '')
    color_dtex = request.GET.get('color_dtex', '')
    
    # Start with all records
    records = ColorRecord.objects.all()
    
    # Apply filters if parameters exist
    if color_name:
        records = records.filter(color_name__icontains=color_name)
        
    if color_number:
        records = records.filter(color_number__icontains=color_number)
        
    if color_dtex:
        records = records.filter(color_dtex=color_dtex)
    
    return render(request, 'colors/color_list.html', {
        'color_records': records,
        'filters': {
            'color_name': color_name,
            'color_number': color_number,
            'color_dtex': color_dtex
        }
    })



getcontext().prec = 10  # Set precision for calculations

def color_detail(request, pk):
    color_record = get_object_or_404(ColorRecord, pk=pk)

    # Get all items using this color
    used_in_items = Item.objects.filter(
        columns__rows__row_type='color_name',
        columns__rows__value=color_record.color_name
    ).distinct()

    total_used = Decimal('0.000')
    each_used = []
    for item in used_in_items:
        # Get all columns that use this color name
        for column in item.columns.all():
            if column.rows.filter(row_type='color_name', value=color_record.color_name).exists():
                try:
                    color_pick = int(column.color_pick)
                    thread_weight = calculate_thread_weight(
                        color_pick, 
                        item.density, 
                        item.quantity
                    )
                    each_used.append(thread_weight)
                    total_used += Decimal(str(thread_weight))
                except (ValueError, TypeError, AttributeError):
                    continue  # Skip invalid entries

    # Calculate remaining stock
    try:
        stock = color_record.stock_kg
    except (AttributeError, ValueError):
        stock = Decimal('0.000')

    remaining = max(stock, Decimal('0.000'))

    return render(request, 'colors/color_detail.html', {
        'color': color_record,
        'each_used': each_used,
        'used_labels': used_in_items,
        'total_used': total_used,
        'remaining': remaining
    })


def run_migrations(request):
    try:
        call_command('migrate', '--noinput')
        return HttpResponse("✅ Migrations applied successfully.")
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}")

def collect_static(request):
    try:
        call_command('collectstatic', '--noinput')
        return HttpResponse("✅ Static files collected.")
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}")


def create_superuser(request):
    try:
        User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        return HttpResponse("✅ Admin user created.")
    except Exception as e:
        return HttpResponse(f"❌ Error: {str(e)}")
