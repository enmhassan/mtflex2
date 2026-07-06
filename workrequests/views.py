from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.views import CreatorRequiredMixin
from .models import WorkRequest
from .forms import WorkRequestForm


class WorkRequestCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = WorkRequestForm()
        return render(request, 'workrequests/create.html', {'form': form})

    def post(self, request):
        form = WorkRequestForm(request.POST)
        if form.is_valid():
            wr = form.save(commit=False)
            wr.created_by = request.user
            # Ensure `done` is never NULL at save time (DB constraint)
            if getattr(wr, 'done', None) is None:
                wr.done = form.cleaned_data.get('done', False)
            # No AI prediction — save user-provided values only
            wr.save()
            messages.success(request, 'Work request created.')
            return redirect(reverse('workrequests:list'))

        return render(request, 'workrequests/create.html', {'form': form})



class WorkRequestDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        wr = WorkRequest.objects.filter(pk=pk).first()
        if not wr:
            messages.error(request, 'Work request not found.')
            return redirect(reverse('workrequests:list'))
        return render(request, 'workrequests/detail.html', {'object': wr})


class WorkRequestListView(LoginRequiredMixin, View):
    def get(self, request):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        qs = WorkRequest.objects.filter(converted_order__isnull=True).order_by('-created_at')
        paginator = Paginator(qs, 5)
        page = request.GET.get('page')
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return render(request, 'workrequests/list.html', {'object_list': page_obj.object_list, 'page_obj': page_obj})



class WorkRequestUpdateView(CreatorRequiredMixin, LoginRequiredMixin, View):
    def get_object(self):
        # This tells the Mixin how to look up the record using the URL's 'pk'
        from django.shortcuts import get_object_or_404
        return get_object_or_404(WorkRequest, pk=self.kwargs.get('pk'))

    def get(self, request, pk):
        wr = WorkRequest.objects.filter(pk=pk).first()
        if not wr:
            messages.error(request, 'Work request not found.')
            return redirect(reverse('workrequests:list'))
        # permission: only admin or creator
        if not (request.user.is_superuser or wr.created_by == request.user):
            messages.error(request, 'You do not have permission to edit this work order.')
            return redirect(reverse('workrequests:detail', args=[pk]))
        from .forms import WorkRequestUpdateForm
        form = WorkRequestUpdateForm(instance=wr)
        return render(request, 'workrequests/edit.html', {'form': form, 'object': wr})

    def post(self, request, pk):
        wr = WorkRequest.objects.filter(pk=pk).first()
        if not wr:
            messages.error(request, 'Work request not found.')
            return redirect(reverse('workrequests:list'))
        if not (request.user.is_superuser or wr.created_by == request.user):
            messages.error(request, 'You do not have permission to edit this work order.')
            return redirect(reverse('workrequests:detail', args=[pk]))
        from .forms import WorkRequestUpdateForm
        form = WorkRequestUpdateForm(request.POST, instance=wr)
        if form.is_valid():
            updated = form.save()
            messages.success(request, 'Work request updated.')
            return redirect(reverse('workrequests:detail', args=[updated.pk]))
        return render(request, 'workrequests/edit.html', {'form': form, 'object': wr})


class WorkRequestDeleteView(CreatorRequiredMixin, LoginRequiredMixin, View):

    def get_object(self):
        # This tells the Mixin how to look up the record using the URL's 'pk'
        from django.shortcuts import get_object_or_404
        return get_object_or_404(WorkRequest, pk=self.kwargs.get('pk'))
    

    def get(self, request, pk):
        wr = WorkRequest.objects.filter(pk=pk).first()
        if not wr:
            messages.error(request, 'Work request not found.')
            return redirect(reverse('workrequests:list'))
        # allow only admin or creator to see confirmation
        if not (request.user.is_superuser or wr.created_by == request.user):
            messages.error(request, 'You do not have permission to delete this work order.')
            return redirect(reverse('workrequests:detail', args=[pk]))
        return render(request, 'workrequests/confirm_delete.html', {'object': wr})

    def post(self, request, pk):
        wr = WorkRequest.objects.filter(pk=pk).first()
        if not wr:
            messages.error(request, 'Work request not found.')
            return redirect(reverse('workrequests:list'))
        if not (request.user.is_superuser or wr.created_by == request.user):
            messages.error(request, 'You do not have permission to delete this work order.')
            return redirect(reverse('workrequests:detail', args=[pk]))
        wr.delete()
        messages.success(request, 'Work request deleted.')
        return redirect(reverse('workrequests:list'))
