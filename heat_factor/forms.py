from django import forms

class PractiscoreUrlForm(forms.Form):
    p_url = forms.URLField(label="Copy-n-Paste Practiscore URL",
                            max_length=150,
                            required=True,
                            widget=forms.TextInput(attrs={'size': '65'})
                           )
