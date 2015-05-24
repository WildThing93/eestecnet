from django.forms import Textarea, CharField
from form_utils.forms import BetterModelForm

from apps.feedback.models import Question, QuestionSet, AnswerSet
from eestecnet.forms import ReadonlyModelForm


class QuestionSetForm(BetterModelForm):
    class Meta:
        model = QuestionSet
        fields=['name','category']
        widgets = {
            'name': Textarea(attrs={'rows': '1'}),
        }


class QuestionForm(BetterModelForm):
    q = CharField(widget=Textarea(attrs={'rows': '1'}), label="Question")

    class Meta:
        model = Question


class AnswerSetForm(BetterModelForm):
    class Meta:
        fields = []
        model = AnswerSet

class AnswerForm(ReadonlyModelForm):
    a = CharField(widget=Textarea(attrs={'rows': '1'}), label="Answer",required=False)

    class Meta:
        model = Question
        fields = ('q', 'a')
    class NewMeta:
        readonly = ('q')
    def is_valid(self):
        return True
