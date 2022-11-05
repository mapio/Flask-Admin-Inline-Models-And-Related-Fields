from flask import Flask
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.form.fields import Select2Field
from flask_admin.model.ajax import DEFAULT_PAGE_SIZE, AjaxModelLoader
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY="dev",
    SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy(app)


class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return self.name


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.ForeignKey("parent.id"))
    parent = db.relationship("Parent", backref="children")

    def __repr__(self):
        return self.name


class Related(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    parent_id = db.Column(db.ForeignKey("parent.id"))
    parent = db.relationship("Parent")
    child_id = db.Column(db.ForeignKey("child.id"))
    child = db.relationship("Child")


class NoDeleteInlineModelFormList(InlineModelFormList):
    def display_row_controls(self, field):
        return False


class NoDeleteInlineModelConverter(InlineModelConverter):
    inline_field_list_type = NoDeleteInlineModelFormList


class ParentView(sqla.ModelView):
    inline_models = [Child]
    inline_model_form_converter = NoDeleteInlineModelConverter
    column_list = ["name", "children"]
    column_searchable_list = ["name", "children.name"]


class AjaxRelatedChildLoader(AjaxModelLoader):
    def __init__(self, name, **options):
        super(AjaxRelatedChildLoader, self).__init__(name, options)

    def format(self, model):
        if not model:
            return None
        return (model.id, str(model))

    def get_one(self, pk):
        return db.get_or_404(Child, pk)

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        return db.session.execute(
            db.select(Child).filter_by(parent_id=query).offset(offset).limit(limit)
        ).scalars()


class RelatedView(sqla.ModelView):
    column_list = ["name", "parent", "child"]
    form_columns = ["name", "parent", "related_child"]
    form_extra_fields = {
        "related_child": Select2Field(
            "Related child", choices=[], allow_blank=True, validate_choice=False
        )
    }
    form_ajax_refs = {"related_child": AjaxRelatedChildLoader("related_child")}
    extra_js = ["/static/related_form.js"]

    def on_form_prefill(self, form, id):
        model = self.get_one(id)
        form.related_child.choices = [
            (str(child.id), child.name) for child in model.parent.children
        ]
        form.related_child.data = str(model.child_id)

    def on_model_change(self, form, model, is_created):
        model.child_id = (
            int(form.related_child.data) if form.related_child.data else None
        )


admin = Admin(
    app,
    index_view=AdminIndexView(url="/"),
    name="Related fields example",
    template_mode="bootstrap3",
)

admin.add_view(ParentView(Parent, db.session))
admin.add_view(RelatedView(Related, db.session))

with app.app_context():
    db.create_all()
    p0 = Parent(name="parent 0")
    c00 = Child(name="child 0 of parent 0", parent=p0)
    c10 = Child(name="child 1 of parent 0", parent=p0)
    c20 = Child(name="child 2 of parent 0", parent=p0)
    p1 = Parent(name="parent 1")
    c01 = Child(name="child 0 of parent 1", parent=p1)
    c11 = Child(name="child 1 of parent 1", parent=p1)
    r0 = Related(name="related 0", parent=p0, child=c10)
    db.session.add(p0)
    db.session.add(p1)
    db.session.add(r0)
    db.session.commit()
