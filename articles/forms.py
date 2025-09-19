"""Forms for user registration and authentication."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Article, Newsletter, Publisher


class UserRegistrationForm(UserCreationForm):
    """Registration form for creating new users with roles."""

    role = forms.ChoiceField(choices=User.Roles.choices)
    affiliated_publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        empty_label="Select a publisher (required for editors)",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "role",
            "affiliated_publisher",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to form fields
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        affiliated_publisher = cleaned_data.get('affiliated_publisher')
        
        # Require publisher selection for editors
        if role == User.Roles.EDITOR and not affiliated_publisher:
            raise forms.ValidationError("Editors must select a publisher.")
        
        return cleaned_data

    def save(self, commit=True):
        """
        Save the user with selected role and hashed password.
        """
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]
        user.affiliated_publisher = self.cleaned_data.get("affiliated_publisher")

        if commit:
            user.save()
        return user
    

class ForgotUsernameForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={
            "class": "form-control",      
            "placeholder": "Enter your email"
        })
    )


class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        email = cleaned.get("email")
        if not username or not email:
            return cleaned

        user = User.objects.filter(
            username__iexact=username, email__iexact=email
        ).first()
        if not user:

            raise forms.ValidationError(
                "No account was found with that username and email."
            )
        self.user = user
        return cleaned


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        # Don’t expose is_approved; editors use approve/unapprove actions
        fields = ["title", "body", "publisher"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "publisher": forms.Select(attrs={"class": "form-select"}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["subject", "content", "publisher"] 
        labels = {"content": "Content"}
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 8}
            ),
            "publisher": forms.Select(attrs={"class": "form-select"}),
        }


class UserProfileForm(forms.ModelForm):
    """Form for users to edit their profile details."""
    
    new_publisher_name = forms.CharField(
        max_length=255,
        required=False,
        label="Or Create New Publisher",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Enter a new publisher name. This will override any selection above and create a new publisher."
    )
    
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "affiliated_publisher"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "affiliated_publisher": forms.Select(attrs={"class": "form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show affiliated_publisher field for editors and journalists
        if self.instance and self.instance.role not in [User.Roles.EDITOR, User.Roles.JOURNALIST]:
            self.fields.pop('affiliated_publisher', None)
        
        # Only show new_publisher_name field for editors
        if self.instance and self.instance.role != User.Roles.EDITOR:
            self.fields.pop('new_publisher_name', None)
    
    def clean(self):
        cleaned_data = super().clean()
        new_publisher_name = cleaned_data.get('new_publisher_name')
        affiliated_publisher = cleaned_data.get('affiliated_publisher')
        
        # If creating a new publisher, validate the name
        if new_publisher_name:
            if affiliated_publisher:
                # Clear the selected publisher if creating a new one
                cleaned_data['affiliated_publisher'] = None
            
            # Check if publisher with this name already exists
            from .models import Publisher
            if Publisher.objects.filter(name__iexact=new_publisher_name).exists():
                raise forms.ValidationError(
                    f"A publisher with the name '{new_publisher_name}' already exists."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        new_publisher_name = self.cleaned_data.get('new_publisher_name')
        
        # If creating a new publisher, create it and assign to user
        if new_publisher_name and user.role == User.Roles.EDITOR:
            from .models import Publisher
            publisher = Publisher.objects.create(name=new_publisher_name)
            user.affiliated_publisher = publisher
        
        if commit:
            user.save()
        return user