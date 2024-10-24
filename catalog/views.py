from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .models import Book, Author, BookInstance
from .forms import RenewBookForm

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact = 'o').order_by('due_back')

def index(request):
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    search_word = request.GET.get('search_word', '')
    search_word_lower = search_word.lower()

    if search_word:
        book_count = Book.objects.filter(title__icontains=search_word_lower).count()
    else:
        book_count = 0

    return render(
        request,
'index.html',context=
{'num_books':num_books,
 'num_instances':num_instances,
 'num_instances_available':num_instances_available,
 'num_authors':num_authors,
 'num_visits':num_visits,
 'book_count':book_count,
 'search_word':search_word,
 }
)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookListView(generic.ListView):
    model = Book

class BookDetailView(generic.DetailView):
    model = Book


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_inst.due_back = book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
        return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks = 3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})
