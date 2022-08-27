from django.db import models
from django.urls import reverse


class Language(models.Model):
    code = models.CharField(max_length=2, primary_key=True, default='na')
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', args=[str(self.id)])


class Dictionary(models.Model):
    name = models.CharField(max_length=30)
    language_from = models.ForeignKey('Language', on_delete=models.CASCADE, related_name='lang_from')
    language_to = models.ForeignKey('Language', on_delete=models.CASCADE, related_name='to')

    class Meta:
        ordering = ['language_from', 'language_to', 'name']

    def __str__(self):
        return f'{self.name} ({self.language_from}-{self.language_to})'

    def get_absolute_url(self):
        return reverse('dictionary', args=[str(self.id)])


class Word(models.Model):
    word = models.CharField(max_length=30)
    notes = models.CharField(max_length=50, blank=True, null=True)
    language = models.ForeignKey('Language', on_delete=models.CASCADE, null=False)
    category = models.ManyToManyField(Category, blank=True)

    class Meta:
        ordering = ['language', 'word']

    def get_notes(self):
        return "" if not self.notes else ' ('+self.notes+')'

    def __str__(self):
        return f'{self.word} ({str(self.language)})'


class DictionaryEntry(models.Model):
    word = models.ForeignKey('Word', on_delete=models.CASCADE, null=False)
    transcription = models.CharField(max_length=30, blank=True, null=True)
    translation = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='translation')
    dictionary = models.ManyToManyField(Dictionary, blank=True)

    class Meta:
        ordering = ['word', 'translation']

    def get_transcription(self):
        return "" if not self.transcription else self.transcription

    def __str__(self):
        return f'{self.word.word} [{self.get_transcription()}] - {self.translation.word}'

    def get_absolute_url(self):
        return reverse('dict-details', args=[str(self.id)])
