# Flask-Admin inline models and related fields with Flask-SQLAlchemy

This repository is meant to show how to solve a couple of problems arising when
using inline editing of related models and related (or cascading) fields in
[Flask-Admin](https://flask-admin.readthedocs.io/) coupled with
[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/).

The use case is the following: assume you have a *parent*-*child* [one-to-many
relation](https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-many)
such as the relation among cities and streets, company departments and
employees, categories and products. Then you may want to have (independent)
forms that allow:

1. to edit the *child* in the context of the *parent*, but not to **delete** it
  in such context,
2. to have a first *select field* for the *parent* dinamically populating (when
  changed) a second **cascading** *select field* for the *child* containing just
  related values.

For example, you want to offer an *admin* of your application the possibility to
rename and add products (but not to delete them), and a *visitor* of your app to
first select a category of products and then choose a specific product in the
choosen category.

The application in this repository shows a simple way to achieve both goals
with, at the best of my undestanding of the tools, as less code as possible.

## How to run the app

As usual you'll need to install the requirements, better if in a [virtual
enviroment](https://docs.python.org/3/tutorial/venv.html), in the same directory
where you have cloned this repo:

```shell
python3 -m venv vevn
. ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

You can check in the [requirements.txt](/requirements.txt) file the *version
numbers* of the tool this example is guaranteed to work with.

Then you can run the application as usual [run the developement
server](https://flask.palletsprojects.com/en/2.2.x/cli/#run-the-development-server)
as

```shell
flask --debug run --port 8080
```

Pointing the browser at [http://localhost:8080/](http://localhost:8080/) you
should be able to reach the application.

Pleas note that the application uses a *prepupulated* [SQLite In-Memory
Database](https://www.sqlite.org/inmemorydb.html), so that every restart
(caused, for example, by editing the code while the application runs in debug
mode), causes a loss of all edits.

## The application

The application is built following what is shown in basic tutorials and examples
easily obtainable on-line. First some *models* are defined, then two *views* and
some support code is used to obtain the two goals described above; the juicy
part is described in the following views subsection.

### Models


First the application is created and configured and connected with SQLAchemy

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L10-L17

Then the two *parent* and *child* models are defined as shown in the SQLAlchemy
documentation

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L20-L35

and a third *related* model is added to store the selections from the form with
related, or cascading, fields described at point 2. above

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L38-L44

### The views

The two goals can be obtained independently, the following two subsections show
how to implement two distinct *views* each one solving one of the above points.

#### Preventing deletion

To inline the *child* model view in the *parent* view just set the
`inline_models` attribute of the *parent* view as usual. 

To customize the inline form so that it will not contain the "Delete ?"
checkbox:

* set the `inline_model_form_converter` attribute of the *parent* view to a
  custom converter obtained in turn by
* subclassing the default converter simply settin the `inline_field_list_type`
  attribute to a custom form list obtained in turn by
* subclassing the default form list by just overriding the
  `display_row_controls` method so that it always returns  `False`.

Easily done than said:

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L47-L60

#### Cascading fields

This goal requires a bit more effort. The idea is to build a form where:

* the *parent* select field is handled by Flask-Admin,
* the *related child* extra select field is a `Select2Field` handled by
  Flask-Admin,
* some Javascript code uses Ajax to populate the *related child* choices when
  the *parent* changes,
* an Ajax endpoint is provided by subclassing `AjaxModelLoader`,
* some Python code "connects" the value of the *related child* form field to the
  model attribute.

Let's start with the attributes part of the view

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L81-L90

Here the interesting part is the definition of `form_columns` [line 83] where
`related_child` substitutes `child`; since such field has no counterpart in the
model, it is added as a `form_extra_fields` [line 84], where it is defined as a
`Select2Field`. Pay attention to the parameters `choices` and `allow_blank` (so
defined because the select will be filled dynamically by the custom Javascript)
and `validate_choice` that is set to `False` as suggested in [Skipping choice
validation](https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.SelectField).

Finally we need to configure the view so that it will automatically scaffold a
endpoint to answer Ajax queries, this is done setting `form_ajax_refs` in line
89 to a subclass of `AjaxModelLoader` and adding some some `extra_js` [line 90]
that we are about to see now.

The code for `AjaxRelatedChildLoader` is trivial

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L63-L78

remember that this has to provide to the Ajax call a list of *child* related to
the queried *parent*. This is the reason why in overriding `get_one` we use the
`Child` model [line 73] and in overriding `get_list` we also use
`filter_by(parent_id=query)` to restrict the list of children to the ones
related to the parent that the Ajax call will put in the `query` parameter as
show in 

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/static/related_form.js#L2-L25

Again the relevant parts are is definition of the `on-change` handler [line 4].
The Ajax call is based on the `$parent_id` extracted [line 8] from the *parent*
field (handled by Flask-Admin) and used as the `query` parameter [line 10]
(together with the name of the endpoint [line 9]) and on the endpoint (generated
by Flask-Admin due the the `form_ajax_refs` configuration in the view) indicated
[line 7]. The callback for the Ajax call [lines 12-23] receives the data and
uses it to populate the select field (once reset to the single empty option) and
triggers a change event [line 22] so that the browser can update the form.

What remains to be done is to connect the value of the *related child* form
field to the *child* attribute of the model. This is done in Python by
overriding two methods of the view

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L92-L102

As its name suggests `on_form_prefill` is called once the edit form has been
scaffolded and some values are yet to be filled; in our case we need to fill
`form.related_child` with the possible `choiices` obtained from the model via
`model.parent.children` (the siblings, so to say, of the current choice) and the
`data` with the current selected *child*. On the other end, once the form has
been submitted and a change in the model has been detected (due to an edit, or a
create) overriding `on_model_change` allows us to set `model.child_id` from the
`form.related_child.data` value.

### Putting things together

Once the views are defined, it's enough to instantiate the administrative
backend and to add to it the views

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L105-L113

Finally, to show some data when the application starts, few records are used to
prepopulate each model

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/1c5963f1fc3d30dab7819f8642a621c7cc09dc0e/app.py#L115-L128