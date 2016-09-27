# coding=utf-8

from __future__ import unicode_literals

from django import template
from content.models import Idea

register = template.Library()


def _get_idea_statuses(idea):
    statuses = list([(s[0], s[1], s[2]) for s in Idea.STATUSES])
    visibilities = dict([(s[0], (s[1], s[2])) for s in idea.VISIBILITIES])
    statuses.append((idea.get_status_values(
        visibilities, Idea.VISIBILITY_ARCHIVED, add_status_value=True)))
    return statuses


def _map_statuses(idea):
    idea_status_list = idea.get_status_list(add_status_value=True)
    statuses = []
    for status, date_field, text in _get_idea_statuses(idea):
        status_dict = {
            'classes': '',
            'date': '',
            'text': text
        }
        for s_val, s_date, s_text in idea_status_list:
            if status == s_val:
                classes = 'visited'
                if status == idea.status:
                    if idea.visibility != idea.VISIBILITY_ARCHIVED:
                        classes = 'active'
                elif status == idea.visibility and \
                                idea.visibility == Idea.VISIBILITY_ARCHIVED:
                        classes = 'active'

                if idea.status == Idea.STATUS_DRAFT:
                    classes = "{} draft".format(classes)
                status_dict.update({
                    'classes': classes,
                    'date': s_date,
                    'text': s_text
                })
                break
        statuses.append(status_dict)

    # pop out unnecessary statuses
    if idea.visibility == Idea.VISIBILITY_ARCHIVED and not idea.decision_given:
        # pop out decision given status
        statuses.pop(2)
    if idea.status != Idea.STATUS_DRAFT:
        # pop out draft status
        statuses.pop(0)
    if idea.visibility != Idea.VISIBILITY_ARCHIVED:
        # pop out archived status
        statuses.pop()

    return statuses


@register.assignment_tag()
def format_idea_statuses_for_progress_bar(idea):
    return _map_statuses(idea)

