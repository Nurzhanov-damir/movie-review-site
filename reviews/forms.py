from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Review, Genre


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'score']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Поделитесь своим мнением о фильме...',
                'class': 'form-control',
            }),
            'score': forms.NumberInput(attrs={
                'min': 1, 'max': 10, 'class': 'form-control',
            }),
        }
        labels = {
            'text': 'Ваш отзыв',
            'score': 'Оценка (1-10)',
        }

    def clean_score(self):
        score = self.cleaned_data['score']
        if score < 1 or score > 10:
            raise forms.ValidationError('Оценка должна быть от 1 до 10.')
        return score


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class MovieSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Поиск по названию фильма...',
            'class': 'form-control',
        }),
    )


class MovieFilterForm(forms.Form):
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label='Все жанры',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    min_rating = forms.ChoiceField(
        choices=[('', 'Любой рейтинг')] + [(str(i), f'{i}+') for i in range(1, 10)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
