from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from exp_Tracker import models
from .models import Account, Expense
from .forms import ExpenseForm
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.generic import ListView
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, F
import plotly.express as px
from plotly.graph_objs import *
from django.contrib.auth.mixins import LoginRequiredMixin



# Create your views here.

def home(request):
    return render(request, 'home/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



def generate_graph(data):
    fig = px.bar(data, x='months', y='expenses', title='Monthly Expenses')
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=True)),
        paper_bgcolor='rgba(0, 0, 0 ,0 )',
        plot_bgcolor='rgba(0, 0, 0, 0 )',
        font_color = 'rgba(0, 0, 0, 1)'
    )
    fig.update_traces(marker_color = 'blue')

    graph_json = fig.to_json()

    return graph_json



class ExpenseListView(LoginRequiredMixin, FormView):
    template_name = 'exp_Tracker/expense_list.html'
    form_class = ExpenseForm
    success_url = "/expenses/"  

    def form_valid(self, form):
        
        expense = form.save(commit=False)
        expense.user = self.request.user
        expense.save()

       
        account, _ = Account.objects.get_or_create(user=self.request.user)
        account.expense_list.add(expense)
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        
        expenses = Expense.objects.filter(user=user).order_by('date')

        expense_data_graph = {}

        for expense in expenses:
            if expense.long_term and expense.end_date:
                current_date = expense.date
                while current_date <= expense.end_date:
                    year_month = current_date.strftime('%Y-%m')
                    if year_month not in expense_data_graph:
                        expense_data_graph[year_month] = []

                    expense_data_graph[year_month].append({
                        'name': expense.name,
                        'amount': expense.amount,
                        'date': expense.date,
                        'end_date': expense.end_date,
                        'long_term': True
                    })
                    current_date = current_date + relativedelta(months=1)
            else:
                year_month = expense.date.strftime('%Y-%m')
                if year_month not in expense_data_graph:
                    expense_data_graph[year_month] = []

                expense_data_graph[year_month].append({
                    'name': expense.name,
                    'amount': expense.amount,
                    'date': expense.date,
                    'long_term': False
                })

        
        sorted_keys = sorted(expense_data_graph.keys())
        aggregated_data = [
            {
                'year_month': key, 
                'expenses': sum(item['amount'] for item in expense_data_graph[key])
            } for key in sorted_keys
        ]   

    
        context['expense_data'] = expense_data_graph  
        context['aggregated_data'] = aggregated_data

        graph_data = {
            'months': [item['year_month'] for item in aggregated_data],
            'expenses': [item['expenses'] for item in aggregated_data],
        }

        if aggregated_data:
            context['graph_data'] = mark_safe(generate_graph(graph_data))
        else:
            context['graph_data'] = mark_safe("{}") 

        return context