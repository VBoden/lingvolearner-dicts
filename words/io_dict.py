from datetime import datetime
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from . import views
from .models import Category, Dictionary, DictionaryEntry, Language
from .forms import ExportToFileForm, ImportFromFileForm
from os import listdir, rename
from os.path import isfile, join


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


def to_entry(line, from_lang, to_lang, categories, dicts):
    partes = line.replace('\n', '').split('|')
    word = views.get_or_create_word(partes[0], from_lang, categories)
    if(' (' in partes[2]):
        trans = partes[2].split(' (')
        translation = trans[0]
        notes = trans[1][:-1]
    else:
        translation = partes[2]
        notes = None
    translation = views.get_or_create_word(translation, to_lang, categories, notes)
    existing = DictionaryEntry.objects.filter(word=word).filter(translation=translation).first()
    if(existing != None):
        return None, existing
    entry = DictionaryEntry(word=word, translation=translation)
    
    entry.transcription = partes[1][1:-1]
    entry.save()
    entry.dictionary.set(dicts)
    entry.save()
    return entry, None


def convert_line(entries_pks, not_aded_entries, fc, dicts, categories, line):
    line = line.replace('\n', '')
    if(len(line)==0):
        return
    entry, not_added = to_entry(line, fc['from_lang'], fc['to'], categories, dicts)
    if (entry != None):
        entries_pks.append(entry.pk)
    if (not_added != None):
        not_aded_entries.append(not_added)


def handle_import_from_dir_post(request):
    entries_pks = []
    not_aded_entries = []
    form = ImportFromFileForm(request.POST)
    if form.is_valid():
        fc = form.cleaned_data
        from_path = 'io/imports/to_be_imported'
        to_path = 'io/imports/imported'
        onlyfiles = [f for f in listdir(from_path) if isfile(join(from_path, f))]
        imported_files = []
        for file in onlyfiles:
            dicts = []
            if(fc['use_filename_as_dict']):
                try:
                    d = Dictionary.objects.get(name=file)
                except ObjectDoesNotExist:
                    d = Dictionary(name=file, language_from=fc['from_lang'], language_to=fc['to'])
                    d.save()
                dicts.append(d)
            if(fc['dictionary'] != None):
                dicts.append(fc['dictionary'])
            categories = []                
            if(fc['category'] != None):
                categories.append(fc['category'])
            with open(join(from_path, file), "r") as f:
                for line in f:
                    print(line)
                    if '%' in line:
                        lines = line.split('%')
                        for l in lines:
                            convert_line(entries_pks, not_aded_entries, fc, dicts, categories, l)
                    else:
                        convert_line(entries_pks, not_aded_entries, fc, dicts, categories, line)
            imported_files.append(file)
            rename(join(from_path, file),join(to_path, file))
            if(fc['only_first']):
                break
        initial = {'from_lang': fc['from_lang'],
               'to':fc['to'],
               'only_first':fc['only_first'],
               'use_filename_as_dict':fc['use_filename_as_dict'],
               }
        if(len(entries_pks) > 0):
            request.session['last_imported'] = entries_pks
            entries = DictionaryEntry.objects.filter(pk__in=entries_pks)
        else:
            entries = []
        context = views.handle_all_entries(request, entries)
        if(len(not_aded_entries) > 0):
            not_ad = ''
            for e in not_aded_entries:
                not_ad = not_ad + f'{e.word.word}|[{e.get_transcription()}]|{e.translation.word}{e.translation.get_notes()}\n'
            context['result'] = 'Importing from '+ str(imported_files)+'. Not added:\n' + not_ad
        else:            
            context['result'] = 'Successfuly imported from ' + str(imported_files)
        return initial, context


def import_from_dir(request):
    print('check results: ')
    print('_import' in request.POST)
    if (request.method == 'POST') and ('_import' in request.POST):
        initial, context = handle_import_from_dir_post(request)
    else:
        from_lang = Language.objects.get(code='es')
        to_lang = Language.objects.get(code='uk')
        initial = {'from_lang': from_lang.code,
                   'to':to_lang,
                   'only_first':True,
                   'use_filename_as_dict':True,
                   }
        entries_pks = request.session.get('last_imported', [])
        entries = DictionaryEntry.objects.filter(pk__in=entries_pks)
        context = views.handle_all_entries(request, entries)
    form = ImportFromFileForm(initial)
    context['form'] = form
    return render(request, 'import_from_dir.html', context=context)
