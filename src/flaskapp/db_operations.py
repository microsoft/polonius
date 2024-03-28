import uuid

from mongoengine import Document

from .models import TriageNote, TriagePage


def generate_uuid() -> str:
    return str(uuid.uuid4())

def saveTriageNote(data):
    try:
        input_data = TriageNote(
                pid=data.get("MRN"),
                stat=data.get("STAT"),
                age=data.get("Age"),
                sex=data.get("Sex"),
                triage=data.get("Triage"),
                correlation_id=data.get("correlation_id")
            )

        db_result_input = save_to_db(input_data)
        if db_result_input and "Error" in db_result_input:
            return db_result_input
    except Exception as e:
        return e

def saveTriagePage(correlation_id, pager_text):
    try:
        pager_response = TriagePage(correlation_id=correlation_id, page=pager_text)

        db_result_pager = save_to_db(pager_response)
        if db_result_pager and "Error" in db_result_pager:
            return db_result_pager
    except Exception as e:
        return e

def save_to_db(collection: Document):
    try:
        collection.save()
    except Exception as e:
        return f"Error saving to database: {str(e)}"
