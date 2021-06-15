import datetime

from django import forms


class GridIronUrlForm(forms.Form):

    p_url = forms.URLField(
        label="Copy-n-Paste Grid Iron Practiscore URL",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'size': '65'})
    )
    # csv = forms.BooleanField(label="CSV Output", required=False)
