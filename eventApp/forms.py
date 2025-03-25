from django import forms


class ReasonForDeleteEventForm(forms.Form):
    """Форма для заполнения причины удаления мероприятия, если оно активно."""
    reason = forms.CharField(
        widget=forms.Textarea,
        label="Причина отмены(необязательно)",
        required=False
    )