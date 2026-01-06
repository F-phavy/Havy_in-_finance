from django import forms
from . models import Expense



class ExpenseForm(forms.ModelForm):
    long_term = forms.BooleanField(required=False)


    class Meta:
        model = Expense
        fields = ['name', 'amount', 'interest_rate', 'date', 'end_date', 'long_term']


        widgets = {
            'name': forms.TextInput(attrs={'class': 'forms-control'}),
            'amount': forms.NumberInput(attrs={'class': 'forms-control'}),
            'date': forms.DateInput(attrs={'class': 'forms-control', 'type': 'date'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'forms-control'}),
            'end_date': forms.DateInput(attrs={'class': 'forms-control', 'type': 'date'}), 
            'long_term': forms.CheckboxInput(attrs={'class': 'forms-control'}),
}



    def clean(self):
            cleaned_data = super().clean()
            long_term = cleaned_data.get("long_term") 
            start_date = cleaned_data.get('date')

            if long_term:
                interest_rate = cleaned_data.get('interest_rate')
                end_date  = cleaned_data.get('end_date')
                amount = cleaned_data.get('amount')
                cleaned_data['long_term'] = True
            else:
                cleaned_data['end_date'] = None
                cleaned_data['interest_rate'] = None


                return cleaned_data

                             