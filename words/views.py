from django.shortcuts import render
from django.views import generic

from .models import Category, Dictionary, DictionaryEntry, Language, Word
from .forms import UpdateEntryForm

class DictionaryEntriesView(generic.ListView):
    model = DictionaryEntry
    paginate_by = 10
    context_object_name = 'words'
#    queryset = Book.objects.filter(title__icontains='war')[:5]
    template_name = 'all_entries.html'

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

def category(request, pk):
    category = Category.objects.get(pk=pk)
    entries = DictionaryEntry.objects.filter(word__category__id__contains=category.id)
    
    context = {
        'category': category,
        'words': entries,
        'categories': Category.objects.all(),
        'dictionaries': Dictionary.objects.all(),
    }
    return render(request, 'category.html', context=context)

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
            context = {
                'words':DictionaryEntry.objects.all()
            }
            return render(request, 'all_entries.html', context=context)
    else:
        from_lang = Language.objects.get(code='es')
        to_lang = Language.objects.get(code='uk')
        form = UpdateEntryForm(initial={'from_lang': from_lang.code,'to':to_lang})
        result = ''
    
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
    
    
    
    