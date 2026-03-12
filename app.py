from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import yt_dlp
import os
import uuid

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def is_tiktok_url(url: str) -> bool:
    return "tiktok.com" in url or "vm.tiktok.com" in url


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("video_url", "").strip()

        if not video_url:
            flash("يرجى إدخال رابط الفيديو.")
            return redirect(url_for("index"))

        if not is_tiktok_url(video_url):
            flash("هذا الرابط لا يبدو كرابط TikTok صحيح.")
            return redirect(url_for("index"))

        file_id = str(uuid.uuid4())
        output_template = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s")

        ydl_opts = {
            "outtmpl": output_template,
            "format": "mp4/best",
            "noplaylist": True,
            "quiet": True,
            "merge_output_format": "mp4",
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                downloaded_path = ydl.prepare_filename(info)

                # لو تم الدمج النهائي إلى mp4
                base_without_ext = os.path.splitext(downloaded_path)[0]
                mp4_path = base_without_ext + ".mp4"
                final_path = mp4_path if os.path.exists(mp4_path) else downloaded_path

                if not os.path.exists(final_path):
                    flash("تمت محاولة التنزيل لكن الملف غير موجود.")
                    return redirect(url_for("index"))

                return send_file(
                    final_path,
                    as_attachment=True,
                    download_name=os.path.basename(final_path)
                )

        except Exception as e:
            flash(f"حدث خطأ أثناء التنزيل: {str(e)}")
            return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)