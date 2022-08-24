from django import forms

from .models import Category, Dictionary, DictionaryEntry, Language, Word

class UpdateEntryForm(forms.Form):
    word = forms.CharField()
    transcription = forms.CharField(required=False)
    translation = forms.CharField()
    from_lang = forms.ModelChoiceField(queryset=Language.objects.all(),label='From')
    to = forms.ModelChoiceField(queryset=Language.objects.all())
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(),required=False)
    dictionaries = forms.ModelMultipleChoiceField(queryset=Dictionary.objects.all(),required=False)
