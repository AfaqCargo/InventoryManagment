from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

class Customer(models.Model):
    """Model for storing customer information"""
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    """Model for storing employee information"""
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=32, blank=False, null=False)
    def __str__(self):
        return f"{self.name} ({self.email})"

class Item(models.Model):
    # Main Item Fields
    PICK_CHOICES = [
        (576, '576'),
        (864, '864'),
        (1152, '1152'),
        (1200, '1200')
    ]

    FOLD_CHOICES = [
        ('cut_fold', 'Cut Fold'),
        ('cut_cut', 'Cut Cut'),
        ('center_fold', 'Center Fold'),
        ('hanger_fold', 'Hanger Fold'),
        ('roll', 'Roll')
    ]

    # Basic Item Information
    date = models.DateField(blank=True, null=True)
    label_name = models.CharField(max_length=200)
    machine = models.CharField(max_length=100)
    density = models.PositiveIntegerField()
    
    # Specific Item Characteristics
    choices = models.IntegerField(choices=PICK_CHOICES)
    pick = models.IntegerField()
    width = models.FloatField(help_text="Width in mm")
    length = models.FloatField(help_text="Length in mm")
    
    # Column-related Fields
    column_count = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Number of columns (1-10)"
    )
    
    # Additional Details
    code = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField()
    preselect = models.CharField(max_length=200, blank=True, null=True)
    fold_method = models.CharField(max_length=50, choices=FOLD_CHOICES)
    
    # Image Upload
    label_image = models.ImageField(
        upload_to=r'.\media\uploads', 
        blank=True, 
        null=True
    )

    # Relationships
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.label_name} - {self.code}"

class ItemColumn(models.Model):
    """
    Represents a dynamic column for an Item
    """
    item = models.ForeignKey(
        Item, 
        related_name='columns', 
        on_delete=models.CASCADE
    )
    column_name = models.CharField(max_length=255, blank=True, null=True)
    column_order = models.IntegerField(default=0)
    color_pick = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('item', 'column_order')
        ordering = ['column_order']

class ItemColumnRow(models.Model):
    """
    Represents rows within a column for an Item
    """
    column = models.ForeignKey(
        ItemColumn, 
        related_name='rows', 
        on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255, blank=True, null=True)
    row_order = models.IntegerField(default=0)

    ROW_TYPES = [
        ('color_name', 'Color Name'),
        ('dtex', 'DTEX'),
        ('color_number', 'Color Number')
    ]
    row_type = models.CharField(max_length=20, choices=ROW_TYPES)

    class Meta:
        unique_together = ('column', 'row_order')
        ordering = ['row_order']


class Orders(models.Model):
    date = models.DateField()
    item_data = models.ForeignKey(
        Item,  
        on_delete=models.CASCADE
        )
    customer_data = models.ForeignKey(
        Customer,  
        on_delete=models.CASCADE
        )
    quantity = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_action_display()}: {self.description}"
    
def calculate_thread_weight(color_pick, denier, quantity):
    """
    Calculate thread weight in kilograms for a garment label.
    
    Args:
        color_pick (float): Thread length per label (in cm)
        denier (int): Thread thickness (grams per 9,000 meters)
        quantity (int): Number of labels
    
    Returns:
        float: Total thread weight in kilograms (rounded to 3 decimal places)
    """
    # Formula: (Color Pick × Denier × Quantity) ÷ 761,682,243
    weight_grams = (color_pick * denier * quantity) / 761682243
    return round(weight_grams, 3)

class ColorRecord(models.Model):
    color_name = models.CharField(max_length=100, verbose_name="Color Name")
    color_dtex = models.PositiveIntegerField(verbose_name="DTEX")
    color_number = models.CharField(max_length=50, verbose_name="Color Number")
    rack_no = models.PositiveIntegerField(verbose_name="Rack No")
    stock_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        validators=[MinValueValidator(0)], 
        verbose_name="Stock (kg)"
    )

    def __str__(self):
        return f"{self.color_name} - {self.color_dtex} - {self.color_number}"
    
    def get_total_thread_usage(self):
        """Calculate total thread used in all labels"""
        total = Decimal('0.000')
        used_items = Item.objects.filter(
            itemcolumn__itemcolumnrow__row_type='color_name',
            itemcolumn__itemcolumnrow__value=self.color_name
        ).distinct()
        
        for item in used_items:
            for column in item.itemcolumn_set.all():
                for row in column.itemcolumnrow_set.all():
                    if row.row_type == 'color_name' and row.value == self.color_name:
                        try:
                            next_row = column.itemcolumnrow_set.filter(row_order=row.row_order + 1).first()
                            if next_row and hasattr(column, 'color_pick'):
                                color_pick = int(column.color_pick)
                                thread_weight = calculate_thread_weight(color_pick, item.density, item.quantity)
                                total += thread_weight
                        except (ValueError, TypeError):
                            continue
        return round(total, 3)
    class Meta:
        verbose_name = "Color Record"
        verbose_name_plural = "Color Records"