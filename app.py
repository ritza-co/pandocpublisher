import os
import random
import string
import subprocess

from flask import Flask
from flask import request
from flask import redirect
from flask import send_from_directory

from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"md", "markdown"}
UPLOAD_FOLDER = "/tmp/uploads"
LUA_FILTER = "files/fix-pre-code.lua"
TEMPLATE_PRE = "files/template_pre.html"
TEMPLATE_POST = "files/template_post.html"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_title_and_metadescription(mdfile):
    title = ""
    metadescription = ""
    try:
        with open(mdfile) as f:
            head = [next(f) for x in range(10)]
            head = [x for x in head if len(x) > 2]
            title = head[0].replace("#", "").strip()
            metadescription = " ".join(head[1:3])[:150]
    except Exception as e:
        print("error in get_title_and_metadescription")
        print(e)
    return title, metadescription


def call_pandoc(mdfile, htmlfile):
    try:
        output = subprocess.check_output(
            [
                "pandoc",
                mdfile,
                "--no-highlight",
                "-f",
                "markdown-auto_identifiers-citations",
                "-t",
                "html",
                "--lua-filter",
                LUA_FILTER,
                "-o",
                htmlfile,
            ]
        )
    except subprocess.CalledProcessError as e:
        print("error in call_pandoc")
        print(e.output)


def combine_html(title, metadescription, htmlfile, combinedfile):
    with open(TEMPLATE_PRE, encoding="utf-8") as f:
        pre = f.read()
        pre = pre.replace("{title}", title)
        pre = pre.replace("{metadescription}", metadescription)

    with open(TEMPLATE_POST, encoding="utf-8") as f:
        post = f.read()

    with open(htmlfile, encoding="utf-8") as f:
        content = f.read()
    complete = pre + content + post
    with open(combinedfile, "w", encoding="utf-8") as f:
        f.write(complete)


@app.route("/publishtutorial", methods=["GET", "POST"])
def publish_tutorial():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            return redirect(request.url)

        fle = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if fle.filename == "":
            return redirect(request.url)
        if not fle or not allowed_file(fle.filename):
            return redirect(request.url)

        filename = secure_filename(fle.filename)
        save_name = "".join(random.sample(string.ascii_letters, 6))
        
        out_noex = os.path.join(app.config["UPLOAD_FOLDER"], save_name)
        out_md = out_noex + ".md"
        out_tmp_html = out_noex + "-tmp.html"
        out_html_final = save_name + ".html"
        fle.save(out_md)
        print("getting title and metadescription")
        title, metadescription = get_title_and_metadescription(out_md)
        print("calling pandoc")
        call_pandoc(out_md, out_tmp_html)
        print("combining files")
        combine_html(title, metadescription, out_tmp_html, os.path.join(UPLOAD_FOLDER, out_html_final))
        return send_from_directory(UPLOAD_FOLDER, out_html_final, as_attachment=True)

    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <p>Upload a markdown file and get a beautiful HTML file with code highlighting in return</p>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """


if __name__ == "__main__":
    app.run()
