from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
import re

from .models import Category, Dictionary, DictionaryEntry, Language, Word
from .forms import UpdateEntryForm, UpdateEntriesForm, FiltersForm


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


def filters(request):
    if(request.POST):
        if('_apply_filters' in request.POST):
            form = FiltersForm(request.POST)
            if form.is_valid():
                fc = form.cleaned_data
                request.session['category'] = None if not fc['category'] else fc['category'].pk
                request.session['category_exclude'] = fc['category_exclude']
                request.session['dictionary'] = None if not fc['dictionary'] else fc['dictionary'].pk
                request.session['dictionary_exclude'] = fc['dictionary_exclude']
        elif('_reset_filters' in request.POST):
            param_names = ['category', 'category_exclude', 'dictionary', 'dictionary_exclude']
            for param in param_names:
                request.session[param] = None
    return redirect(reverse('allwords'), template_name='all_entries.html')


def create_filter_form(request):
    initial = {}
    category_pk = request.session.get('category')
    if(category_pk):
        initial['category'] = Category.objects.get(pk=category_pk)
    dictionary_pk = request.session.get('dictionary')
    if(dictionary_pk):
        initial['dictionary'] = Dictionary.objects.get(pk=dictionary_pk)
    simple_values = ['category_exclude', 'dictionary_exclude']
    for param in simple_values:
        value = request.session.get(param)
        if(value):
            initial[param] = value
    
    form = FiltersForm(initial=initial)
    return form


def all_entries(request):
    page = 1
    per_page = request.session.get('per_page', 2)
    if(request.GET):
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", per_page)
        request.session['per_page'] = per_page

    form = manage_entries_request(request)
    entries = DictionaryEntry.objects.all()
    paginator = Paginator(entries, per_page)
    page_object = paginator.get_page(page)
    
    context = {
        'words':page_object.object_list,
        'categories': Category.objects.all(),
        'dictionaries': Dictionary.objects.all(),
        'form':form,
        'filter_form':create_filter_form(request),
        'is_paginated': True,
        "page_obj": page_object
    }
    return render(request, 'all_entries.html', context=context)


def category(request, pk):
    page = 1
    per_page = request.session.get('per_page', 2)
    if(request.GET):
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", per_page)
        request.session['per_page'] = per_page
    
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
    form = manage_entries_request(request)
    dictionary = Dictionary.objects.get(pk=pk)
    entries = DictionaryEntry.objects.filter(dictionary__id__contains=dictionary.id)
    
    context = {
        'dictionary': dictionary,
        'words': entries,
        'categories': Category.objects.all(),
        'dictionaries': Dictionary.objects.all(),
        'form':form,
    }
    return render(request, 'dictionary.html', context=context)


def add_entry(request, pk=None):
#    return edit_entry(request,None)

# def edit_entry(request, pk):
    result = ''
    if request.method == 'POST':
        form = UpdateEntryForm(request.POST)
        if form.is_valid():
            fc = form.cleaned_data 
                
            from_lang = Language.objects.get(code=fc['from_lang'].code)
            to = Language.objects.get(code=fc['to'].code)
            categories = fc['categories']
            if(fc['entry'] != None and not fc['entry_save_as_new']):
                entry = fc['entry']
                if(fc['word_save_as_new']):
                    entry.word = create_word(fc['word'], from_lang, categories)
                else:
                    change_word(entry.word, fc['word'], from_lang, categories)                                
                
                if(fc['translation_save_as_new']):
                    entry.translation = create_word(fc['translation'], to, categories)
                else:
                    change_word(entry.translation, fc['translation'], to, categories)
                entry.transcription = fc['transcription']
                entry.save()
                entry.dictionary.set(fc['dictionaries'])
                result = "Seccessfuly added: " + str(entry)
            else:
                word = get_or_create_word(fc['word'], from_lang, categories)
                translation = get_or_create_word(fc['translation'], to, categories)
                entry = DictionaryEntry(word=word, translation=translation)
                
                entry.transcription = fc['transcription']
                entry.save()
                entry.dictionary.set(fc['dictionaries'])
                result = "Seccessfuly added: " + str(entry) 
        if('_save' in request.POST):
            return all_entries(request)        
        elif('_continue' in request.POST):
            path = re.sub('/(\d)*$', '/' + str(entry.pk), request.path_info)
            context = {
                'form':form,
                'result':result
            }
            return redirect(path, template_name='edit_entry.html', context=context)            
        elif('_addanother' in request.POST):
            form = get_initial_update_form()
            path = re.sub('/(\d)*$', '/', request.path_info)
            context = {
                'form':form,
                'result':result
            }
            return redirect(path, template_name='edit_entry.html', context=context)
    else:
        entry = None
        if(pk != None):
            try:
                entry = DictionaryEntry.objects.get(pk=pk)
            except ObjectDoesNotExist:
                pass
        form = get_initial_update_form(entry)
    
    context = {
        'form':form,
        'result':result
    }
    return render(request, 'edit_entry.html', context=context)


def get_initial_update_form(entry=None):
    from_lang = Language.objects.get(code='es')
    to_lang = Language.objects.get(code='uk')
    if(entry != None):
        initial = {'from_lang': entry.word.language.code, 'to':entry.translation.language.code} 
        initial['entry'] = entry
        initial['word'] = entry.word.word
        initial['transcription'] = entry.transcription
        initial['translation'] = entry.translation.word
        initial['categories'] = entry.word.category.all().values_list("pk", flat=True)
        initial['dictionaries'] = entry.dictionary.all().values_list("pk", flat=True)     
    else:
        initial = {'from_lang': from_lang.code, 'to':to_lang}        
    form = UpdateEntryForm(initial)
    return form


def get_or_create_word(word_text, lang, categories):
    try:
        return Word.objects.filter(word=word_text).first()
    except ObjectDoesNotExist:
       word = Word(word=word_text)
    word.language = lang
    word.save()
    word.category.set(categories)
    word.save()
    return word


def create_word(word_text, lang, categories):
    word = Word(word=word_text)
    word.language = lang
    word.save()
    word.category.set(categories)
    word.save()
    return word

       
def change_word(entry_word, word_text, lang, categories): 
    entry_word.word = word_text
    entry_word.language = lang
    entry_word.category.set(categories)
    entry_word.save()

    
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
