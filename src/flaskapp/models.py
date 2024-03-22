"""
MongoDB Models for Mongoengine
"""

import json

from mongoengine import (
    BooleanField,
    Document,
    IntField,
    StringField,
)


class TriageNote(Document):
    pid = StringField(required=True)
    stat = BooleanField(required=True)
    age = IntField(required=False)
    sex = StringField(required=False)
    triage = StringField(required=True)
    correlation_id = StringField(required=True)

    def __str__(self):
        return json.dumps(self)


class TriagePage(Document):
    correlation_id = StringField(required=True)
    page = StringField(required=True)
    iss_category = StringField(required=False)

    def __str__(self):
        return json.dumps(self)
