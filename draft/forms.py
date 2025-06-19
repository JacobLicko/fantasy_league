from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import League

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    
class JoinLeagueForm(forms.Form):
    code = forms.CharField(
        max_length=8,
        label="League Code",
        widget=forms.TextInput(attrs={'placeholder': 'Enter League Code'})
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip().upper()
        try:
            league = League.objects.get(code=code)
        except League.DoesNotExist:
            raise forms.ValidationError("No League found with that code.")
        
        # enforce capacity
        if league.members.count() >= league.max_players:
            raise forms.ValidationError("That League is already full.")

        return code
    
class CreateLeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = [
            'max_players',
            'name',
            'draft_type',
            'region',
            'draft_date',
            'draft_time',
        ]

        widgets = {
            'max_players': forms.RadioSelect,
            'draft_type': forms.RadioSelect,
            'region': forms.RadioSelect,
            'draft_date': forms.DateInput(attrs={'type':'date'}),
            'draft_time': forms.TimeInput(attrs={'type':'time'}),
        }
    
    def clean_draft_type(self):
        choice = self.cleaned_data.get('draft_type')
        if choice == 'auction':
            raise forms.ValidationError("Auction feature not implemented yet.")
        return choice