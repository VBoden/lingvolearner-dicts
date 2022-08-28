from django import forms

from .models import Category, Dictionary, DictionaryEntry, Language, Word


class UpdateEntryForm(forms.Form):
    entry = forms.ModelChoiceField(queryset=DictionaryEntry.objects.all(), widget=forms.HiddenInput(), required=False)
    word = forms.CharField()
    word_save_as_new = forms.BooleanField(required=False, label='Save word as new')
    transcription = forms.CharField(required=False)
    translation = forms.CharField()
    notes = forms.CharField(required=False)
    translation_save_as_new = forms.BooleanField(required=False, label='Save translation as new')
    from_lang = forms.ModelChoiceField(queryset=Language.objects.all(), label='From')
    to = forms.ModelChoiceField(queryset=Language.objects.all())
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False)
    dictionaries = forms.ModelMultipleChoiceField(queryset=Dictionary.objects.all(), required=False)
    entry_save_as_new = forms.BooleanField(required=False, label='Save as new')


class UpdateEntriesForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    dictionary = forms.ModelChoiceField(queryset=Dictionary.objects.all(), required=False)


class FiltersForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    category_exclude = forms.BooleanField(required=False, label='exclude')
    dictionary = forms.ModelChoiceField(queryset=Dictionary.objects.all(), required=False)
    dictionary_exclude = forms.BooleanField(required=False, label='exclude')
    sortby = forms.ChoiceField(choices = (('word','word'),('pk','id')),label='sort by')
    sortby_desc = forms.BooleanField(required=False, label='z-a')


class ExportToFileForm(forms.Form):
    only_selected = forms.BooleanField(required=False, label='selected only')
    file_name = forms.CharField()
    file_name_ending = forms.CharField()

class ImportFromFileForm(forms.Form):
    from_lang = forms.ModelChoiceField(queryset=Language.objects.all(), label='From language')
    to = forms.ModelChoiceField(queryset=Language.objects.all(), label='To language')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label='Assign to category')
    dictionary = forms.ModelChoiceField(queryset=Dictionary.objects.all(), required=False, label='Assign to dictionary')
    use_filename_as_dict = forms.BooleanField(required=False, label='Use filename as dict')
    only_first = forms.BooleanField(required=False, label='Import only first')

