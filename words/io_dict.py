from datetime import datetime
from django.shortcuts import render, redirect
from . import views
from .models import Category, Dictionary, DictionaryEntry
from .forms import ExportToFileForm


def export_to_file(request):
    context = views.handle_all_entries(request)
    initial = {}
    dictionary_pk = request.session.get('dictionary')
    category_pk = request.session.get('category')
    initial['file_name'] = ''
    if(dictionary_pk):
        dictionary = Dictionary.objects.get(pk=dictionary_pk)
        initial['file_name'] = dictionary.name
    elif(category_pk):
        category = Category.objects.get(pk=category_pk)
        initial['file_name'] = category.name
    first_entry = context['words'][0]
    initial['file_name'] = first_entry.word.language.code + '-' + first_entry.translation.language.code + '_' + initial['file_name']
    now = datetime.now()
    print(now.strftime("%d-%m-%Y_%H-%M-%S"))
    initial['file_name_ending'] = '_' + now.strftime("%d-%m-%Y_%H-%M-%S") + '.vcb'
    context['form'] = ExportToFileForm(initial)
    if request.method == 'POST':
        form = ExportToFileForm(request.POST)
        if form.is_valid():
            fc = form.cleaned_data
            initial['file_name'] = fc['file_name']
            entries = []
            for e in request.POST.getlist('entries'):
                entries.append(DictionaryEntry.objects.get(pk=e))
            if(fc['only_selected']):
                if(len(entries) == 0):
                    context['result'] = 'Export error: can\'t export only selected as not selection provided!'
                else:
                    do_export(entries, fc['file_name'], fc['file_name_ending'])
                    context['result'] = 'Entries successfuly exported to file ' + fc['file_name'] + fc['file_name_ending']
            else:
                do_export(views.get_entries(request), fc['file_name'], fc['file_name_ending'])
                context['result'] = 'Entries successfuly exported to file ' + fc['file_name'] + fc['file_name_ending']
    return render(request, 'export_to_file.html', context=context)


def do_export(entries, file_name, file_name_ending):
    f = open("io/exports/" + file_name + file_name_ending, "x")
    f.close()
    with open("io/exports/" + file_name + file_name_ending, "a") as f:
        for e in entries:
            line = f'{e.word.word}|[{e.get_transcription()}]|{e.translation.word}{e.translation.get_notes()}\n'
            f.write(line)

