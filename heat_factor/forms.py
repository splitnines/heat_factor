from django import forms

class PractiscoreUrlForm(forms.Form):

    p_url = forms.URLField(
        label="Copy-n-Paste Practiscore URL",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'size': '65'})
    )



class GetUppedForm(forms.Form):

    mem_num = forms.CharField(
        label="USPSA Membership Number",
        max_length=10,
        widget=forms.TextInput(attrs={'size': '10'}),
        required=True,
    )

    DIVISION_LIST = [
        ('',''),
        ('Open', 'Open'),
        ('Limited', 'Limited'),
        ('Production', 'Production'),
        ('Carry Optics', 'Carry Optics'),
        ('PCC', 'PCC'),
        ('Single Stack', 'Single Stack'),
        ('Limited 10', 'Limited 10'),
        ('Revolver', 'Revolver')
    ]

    division = forms.CharField(
        label="Select USPSA Division",
        widget=forms.Select(choices=DIVISION_LIST),
        required=True,
    )



class AccuStatsForm1(forms.Form):

    username = forms.CharField(
        label="Practiscore username/email",
        max_length=50,
        widget=forms.TextInput(attrs={'size': '50'}),
        required=True,
    )

    password = forms.CharField(
        label="Practiscore password",
        max_length=32,
        widget=forms.PasswordInput(attrs={'size': '32'}),
        required=True,
    )

    mem_num = forms.CharField(
        label="USPSA Membership Number",
        max_length=10,
        widget=forms.TextInput(attrs={'size': '10'}),
        required=True,
    )



class AccuStatsForm2(forms.Form):
    pass
