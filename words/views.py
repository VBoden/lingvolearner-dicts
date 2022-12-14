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


def reset_filters(request):
    param_names = ['category', 'category_exclude', 'dictionary', 'dictionary_exclude']
    for param in param_names:
        request.session[param] = None


def change_per_page(request):
    if(request.POST):
        print('\n\n')
        print(request.POST.get('per_page'))
        request.session['per_page'] = request.POST.get('per_page')
    return redirect(reverse('allwords'), template_name='all_entries.html')


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
                request.session['sortby'] = fc['sortby']
                request.session['sortby_desc'] = fc['sortby_desc']
        elif('_reset_filters' in request.POST):
            reset_filters(request)
    if(request.POST.get('source') == reverse('allwords')):
        return redirect(reverse('allwords'), template_name='all_entries.html')
    else:
        return redirect(reverse('export_to_file'), template_name='export_to_file.html')


def create_filter_form(request):
    initial = {}
    initial['category'] = get_category_from_session(request)
    initial['dictionary'] = get_dictionary_from_session(request)
    simple_values = ['category_exclude', 'dictionary_exclude', 'sortby', 'sortby_desc']
    for param in simple_values:
        value = request.session.get(param)
        if(value):
            initial[param] = value
    
    form = FiltersForm(initial=initial)
    return form


def get_category_from_session(request):
    category_pk = request.session.get('category')
    if(category_pk):
        return Category.objects.get(pk=category_pk)
    return None


def get_dictionary_from_session(request):
    dictionary_pk = request.session.get('dictionary')
    if(dictionary_pk):
        return Dictionary.objects.get(pk=dictionary_pk)
    return None


def all_entries(request):
    if(request.session.get('reset_filters', False)):
        request.session['reset_filters'] = False
        reset_filters(request)
    context = handle_all_entries(request)
    return render(request, 'all_entries.html', context=context)


def get_entries(request):
    entries = DictionaryEntry.objects.all()
    category = get_category_from_session(request)
    dictionary = get_dictionary_from_session(request)
    if (category):
        if (request.session.get('category_exclude')):
            entries = DictionaryEntry.objects.exclude(word__category__id=category.id)
        else:
            entries = DictionaryEntry.objects.filter(word__category__id=category.id)
    elif (dictionary):
        if (request.session.get('dictionary_exclude')):
            entries = DictionaryEntry.objects.exclude(dictionary__id=dictionary.id)
        else:
            entries = DictionaryEntry.objects.filter(dictionary__id=dictionary.id)
    order_sign = '' if not request.session.get('sortby_desc', False) else '-'
    entries = entries.order_by(order_sign + request.session.get('sortby', 'word'))
    return entries


def handle_all_entries(request, entries=None):
    page = 1
    per_page = request.session.get('per_page', 2)
    if(request.GET):
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", per_page)
        request.session['per_page'] = per_page

    form = manage_entries_request(request)
    if(entries == None):
        entries = get_entries(request)
    paginator = Paginator(entries, per_page)
    page_object = paginator.get_page(page)
    
    context = {
        'words':page_object.object_list,
        'categories': Category.objects.all().order_by('name'),
        'dictionaries': Dictionary.objects.all().order_by('-id'),
        'form':form,
        'filter_form':create_filter_form(request),
        'is_paginated': True,
        'page_obj': page_object,
        'per_page':per_page,
        'per_page_values':['5', '10', '25', '50', '100', '1000'],
    }
    return context


def category(request, pk):
    reset_filters(request)
    request.session['category'] = None if not pk else pk
    request.session['reset_filters'] = True
    context = handle_all_entries(request)
    context['category'] = Category.objects.get(pk=pk)
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
    reset_filters(request)
    request.session['reset_filters'] = True
    request.session['dictionary'] = None if not pk else pk
    context = handle_all_entries(request)
    context['dictionary'] = Dictionary.objects.get(pk=pk)
    return render(request, 'dictionary.html', context=context)


def add_entry(request, pk=None):
    result = 'Changes saved'
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
                    entry.translation = create_word(fc['translation'], to, categories, fc['notes'])
                else:
                    change_word(entry.translation, fc['translation'], to, categories, fc['notes'])
                entry.transcription = fc['transcription']
                entry.save()
                entry.dictionary.set(fc['dictionaries'])
                entry.save()
                result = "Seccessfuly added: " + str(entry)
            else:
                word = get_or_create_word(fc['word'], from_lang, categories)
                translation = get_or_create_word(fc['translation'], to, categories, fc['notes'])
                entry = DictionaryEntry(word=word, translation=translation)
                
                entry.transcription = fc['transcription']
                entry.save()
                entry.dictionary.set(fc['dictionaries'])
                entry.save()
                result = "Seccessfuly added: " + str(entry) 
        if('_save' in request.POST):
            return redirect(reverse('allwords'), template_name='all_entries.html')
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
    if(entry != None):
        initial = {'from_lang': entry.word.language.code, 'to':entry.translation.language.code} 
        initial['entry'] = entry
        initial['word'] = entry.word.word
        initial['transcription'] = entry.transcription
        initial['translation'] = entry.translation.word
        initial['notes'] = entry.translation.notes
        initial['categories'] = entry.word.category.all().values_list("pk", flat=True)
        initial['dictionaries'] = entry.dictionary.all().values_list("pk", flat=True)     
    else:
        from_lang = Language.objects.get(code='es')
        to_lang = Language.objects.get(code='uk')
        initial = {'from_lang': from_lang.code, 'to':to_lang}        
    form = UpdateEntryForm(initial)
    return form


def get_or_create_word(word_text, lang, categories, notes=None):
    if(notes != None):
        existing = Word.objects.filter(word=word_text).filter(notes=notes).first()
    else:
        existing = Word.objects.filter(word=word_text).first()
    if(existing != None):
        return existing
    else:
       word = Word(word=word_text)
    word.language = lang
    if(notes != None):
        word.notes = notes
    word.save()
    print('saved word:')
    print(word)
    word.category.set(categories)
    word.save()
    print('saved2 word:')
    print(word)
    return word


def create_word(word_text, lang, categories, notes=None):
    word = Word(word=word_text)
    word.language = lang
    if(notes != None):
        word.notes = notes
    word.save()
    word.category.set(categories)
    word.save()
    return word

       
def change_word(entry_word, word_text, lang, categories, notes=None):
    entry_word.word = word_text
    entry_word.language = lang
    entry_word.category.set(categories)
    if(notes != None):
        entry_word.notes = notes
    entry_word.save()

    
def edit_entries(request):
    form = UpdateEntriesForm(request.POST)
    entries = []
    if(len(request.POST.getlist('entries'))>0):
        for e in request.POST.getlist('entries'):
            entries.append(DictionaryEntry.objects.get(pk=e))
    else:
        entries = get_entries(request)
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
            entries_pks = request.session.get('last_imported', [])
            for entry in entries:
                if(entry.pk in entries_pks):
                    entries_pks.remove(entry.pk)
                entry.word.delete()
                entry.translation.delete()
                entry.delete()
            request.session['last_imported'] = entries_pks
        elif('_delete_entries' in request.POST):
            entries_pks = request.session.get('last_imported', [])
            for entry in entries:
                if(entry.pk in entries_pks):
                    entries_pks.remove(entry.pk)
                    print('after remove')
                    print(entries_pks)
                entry.delete()
            request.session['last_imported'] = entries_pks
    return form
