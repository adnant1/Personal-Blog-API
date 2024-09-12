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