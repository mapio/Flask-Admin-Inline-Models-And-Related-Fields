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
enviroment](https://docs.python.org/3/tutorial/venv.html), in the same directory where you have cloned this repo:

```shell
python3 -m venv vevn
. ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

You can check in the [requirements.txt](/requirements.txt) file the *version numbers* of the tool this example is guaranteed to work with.

Then you can run the application as usual [run the developement server](https://flask.palletsprojects.com/en/2.2.x/cli/#run-the-development-server) as

```shell
flask --debug run --port 8080
```

Pointing the browser at [http://localhost:8080/](http://localhost:8080/) you should be able to reach the application.

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

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/f06e69e39cfca5585c2cc40a3cc3c1006da44678/app.py#L10-L17

Then the two *parent* and *child* models are defined as shown in the SQLAlchemy documentation

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/f06e69e39cfca5585c2cc40a3cc3c1006da44678/app.py#L20-L35

and a third *related* model is added to store the selections from the form with related, or cascading, fields described at point 2. above

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/f06e69e39cfca5585c2cc40a3cc3c1006da44678/app.py#L38-L44

### The views

The two goals can be obtained independently, the following two subsections show how to implement two distinct *views* each one solving one of the above points.

#### Preventing deletion

To inline the *child* model view in the *parent* view just set the
`inline_models` attribute of the *parent* view as usual. 

To customize the inline form so that it will not contain the "Delete ?"
checkbox:

* set the `inline_model_form_converter` attribute of the *parent* view to a custom converter obtained in turn by
* subclassing the default converter simply adding the `inline_field_list_type` attribute as a
* subclass of the default form list where you override the `display_row_controls` method so that it always returns  `False`.

Easily done than said

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/f06e69e39cfca5585c2cc40a3cc3c1006da44678/app.py#L47-L60

#### Cascading fields


### Putting things together

Once the views are defined, it's enough to instantiate the administrative backend and to add to it the views

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/f06e69e39cfca5585c2cc40a3cc3c1006da44678/app.py#L105-L113

Finally, to show some data when the application starts, few records are used to prepopulate each model

https://github.com/mapio/Flask-Admin-Inline-Models-And-Related-Fields/blob/f06e69e39cfca5585c2cc40a3cc3c1006da44678/app.py#L105-L113