# -*- coding: utf-8 -*-

import os
from io import BytesIO
from os.path import join
from flask import Flask, request, redirect, url_for, render_template, send_file
from werkzeug import secure_filename

from PIL import Image
from StringIO import StringIO

import zipfile
import time

# 要注意從手機上傳的圖片，可能沒有 extension
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

# 用來限定最大檔案的大小，底下設為 5 Mb
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        platform = request.form['platform']
        print "received filename:", file.filename
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            im = Image.open(StringIO(file.read()))
            
            # 判斷是要 ios 還是 android icons
            size = []
            if platform=='ios':
                sizes = [(180, 180), (120, 120), (60, 60), (152, 152), (76, 76)]
            elif platform=='android':
                sizes = [(36, 36), (48, 48), (72, 72), (96, 96)]
        
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zf:
                for size in sizes:    
                    ic = im.copy()
                    ic.thumbnail(size, Image.ANTIALIAS)
                    output = StringIO()
                    ic.save(output, 'PNG')
                    iconname=str(size[0]) + "x" + str(size[1]) + ".png"
                    data = zipfile.ZipInfo(iconname)
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    zf.writestr(iconname, output.getvalue())
                    output.close()
            memory_file.seek(0)
            return send_file(memory_file, attachment_filename=platform+'-icons.zip', as_attachment=True)
    return render_template("iconmaker.html")

if __name__=='__main__':
    app.run(host='0.0.0.0')