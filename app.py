from flask import (
    Flask, redirect, render_template, request, flash
)
from contacts_model import Contact
import time

Contact.load_db()

# ========================================================
# Flask App
# ========================================================

app = Flask(__name__)

app.secret_key = b'hypermedia rocks'

app.config["TEMPLATES_AUTO_RELOAD"] = True

HYPERVIEW_MIME_TYPES = ['application/vnd.hyperview+xml', 'application/vnd.hyperview_fragment+xml']

def is_hyperview_request(req):
    for t in HYPERVIEW_MIME_TYPES:
        if t in req.headers.get('Accept', ''):
            return True
    return False


@app.route("/")
def index():
    return redirect("/contacts")


@app.route("/contacts")
def contacts():
    search = request.args.get("q")
    page = int(request.args.get("page", 1))
    if search:
        contacts_set = Contact.search(search)
        if request.headers.get('HX-Trigger') == 'search':
            return render_template("rows.html", contacts=contacts_set, page=page)
    else:
        contacts_set = Contact.all(page)
    return render_template("hv/index.html", contacts=contacts_set, page=page)


@app.route("/contacts/count")
def contacts_count():
    count = Contact.count()
    return "(" + str(count) + " total Contacts)"


@app.route("/contacts/new", methods=['GET'])
def contacts_new_get():
    return render_template("new.html", contact=Contact())


@app.route("/contacts/new", methods=['POST'])
def contacts_new():
    c = Contact(None, request.form['first_name'], request.form['last_name'], request.form['phone'],
                request.form['email'])
    if c.save():
        flash("Created New Contact!")
        return redirect("/contacts")
    else:
        return render_template("new.html", contact=c)


@app.route("/contacts/<contact_id>")
def contacts_view(contact_id=0):
    contact = Contact.find(contact_id)
    template = 'hv/show.xml' if is_hyperview_request(request) else 'show.html'
    return render_template(template, contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id=0):
    contact = Contact.find(contact_id)
    template = 'hv/edit.xml' if is_hyperview_request(request) else 'edit.html'
    return render_template(template, contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id=0):
    c = Contact.find(contact_id)
    c.update(request.form['first_name'], request.form['last_name'], request.form['phone'], request.form['email'])
    if c.save():
        flash("Updated Contact!")
        #return redirect("/contacts/" + str(contact_id))
        return render_template('hv/_details.xml', contact=c, updated=True)
    else:
        template = 'hv/edit.xml' if is_hyperview_request(request) else 'edit.html'
        return render_template(template, contact=c)


@app.route("/contacts/<contact_id>/email", methods=["GET"])
def contacts_email_get(contact_id=0):
    c = Contact.find(contact_id)
    c.email = request.args.get('email')
    c.validate()
    return c.errors.get('email') or ""


@app.route("/contacts/<contact_id>", methods=["DELETE"])
def contacts_delete(contact_id=0):
    contact = Contact.find(contact_id)
    contact.delete()
    if request.headers.get('HX-Trigger') == 'delete-brn':
        flash("Deleted Contact!")
        return redirect("/contacts", 303)
    else:
        return ""


@app.route("/contacts/", methods=["DELETE"])
def contacts_delete_all():
    contact_ids = list(map(int, request.form.getlist("selected_contact_ids")))
    for contact_id in contact_ids:
        contact = Contact.find(contact_id)
        contact.delete()
    flash("Deleted Contacts!")
    contacts_set = Contact.all(1)

    if is_hyperview_request(request):
        return render_template('hv/_deleted.xml')
    else:
        return render_template("index.html", contacts=contacts_set)


if __name__ == "__main__":
    app.run()
