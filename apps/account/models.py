from autoslug import AutoSlugField
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager)

from apps.teams.models import Team


class EestecerManager(BaseUserManager):
    """ A manager taking care of creating :class:`Eestecer` objects. """

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        user.update_forum(password)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


FIELDS_OF_STUDY = (
    ("ee", "Electrical Engineering"),
    ("it", "Information Technology"),
    ("cs", "Computer Science"),
    ("bm", "Biomedical Engineering"),
    ("tc", "Telecommunications"),
    ("pe", "Power Engineering"),
    ("se", "Software Engineering"),
    ("au", "Automatics"),
    ("ns", "Natural Sciences"),
    ("ss", "Social Sciences"),
    ("ec", "Economy"),
    ("oe", "Other engineering subjects"),
    ("oo", "Other"),
)
FOOD_CHOICES = (
    ('none', 'None'),
    ('kosher', 'Kosher'),
    ('halal', 'Halal'),
    ('nopork', 'No Pork'),
    ('nofish', 'Pescarian'),
    ('veggie', 'Vegetarian'),
    ('vegan', 'Vegan'),
)
GENDER_CHOICES = (('m', 'Male'), ('f', 'Female'), ('x', 'Other'), )
TSHIRT_SIZE = (('mxs', 'Male XS'), ('ms', 'Male S'), ('mm', 'Male M'), ('ml', 'Male L'),
               ('mxl', 'Male XL'), ('mxxl', 'Male XXL'), ('mxxxl', 'Male XXXL'),
               ('fxs', 'Female XS'), ('fs', 'Female S'), ('fm', 'Female M'),
               ('fl', 'Female L'), ('fxl', 'Female XL'), ('fxxl', 'Female XXL'),
               ('fxxxl', 'Female XXXL'), )


def get_eestecer_slug(instance):
    if instance.middle_name:
        return "%s-%s-%s" % (
        instance.first_name, instance.middle_name, instance.last_name)
    else:
        return "%s-%s-%s" % (
        instance.first_name, instance.middle_name, instance.last_name)


class Eestecer(AbstractBaseUser, PermissionsMixin):
    #Basic Information
    def name(self):
        return self.get_full_name()
    thumbnail = models.ImageField(upload_to="users",null=True,blank=True)
    description = models.TextField(blank=True, null=True)
    slug = AutoSlugField(populate_from=get_eestecer_slug)
    #Contact information
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    skype = models.CharField(_('Skype Account'), max_length=30, null=True, blank=True)
    hangouts = models.CharField (max_length=30, null=True, blank=True)
    mobile = models.CharField(_('Mobile Phone Number'), max_length=30, null=True,
                              blank=True,
                              help_text=_(
                                  'Please provide your phone number in +XX XXX XXXXXX '
                                  'format'))
    #Names
    first_name = models.CharField(_('first name'), max_length=30)
    middle_name = models.CharField(_('middle name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30)
    second_last_name = models.CharField(_('second last name'), max_length=30, blank=True)
    """ For our friends from the iberic peninsula"""
    date_of_birth = models.DateField(blank=True, null=True)
    show_date_of_birth = models.BooleanField(default=True)
    receive_eestec_active = models.BooleanField(default=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES)
    tshirt_size = models.CharField(max_length=15, choices=TSHIRT_SIZE, blank=True,
                                   null=True)
    allergies = models.CharField(max_length=50, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    activation_link = models.CharField(max_length=50, blank=True, null=True)
    """Passport number required by many hostels. Makes it easier for organizers."""
    field_of_study = models.CharField(max_length=50, choices=FIELDS_OF_STUDY)
    food_preferences = models.CharField(max_length=15, choices=FOOD_CHOICES,
                                        default='none')
    """ Food preferences, for example vegetarian or no pork. """
    curriculum_vitae = models.FileField(upload_to="cvs", blank=True, null=True)
    """ For the future incorporation of Lykeion """
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    """Should be set by the user to the time they joined eestec. For new users it will
    be the moment they register with the website"""

    def events_participated(self):
        """ Returns the number of :class:`Events <Event>` a :class:`User <account
        .models.Eestecer>` has been to"""
        return len(self.events.all())

    def last_event(self):
        """ Returns the Date of the last :class:`Event` a :class:`User <account.models
        .Eestecer>` has been to"""
        return self.events.all().order_by('-start_date').first()

    def teams_administered(self):
        if self.is_superuser:
            return Team.objects.all()
        return self.teams.filter(membership__privileged=True)

    #Django information
    is_staff = models.BooleanField(_('active'), default=False)
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_(
                                        'Designates whether this user should be '
                                        'treated as '
                                        'active. Unselect this instead of deleting '
                                        'accounts.'))
    """Designates whether this user should be treated as active. Unselect this instead
    of deleting accounts"""

    def is_trainer(self):
        return len(self.teams.filter(name="Training Team"))

    def lc(self):
        return self.teams.filter(category__in=['jlc', 'lc', 'observer'])

    def as_self(self):
        return render_to_string('account/self.html', {'object': self})

    def as_html(self):
        return render_to_string('account/eestecer.html', {'object': self})

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender']

    objects = EestecerManager()

    def clean(self):
        self.email = self.email.lower()
        if self.first_name:
            self.first_name = self.first_name.lower()
        if self.middle_name:
            self.middle_name = self.middle_name.lower()
        if self.last_name:
            self.last_name = self.last_name.lower()
        if self.second_last_name:
            self.second_last_name = self.second_last_name.lower()


    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        unique_together = (('first_name', 'middle_name', 'last_name'),)
        ordering = ["first_name", "last_name"]
    def get_full_name(self):
        """ Returns the first_name plus the last_name, with a space in between. """
        full_name = self.first_name.capitalize()
        if self.middle_name:
            full_name+=" "+self.middle_name.capitalize()
        full_name+=" "+self.last_name.capitalize()
        if self.second_last_name:
            full_name+=" "+self.second_last_name.capitalize()
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return '%s %s' % (self.first_name, self.last_name)
    def __unicode__(self):
        return self.get_full_name()
    def get_absolute_url(self):
        return "/people/"+  self.slug
    def update_forum(self,password=None):
        import urllib2
        import urllib
        url="https://forum.eestec.net/connector.php"
        try:
            from eestecnet.settings.secret import FORUM_PASSWORD
        except:
            FORUM_PASSWORD=""
        values={
            "secretpassword":FORUM_PASSWORD,
            u"uid": self.pk,
            u"username": self.email,
            u"first_name": self.first_name.encode('utf-8'),
            u"last_name": self.last_name.encode('utf-8'),
            u'skype': self.skype,
            u'google': self.hangouts,
            u'bday': self.date_of_birth,
            u'birthdayprivacy': self.show_date_of_birth,
            }
        if password:
            values['password']=password
        if self.thumbnail:
            values['avatar'] = self.thumbnail.url
        data=urllib.urlencode(values)
        req = urllib2.Request(url + u'?' + data)
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        try:
            response = opener.open(url+'?'+data)
        except:
            pass


class Position(models.Model):
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name


class Achievement(models.Model):
    person = models.ForeignKey(Eestecer, related_name='achievements')
    position = models.ForeignKey(Position)
    member = models.ForeignKey('teams.Team', blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    event = models.ForeignKey('events.Event', null=True, blank=True)
    def __unicode__(self):
        return self.person.get_short_name() + " - " + self.position.name