from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect
from mailqueue.models import MailerMessage

from eestecnet import *


def init(request):
    create_local_admins()
    create_eestec_lcs()
    create_eestec_teams()
    create_eestec_news()
    create_eestec_people()
    create_inktronics()
    create_positions_for_achievements()
    create_pages()
    create_stubs()
    return redirect("/")
def newsletter(request):
    try:
        validate_email( request.POST['mailsub'] )
    except ValidationError:
        return redirect("/")
    message=MailerMessage()
    message.subject = "add to newsletter"
    message.content="Dear VC-IA, please kindly add "+request.POST['mailsub']+"to the newsletter list."
    message.from_address = "noreply@eestec.net",
    message.to_address = "vc-ia@eestec.net"
    message.save()
    return redirect("/")


from django.forms.models import (
    BaseInlineFormSet,
    inlineformset_factory,
)


class BaseNestedFormset(BaseInlineFormSet):

    def add_fields(self, form, index):

        # allow the super class to create the fields as usual
        super(BaseNestedFormset, self).add_fields(form, index)

        form.nested = self.nested_formset_class(
            instance=form.instance,
            data=form.data if self.is_bound else None,
            prefix='%s-%s' % (
                form.prefix,
                self.nested_formset_class.get_default_prefix(),
            ),
        )

    def is_valid(self):

        result = super(BaseNestedFormset, self).is_valid()

        if self.is_bound:
            # look at any nested formsets, as well
            for form in self.forms:
                result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):

        result = super(BaseNestedFormset, self).save(commit=commit)

        for form in self:
            form.nested.save(commit=commit)

        return result
def nested_formset_factory(parent_model, child_model, grandchild_model):

    parent_child = inlineformset_factory(
        parent_model,
        child_model,
        formset=BaseNestedFormset,
    )

    parent_child.nested_formset_class = inlineformset_factory(
        child_model,
        grandchild_model,
    )

    return parent_child