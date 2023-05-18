import datetime

from django import forms

DAY = datetime.date.today()

DIVISION_LIST = [
    ('', ''),
    ('Open', 'Open'),
    ('Limited', 'Limited'),
    ('Production', 'Production'),
    ('Carry Optics', 'Carry Optics'),
    ('Limited Optics', 'Limited Optics')
    ('PCC', 'PCC'),
    ('Single Stack', 'Single Stack'),
    ('Limited 10', 'Limited 10'),
    ('Revolver', 'Revolver')
]


class PractiscoreUrlForm(forms.Form):

    p_url = forms.URLField(
        label="Copy-n-Paste Practiscore URL",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'size': '65'})
    )


class GetUppedForm(forms.Form):

    mem_num_1 = forms.CharField(
        label="USPSA Membership Number",
        max_length=10,
        widget=forms.TextInput(attrs={'size': '10'}),
        required=True,
    )

    division_1 = forms.CharField(
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

    division = forms.CharField(
        label="Select USPSA Division",
        widget=forms.Select(choices=DIVISION_LIST),
        required=True,
    )

    shooter_end_date = forms.DateField(
        initial=datetime.date.fromisoformat(str(DAY)),
        widget=forms.HiddenInput(),
        required=False,
    )

    shooter_start_date = forms.DateField(
        initial=datetime.date.fromisoformat('2020-01-01'),
        widget=forms.HiddenInput(),
        required=False,
    )


class AccuStatsForm2(forms.Form):

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

    division = forms.CharField(
        label="Select USPSA Division",
        widget=forms.Select(choices=DIVISION_LIST),
        required=True,
    )

    shooter_end_date = forms.DateField(
        initial=datetime.date.fromisoformat(str(DAY)),
        required=False,
    )

    shooter_start_date = forms.DateField(
        initial=datetime.date.fromisoformat('2019-01-01'),
        required=False,
    )

    delete_match = forms.CharField(
        label="Exclude Dates",
        max_length=60,
        widget=forms.TextInput(
            attrs={
                'size': '32',
                'placeholder': 'Example: 2020-03-15, 2019-09-22'
            }
        ),
        required=False,
    )


class PPSForm1(forms.Form):

    username_pps = forms.CharField(
        label="Practiscore username/email",
        max_length=50,
        widget=forms.TextInput(attrs={'size': '50'}),
        required=True,
    )

    password_pps = forms.CharField(
        label="Practiscore password",
        max_length=32,
        widget=forms.PasswordInput(attrs={'size': '32'}),
        required=True,
    )

    mem_num_pps = forms.CharField(
        label="USPSA Membership Number",
        max_length=10,
        widget=forms.TextInput(attrs={'size': '10'}),
        required=True,
    )

    division_pps = forms.CharField(
        label="Select USPSA Division",
        widget=forms.Select(choices=DIVISION_LIST),
        required=True,
    )

    end_date_pps = forms.DateField(
        initial=datetime.date.fromisoformat(str(DAY)),
        widget=forms.HiddenInput(),
        required=False,
    )

    start_date_pps = forms.DateField(
        initial=datetime.date.fromisoformat('2017-01-01'),
        widget=forms.HiddenInput(),
        required=False,
    )


class PPSForm2(forms.Form):

    username_pps = forms.CharField(
        label="Practiscore username/email",
        max_length=50,
        widget=forms.TextInput(attrs={'size': '50'}),
        required=True,
    )

    password_pps = forms.CharField(
        label="Practiscore password",
        max_length=32,
        widget=forms.PasswordInput(attrs={'size': '32'}),
        required=True,
    )

    mem_num_pps = forms.CharField(
        label="USPSA Membership Number",
        max_length=10,
        widget=forms.TextInput(attrs={'size': '10'}),
        required=True,
    )

    division_pps = forms.CharField(
        label="Select USPSA Division",
        widget=forms.Select(choices=DIVISION_LIST),
        required=True,
    )

    end_date_pps = forms.DateField(
        initial=datetime.date.fromisoformat(str(DAY)),
        required=False,
    )

    start_date_pps = forms.DateField(
        initial=datetime.date.fromisoformat('2017-01-01'),
        required=False,
    )

    delete_match_pps = forms.CharField(
        label="Exclude Dates",
        max_length=60,
        widget=forms.TextInput(
            attrs={
                'size': '32',
                'placeholder': 'Example: 2020-03-15, 2019-09-22'
            }
        ),
        required=False,
    )
