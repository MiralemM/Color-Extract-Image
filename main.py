from flask import Flask, render_template, send_from_directory, url_for
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from colorthief import ColorThief
import matplotlib.pyplot as plt


app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"
app.config["UPLOADED_PHOTOS_DEST"] = "uploads"

photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)


def palette_table(file_url):
    ct = ColorThief(file_url)
    palette = ct.get_palette(color_count=11)
    plt.imshow([[palette[i] for i in range(10)]])
    rgb_colors = []
    hex_colors = []
    for color in palette:
        rgb_colors.append(color)
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        hex_colors.append(hex_color)

    return rgb_colors, hex_colors


class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, "Only images are allowed."),
            FileRequired("File field should not be empty.")
        ]
    )
    submit = SubmitField("Upload")


@app.route("/uploads/<filename>")
def get_file(filename):
    return send_from_directory(app.config["UPLOADED_PHOTOS_DEST"], filename)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    form = UploadForm()
    rgbs = [(35, 31, 33), (178, 146, 154), (132, 87, 94), (151, 149, 161), (94, 55, 58), (95, 89, 106), (181, 38, 48),
            (59, 61, 75), (95, 95, 86), (147, 150, 141)]
    hexs = ['#231f21', '#b2929a', '#84575e', '#9795a1', '#5e373a', '#5f596a', '#b52630', '#3b3d4b', '#5f5f56',
            '#93968d']
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for("get_file", filename=filename)
        url_file = f"uploads/{filename}"
        palette_table(file_url=url_file)
        upload_rgbs = palette_table(file_url=url_file)[0]
        upload_hexs = palette_table(file_url=url_file)[1]
        return render_template("upload.html", form=form, file_url=file_url, palette_table=palette_table,
                               upload_hexs=upload_hexs, upload_rgbs=upload_rgbs)
    else:
        file_url = None
    return render_template("upload.html", form=form, file_url=file_url, palette_table=palette_table, rgbs=rgbs,
                           hexs=hexs)


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
