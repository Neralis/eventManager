from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from .forms import EventForm, EventImagesForm
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Event,Category, EventImages
from django.db.models import Count ,F


def primer(request):
   
    return render(request, 'primer.html')


class EventListView(ListView):
    model = Event
    template_name = 'event_list.html'
    paginate_by = 20


    def get_queryset(self):
        queryset = super().get_queryset()
        

        event_format = self.request.GET.get('event_format')
        if event_format in ["Online", "Offline"]:
            queryset = queryset.filter(event_format=event_format)

        date_start = self.request.GET.get('date_start')
        if date_start:
            parsed_date = parse_date(date_start)  # Преобразуем строку в дату
            if parsed_date:
                queryset = queryset.filter(date_start__date=parsed_date)

        category_id = self.request.GET.get("category")
        if category_id:
            try:
                category_id = int(category_id)  # Преобразуем строку в число
                queryset = queryset.filter(category=category_id)  # category вместо category_id
            except (TypeError, ValueError):
                pass

        city = self.request.GET.get("city")
        if city and city != "all":  # Если city не "all", применяем фильтр
            queryset = queryset.filter(city=city)


        queryset = queryset.annotate(count_place=F('participants_limit') - Count('participants'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['cities'] = Event.objects.exclude(city__isnull=True).exclude(city="").values_list("city", flat=True).distinct()

        queryset = self.get_queryset()
        
        context['event_count'] = queryset.count()

        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object = self.get_object()  # Явно получаем объект

        context['count_place'] = object.participants_limit - object.participants.count()
        context['event_images'] = object.event_images.all()  # Это QuerySet изображений
        context['organizer_phone'] = object.organizer.phone
        context['organizer_events'] = Event.objects.filter(organizer=object.organizer).exclude(id=object.id)[:6]
        context['reviews'] = object.reviews.all()
        context['similiar_events'] = Event.objects.filter(category__in=object.category.all()).exclude(id=object.id)[:6]

        return context

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event_create.html'

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['event_format'] = self.request.POST.get('event_format', 'Offline')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Получаем загруженные изображения из запроса
        images = self.request.FILES.getlist('event_images')
        for image in images:
            EventImages.objects.create(event=self.object, image=image)
        
        return response



class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'event_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['event_format'] = self.request.POST.get('event_format', 'Offline')
        context['images'] = EventImages.objects.filter(event=self.object)
        return context

    def form_valid(self, form):
        print("✅ Форма валидна, объект сохраняется!")
        
        # Сохраняем форму, но не коммитим изменения в базу данных
        self.object = form.save(commit=False)
        
        # Проверяем, нужно ли удалить главное изображение
        if self.request.POST.get('remove_main_photo') == 'true':
            # Удаляем файл с диска, если нужно
            if self.object.main_photo:
                import os
                if os.path.isfile(self.object.main_photo.path):
                    os.remove(self.object.main_photo.path)
                self.object.main_photo = None
        
        # Сохраняем изменения в мероприятии
        self.object.save()
        
        # Обрабатываем удаление дополнительных изображений
        images_to_remove = self.request.POST.get('images_to_remove', '')
        if images_to_remove:
            image_ids = [int(id) for id in images_to_remove.split(',') if id.isdigit()]
            if image_ids:
                # Получаем изображения, которые нужно удалить
                images_to_delete = EventImages.objects.filter(id__in=image_ids, event=self.object)
                
                # Удаляем файлы с диска
                import os
                for img in images_to_delete:
                    if os.path.isfile(img.image.path):
                        os.remove(img.image.path)
                
                # Удаляем записи из базы данных
                images_to_delete.delete()
        
        # Обрабатываем новые дополнительные изображения
        images = self.request.FILES.getlist('event_images')
        for image in images:
            EventImages.objects.create(event=self.object, image=image)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class EventDeleteAjaxView(View):
    def delete(self, request, pk, *args, **kwargs):
        try:
            event = get_object_or_404(Event, pk=pk)
            event.delete()
            return JsonResponse({"message": "Событие удалено"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)







