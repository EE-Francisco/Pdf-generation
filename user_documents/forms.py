from django import forms
from django.core.exceptions import ValidationError
from .models import Product, SUBCATEGORY_CHOICES


class ProductForm(forms.ModelForm):
    subcategory = forms.ChoiceField(choices=SUBCATEGORY_CHOICES, required=False)

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subcategory'].widget.attrs['id'] = 'id_subcategory'

    def clean(self):
        cleaned_data = super().clean()
        product_name = cleaned_data.get('product_name')
        subcategory = cleaned_data.get('subcategory')

        if product_name and subcategory:
            valid_subcategories = [choice[0] for choice in SUBCATEGORY_CHOICES]
            if subcategory not in valid_subcategories:
                raise ValidationError('Seleccione una subcategoría válida.')

        return cleaned_data

    class Media:
        js = ('js/product_form.js',)
