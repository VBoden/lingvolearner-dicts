from django.shortcuts import render
from django.views import generic
from django.core.paginator import Paginator

from .models import Category, Dictionary, DictionaryEntry, Language, Word
from .forms import UpdateEntryForm, UpdateEntriesForm

class DictionaryEntriesView(generic.ListView):
    model = DictionaryEntry
    paginate_by = 2
    context_object_name = 'words'
#    queryset = Book.objects.filter(title__icontains='war')[:5]
    template_name = 'all_entries.html'
    
    def setup(self, request, *args, **kwargs):
        self.form = manage_entries_request(request)
        return super().setup(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = DictionaryEntry.objects.all().count()
    num_instances = DictionaryEntry.objects.all().count()

    # Available books (status = 'a')
#    num_instances_available = DictionaryEntry.objects.filter(status__exact='a').count()
    num_instances_available = DictionaryEntry.objects.count()

    # The 'all()' is implied by default.
#    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': DictionaryEntry.objects.all(),
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def categories_dicts(request):

    context = {
        'categories': Category.objects.all(),
        'dictionaries': Dictionary.objects.all(),
    }

    return render(request, 'categories_and_dicts.html', context=context)

def all_entries(request):
    page = 1
    per_page = 2
    if(request.GET):
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 2)

    form = manage_entries_request(request)
    entries = DictionaryEntry.objects.all()
    paginator = Paginator(entries, per_page)
    page_object = paginator.get_page(page)
    
    context = {
        'words':page_object.object_list,
        'categories': Category.objects.all(),
        'dictionaries': Dictionary.objects.all(),
        'form':form,
        'is_paginated': True,
        "page_obj": page_object
    }
    return render(request, 'all_entries.html', context=context)

def category(request, pk):
    page = 1
    per_page = 2
    if(request.GET):
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 2)
    
    form = manage_entries_request(request)
    category = Category.objects.get(pk=pk)
    entries = DictionaryEntry.objects.filter(word__category__id__contains=category.id)
    paginator = Paginator(entries, per_page)
    page_object = paginator.get_page(page)
    
    context = {
        'category': category,
        'words':page_object.object_list,
        'categories': Category.objects.all(),
        'dictionaries': Dictionary.objects.all(),
        'form':form,
        'is_paginated': True,
        "page_obj": page_object
    }
    return render(request, 'category.html', context=context)

def manage_entries_request(request):
    
    if request.method == 'POST':
        print('\n\n\n\n\n==post===')
        print(request)
        form = edit_entries(request)        
    else:        
        print('\n\n\n\n\n===get==')
        print(request)
        form = UpdateEntriesForm()
    return form

def dictionary(request, pk):
    dictionary = Dictionary.objects.get(pk=pk)
    entries = DictionaryEntry.objects.filter(dictionary__id__contains=dictionary.id)
    
    context = {
        'dictionary': dictionary,
        'words': entries,
        'categories': Category.objects.all(),
        'dictionaries': Dictionary.objects.all(),
    }
    return render(request, 'dictionary.html', context=context)

def add_entry(request):
    return edit_entry(request,None)

def edit_entry(request, pk):
    result = ''
    if request.method == 'POST':
        form = UpdateEntryForm(request.POST)
        if form.is_valid():
            fc = form.cleaned_data 
                
            from_lang = Language.objects.get(code=fc['from_lang'].code)
            word = create_word(fc['word'],from_lang,fc['categories'])
            to = Language.objects.get(code=fc['to'].code)
            translation = create_word(fc['translation'],to,fc['categories'])
            entry = DictionaryEntry(word = word, transcription=fc['transcription'],translation=translation)
            entry.save()
            entry.dictionary.set(fc['dictionaries'])
            result = "Seccessfuly added: "+ str(entry)
        if('_save' in request.POST):
#            context = {
#                'words':DictionaryEntry.objects.all()
#            }
#            return render(request, 'all_entries.html', context=context)
            return all_entries(request)
    else:
        from_lang = Language.objects.get(code='es')
        to_lang = Language.objects.get(code='uk')
        form = UpdateEntryForm(initial={'from_lang': from_lang.code,'to':to_lang})
    
    context = {
        'form':form,
        'result':result
    }
    return render(request, 'edit_entry.html', context=context)
    
def create_word(word_text,lang,categories):
    word = Word(word=word_text,language=lang)
    word.save()
    word.category.set(categories)
    word.save()
    return word
    
def edit_entries(request):
    form = UpdateEntriesForm(request.POST)
    entries = []
    for e in request.POST.getlist('entries'):
        entries.append(DictionaryEntry.objects.get(pk=e))
    if form.is_valid():
        fc = form.cleaned_data
        if('_add_dictionary' in request.POST and fc['dictionary'] != None):
            for entry in entries:
                entry.dictionary.add(fc['dictionary'])
                entry.save()
        elif('_remove_dictionary' in request.POST and fc['dictionary'] != None):
            for entry in entries:
                entry.dictionary.remove(fc['dictionary'])
                entry.save()
        elif('_add_category' in request.POST and fc['category'] != None):
            for entry in entries:
                entry.word.category.add(fc['category'])
                entry.translation.category.add(fc['category'])
                entry.save()
        elif('_remove_category' in request.POST and fc['category'] != None):
            for entry in entries:
                entry.word.category.remove(fc['category'])
                entry.translation.category.remove(fc['category'])
                entry.save()
        elif('_delete_entries_with_words' in request.POST):
            for entry in entries:
                entry.word.delete()
                entry.translation.delete()
                entry.delete()
        elif('_delete_entries' in request.POST):
            for entry in entries:
                entry.delete()
    return form