from datetime import datetime
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.views import StaffRequiredMixin
from assets.models import Asset
from .forms import WorkOrderForm
from workrequests.models import WorkRequest
from .models import WorkOrder
from django.views.generic import ListView, TemplateView
from django.utils import timezone


def apply_workorder_filters(request, qs):
    asset_id = request.GET.get('asset')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if asset_id:
        try:
            qs = qs.filter(asset_id=int(asset_id))
        except (ValueError, TypeError):
            pass

    if from_date:
        try:
            start = datetime.strptime(from_date, '%Y-%m-%d')
            qs = qs.filter(created_at__date__gte=start.date())
        except ValueError:
            pass

    if to_date:
        try:
            end = datetime.strptime(to_date, '%Y-%m-%d')
            qs = qs.filter(created_at__date__lte=end.date())
        except ValueError:
            pass

    return qs


class DashboardOverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'workorders/dashboard.html'  # Or 'workorders/dashboard.html' depending on setup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Base QuerySets for Operations
        work_orders_qs = WorkOrder.objects.all()
        work_requests_qs = WorkRequest.objects.all()

        # 2. Extract Precise Numerical Metrics
        context['pending_count'] = work_orders_qs.filter(
            status__in=['open', 'in_progress', 'Open', 'In Progress']
        ).count()
        
        context['high_priority_count'] = work_orders_qs.filter(
            status__in=['open', 'in_progress', 'Open', 'In Progress'],
            priority__iexact='high'
        ).count()
        
        context['closed_count'] = work_orders_qs.filter(
            status__iexact='closed'
        ).count()
        
        # Adjust filtering logic here if you track approved requests via a status boolean/string
        context['request_count'] = work_requests_qs.count() 

        # 3. Pull Segmented Datasets for Card Queues (Sliced for performance optimization)
        context['active_work_orders'] = work_orders_qs.filter(
            status__in=['open', 'in_progress', 'Open', 'In Progress']
        ).order_by('-priority', '-created_at')[:5]  # Emergency priority ranks first

        context['incoming_requests'] = work_requests_qs.order_by('-created_at')[:4]

        return context

class ConvertRequestToOrderView(StaffRequiredMixin, View):
    template_name = 'workorders/convert_request.html'

    def get(self, request, request_id):
        # 1. Fetch the original work request to pre-populate the form
        work_request = get_object_or_404(WorkRequest, pk=request_id)
        
        context = {
            'work_request': work_request
        }
        return render(request, self.template_name, context)

    def post(self, request, request_id):
        # 2. Fetch the work request being referenced
        work_request = get_object_or_404(WorkRequest, pk=request_id)
        # 3. Extract inputs from the engineer's form submission
        title = request.POST.get('title')
        category = request.POST.get('category')
        priority = request.POST.get('priority')
        eng_description = request.POST.get('description')
        
        # 4. Create the official technical Work Order mapped back to the request
        WorkOrder.objects.create(
            work_request=work_request,
            title=title,
            description=work_request.description,  # Retain original operator notes
            eng_description=eng_description,  # Engineer's technical instructions
            category=category,
            priority=priority,
            asset=work_request.asset,  # Automatically map the production asset
            created_by=request.user,    # Tracks the logged-in engineer who approved it
            status='open',
            request_by=work_request.created_by if work_request.created_by else None,
            request_created_at=work_request.created_at if work_request.created_at else None,
        )
        
        # Redirect back to your primary maintenance control dashboard
        return redirect(reverse('workorders:list'))


class WorkOrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = WorkOrderForm()
        return render(request, 'workorders/create.html', {'form': form})

    def post(self, request):
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            wo = form.save(commit=False)
            wo.created_by = request.user
            # Ensure `done` is never NULL at save time (DB constraint)
            if getattr(wo, 'done', None) is None:
                wo.done = form.cleaned_data.get('done', False)
            # No AI prediction — save user-provided values only
            wo.save()
            messages.success(request, 'Work order created.')
            return redirect(reverse('workorders:list'))

        return render(request, 'workorders/create.html', {'form': form})


class WorkOrderListView(LoginRequiredMixin, View):
    def get(self, request):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

        qs = WorkOrder.objects.filter(status__in=['open', 'in_progress', 'Open', 'In Progress']).order_by('-created_at')
        qs = apply_workorder_filters(request, qs)

        paginator = Paginator(qs, 20)
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']

        return render(
            request,
            'workorders/list.html',
            {
                'object_list': page_obj.object_list,
                'page_obj': page_obj,
                'assets': Asset.objects.all().order_by('asset_name'),
                'filter_asset': request.GET.get('asset', ''),
                'filter_from_date': request.GET.get('from_date', ''),
                'filter_to_date': request.GET.get('to_date', ''),
                'query_string': query_params.urlencode(),
            }
        )

class ClosedWorkOrderListView(LoginRequiredMixin, View):
    def get(self, request):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

        qs = WorkOrder.objects.filter(status='closed').order_by('-created_at')
        qs = apply_workorder_filters(request, qs)

        paginator = Paginator(qs, 30)
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        query_params = request.GET.copy()
        if 'page' in query_params:
            del query_params['page']

        return render(
            request,
            'workorders/closed.html',
            {
                'object_list': page_obj.object_list,
                'page_obj': page_obj,
                'assets': Asset.objects.all().order_by('asset_name'),
                'filter_asset': request.GET.get('asset', ''),
                'filter_from_date': request.GET.get('from_date', ''),
                'filter_to_date': request.GET.get('to_date', ''),
                'query_string': query_params.urlencode(),
            }
        )


class WorkOrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        wo = WorkOrder.objects.filter(pk=pk).first()
        if not wo:
            messages.error(request, 'Work order not found.')
            return redirect(reverse('workorders:list'))
        return render(request, 'workorders/detail.html', {'object': wo})


class WorkOrderUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        wo = WorkOrder.objects.filter(pk=pk).first()
        if not wo:
            messages.error(request, 'Work order not found.')
            return redirect(reverse('workorders:list'))
        # permission: only admin or creator
        if not (request.user.is_superuser or wo.created_by == request.user):
            messages.error(request, 'You do not have permission to edit this work order.')
            return redirect(reverse('workorders:detail', args=[pk]))
        from .forms import WorkOrderUpdateForm
        form = WorkOrderUpdateForm(instance=wo)
        return render(request, 'workorders/edit.html', {'form': form, 'object': wo})

    def post(self, request, pk):
        wo = WorkOrder.objects.filter(pk=pk).first()
        if not wo:
            messages.error(request, 'Work order not found.')
            return redirect(reverse('workorders:list'))
        if not (request.user.is_superuser or wo.created_by == request.user):
            messages.error(request, 'You do not have permission to edit this work order.')
            return redirect(reverse('workorders:detail', args=[pk]))
        from .forms import WorkOrderUpdateForm
        form = WorkOrderUpdateForm(request.POST, instance=wo)
        if form.is_valid():
            updated = form.save()
            messages.success(request, 'Work order updated.')
            return redirect(reverse('workorders:detail', args=[updated.pk]))
        return render(request, 'workorders/edit.html', {'form': form, 'object': wo})


class WorkOrderDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        wo = WorkOrder.objects.filter(pk=pk).first()
        if not wo:
            messages.error(request, 'Work order not found.')
            return redirect(reverse('workorders:list'))
        # allow only admin or creator to see confirmation
        if not (request.user.is_superuser or wo.created_by == request.user):
            messages.error(request, 'You do not have permission to delete this work order.')
            return redirect(reverse('workorders:detail', args=[pk]))
        return render(request, 'workorders/confirm_delete.html', {'object': wo})

    def post(self, request, pk):
        wo = WorkOrder.objects.filter(pk=pk).first()
        if not wo:
            messages.error(request, 'Work order not found.')
            return redirect(reverse('workorders:list'))
        if not (request.user.is_superuser or wo.created_by == request.user):
            messages.error(request, 'You do not have permission to delete this work order.')
            return redirect(reverse('workorders:detail', args=[pk]))
        wo.delete()
        messages.success(request, 'Work order deleted.')
        return redirect(reverse('workorders:list'))
  

class MonthlyWorkOrderReportView(ListView):
    model = Asset
    template_name = 'workorders/monthly_report.html'
    context_object_name = 'machines'

    def get_queryset(self):
        # 1. Fallback to current date if parameters aren't chosen yet
        now = timezone.now()
        
        # 2. Extract selected values from GET request parameters
        selected_month = self.request.GET.get('month')
        selected_year = self.request.GET.get('year')
        
        # Validate and parse input parameters; fallback to current if invalid
        try:
            month = int(selected_month) if selected_month else now.month
            year = int(selected_year) if selected_year else now.year
            # Create a localized datetime object for the first day of that target month
            start_of_month = timezone.make_aware(datetime(year, month, 1))
        except ValueError:
            month = now.month
            year = now.year
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 3. Handle upper bound calculation safely (handles year wrapping for December)
        if month == 12:
            end_of_month = timezone.make_aware(datetime(year + 1, 1, 1))
        else:
            end_of_month = timezone.make_aware(datetime(year, month + 1, 1))

        # 4. Filter work orders within this exact custom time range window
        monthly_work_orders = WorkOrder.objects.filter(
            created_at__gte=start_of_month,
            created_at__lt=end_of_month
        ).order_by('-created_at')

        # 5. Filter assets that have records within this specific timeframe
        return Asset.objects.filter(
            workorder__created_at__gte=start_of_month,
            workorder__created_at__lt=end_of_month
        ).distinct().prefetch_related(
            Prefetch('workorder_set', queryset=monthly_work_orders, to_attr='current_month_orders')
        ).order_by('asset_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Pass the currently active selections back to the template context
        selected_month = self.request.GET.get('month')
        selected_year = self.request.GET.get('year')
        
        context['current_month'] = int(selected_month) if selected_month else now.month
        context['current_year'] = int(selected_year) if selected_year else now.year
        
        # Generate year arrays for selection window options (e.g., last 5 years)
        context['year_range'] = range(now.year - 4, now.year + 1)
        
        # Nice string label for report printing headers
        target_date = datetime(context['current_year'], context['current_month'], 1)
        context['report_month_label'] = target_date.strftime('%B %Y')
        
        return context