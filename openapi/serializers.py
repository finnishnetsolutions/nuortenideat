# coding=utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers
from rest_framework.reverse import reverse

from account.models import User
from content.models import Idea, IdeaSurvey
from nkcomments.models import CustomComment
from openapi.base_serializers import MultilingualTextField, MultilingualUrlField
from organization.models import Organization
from survey.models import Survey, SurveyOption, SurveyQuestion
from tagging.models import Tag

from . import base_serializers as base


class IdeaStatusField(serializers.ChoiceField):
    FRIENDLY_STATUSES = (
        (Idea.STATUS_DRAFT, "draft"),
        (Idea.STATUS_PUBLISHED, "published"),
        (Idea.STATUS_TRANSFERRED, "transferred-forward"),
        (Idea.STATUS_DECISION_GIVEN, "decision-given"),
    )
    #STATUS_CHOICES =

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = self.FRIENDLY_STATUSES
        kwargs['help_text'] = ' or '.join(
            map(lambda v: '"{}"'.format(v),
            [status[1] for status in self.FRIENDLY_STATUSES])
        )
        super(IdeaStatusField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        try:
            return dict(self.FRIENDLY_STATUSES)[value]
        except KeyError:
            return "unknown"


class TargetOrganizationSerializer(base.HyperlinkedModelSerializer):
    name = MultilingualTextField()

    class Meta:
        model = Organization
        fields = ('url', 'name', )


class IdeaSerializer(base.HyperlinkedModelSerializer):
    title = MultilingualTextField(help_text="title of the Idea")
    status = IdeaStatusField()

    class Meta:
        model = Idea
        fields = ('url', 'title', 'status', )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', )


class OrganizationSerializer(base.HyperlinkedModelSerializer):
    name = MultilingualTextField(help_text="name of the Organization")

    class Meta:
        model = Organization
        fields = ('url', 'name', )


class OrganizationIdeasSummarySerializer(serializers.Serializer):
    url = serializers.SerializerMethodField('_ideas_url',
                                            help_text="API URL for Ideas targeting the "
                                                      "Organization")
    count = base.SerializerMethodIntegerField('_ideas_count',
                                              help_text="number of public Ideas "
                                                        "targeting the Organization")

    def _ideas_count(self, obj):
        return Idea.objects.filter(visibility=Idea.VISIBILITY_PUBLIC,
                                   target_organizations__pk=obj.pk).count()

    def _ideas_url(self, obj):
        return reverse('openapi:organization-ideas', kwargs={'pk': obj.pk},
                       request=self.context['request'])


class OrganizationDetailSerializer(base.HyperlinkedModelSerializer):
    name = MultilingualTextField(help_text="name of the Organization")
    description = MultilingualTextField(source='description_plaintext',
                                        help_text="description of the Organization "
                                                  "without formatting")
    contacts = UserSerializer(source='admins', many=True, help_text="contacts of the "
                                                                    "Organization")
    ideas = OrganizationIdeasSummarySerializer(source='*',
                                               help_text="summary of Ideas targeting the "
                                                         "Organization")
    webUrl = MultilingualUrlField()

    class Meta:
        model = Organization
        fields = ('url', 'name', 'description', 'contacts', 'ideas', 'webUrl', )


class IdeaVotesSerializer(serializers.Serializer):
    up = serializers.IntegerField(source='up.count',
                                  help_text="number of 'thumbs up' the Idea has received")
    down = serializers.IntegerField(source='down.count',
                                    help_text="number of 'thumbs down' the Idea has "
                                              "received")


class IdeaCommentsSerializer(serializers.Serializer):
    count = serializers.IntegerField(source='public_comments.public.count',
                                     help_text="number of public comments the idea has "
                                               "received")
    url = serializers.SerializerMethodField('_comments_url',
                                            help_text="API URL for the idea's comments")

    def _comments_url(self, obj):
        return reverse('openapi:idea-comments', kwargs={'pk': obj.pk},
                       request=self.context['request'])


class SurveyBaseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    webUrl = MultilingualUrlField()

    def get_url(self, obj):
        return reverse('openapi:{}-detail'.format(obj.content_type.model),
                       kwargs={'pk': obj.pk}, request=self.context['request'])

    def get_is_closed(self, obj):
        return not obj.is_open()


class SurveySerializer(SurveyBaseSerializer):
    is_closed = serializers.SerializerMethodField(help_text="survey has expired")

    class Meta:
        model = IdeaSurvey
        fields = ('url', 'is_closed', )


class SurveyQuestionSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        source='content_object.elements.questions.count',
        help_text="number of questions in survey")
    url = serializers.SerializerMethodField('_questions_url',
                                            help_text="API URL for the questions "
                                                      "in survey")

    def _questions_url(self, obj):
        return reverse('openapi:survey-questions',
                       kwargs={'pk': obj.content_object.pk},
                       request=self.context['request'])


class SurveyDetailSerializer(SurveySerializer):

    questions = SurveyQuestionSerializer(source='*',
                                         help_text="Survey questions summary")

    class Meta:
        model = IdeaSurvey
        fields = ('url', 'is_closed', 'questions',
                  'webUrl')


class IdeaSurveySummarySerializer(serializers.Serializer):
    url = serializers.SerializerMethodField('_survey_url',
                                            help_text="API URL for Surveys "
                                                      "associated with the Idea")
    count = base.SerializerMethodIntegerField('_survey_count',
                                              help_text="number of public Surveys "
                                                        "associated with the Idea")

    def _survey_count(self, obj):
        ct = ContentType.objects.get_for_model(Survey)
        data = obj.idea_surveys.exclude(status=IdeaSurvey.STATUS_DRAFT).\
            filter(content_type_id=ct)
        return data.count()

    def _survey_url(self, obj):
        return reverse('openapi:idea-surveys', kwargs={'pk': obj.pk},
                       request=self.context['request'])


class IdeaDetailSerializer(base.HyperlinkedModelSerializer):
    title = MultilingualTextField(help_text="title of the Idea")
    description = MultilingualTextField(source='description_plaintext',
                                        help_text="description of the Idea without "
                                                  "formatting")
    initiatorOrganization = OrganizationSerializer(
        source='initiator_organization',
        help_text="Organization who created the Idea, if the Idea was created by an "
                  "Organization; null otherwise"
    )

    targetOrganizations = TargetOrganizationSerializer(  # NOQA
        source='target_organizations', many=True,
        help_text="Organizations the Idea targets"
    )
    status = IdeaStatusField()
    published = serializers.DateTimeField(help_text="timestamp when the idea was "
                                                    "published")
    owners = UserSerializer(many=True, help_text="Idea authors/owners")
    webUrl = MultilingualUrlField()

    votes = IdeaVotesSerializer(help_text="Idea votes summary")
    comments = IdeaCommentsSerializer(source='*', help_text="Idea comments summary")
    surveys = IdeaSurveySummarySerializer(source='*', help_text="Idea surveys summary")

    class Meta:
        model = Idea
        fields = ('url', 'published', 'title', 'status', 'description', 'owners',
                  'initiatorOrganization', 'targetOrganizations', 'webUrl', 'votes',
                  'comments', 'surveys')


class TagIdeasSummarySerializer(serializers.Serializer):
    url = serializers.SerializerMethodField('_ideas_url',
                                            help_text="API URL for Ideas associated with "
                                                      "the Tag")
    count = base.SerializerMethodIntegerField('_ideas_count',
                                              help_text="number of public Ideas "
                                                        "associated with the Tag")

    def _ideas_count(self, obj):
        return Idea.objects.filter(visibility=Idea.VISIBILITY_PUBLIC,
                                   tags__pk=obj.pk).count()

    def _ideas_url(self, obj):
        return reverse('openapi:tag-ideas', kwargs={'pk': obj.pk},
                       request=self.context['request'])


class TagSerializer(base.HyperlinkedModelSerializer):
    name = MultilingualTextField(help_text='label of the Tag')
    ideas = TagIdeasSummarySerializer(source='*')

    class Meta:
        model = Tag
        fields = ('url', 'name', 'ideas', )


class CommentAuthorSerializer(serializers.Serializer):
    anonymous = serializers.BooleanField(source='is_anonymous',
                                         help_text="true if the user was not logged in "
                                                   "when posting the comment; false "
                                                   "otherwise.")
    name = serializers.CharField(source='user_name',
                                 help_text="name given by non-logged-in user when "
                                           "posting the comment; null if the user was "
                                           "logged in")
    user = UserSerializer(help_text="logged in user details; null if the user was "
                                    "anonymous")

    class Meta:
        fields = ('anonymous', 'name', 'user', )


class CommentSerializer(base.HyperlinkedModelSerializer):
    author = CommentAuthorSerializer(source='*', help_text="comment creator details")
    comment = serializers.CharField(source='comment_plaintext',
                                    help_text="comment text content without formatting")
    created = serializers.DateTimeField(source='submit_date',
                                        help_text="timestamp when the comment was posted")

    class Meta:
        model = CustomComment
        fields = ('comment', 'created', 'author', )



class QuestionOptionsSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(help_text="primary key for option")
    text = serializers.CharField(help_text="answer option")

    class Meta:
        model = SurveyOption
        fields = ('pk', 'text', )


class QuestionAnswersSerializer(serializers.ModelSerializer):
    option_id = serializers.IntegerField(help_text="answer refers to option primary key")
    text = serializers.CharField(help_text="textual answer to question")

    class Meta:
        model = SurveyOption
        fields = ('text', 'option_id')


class QuestionSerializer(serializers.ModelSerializer):

    question = MultilingualTextField(source='text', help_text='the question')
    type = serializers.SerializerMethodField(help_text="type of question")
    instruction = MultilingualTextField(
        source='instruction_text', help_text="instructions for answering the question")

    options = QuestionOptionsSerializer(many=True,
                                        help_text="answer options for question")

    # todo: show answers on if show_results = SHOW_RESULTS_EVERYONE
    #answers = QuestionAnswersSerializer(many=True,
    #                                    help_text="submitted answers to question")

    def get_type(self, obj):
        return obj.get_type_display()

    class Meta:
        model = SurveyQuestion
        fields = ('question', 'type', 'instruction', 'options', )


class PaginatedIdeaSerializer(base.PaginationSerializer):
    results = IdeaSerializer(many=True)

    class Meta:
        object_serializer_class = IdeaSerializer


class PaginatedCommentSerializer(base.PaginationSerializer):
    results = CommentSerializer(many=True)

    class Meta:
        object_serializer_class = CommentSerializer


class PaginatedTagSerializer(base.PaginationSerializer):
    results = TagSerializer(many=True)

    class Meta:
        object_serializer_class = TagSerializer


class PaginatedOrganizationSerializer(base.PaginationSerializer):
    results = OrganizationSerializer(many=True)

    class Meta:
        object_serializer_class = OrganizationSerializer


class PaginatedSurveySerializer(base.PaginationSerializer):
    results = SurveySerializer(many=True)

    class Meta:
        object_serializer_class = SurveyDetailSerializer


class PaginatedQuestionSerializer(base.PaginationSerializer):
    results = QuestionSerializer(many=True)

    class Meta:
        object_serializer_class = QuestionSerializer
