from django.contrib import admin
from .models import *
from .forms import ProductForm


class PatientRecordInline(admin.StackedInline):
    model = PatientRecord
    extra = 0


class RawMaterialQuantityInline(admin.StackedInline):
    model = RawMaterialQuantity
    extra = 0


class PatientAdmin(admin.ModelAdmin):
    inlines = [PatientRecordInline]
    list_display = ("name", "cc", "product_name")
    search_fields = ("name", "cc", "product_name__product_name")


class PatientRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "date")


class TraceabilityAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "purchase_date", "supplies")
    search_fields = ("invoice_number", "supplies")


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    inlines = [RawMaterialQuantityInline]
    list_display = ("product_name", "subcategory")
    search_fields = ("product_name",)
    fieldsets = (
        (None, {
            'fields': ('product_name', 'subcategory')
        }),
    )


class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ("raw_material_name", )


class RawMaterialQuantityAdmin(admin.ModelAdmin):
    list_display = ("product", "raw_material", "quantity")


admin.site.register(Patient, PatientAdmin)
admin.site.register(PatientRecord, PatientRecordAdmin)
admin.site.register(Traceability, TraceabilityAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(RawMaterial, RawMaterialAdmin)
admin.site.register(RawMaterialQuantity, RawMaterialQuantityAdmin)
