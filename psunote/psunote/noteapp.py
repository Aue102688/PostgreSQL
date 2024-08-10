import flask

import models
import forms


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

models.init_app(app)

def refresh_tags(note):
    db = models.db
    db.session.refresh(note)  # Refresh the note's relationships from the database
    return note

@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
    )

@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
def notes_edit(note_id):
    db = models.db
    note = db.session.execute(db.select(models.Note).where(models.Note.id == note_id)).scalars().first()
    
    if not note:
        return flask.redirect(flask.url_for("index"))

    form = forms.NoteForm(obj=note)
    if form.validate_on_submit():
        form.populate_obj(note)
        note.tags = []

        for tag_name in form.tags.data:
            tag = (
                db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
                .scalars()
                .first()
            )

            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)

            note.tags.append(tag)

        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    return flask.render_template("notes-edit.html", form=form, note=note
    )


@app.route("/notes/<int:note_id>/edit-tags", methods=["GET", "POST"])
def tags_edit(note_id):
    db = models.db
    note = db.session.execute(db.select(models.Note).where(models.Note.id == note_id)).scalars().first()

    if not note:
        return flask.redirect(flask.url_for("index"))

    form = forms.NoteForm(obj=note)

    # Pre-populate the form with existing tags
    if flask.request.method == "GET":
        form.tags.data = [tag.name for tag in note.tags]

    if form.validate_on_submit():
        # Clear the existing tags
        note.tags.clear()

        # Add the new or existing tags
        for tag_name in form.tags.data:
            tag = db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name)).scalars().first()
            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)
            note.tags.append(tag)

        # Commit the changes to the database
        db.session.commit()
        
        # Redirect to the index page after successful edit
        return flask.redirect(flask.url_for("index"))

    return flask.render_template("tags-edit.html", form=form, note=note)




if __name__ == "__main__":
    app.run(debug=True)
