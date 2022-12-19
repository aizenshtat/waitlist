from flask import Flask, render_template, request, redirect, url_for, make_response, send_file, send_from_directory
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import qrcode
from PIL import Image

cs_host = 'https://aizenshtat-bug-free-potato-q99qqwx59g7395jx-5000.preview.app.github.dev/'
app = Flask(__name__)

# Set up database
engine = create_engine('sqlite:///wait_lists.db')
Base = declarative_base()

class WaitList(Base):
    __tablename__ = 'wait_lists'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    entries = relationship("WaitListEntry", cascade="all, delete-orphan", back_populates="wait_list", primaryjoin="WaitList.id==WaitListEntry.wait_list_id")

class WaitListEntry(Base):
    __tablename__ = 'wait_list_entries'
    id = Column(Integer, primary_key=True)
    wait_list_id = Column(Integer, ForeignKey('wait_lists.id'))
    name = Column(String)
    timestamp = Column(DateTime)
    rank = Column(Integer)
    wait_list = relationship("WaitList", back_populates="entries")

Base.metadata.create_all(engine)

# Set up database session
Session = sessionmaker(bind=engine)
session = Session()

@app.route("/")
def index():
    return redirect(url_for("manage_wait_lists"))

@app.route("/manage", methods=["GET", "POST"])
def manage_wait_lists():
    if request.method == "POST":
        if request.form["submit_button"] == "Create Wait List":
            name = request.form["name"]
            wait_list = WaitList(name=name)
            session.add(wait_list)
            session.commit()
        elif request.form["submit_button"] == "Edit":
            wait_list_id = request.form["wait_list_id"]
            new_name = request.form["new_name"]
            wait_list = session.query(WaitList).filter_by(id=wait_list_id).first()
            wait_list.name = new_name
            session.commit()
        elif request.form["submit_button"] == "Delete":
            wait_list_id = request.form["wait_list_id"]
            wait_list = session.query(WaitList).filter_by(id=wait_list_id).first()
            session.delete(wait_list)
            session.commit()
    wait_lists = session.query(WaitList).all()
    return render_template("manage.html", wait_lists=wait_lists)

@app.route("/waitlist/<wait_list_id>", methods=["GET", "POST"])
def wait_list(wait_list_id):
    wait_list = session.query(WaitList).filter_by(id=wait_list_id).first()
    if request.method == "POST":
        if request.form["submit_button"] == "Add to Wait List":
            item_name = request.form["name"]
            timestamp = datetime.now()
            wait_list_entry = WaitListEntry(wait_list_id=wait_list_id, name=item_name, timestamp=timestamp, rank=len(wait_list.entries) + 1)
            session.add(wait_list_entry)
            session.commit()
        elif request.form["submit_button"] == "Next in Wait List":
            next_item = session.query(WaitListEntry).filter_by(wait_list_id=wait_list_id).order_by(WaitListEntry.rank).first()
            session.delete(next_item)
            session.commit()
            for i in range(len(wait_list.entries)):
                wait_list.entries[i].rank -= 1
                session.commit()
        elif request.form["submit_button"] == "Move Up":
            entry_id = request.form["entry_id"]
            entry = session.query(WaitListEntry).filter_by(id=entry_id).first()
            if entry.rank > 1:
               # Get the entry that is currently ranked one position above the current entry
                prev_entry = session.query(WaitListEntry).filter_by(wait_list_id=wait_list_id, rank=entry.rank-1).first()
                # Swap the ranks of the two entries
                entry.rank, prev_entry.rank = prev_entry.rank, entry.rank
                session.commit()
        elif request.form["submit_button"] == "Move Down":
            entry_id = request.form["entry_id"]
            entry = session.query(WaitListEntry).filter_by(id=entry_id).first()
            if entry.rank < len(wait_list.entries):
               # Get the entry that is currently ranked one position below the current entry
                next_entry = session.query(WaitListEntry).filter_by(wait_list_id=wait_list_id, rank=entry.rank+1).first()
                # Swap the ranks of the two entries
                entry.rank, next_entry.rank = next_entry.rank, entry.rank
                session.commit()
        elif request.form["submit_button"] == "Edit":
            entry_id = request.form["entry_id"]
            entry = session.query(WaitListEntry).filter_by(id=entry_id).first()
            entry.name = request.form["name"]
            session.commit()
        elif request.form["submit_button"] == "Delete":
            entry_id = request.form["entry_id"]
            entry = session.query(WaitListEntry).filter_by(id=entry_id).first()
            session.delete(entry)
            session.commit()
            for i in range(entry.rank - 1, len(wait_list.entries)):
                wait_list.entries[i].rank -= 1
                session.commit()
    wait_list_entries = session.query(WaitListEntry).filter_by(wait_list_id=wait_list_id).order_by(WaitListEntry.rank).all()
    return render_template("wait_list.html", wait_list_id=wait_list_id, name=wait_list.name, wait_list=wait_list_entries)

@app.route("/entry/<entry_id>")
def entry_detail(entry_id):
    entry = session.query(WaitListEntry).filter_by(id=entry_id).first()
    return render_template("entry_detail.html", entry=entry)

@app.route("/add_to_waitlist/<wait_list_id>")
def add_to_waitlist(wait_list_id):
    wait_list = session.query(WaitList).filter_by(id=wait_list_id).first()
    timestamp = datetime.now()
    wait_list_entry = WaitListEntry(wait_list_id=wait_list_id, name="", timestamp=timestamp, rank=len(wait_list.entries) + 1)
    session.add(wait_list_entry)
    session.commit()
    return redirect(url_for("entry_detail", entry_id=wait_list_entry.id))

@app.route("/qr/<wait_list_id>")
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

if __name__ == "__main__":
    app.run()
