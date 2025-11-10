from django import forms

DHCP_CHOICES = [
    ('DHCPv4', 'DHCPv4'),
    ('DHCPv6', 'DHCPv6'),
]

class DHCPRequestForm(forms.Form):
    mac_address = forms.CharField(
        max_length=17,
        label='MAC Address',
        widget=forms.TextInput(attrs={
            'placeholder': '00:1A:2B:3C:4D:5E',
            'class': 'form-control'
        })
    )
    dhcp_version = forms.ChoiceField(
        choices=DHCP_CHOICES,
        label='DHCP Version',
        widget=forms.Select(attrs={'class': 'form-control'})
    )