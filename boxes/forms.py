from django.forms import ModelForm, Form, CharField, Textarea, BooleanField
from .models import Box
from django.utils import timezone


class CreateBoxForm(ModelForm):
    never_expires = BooleanField(required=False)

    field_order = [
        "name",
        "never_expires",
        "expires_at",
        "max_messages",
        "description"]

    class Meta:
        model = Box
        fields = [
            "name",
            "description",
            "expires_at",
            "max_messages"]

    def clean_expires_at(self):
        # Validate the expiration date
        expires_at = self.cleaned_data.get("expires_at", "")
        never_expires = self.cleaned_data.get("never_expires", "")
        current_tz = timezone.get_current_timezone()
        if never_expires:
            expires_at = None
            self.cleaned_data["expires_at"] = expires_at
        if expires_at:
            # Check if the expiration date is a past date
            if timezone.localtime(timezone.now(), current_tz) > expires_at:
                self.add_error('expires_at', "The date must be on the future.")
        if not expires_at and not never_expires:
            self.add_error('expires_at',
                           "This field is required, unless box is set to "
                           "never expire.")
        return expires_at

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.pop("never_expires")
        return cleaned_data


class SubmitBoxForm(Form):
    message = CharField(widget=Textarea)

    def clean_message(self):
        # Quick check if the message really came encrypted
        message = self.cleaned_data.get("message")
        lines = message.split("\r\n")

        begin = "-----BEGIN PGP MESSAGE-----"
        end = "-----END PGP MESSAGE-----"

        try:
            if lines[0] != begin or lines[-1] != end:
                self.add_error("message", "Invalid PGP message")
        except IndexError:
            self.add_error("message", "Invalid PGP message")
        return message
