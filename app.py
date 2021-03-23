from flask import Flask, render_template, request, redirect, flash, Response#, url_for
from flask_bootstrap import Bootstrap
import boto3
import os
from filters import datetimeformat, file_type
from werkzeug.utils import secure_filename

from PIL import Image, ImageOps, ImageFilter

app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type


UPLOAD_FOLDER = '/home/ubuntu/flaskapp/output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

"""
    home page
"""
@app.route("/")
def home_func():
    return render_template("home.html")

"""
    calls main page of web application
"""
@app.route('/files')
def files():
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket("publicimagprocessor")
    summaries = my_bucket.objects.all()
    return render_template('files.html', my_bucket=my_bucket, files=summaries)

"""
    handles bucket image delete 
"""
@app.route('/delete', methods=['POST'])
def delete():
    s3_resource = boto3.resource('s3')

    key = request.form['key']
    my_bucket = s3_resource.Bucket("publicimagprocessor")
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect("http://34.196.99.28:8080/files")

"""
    handles image downloading  
"""
@app.route('/download', methods=['POST'])
def download():
    s3_resource = boto3.resource('s3')
    
    key = request.form['key']
    my_bucket = s3_resource.Bucket("publicimagprocessor")
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

"""
    processes image to be uploaded to bucket
"""
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    try:
        file = request.files['file']    
        img_name = imagePro(request.form.get("select1"), file)    
        s3_resource = boto3.resource('s3')
        my_bucket = s3_resource.Bucket("publicimagprocessor")
        my_bucket.upload_file(img_name, file.filename)
        flash('File uploaded successfully')
    except:
        return redirect("http://34.196.99.28:8080/files")
    return redirect("http://34.196.99.28:8080/files")

"""
    handles the processing of uploaded image and application of filter
"""
def imagePro(preset, file):
    filename = secure_filename(file.filename)
    inputFile = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(inputFile) 
    
    f=filename.split('.')
    outputfilename = f[0] + '-out.png'
    outputfile = '/home/ubuntu/flaskapp/output/' + outputfilename
    
    im = Image.open(inputFile)
    if preset == 'gray':
        im = ImageOps.grayscale(im)
    if preset == 'edge':
        im = ImageOps.grayscale(im)
        im = im.filter(ImageFilter.FIND_EDGES)     
    if preset == 'blur':
        im = im.filter(ImageFilter.BLUR)
    im.save(outputfile)
    return outputfile

if __name__ == "__main__":
    app.run()