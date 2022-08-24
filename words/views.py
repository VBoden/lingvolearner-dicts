from django.shortcuts import render

from .models import Category, Dictionary, DictionaryEntry, Language, Word

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
