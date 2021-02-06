import os
import time
import uuid

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .validators import validate_file_extension


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "src.%s" % (ext)
    return os.path.join('submitions/', '%s/' % instance.contest.short_name, 'user_%s/' % instance.user.id,
                        'submition_%s/' % time.strftime("%Y%m%d%H%M%S"), filename)


def get_tests_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('contests/%s' % instance.contest.short_name, 'tests/', filename)


def get_contest_detail_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "sow.%s" % (ext)
    return os.path.join('contests/%s' % instance.short_name, filename)


def get_contest_code_path(instance, filename):
    return os.path.join('contests/%s' % instance.short_name, 'src/', filename)


def get_contest_data_path(instance, filename):
    return os.path.join('contests/%s' % instance.contest.short_name, 'data/', filename)


def get_contest_ins_files_path(instance, filename):
    return os.path.join('contests/%s' % instance.short_name, 'src/temp/in', filename)


def get_contest_outs_files_path(instance, filename):
    return os.path.join('contests/%s' % instance.short_name, 'src/temp/out', filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    number = models.IntegerField(null=True, blank=True)
    gprd = models.BooleanField(null=True, default=True, blank=True)
    valid = models.BooleanField(null=False, default=False, blank=False)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Contest(models.Model):
    title = models.CharField(max_length=128)
    short_name = models.CharField(max_length=16, blank=False, unique=True)
    description = models.TextField(null=True, blank=True)
    #	sow = models.FileField(upload_to=get_contest_detail_path, blank=True, null=True, max_length=512)
    sow = models.URLField(max_length=200, blank=True)

    reference_code = models.FileField(upload_to=get_contest_code_path, blank=True, null=True)

    start_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    min_team_members = models.PositiveSmallIntegerField(default=1)
    max_team_members = models.PositiveSmallIntegerField(default=3)
    compile_flags = models.CharField(max_length=120)
    linkage_flags = models.CharField(max_length=120)
    max_classification = models.IntegerField(default=20)
    visible = models.BooleanField(null=False, default=True, blank=False)
    automatic_weight = models.BooleanField(null=False, default=True, blank=False)
    max_submitions = models.PositiveIntegerField(default=0)
    # safexec options
    cpu = models.PositiveIntegerField(default=1)  # <seconds>		Default: 1 second(s)
    mem = models.PositiveIntegerField(default=32768)  # <kbytes>		Default: 32768 kbyte(s)
    space = models.PositiveIntegerField(default=0)  # <kbytes>		Default: 0 kbyte(s)
    minuid = models.PositiveIntegerField(default=5000)  # <uid>			Default: 5000
    maxuid = models.PositiveIntegerField(default=65535)  # <uid>			Default: 65535
    core = models.PositiveIntegerField(default=0)  # <kbytes>		Default: 0 kbyte(s)
    nproc = models.PositiveIntegerField(default=0)  # <number>		Default: 0 proccess(es)
    fsize = models.PositiveIntegerField(default=8192)  # <kbytes>		Default: 8192 kbyte(s)
    stack = models.PositiveIntegerField(default=8192)  # <kbytes>		Default: 8192 kbyte(s)
    clock = models.PositiveIntegerField(default=10)  # <seconds>		Wall clock timeout (default: 10)
    chroot = models.CharField(default='/tmp', max_length=128)  # <path>		Directory to chrooted (default: /tmp)

    def isOpen(self):
        print(1)
        """Returns true if the contest is on going."""
        from django.utils import timezone
        if timezone.now() < self.end_date and timezone.now() > self.start_date:
            print('true')
            return True
        print('false')
        return False

    # objects = ContestManager()

    def getUserTeam(self, user):
        return self.team_set.filter(contest=self, users__exact=user).first()

    def getTestDetails(self):
        return self.cpu, self.mem, self.space, self.minuid, self.maxuid, self.core, self.nproc, self.fsize, self.stack, self.clock

    def getTests(self):
        return self.test_set.all()

    def getTeams(self):
        return self.team_set.all()

    def checkAttempts(self, user):
        team = self.getUserTeam(user)
        if not team:
            return False
        attempts = team.getAttempts()
        if self.max_submitions > 0:
            if attempts and attempts.count() >= self.max_submitions:
                return False
        return True

    def userHasTeam(self, user):
        team = self.getUserTeam(user)
        return not not team

    def getTestsCount(self):
        n = self.getTests().count()
        mandatory = self.getTests().filter(mandatory=True).count()
        diff = n - mandatory
        return n, mandatory, diff

# def checkAttempts(self, request, attempts):
#	if self.max_submitions > 0:
#		if attempts and attempts.count() >= self.max_submitions:
#			messages.error(request, "You have reached the maximum number of submissions for this contest.")
#			return False
#	return True

# def checkIsOpen(self, request):
#	if not self.is_open:
#		messages.error(request, "This contest is not active.")
#		return False
#	return True


class Test(models.Model):
    contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
    input_file = models.FileField(upload_to=get_tests_path, blank=False, null=False, max_length=512)
    output_file = models.FileField(upload_to=get_tests_path, blank=False, null=False, max_length=512)

    mandatory = models.BooleanField(null=False, default=False)
    weight_pct = models.DecimalField(default=10, null=False, decimal_places=2, max_digits=6)
    run_arguments = models.CharField(max_length=512, null=True, blank=True)
    type_of_feedback = models.PositiveIntegerField(default=1, null=False, blank=False)
    # test specific options
    override_exec_options = models.BooleanField(null=False, default=False)
    cpu = models.PositiveIntegerField(default=1)  # <seconds>           Default: 1 second(s)
    mem = models.PositiveIntegerField(default=32768)  # <kbytes>            Default: 32768 kbyte(s)
    space = models.PositiveIntegerField(default=0)  # <kbytes>            Default: 0 kbyte(s)
    core = models.PositiveIntegerField(default=0)  # <kbytes>            Default: 0 kbyte(s)
    nproc = models.PositiveIntegerField(default=0)  # <number>            Default: 0 proccess(es)
    fsize = models.PositiveIntegerField(default=8192)  # <kbytes>            Dfault: 8192 kbyte(s)
    stack = models.PositiveIntegerField(default=8192)  # <kbytes>            Default: 8192 kbyte(s)
    clock = models.PositiveIntegerField(default=10)  # <seconds>           Wall clock timeout (default: 10)
    check_leak = models.BooleanField(null=False, default=False)

    def getContest(self):
        return self.contest

    def getDetails(self):
        # TODO: Check the minuid and maxuid
        return self.cpu, self.mem, self.space, self.getContest().minuid, self.getContest().maxuid, self.core, self.nproc, self.fsize, self.stack, self.clock


class Team(models.Model):
    name = models.SlugField(max_length=50, blank=False)
    contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
    join_code = models.SlugField(max_length=32, blank=False, null=False, unique=True)
    users = models.ManyToManyField(User)
    # image  = models.ImageField(upload_to='images/', blank=True, null=True)

    class Meta:
        unique_together = (('contest', 'join_code'), ('contest', 'name'))

    def getName(self):
        return self.name

    def getContest(self):
        return self.contest

    def getUsers(self):
        return self.users.all()

    def hasUser(self, user):
        return self.users.filter(id=user.id).exists()

    def getJoinCode(self):
        return self.join_code

    def getAttempts(self):
        return Attempt.objects.filter(team=self).order_by('-date')

    def isFull(self):
        return self.users.count() >= self.contest.max_team_members


# TODO: Its possible to make this inside the Model?
# get the team attempts
# def getAttempts(self):
#	members_ids = self.teammember_set.values_list('user__id', flat=True).distinct()
#	if not members_ids:
#		return None
#	return Attempt.objects.filter(contest=self.contest, user__in=members_ids).order_by('-date')


class Attempt(models.Model):
    contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, default=1, null=False, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, default=1, null=True,
                             on_delete=models.SET_NULL)  # this is redundant but it's just easier...
    date = models.DateTimeField(auto_now_add=True, blank=True)
    file = models.FileField(upload_to=get_file_path, blank=False, null=False, max_length=512,
                            validators=[validate_file_extension])

    comment = models.CharField(null=True, max_length=128, blank=True)
    compile_error = models.BooleanField(null=False, default=False, blank=True)
    failed_mandatory_test = models.BooleanField(null=False, default=False, blank=True)
    error_description = models.TextField(null=True, blank=True)
    grade = models.IntegerField(blank=True, null=True, default=0)
    time_benchmark = models.IntegerField(blank=True, null=True, default=0)
    memory_benchmark = models.IntegerField(blank=True, null=True, default=0)
    elapsed_time = models.IntegerField(blank=True, null=True, default=0)
    cpu_time = models.DecimalField(blank=True, null=True, decimal_places=3, max_digits=8)
    static_analysis = models.TextField(blank=True, null=True)

    def getContest(self):
        return self.contest

    def getTeam(self):
        return self.team

    def getClassifications(self):
        return self.classification_set.all()

    def getPassedTestsCount(self):
        n = self.getClassifications().filter(passed=True).count()
        mandatory = self.getClassifications().filter(passed=True, test__mandatory=True).count()
        diff = self.getClassifications().filter(passed=True, test__mandatory=False).count()
        return n, mandatory, diff


    def get_absolute_url(self):
        return "/contests/%i/attempt/%i/" % (self.contest.id, self.id)


class SafeExecError(models.Model):
    description = models.CharField(null=False, max_length=128, unique=True, blank=False)


class Classification(models.Model):
    attempt = models.ForeignKey(Attempt, default=1, null=False, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, default=1, null=False, on_delete=models.CASCADE)
    passed = models.BooleanField(null=False, default=False)
    output = models.FileField(blank=True, null=True, max_length=512)
    execution_time = models.IntegerField(blank=True, null=True)
    error_description = models.TextField(null=True, blank=True)
    #	error = models.ForeignKey(SafeExecError, blank=True, null=True, on_delete=models.SET_NULL)
    memory_usage = models.IntegerField(blank=True, null=True)
    elapsed_time = models.DecimalField(blank=True, null=True, decimal_places=3, max_digits=8)
    #	exception = models.TextField(null=True, blank=True)
    timeout = models.BooleanField(null=False, default=False)
    result = models.IntegerField(null=False, default=0)
    diff = models.TextField(default='')

"""
class TeamMember(models.Model):
    team = models.ForeignKey(Team, default=1, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, default=1, null=False, on_delete=models.CASCADE)
    approved = models.BooleanField(null=False, default=False, blank=True)
    unique_together = ('team', 'user')

"""


# class TeamManager(models.Manager):
#	use_for_related_fields = True

#	def number_of_elements(self, user, team):
#		Full_team_obj = TeamMember.objects.all().select_related('team').filter(team__contest = contest_obj.id).first()

class UserContestDateException(models.Model):
    contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, default=1, null=False, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    unique_together = ('contest', 'user')


class ContestTestDataFile(models.Model):
    contest = models.ForeignKey(Contest, default=1, null=False, on_delete=models.CASCADE)
    data_file = models.FileField(upload_to=get_contest_data_path, blank=False, null=False, max_length=512)
    file_name = models.CharField(max_length=150, blank=False)
    unique_together = ('contest', 'file_name')

class Group(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)
    users = models.ManyToManyField(User, blank=True)
    contests = models.ManyToManyField(Contest, blank=True)
    join_code = models.SlugField(max_length=32, blank=False, null=False, unique=True, default="replace_me")
    registration_open = models.BooleanField(null=False, default=False)

    def getName(self):
        return self.name

    def getUsers(self):
        return self.users.all()

    def getContests(self):
        return self.contests.all()

    def getJoinCode(self):
        return self.join_code

    def isRegistrationOpen(self):
        return self.registration_open

    def hasUser(self, user):
        return self.users.filter(id=user.id).exists()
