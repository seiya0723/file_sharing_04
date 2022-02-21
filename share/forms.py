from django import forms

from .models import Document,Review

class DocumentForm(forms.ModelForm):

    class Meta:
        model   = Document
        #mimeを追加する。userも追加する。
        fields = ["name", "content", "mime", "user"]

class ReviewForm(forms.ModelForm):

    class Meta:
        model   = Review
        fields = ["document", "user", "comment","star"]


