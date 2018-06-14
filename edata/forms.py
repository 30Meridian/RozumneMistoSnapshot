from weunion.models import Subscriptions
from django import forms


class SubscriptionAdd(forms.ModelForm):
    class Meta:
        model = Subscriptions
        fields = ['parameter', 'comparison','value']
