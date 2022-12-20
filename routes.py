from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, make_response, send_file, send_from_directory
import qrcode
from PIL import Image
from .models import db, WaitList, WaitListEntry

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@main_bp.route("/")
def index():
    return redirect(url_for("manage_wait_lists"))

@main_bp.route("/manage", methods=["GET", "POST"])
def manage_wait_lists():
    if request.method == "POST":
        if request.form["submit_button"] == "Create Wait List":
            name = request.form["name"]
            wait_list = WaitList(name=name)
            db.session.add(wait_list)
            db.session.commit()
        elif request.form["submit_button"] == "Edit":
            wait_list_id = request.form["wait_list_id"]
            new_name = request.form["new_name"]
            wait_list = db.session.query(WaitList).filter_by(id=wait_list_id).first()
            wait_list.name = new_name
            db.session.commit()
        elif request.form["submit_button"] == "Delete":
            wait_list_id = request.form["wait_list_id"]
            wait_list = db.session.query(WaitList).filter_by(id=wait_list_id).first()
            db.session.delete(wait_list)
            db.session.commit()
    wait_lists = db.session.query(WaitList).all()
    return render_template("manage.html", wait_lists=wait_lists)

@main_bp.route("/waitlist/<wait_list_id>", methods=["GET", "POST"])
def wait_list(wait_list_id):
    wait_list = db.session.query(WaitList).filter_by(id=wait_list_id).first()
    if request.method == "POST":
        if request.form["submit_button"] == "Add to Wait List":
            item_name = request.form["name"]
            timestamp = datetime.now()
            wait_list_entry = WaitListEntry(wait_list_id=wait_list_id, name=item_name, timestamp=timestamp, rank=len(wait_list.entries) + 1)
            db.session.add(wait_list_entry)
            db.session.commit()
        elif request.form["submit_button"] == "Next in Wait List":
            next_item = db.session.query(WaitListEntry).filter_by(wait_list_id=wait_list_id).order_by(WaitListEntry.rank).first()
            db.session.delete(next_item)
            db.session.commit()
            for i in range(len(wait_list.entries)):
                wait_list.entries[i].rank -= 1
                db.session.commit()
        elif request.form["submit_button"] == "Move Up":
            entry_id = request.form["entry_id"]
            entry = db.session.query(WaitListEntry).filter_by(id=entry_id).first()
            if entry.rank > 1:
               # Get the entry that is currently ranked one position above the current entry
                prev_entry = db.session.query(WaitListEntry).filter_by(wait_list_id=wait_list_id, rank=entry.rank-1).first()
                # Swap the ranks of the two entries
                entry.rank, prev_entry.rank = prev_entry.rank, entry.rank
                db.session.commit()
        elif request.form["submit_button"] == "Move Down":
            entry_id = request.form["entry_id"]
            entry = db.session.query(WaitListEntry).filter_by(id=entry_id).first()
            if entry.rank < len(wait_list.entries):
               # Get the entry that is currently ranked one position below the current entry
                next_entry = db.session.query(WaitListEntry).filter_by(wait_list_id=wait_list_id, rank=entry.rank+1).first()
                # Swap the ranks of the two entries
                entry.rank, next_entry.rank = next_entry.rank, entry.rank
                db.session.commit()
        elif request.form["submit_button"] == "Edit":
            entry_id = request.form["entry_id"]
            entry = db.session.query(WaitListEntry).filter_by(id=entry_id).first()
            entry.name = request.form["name"]
            db.session.commit()
        elif request.form["submit_button"] == "Delete":
            entry_id = request.form["entry_id"]
            entry = db.session.query(WaitListEntry).filter_by(id=entry_id).first()
            db.session.delete(entry)
            db.session.commit()
            for i in range(entry.rank - 1, len(wait_list.entries)):
                wait_list.entries[i].rank -= 1
                db.session.commit()
    wait_list_entries = db.session.query(WaitListEntry).filter_by(wait_list_id=wait_list_id).order_by(WaitListEntry.rank).all()
    return render_template("wait_list.html", wait_list_id=wait_list_id, name=wait_list.name, wait_list=wait_list_entries)

@main_bp.route("/entry/<entry_id>")
def entry_detail(entry_id):
    entry = db.session.query(WaitListEntry).filter_by(id=entry_id).first()
    return render_template("entry_detail.html", entry=entry)

@main_bp.route("/add_to_waitlist/<wait_list_id>")
def add_to_waitlist(wait_list_id):
    wait_list = db.session.query(WaitList).filter_by(id=wait_list_id).first()
    timestamp = datetime.now()
    wait_list_entry = WaitListEntry(wait_list_id=wait_list_id, name="", timestamp=timestamp, rank=len(wait_list.entries) + 1)
    db.session.add(wait_list_entry)
    db.session.commit()
    return redirect(url_for("entry_detail", entry_id=wait_list_entry.id))

@main_bp.route("/qr/<wait_list_id>")
def qr(wait_list_id):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(cs_host + "add_to_waitlist/" + wait_list_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to file
    img.save(f"static/qr_codes/{wait_list_id}.png")
    
    return send_from_directory(
        "static/qr_codes", f"{wait_list_id}.png", mimetype="image/png"
    )