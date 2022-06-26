from django import forms
from material import Row, Layout

from .config import *
from .utils import populate_posts


class OptionForm(forms.Form):
    choice = forms.ChoiceField(choices=OPTIONS, label="What would you like to do?",
                               help_text="You are only eligible to Vote or Contest if you are a student of BSK.",
                               widget=forms.RadioSelect, initial="Vote")
    student_id = forms.CharField(label='Student ID', help_text="Specify your student ID", widget=forms.TextInput(attrs={'placeholder': "eg. DY103SI"}))
    post = forms.ChoiceField(choices=(), label="Post:", help_text="What post would you like to Vote for?")
    vote_for = forms.ChoiceField(choices=VOTE_OPTIONS, label="Vote for:", help_text="Who would you like to Vote for?", required=False,
                                 widget=forms.Select(attrs={'class': 'remove-elem'}))

    def __init__(self, *args, **kwargs):
        super(OptionForm, self).__init__(*args, **kwargs)
        self.fields['post'].choices = populate_posts()

    layout = Layout('choice', 'student_id', 'post', 'vote_for')


class RegisterForm(forms.Form):
    # student_id = forms.CharField(label='Student ID', help_text="Specify your student ID", widget=forms.TextInput(attrs={'placeholder': ""}))
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': ''}))
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': ''}))
    student_class = forms.ChoiceField(label='Class', help_text='Please select your current Class.', choices=CLASSES)
    student_house = forms.ChoiceField(label='House', help_text='Please select your House.', choices=HOUSES)

    layout = Layout(Row('first_name', 'last_name'), Row('student_class', 'student_house'))
