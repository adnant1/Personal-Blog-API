from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

#Create flask instance
app = Flask(__name__)

#Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://root:Flint346297@localhost/blog_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#Blog model
class Blog(db.Model):
    __tablename__ = "blogs"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(50), nullable = False)
    content = db.Column(db.Text, nullable = False)
    tag = db.Column(db.String(50))

    #Method that will turn the Todo model into a dict so its easier to turn to JSON
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tag": self.tag
            }








if __name__ == "__main__":
    app.run(debug=True)