from django.views.generic import ListView, CreateView, DeleteView
from reviewApp.models import Review


class ReviewListView(ListView):
    model = Review
    paginate_by = 8

    def get_queryset(self):
        '''Для переключателя сортировки (через параметры) по типу /events/?order=-date  # Сортировка по дате'''

        # Сделать переключение параметра через url, для динамичесокой сортировки по убыванию и возрастанию

        order = self.request.GET.get("order", "date")
        return Review.objects.order_by(order)


class ReviewCreateView(CreateView):
    model = Review
    fields = ('text', 'rating')

class DeleteReviewView(DeleteView):
    model = Review