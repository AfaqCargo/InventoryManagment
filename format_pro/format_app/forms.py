from django.utils import timezone
from django import forms
from .models import *
from django.core.validators import (
    RegexValidator, 
    EmailValidator, 
    MinLengthValidator,
    MaxLengthValidator
)
from django.core.exceptions import ValidationError
import re

class CustomerForm(forms.ModelForm):
    name = forms.CharField(
        validators=[MinLengthValidator(2, 'Name must be at least 2 characters long')],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Customer name is required',
            'invalid': 'Enter a valid name'
        }
    )
    
    phone = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^(\+\d{1,3}[-.\s]?)?(\(\d{1,4}\)[-.\s]?)?(\d{1,4}[-.\s]?){1,4}\d{1,4}$', 
                message='Enter a valid phone number. Use digits only, optional + prefix allowed.'
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Phone number is required',
            'invalid': 'Enter a valid phone number'
        }
    )
    
    email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Email address is required',
            'invalid': 'Enter a valid email address'
        }
    )

    city = forms.CharField(
        validators=[MinLengthValidator(3, 'City must be filled')],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'City is required',
            'invalid': 'Enter your city'
        }
    )

    address = forms.CharField(
        validators=[MinLengthValidator(5, 'Address must be at least 5 characters long')],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Address is required',
            'invalid': 'Enter a complete address'
        }
    )

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'city', 'address']
        
    def clean_name(self):
        name = self.cleaned_data['name']
        # Remove extra whitespaces and capitalize
        return ' '.join(name.split()).title()
    
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Remove non-digit characters and standardize
        phone = ''.join(filter(str.isdigit, phone))
        
        # Optional: Format phone number 
        if len(phone) == 10:
            return f'({phone[:3]}) {phone[3:6]}-{phone[6:]}'
        return phone

class EmployeeForm(forms.ModelForm):
    name = forms.CharField(
        validators=[MinLengthValidator(2, 'Name must be at least 2 characters long')],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Employee name is required',
            'invalid': 'Enter a valid name'
        }
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[
            MinLengthValidator(8, 'Password must be at least 8 characters long'),
            MaxLengthValidator(32, 'Password must not exceed 32 characters'),
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).+$',
                message='Password must include uppercase, lowercase, number, and special character'
            )
        ],
        error_messages={
            'required': 'Password is required',
            'invalid': 'Enter a valid password'
        }
    )

    email = forms.EmailField(
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Email address is required',
            'invalid': 'Enter a valid email address'
        }
    )

    class Meta:
        model = Employee
        fields = ['name', 'email', 'password']
    
    def clean_password(self):
        password = self.cleaned_data['password']
        
        # Additional password strength checks
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        
        if len(password) > 32:
            raise ValidationError('Password must not exceed 32 characters')
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number')
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')
        
        return password


    def clean_name(self):
        name = self.cleaned_data['name']
        return ' '.join(name.split()).title()
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class ItemForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False  # Set to False since model allows blank=True, null=True
    )
    label_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=200  # Match the model's max_length
    )
    machine = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100  # Match the model's max_length
    )
    density = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
    )
    pick = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
    )
    choices = forms.ChoiceField(
        choices=Item.PICK_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    width = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        help_text="Width in mm"  # Added from model's help_text
    )
    length = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        help_text="Length in mm"  # Added from model's help_text
    )
    column_count = forms.IntegerField(
        widget=forms.Select(
            attrs={'class': 'form-control'},
            choices=[(i, str(i)) for i in range(0, 11)]
        ),
        validators=[MinValueValidator(1), MaxValueValidator(10)],  # Match model validators
        help_text="Number of columns (1-10)"  # Added from model's help_text
    )
    code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100  # Match the model's max_length
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
    )
    preselect = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=200  # Match the model's max_length
    )
    fold_method = forms.ChoiceField(
        choices=Item.FOLD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    label_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False,
    )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        model = Item
        fields = [
            'id', 'date', 'label_name', 'machine', 'density',
            'pick', 'choices', 'width', 'length', 'column_count',
            'code', 'quantity', 'preselect',
            'fold_method', 'label_image', 'customer'
        ]
   
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError('Date cannot be in the future')
        return date
    
    def clean_machine(self):
        machine = self.cleaned_data.get('machine')
        if not machine:
            raise ValidationError('Machine name is required')
        if not isinstance(machine, str):
            raise ValidationError('Machine must be text')
        return machine
    
    def clean_density(self):
        density = self.cleaned_data.get('density')
        if density is None:
            raise ValidationError('Density is required')
        try:
            density = int(density)
        except (ValueError, TypeError):
            raise ValidationError('Density must be a whole number')
        if density <= 0:
            raise ValidationError('Density must be greater than zero')
        return density
    
    def clean_width(self):
        width = self.cleaned_data.get('width')
        if width and width <= 0:
            raise ValidationError('Width must be greater than zero')
        return width
    
    def clean_length(self):
        length = self.cleaned_data.get('length')
        if length and length <= 0:
            raise ValidationError('Length must be greater than zero')
        return length
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise ValidationError('Quantity must be greater than zero')
        return quantity
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Check for uniqueness, excluding the current instance when editing
            instance = getattr(self, 'instance', None)
            if instance and instance.pk:
                qs = Item.objects.filter(code=code).exclude(pk=instance.pk)
            else:
                qs = Item.objects.filter(code=code)
            
            if qs.exists():
                raise ValidationError('This code is already in use')
        return code
   
    def clean(self):
        cleaned_data = super().clean()
        # Add cross-field validations if needed
        return cleaned_data

class ItemColumnForm(forms.ModelForm):
    class Meta:
        model = ItemColumn
        fields = ['column_name']
        widgets = {
            'column_number': forms.TextInput(
                attrs={'placeholder': 'Column'}
            )
        }

class ItemColumnRowForm(forms.ModelForm):
    class Meta:
        model = ItemColumnRow
        fields = ['value']
        widgets = {
            'value': forms.TextInput(
                attrs={'placeholder': 'Row'}
            )
        }

class OrdersForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['date', 'item_data', 'customer_data', 'quantity', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'item_data': forms.Select(attrs={'class': 'form-control'}),
            'customer_data': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'item_data': 'Item',
            'customer_data': 'Customer',
        }
    
    def __init__(self, *args, **kwargs):
        super(OrdersForm, self).__init__(*args, **kwargs)
        # Make the status field a dropdown with predefined choices
        self.fields['status'].widget = forms.Select(choices=[
            ('', '---------'),
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled')
        ])
        
        # Set quantity field as required
        self.fields['quantity'].required = True
        
        # Optional: You can customize the querysets for item_data and customer_data
        # For example, to show only active items:
        # self.fields['item_data'].queryset = Item.objects.filter(active=True)
        
        # Add help text for fields
        self.fields['date'].help_text = "Order date"
        self.fields['quantity'].help_text = "Number of items ordered"
        
        # Add validators
        self.fields['quantity'].validators.append(self.validate_positive_quantity)
    
    def validate_positive_quantity(self, value):
        if value <= 0:
            raise forms.ValidationError("Quantity must be greater than zero")
        return value
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        # You can add custom validation for date here
        # For example, to prevent future dates:
        from datetime import date as current_date
        if date > current_date.today():
            raise forms.ValidationError("Order date cannot be in the future")
        return date
    

class ColorRecordForm(forms.ModelForm):
    class Meta:
        model = ColorRecord
        fields = ['color_name', 'color_dtex', 'color_number', 'rack_no', 'stock_kg']
        widgets = {
            'color_name': forms.TextInput(attrs={'class': 'form-control'}),
            'color_dtex': forms.NumberInput(attrs={'class': 'form-control'}),
            'color_number': forms.TextInput(attrs={'class': 'form-control'}),
            'rack_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }