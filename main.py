from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

#Create flask instance
app = Flask(__name__)

#Configure secret key
#Fix later before making repo public
app.config["SECRET_KEY"] = 'flint346297'

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

#User model
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    #When the token is decoded this is the id that will show up, will not match the actual id from the table
    public_id = db.Column(db.String(50), unique = True)
    name = db.Column(db.String(50), nullable = False)
    password = db.Column(db.String(100), nullable = False)
    admin = db.Column(db.Boolean, default = False)

    #to dict method
    def to_dict(self):
        return {
            "public_id": self.public_id,
            "name": self.name,
            "password": self.password,
            "admin": self.admin
        }


#User Admin routes

#Get all users
@app.route('/users', methods=["GET"])
def get_all_users():

    users = User.query.all()

    return jsonify([user.to_dict() for user in users]), 200


#Return a single user
@app.route('/user/<public_id>', methods=["GET"])
def get_single_user(public_id):

    #Use filter by when querying the data based off anything but the primary key
    #Returns a query object, so use .first() to get the first user returned
    user = User.query.filter_by(public_id = public_id).first()

    if user:
        return jsonify({"user": user.to_dict()}), 200
    
    return jsonify({"error": "user not found"}), 404


#Create a user
@app.route('/user', methods=["POST"])
def create_user():

    data = request.get_json()

    #Hash the password, this method is the default method
    hashed_password = generate_password_hash(data['password'], method="pbkdf2:sha256")

    #Create new user
    #UUID4 creates a UUID based on random numbers
    new_user = User(
        public_id = str(uuid.uuid4()),
        name = data["name"],
        password = hashed_password
    )

    #add the user to the db
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "new user created successfully"}), 201


#Promote a user to admin
@app.route('/user/<public_id>', methods=["PUT"])
def promote_user(public_id):

    user = User.query.filter_by(public_id = public_id).first()

    if user:
        user.admin = True
        db.session.commit()
        return jsonify({"message": "user promoted successfully"}), 200

    return jsonify({"error": "user not found"}), 404


#Delete a user
@app.route('/user/<public_id>', methods=["DELETE"])
def delete_user(public_id):

    user = User.query.filter_by(public_id = public_id).first()

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "user deleted successfully"}), 200

    return jsonify({"error": "user not found"}), 404


#Blog routes

#Post a new blog
@app.route("/blog", methods=["POST"])
def post_blog():

    data = request.get_json()

    #Create new blog
    blog = Blog(
        title = data["title"],
        content = data["content"],
        tag = data.get("tag", "")
    )

    #add the blog to the db
    db.session.add(blog)
    db.session.commit()

    return jsonify({"message": "Blog posted successfully", "Blog": blog.to_dict()}), 201


#Return all blogs
@app.route("/blogs", methods=["GET"])
def get_blogs():

    #get all blogs
    blogs = Blog.query.all()

    return jsonify([blog.to_dict() for blog in blogs]), 200

#Return a single blog
@app.route("/blog/<int:id>", methods=["GET"])
def get_blog(id):

    blog = Blog.query.get(id)

    if blog:
        return jsonify({"blog": blog.to_dict()}), 200
    else:
        return jsonify({"error": "blog post not found."}), 404

#Update a single blog
@app.route("/blog/<int:id>", methods=["PUT"])
def update_blog(id):

    blog = Blog.query.get(id)
    data = request.get_json()

    if blog:
        blog.title = data.get("title", blog.title)
        blog.content = data.get("content", blog.content)
        blog.tag = data.get("tag", blog.tag)

        db.session.commit()
        return jsonify({"message": "blog post updated successfully", "blog": blog.to_dict()}), 200
    
    return jsonify({"error": "blog post not found"}), 404

#Delete a blog post
@app.route("/blog/<int:id>", methods=["DELETE"])
def delete_blog(id):

    blog = Blog.query.get(id)

    if blog:
        db.session.delete(blog)
        db.session.commit()
        return jsonify({"message": "blog post deleted successfully"}), 200
    
    return jsonify({"error": "blog post not found."}), 404



if __name__ == "__main__":
    app.run(debug=True)