from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
# bad practice
link_wall_username = "admin"
link_wall_password = "hello1234"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkwall.db'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)

db = SQLAlchemy(app)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linkurl = db.Column(db.String(200), nullable=False)
    tag = db.Column(db.String(50), nullable=False)


@app.route('/login', methods=["GET", "POST"])
def login():
    if(session.get("isAdmin") == "YES"):
        return redirect("/admin")
    else:
        if(request.method == "POST"):
            if(request.form["username"] == link_wall_username and request.form["password"] == link_wall_password):
                session["isAdmin"] = "YES"
                return redirect("/admin")
            else:
                return "Wrong Credentials"

        return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/links')


@app.route('/admin', methods=["GET", "POST"])
def link():
    if(session.get("isAdmin") == "YES"):
        if(request.method == "POST"):
            linkpost = request.form["linkpost"]
            tag = request.form["tag"]
            print(tag)
            if(len(str(linkpost)) != 0):
                new_linkpost = Link(linkurl=linkpost, tag=tag)
                try:
                    db.session.add(new_linkpost)
                    db.session.commit()
                    return redirect('/admin')
                except:
                    return 'There was an issue adding the link'
            else:
                return redirect('/admin')
        else:
            links = Link.query.order_by(Link.id).all()
            return render_template("admin.html", links=links)
    else:
        return "You are not logged in :)"


@app.route('/delete/<int:id>')
def delete(id):
    if(session.get("isAdmin") == "YES"):
        link_to_delete = Link.query.get_or_404(id)

        try:
            db.session.delete(link_to_delete)
            db.session.commit()
            return redirect('/admin')
        except:
            return 'There was a problem deleting that task'
    else:
        return "You are not supposed to be here naughty human/thing"


@app.route('/tag/<tag>')
def tag(tag):
    if(session.get("isAdmin") == "YES"):
        all_links = Link.query.order_by(Link.id).all()
        links = []
        for link in all_links:
            if(link.tag==tag):
                links.append(link)      
        return render_template("tag.html", links=links,tag=tag)
    else:
        return "You are not supposed to be here naughty human/thing"


@app.route('/')
@app.route('/links')
def display_links():
    links = Link.query.order_by(Link.id).all()
    tags = []
    for link in links:
        tags.append(link.tag)
    unique_tags = list(set(tags))
    return render_template("links.html", links=links,unique_tags=unique_tags)


if __name__ == "__main__":
    app.run(debug=True)
