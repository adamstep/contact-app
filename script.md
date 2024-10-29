# Create contacts list

## Create dir

!mkdir templates/hv


## Create layout

templates/hv/layout.xml

```
<doc xmlns="https://hyperview.org/hyperview">
  <screen>
    <styles>
      <style id="header" flexDirection="row" justifyContent="space-between" alignItems="center" borderBottomColor="#ccc" borderBottomWidth="1" paddingLeft="24" paddingRight="24" paddingVertical="16" backgroundColor="white" />
      <style id="header-title" fontSize="16" color="black" fontWeight="500" />
      <style id="header-button" fontSize="16" color="blue" />

      <style id="body" flex="1"></style>
      <style id="main" flex="1" backgroundColor="#eee"></style>

      <style id="search-field" paddingHorizontal="24" paddingVertical="8" borderBottomWidth="1" borderBottomColor="#ddd" backgroundColor="#eee" />

      <style id="contact-item" borderBottomColor="#ddd" borderBottomWidth="1" paddingLeft="24" paddingRight="24" paddingVertical="16" backgroundColor="white" />
      <style id="contact-item-label" fontWeight="500" />
      <style id="load-more-item" paddingVertical="16" />
      <style id="swipe-button" height="100%" justifyContent="center" textAlign="center" paddingLeft="24" />

      <style id="contact-name" fontSize="24" textAlign="center" marginVertical="32" fontWeight="500" />
      <style id="contact-section" margin="8" backgroundColor="white" borderRadius="8" padding="8" marginHorizontal="24" />
      <style id="contact-section-label" fontSize="12" color="#aaa" marginBottom="4" />
      <style id="contact-section-info" fontSize="14" fontWeight="500" color="blue" />

      <style id="edit-group" marginVertical="32" />
      <style id="edit-field" borderBottomWidth="1" borderColor="#ddd" paddingHorizontal="24" paddingVertical="16" backgroundColor="white" />
      <style id="edit-field-error" color="red" fontSize="12" marginTop="4" />

      <style id="button" borderBottomWidth="1" borderColor="#ddd" paddingHorizontal="24" paddingVertical="16" backgroundColor="white" />
      <style id="button-label" color="blue" fontWeight="500" />
      <style id="button-label-delete" color="red" />

    </styles>

    <body style="body" safe-area="true">
      <header style="header">
        {% block header %}
          <text style="header-title">Contacts.app</text>
        {% endblock %}
      </header>

      <view style="main">
        {% block content %}{% endblock %}
      </view>
    </body>

  </screen>
</doc>
```


## Create index

templates/hv/index.xml


```
{% extends 'hv/layout.xml' %}

{% block header %}
  <text style="header-title">
    Contacts
  </text>
{% endblock %}

{% block content %}
  <form>
    <text-field name="q" value="" placeholder="Search..." style="search-field" />
    <list id="contacts-list">
      {% include 'hv/rows.xml' %}
    </list>
  </form>
{% endblock %}
```

## Create rows

templates/hv/rows.xml

```
<items xmlns="https://hyperview.org/hyperview">
  {% for contact in contacts %}
    <item key="{{ contact.id }}" style="contact-item">
      <behavior trigger="press" action="push" href="/contacts/{{ contact.id }}" />
      <text style="contact-item-label">
        {% if contact.first %}
          {{ contact.first }} {{ contact.last }}
        {% elif contact.phone %}
          {{ contact.phone }}
        {% elif contact.email %}
          {{ contact.email }}
        {% endif %}
      </text>
    </item>
  {% endfor %}
</items>
```

## Update contacts route

app.py

- Add under page page:
```
rows_only = request.args.get("rows_only") == "true"
```
- Remove Hx-Trigger code
- Add switch based on query param
```
template_name = "hv/rows.xml" if rows_only else "hv/index.xml"
```
- Update rendered template:
```
return render_template(template_name, contacts=contacts_set)
```


# Searching contacts

templates/hv/index.xml

open/close `<text-field></text-field>`

```
<behavior
    trigger="change"
    action="replace-inner"
    target="contacts-list"
    href="/contacts?rows_only=true"
    verb="get"
/>
```


# Infinite scroll

templates/hv/rows.xml

```
  {% if contacts|length > 0 %}
    <item key="load-more" id="load-more" style="load-more-item">
      <behavior
        trigger="visible"
        action="replace"
        target="load-more"
        href="/contacts?rows_only=true&page={{ page + 1 }}"
        verb="get" />
      <spinner />
    </item>
  {% endif %}
```


# Pull-to-refresh

hv/index.xml

```
<list id="contacts-list" trigger="refresh" action="replace-inner" target="contacts-list" href="/contacts?rows_only=true">
```

# Viewing details

hv/rows.xml

```
<behavior trigger="press" action="push" href="/contacts/{{ contact.id }}" />
```

app.py

```
@app.route("/contacts/<contact_id>")
def contacts_view(contact_id=0):
    contact = Contact.find(contact_id)
    return render_template("hv/show.xml", contact=contact)
```

hv/show.xml

```
{% extends 'hv/layout.xml' %}

{% block header %}
  <text style="header-button">
    <behavior trigger="press" action="back" />
    Back
  </text>
{% endblock %}

{% block content %}
<view style="details">
  <text style="contact-name">
    {{ contact.first }} {{ contact.last }}
  </text>

  <view style="contact-section">
    <text style="contact-section-label">Phone</text>
    <text style="contact-section-info">{{contact.phone}}</text>
  </view>

  <view style="contact-section">
    <text style="contact-section-label">Email</text>
    <text style="contact-section-info">{{contact.email}}</text>
  </view>
</view>
{% endblock %}
```


# Editing contacts

hv/show.xml, in the header:

```
  <text style="header-button">
    <behavior trigger="press" action="reload"
      href="/contacts/{{contact.id}}/edit" />
    Edit
  </text>
```

app.py

```
@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id=0):
    contact = Contact.find(contact_id)
    return render_template("hv/edit.xml", contact=contact)
```

hv/edit.xml

```
{% extends 'hv/layout.xml' %}

{% block header %}
  <text style="header-button">
    <behavior trigger="press" action="back" href="#" />
    Back
  </text>
{% endblock %}

{% block content %}
<form>
  <view id="form-fields">
    {% include 'hv/form_fields.xml' %}
  </view>

  <view style="button">
    <behavior
      trigger="press"
      action="replace-inner"
      target="form-fields"
      href="/contacts/{{contact.id}}/edit"
      verb="post"
    />
    <text style="button-label">Save</text>
  </view>
  <view style="button">
    <behavior trigger="press" action="reload"
      href="/contacts/{{contact.id}}" />
    <text style="button-label">Cancel</text>
  </view> 
</form>
{% endblock %}
```

hv/form_fields.xml

```
<view xmlns="https://hyperview.org/hyperview" style="edit-group">
  <view style="edit-field">
    <text-field name="first_name" placeholder="First name" value="{{ contact.first|default('', true) }}" />
  </view>

  <view style="edit-field">
    <text-field name="last_name" placeholder="Last name" value="{{ contact.last|default('', true) }}" />
  </view>

  <view style="edit-field">
    <text-field name="email" placeholder="Email" value="{{ contact.email|default('', true) }}" />
    {% if contact.errors.email %}
      <text style="edit-field-error">{{ contact.errors.email }}</text>
    {% endif %}
  </view>

  <view style="edit-field">
    <text-field name="phone" placeholder="Phone number" value="{{ contact.phone|default('', true) }}" mask="(999) 999-9999" />
  </view>
</view>
```

app.py

```
@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id=0):
    c = Contact.find(contact_id)
    c.update(
      request.form['first_name'],
      request.form['last_name'], 
      request.form['phone'], 
      request.form['email'])
    if c.save():
        flash("Updated Contact!")
        return render_template("hv/form_fields.xml", contact=c, saved=True)
    else:
        return render_template("hv/form_fields.xml", contact=c) 
```


form_field.xml

```
  {% if saved %}
    <behavior trigger="load" once="true" action="reload" href="/contacts/{{contact.id}}" />
  {% endif %}
```

```
  {% if saved %}
    <behavior trigger="load" once="true" action="dispatch-event" event-name="contact-updated" />
    <behavior trigger="load" once="true" action="reload" href="/contacts/{{contact.id}}" />
  {% endif %}
```

hx/index.xml, in form. Reload app after

```
  <behavior
    trigger="on-event"
    event-name="contact-updated"
    action="replace-inner"
    target="contacts-list"
    href="/contacts?rows_only=true"
  />
```


# Deleting contacts

hv/edit.xml

```
<view style="button">
  <behavior
    trigger="press"
    action="append"
    target="form-fields"
    href="/contacts/{{contact.id}}/delete"
    verb="post"
  />
  <text style="button-label button-label-delete">Delete Contact</text>
</view>
```


hv/deleted.xml

```
<view>
  <behavior trigger="load" action="dispatch-event" event-name="contact-updated" />
  <behavior trigger="load" action="back" />
</view>
```


app.py, change method

```
@app.route("/contacts/<contact_id>/delete", methods=["POST"])
def contacts_delete(contact_id=0):
    contact = Contact.find(contact_id)
    contact.delete()
    flash("Deleted Contact!")
    return render_template("hv/deleted.xml")
```

hv/edit.xml

```
  <behavior
    xmlns:alert="https://hyperview.org/hyperview-alert"
    trigger="press"
    action="alert"
    alert:title="Confirm delete"
    alert:message="Are you sure you want to delete {{ contact.first }}?"
  >
    <alert:option alert:label="Confirm">
      <behavior
        trigger="press"
        action="append"
        target="form-fields"
        href="/contacts/{{contact.id}}/delete"
        verb="post"
      />
    </alert:option>
    <alert:option alert:label="Cancel" />
  </behavior>
```


# Adding contacts

hv/index.xml

Add button

```
  <text style="header-button">
    <behavior trigger="press" action="new" href="/contacts/new" />
    Add
  </text>
```


hv/templates/new.xml

```
{% extends 'hv/layout.xml' %}

{% block header %}
  <text style="header-button">
    <behavior trigger="press" action="back" href="#" />
    Back
  </text>
{% endblock %}

{% block content %}
<form>
  <view id="form-fields">
    {% include 'hv/form_fields.xml' %}
  </view>

  <view style="edit-group">
    <view style="button">
      <behavior trigger="press" action="replace" target="form-fields" href="/contacts/new" verb="post" />
      <text style="button-label">Add Contact</text>
    </view>
  </view>
</form>
{% endblock %}
```

app.py

```
@app.route("/contacts/new", methods=['GET'])
def contacts_new_get():
    return render_template("hv/new.xml", contact=Contact())

@app.route("/contacts/new", methods=['POST'])
def contacts_new():
    c = Contact(None, request.form['first_name'], request.form['last_name'], request.form['phone'],
                request.form['email'])
    if c.save():
        flash("Created New Contact!")
        return render_template("hv/form_fields.xml", contact=c, saved=True)
    else:
        return render_template("hv/form_fields.xml", contact=c)
```



# Extensible client: messages

Show ~/projects/hyperview/demo/src/message.js

hv/messages.xml
```
{% for message in get_flashed_messages() %}
  <behavior
    xmlns:message="https://hypermedia.systems/hyperview/message"
    trigger="load"
    action="show-message"
    message:text="{{ message }}"
  />
{% endfor %}
```

hv/form_fields.xml
```
{% if saved %}
    {% include "hv/messages.xml" %}
```

hv/deleted.xml
```
{% include "hv/messages.xml" %}
```


# Swipe gesture
Show ~/projects/hyperview/demo/src/swipeable.js

hv/rows.xml
```
    <item key="{{ contact.id }}" id="item-{{ contact.id }}">
      <swipe:row xmlns:swipe="https://hypermedia.systems/hyperview/swipeable">
        <swipe:main>
          <view style="contact-item">
            <behavior trigger="press" action="push" href="/contacts/{{ contact.id }}" />
            <text style="contact-item-label">
              {% if contact.first %}
                {{ contact.first }} {{ contact.last }}
              {% elif contact.phone %}
                {{ contact.phone }}
              {% elif contact.email %}
                {{ contact.email }}
              {% endif %}
            </text>
          </view>
        </swipe:main>
       </swipe:row>
    </item>
```

```
        <swipe:button>
          <view style="swipe-button">
            <text style="button-label">Edit</text>
          </view>
        </swipe:button>

        <swipe:button>
          <view style="swipe-button">
            <text style="button-label-delete">Delete</text>
          </view>
        </swipe:button>
```


edit:
```
<behavior trigger="press" action="push" href="/contacts/{{ contact.id }}/edit" />
```

delete:
```
                <behavior
                  xmlns:alert="https://hyperview.org/hyperview-alert"
                  trigger="press"
                  action="alert"
                  alert:title="Confirm delete"
                  alert:message="Are you sure you want to delete {{ contact.first }}?"
                >
                  <alert:option alert:label="Confirm">
                    <behavior
                      trigger="press"
                      action="append"
                      target="item-{{ contact.id }}"
                      href="/contacts/{{ contact.id }}/delete"
                      verb="post"
                    />
                  </alert:option>
                  <alert:option alert:label="Cancel" />
                </behavior>
```
