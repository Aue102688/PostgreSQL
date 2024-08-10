from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from wtforms import Field, widgets, StringField
from wtforms.validators import DataRequired

import models


class TagListField(Field):
    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.data = []

    def process_formdata(self, valuelist):
        print("Incoming valuelist:", valuelist)
        data = []
        if valuelist:
            # ตรวจสอบว่า valuelist เป็น string หรือไม่
            if isinstance(valuelist[0], str):
                data = [x.strip() for x in valuelist[0].split(",")]
            else:
                # ในกรณีที่เป็น Tag objects
                data = [tag.name for tag in valuelist]

        print("Processed data:", data)

        if not self.remove_duplicates:
            self.data = data
            return

        self.data = []
        for d in data:
            if d not in self.data:
                self.data.append(d)
        print("Final data:", self.data)

    def _value(self):
        if self.data:
                # ตรวจสอบว่าทุกค่าใน self.data เป็น string
                return ", ".join([str(tag) if isinstance(tag, str) else tag.name for tag in self.data])
        else:
            return ""


BaseNoteForm = model_form(
    models.Note, base_class=FlaskForm, exclude=["created_date", "updated_date"], db_session=models.db.session
)


class TagForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])

BaseNoteForm = model_form(
    models.Note, base_class=FlaskForm, exclude=["created_date", "updated_date", "tags"], db_session=models.db.session
)

class NoteForm(BaseNoteForm):
    tags = TagListField("Tag")
