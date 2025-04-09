from django.db.models import Count
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView

from participantApp.models import Participants
from userApp.models import NotAuthUser
from .forms import EventForm
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from .models import Event,Category, EventImages
from django.db.models import Count ,F
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def registration_not_auth_user(request, event_id):
    if request.method == "GET":
        return render(request, "registration_not_auth_user.html", {"event_id": event_id})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            phone = data.get("phone")
            email = data.get("email")

            if not email or not phone:
                return JsonResponse({"message": "Укажите email и телефон"}, status=400)

            event = Event.objects.get(id=event_id)

            if event.registration_status == True:
                return JsonResponse({"message" : "Чтобы записаться на это мероприятие нужно войти аккаунт!"}, status=400)

            if event.participants.count() >= event.participants_limit:
                return JsonResponse({"message": "Нет свободных мест на мероприятие"}, status=400)

            not_auth_user, created = NotAuthUser.objects.get_or_create(
                email=email, 
                phone=phone
            )

            if Participants.objects.filter(event=event, not_auth_user=not_auth_user).exists():
                return JsonResponse({"message": "Вы уже зарегистрированы на это мероприятие"}, status=400)

            Participants.objects.create(event=event, not_auth_user=not_auth_user)

            return JsonResponse({"message": "Вы успешно зарегистрировались на мероприятие!"})

        except Event.DoesNotExist:
            return JsonResponse({"message": "Мероприятие не найдено"}, status=404)
        except Exception as e:
            import traceback
            traceback.print_exc()  
            return JsonResponse({"message": f"Ошибка: {str(e)}"}, status=500)

    return JsonResponse({"message": "Метод не поддерживается"}, status=405)



@csrf_exempt
def register_for_event(request, event_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Неверный запрос"}, status=400)

    if not request.user.is_authenticated:
        # Если не аутентифицирован, возвращаем HTML форму
        return render(request, "registration_for_event.html", {"event_id": event_id})

    try:
        event = Event.objects.annotate(
            count_place=F('participants_limit') - Count('participants')
        ).get(id=event_id)

        if event.count_place <= 0:
            return JsonResponse({"success": False, "message": "Нет свободных мест"}, status=400)

        if request.user.is_authenticated:
            if Participants.objects.filter(event=event, user=request.user).exists():
                return JsonResponse({"success": False, "message": "Вы уже записаны"}, status=400)

            Participants.objects.create(event=event, user=request.user)
            return JsonResponse({"success": True, "message": "Вы успешно записаны!"})

    except Event.DoesNotExist:
        return JsonResponse({"success": False, "message": "Событие не найдено"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Ошибка сервера: {str(e)}"}, status=500)
        
class EventListView(ListView):
    model = Event
    template_name = 'event_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


    def get_queryset(self):
        queryset = super().get_queryset()
        

        event_format = self.request.GET.get('event_format')
        if event_format in ["Online", "Offline"]:
            queryset = queryset.filter(event_format=event_format)

        date_start = self.request.GET.get('date_start')
        if date_start:
            parsed_date = parse_date(date_start) 
            if parsed_date:
                queryset = queryset.filter(date_start__date=parsed_date)

        category_id = self.request.GET.get("category")
        if category_id:
            try:
                category_id = int(category_id)  
                queryset = queryset.filter(category=category_id) 
            except (TypeError, ValueError):
                pass

        city = self.request.GET.get("city")
        if city and city != "all":  
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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event_create.html'
    
    
    def get(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated:
            raise Http404("Для создания события вы должны быть зарегистрированы")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['event_format'] = self.request.POST.get('event_format', 'Offline')
        return context

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        response = super().form_valid(form)
        
        images = self.request.FILES.getlist('event_images')
        for image in images:
            EventImages.objects.create(event=self.object, image=image)
        
        return response



class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'event_update.html'

    def get(self, request, *args, **kwargs):
        event = self.get_object() 
        if event.organizer != request.user:
            raise Http404("У вас нет прав для редактирования этого события")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()
        context['event_format'] = self.request.POST.get('event_format', 'Offline')
        context['images'] = EventImages.objects.filter(event=self.object)

        return context
    
    def form_valid(self, form):    
        self.object = form.save(commit=False)
        
        if self.request.POST.get('remove_main_photo') == 'true':

            if self.object.main_photo:
                import os
                if os.path.isfile(self.object.main_photo.path):
                    os.remove(self.object.main_photo.path)
                self.object.main_photo = None
        

        self.object.save()
        

        images_to_remove = self.request.POST.get('images_to_remove', '')
        if images_to_remove:
            image_ids = [int(id) for id in images_to_remove.split(',') if id.isdigit()]
            if image_ids:

                images_to_delete = EventImages.objects.filter(id__in=image_ids, event=self.object)
                
                import os
                for img in images_to_delete:
                    if os.path.isfile(img.image.path):
                        os.remove(img.image.path)
                
                images_to_delete.delete()

        images = self.request.FILES.getlist('event_images')
        for image in images:
            EventImages.objects.create(event=self.object, image=image)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.pk})
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    

class EventDeleteAjaxView(View):
    def delete(self, request, pk):
        try:
            event = get_object_or_404(Event, pk=pk)
            
            if event.organizer != request.user:
                return JsonResponse(any)
            
            event.delete()
            return JsonResponse({"message": "Событие удалено"}, status=200)
        except Exception as e:
            return JsonResponse({"error": "Нет прав для удаления"}, status=400)
        

class SearchResultView(ListView):
    model = Event
    template_name = 'event_search.html'
    context_object_name = 'event_list'
    
    def get_queryset(self):
        queryset = Event.objects.all()

        event_format = self.request.GET.get('event_format')
        if event_format in ["Online", "Offline"]:
            queryset = queryset.filter(event_format=event_format)

        date_start = self.request.GET.get('date_start')
        if date_start:
            parsed_date = parse_date(date_start) 
            if parsed_date:
                queryset = queryset.filter(date_start__date=parsed_date)

        category_id = self.request.GET.get("category")
        if category_id:
            try:
                category_id = int(category_id)  
                queryset = queryset.filter(category=category_id)  
            except (TypeError, ValueError):
                pass

        city = self.request.GET.get("city")
        if city and city != "all": 
            queryset = queryset.filter(city=city)

        query = self.request.GET.get('q')
        queryset = queryset.filter(Q(title__icontains = query) | Q(city__icontains=query))

        queryset = queryset.annotate(count_place=F('participants_limit') - Count('participants'))

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['cities'] = Event.objects.exclude(city__isnull=True).exclude(city="").values_list("city", flat=True).distinct()
        context['event_count'] = self.get_queryset().count()
        return context
    







