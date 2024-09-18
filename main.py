from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
import os

#Create flask instance
app = Flask(__name__)

#Configure secret key
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

#Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://root:Flint346297@localhost/blog_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#Blog model
class Blog(db.Model):
    __tablename__ = "blogs"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    author = db.Column(db.String(50), nullable = False)
    title = db.Column(db.String(50), nullable = False)
    content = db.Column(db.Text, nullable = False)
    tag = db.Column(db.String(50))

    #Method that will turn the Todo model into a dict so its easier to turn to JSON
    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
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


#A decorator that ensures a valid JWT token is provided in the request headers before accessing protected routes.
#Takes in a function, usually another route
def token_required(f):
    @wraps(f)
    #replaces the original function f when it's called
    def decorated(*args, **kwargs):
        token = None

        #x-access-token is a custom header where the client is expected to send the JWT token.
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        
        #If the token is empty
        if not token:
            return jsonify({"error": "token is missing."}), 401
        
        #Attempting to decode the token
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data["public_id"]).first()
        except:
            return jsonify({"error": "token is invalid."}), 401
        
        #If the token is valid, then the decorated function f is called, passing in the user as an argument
        return f(current_user, *args, **kwargs)
    
    #returns the decorated function, which is now wrapped around the original function f with the token authentication logic.
    return decorated

#User Admin routes

#Get all users
@app.route('/users', methods=["GET"])
@token_required
def get_all_users(current_user):

    #Check if the user is an admin
    if not current_user.admin:
        #403 is the status code for forbidden
        return({"error": "user not authorized."}), 403

    users = User.query.all()

    return jsonify([user.to_dict() for user in users]), 200


#Return a single user
@app.route('/user/<public_id>', methods=["GET"])
@token_required
def get_single_user(current_user, public_id):

    #Check if the user is an admin
    if not current_user.admin:
        #403 is the status code for forbidden
        return({"error": "user not authorized."}), 403

    #Use filter by when querying the data based off anything but the primary key
    #Returns a query object, so use .first() to get the first user returned
    user = User.query.filter_by(public_id = public_id).first()

    if user:
        return jsonify({"user": user.to_dict()}), 200
    
    return jsonify({"error": "user not found"}), 404


#Create a user
@app.route('/user', methods=["POST"])
@token_required
def create_user(current_user):

    #Check if the user is an admin
    if not current_user.admin:
        #403 is the status code for forbidden
        return({"error": "user not authorized."}), 403

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
@token_required
def promote_user(current_user, public_id):

    #Check if the user is an admin
    if not current_user.admin:
        #403 is the status code for forbidden
        return({"error": "user not authorized."}), 403

    user = User.query.filter_by(public_id = public_id).first()

    if user:
        user.admin = True
        db.session.commit()
        return jsonify({"message": "user promoted successfully"}), 200

    return jsonify({"error": "user not found"}), 404


#Delete a user
@app.route('/user/<public_id>', methods=["DELETE"])
@token_required
def delete_user(current_user, public_id):

    #Check if the user is an admin
    if not current_user.admin:
        #403 is the status code for forbidden
        return({"error": "user not authorized."}), 403

    user = User.query.filter_by(public_id = public_id).first()

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "user deleted successfully"}), 200

    return jsonify({"error": "user not found"}), 404


#User login
@app.route("/login")
def login():

    #Retrieves the authorization credentials 
    auth = request.authorization

    #If the user isn't authenticated or no user or password
    if not auth or not auth.username or not auth.password:
        return make_response("Could not verify", 401, {"WWW-Authenticate" : "Basic realm='Login required.'"})
    
    #Find the user
    user = User.query.filter_by(name = auth.username).first()

    if not user:
        return make_response("Could not verify", 401, {"WWW-Authenticate" : "Basic realm='Login required.'"})
    
    #Now check the user's password
    if check_password_hash(user.password, auth.password):

        #If the password is correct
        #Create a token for the user, encoding the users public id, set expiration date to 30 mins, and encode using the secret key
        #Params (payload, key, algorithm): Information to be stored in the token, and the key to encode it, alg to encode default: HS256
        token = jwt.encode({"public_id": user.public_id, 'exp': datetime.now(timezone.utc) + timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"token": token})
    
    #If password is incorrect
    return make_response("Could not verify", 401, {"WWW-Authenticate" : "Basic realm='Login required.'"})


#Blog routes

#Post a new blog
@app.route("/blog", methods=["POST"])
@token_required
def post_blog(current_user):

    data = request.get_json()

    #Create new blog
    blog = Blog(
        author = current_user.name,
        title = data["title"],
        content = data["content"],
        tag = data.get("tag", "")
    )

    #add the blog to the db
    db.session.add(blog)
    db.session.commit()

    return jsonify({"message": "Blog posted successfully", "Blog": blog.to_dict()}), 201


#Admin route to return all blogs in the db
@app.route("/blogs", methods=["GET"])
@token_required
def get_blogs(current_user):

    #Check if the user is an admin
    if not current_user.admin:
        #403 is the status code for forbidden
        return({"error": "user not authorized."}), 403

    #get all blogs
    blogs = Blog.query.all()

    return jsonify([blog.to_dict() for blog in blogs]), 200


#Return blogs by an author
@app.route("/blogs/<author_name>", methods=["GET"])
@token_required
def get_author_blogs(current_user, author_name):

    #Check if theres an author by that name
    author = User.query.filter_by(name=author_name).first()

    if not author:
        return jsonify({"error": "no author by that name."}), 404

    blogs = Blog.query.filter_by(author=author_name).all()

    if blogs:
        return jsonify({"blogs": [blog.to_dict() for blog in blogs]}), 200
    else:
        return jsonify({"error": "no blogs by this author."}), 404


#Update a single blog
@app.route("/blog/<int:id>", methods=["PUT"])
@token_required
def update_blog(current_user, id):    

    blog = Blog.query.get(id)
    data = request.get_json()

    if blog:

        if not current_user.name == blog.author:
            return jsonify({"error": "this is not your blog."}), 403

        blog.title = data.get("title", blog.title)
        blog.content = data.get("content", blog.content)
        blog.tag = data.get("tag", blog.tag)

        db.session.commit()
        return jsonify({"message": "blog post updated successfully", "blog": blog.to_dict()}), 200
    
    return jsonify({"error": "blog post not found"}), 404


#Delete a blog post
@app.route("/blog/<int:id>", methods=["DELETE"])
@token_required
def delete_blog(current_user, id):

    blog = Blog.query.get(id)

    if blog:

        if not current_user.name == blog.author:
            return jsonify({"error": "this is not your blog."}), 403
        
        db.session.delete(blog)
        db.session.commit()
        return jsonify({"message": "blog post deleted successfully"}), 200
    
    return jsonify({"error": "blog post not found."}), 404



if __name__ == "__main__":
    app.run(debug=True)