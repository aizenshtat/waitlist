from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

# Connect to the database file
conn = sqlite3.connect("wait_lists.db")

# Create the "wait_lists" table
conn.execute("CREATE TABLE wait_lists (name text PRIMARY KEY, timestamp text)")

# Create the "wait_list_items" table
conn.execute("CREATE TABLE wait_list_items (wait_list_name text, name text, timestamp text, rank integer, PRIMARY KEY (wait_list_name, name))")

# Commit the changes to the database
conn.commit()

# Close the connection
conn.close()

app = Flask(__name__)

wait_lists = {}

@app.route("/")
def index():
    return redirect(url_for("manage_wait_lists"))

@app.route("/manage", methods=["GET", "POST"])
def manage_wait_lists():
    if request.method == "POST":
        if request.form["submit_button"] == "Create Wait List":
            name = request.form["name"]
            if name not in wait_lists:
                wait_lists[name] = []
        elif request.form["submit_button"] == "Edit":
            old_name = request.form["name"]
            new_name = request.form["new_name"]
            if new_name not in wait_lists:
                wait_lists[new_name] = wait_lists[old_name]
                del wait_lists[old_name]
        elif request.form["submit_button"] == "Delete":
            name = request.form["name"]
            del wait_lists[name]
    return render_template("manage.html", wait_lists=wait_lists)

@app.route("/waitlist/<name>", methods=["GET", "POST"])
def wait_list(name):
    if request.method == "POST":
        if request.form["submit_button"] == "Add to Wait List":
            item_name = request.form["name"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            wait_lists[name].append({"name": item_name, "timestamp": timestamp, "rank": len(wait_lists[name]) + 1})
        elif request.form["submit_button"] == "Next in Wait List":
            next_item = wait_lists[name][0]
            wait_lists[name].pop(0)
            for i in range(len(wait_lists[name])):
                wait_lists[name][i]["rank"] -= 1
        elif request.form["submit_button"] == "Move Up":
            index = int(request.form["index"])
            if index > 0:
                wait_lists[name][index], wait_lists[name][index - 1] = wait_lists[name][index - 1], wait_lists[name][index]
                wait_lists[name][index]["rank"], wait_lists[name][index - 1]["rank"] = wait_lists[name][index - 1]["rank"], wait_lists[name][index]["rank"]
        elif request.form["submit_button"] == "Move Down":
            index = int(request.form["index"])
            if index < len(wait_lists[name]) - 1:
                wait_lists[name][index], wait_lists[name][index + 1] = wait_lists[name][index + 1], wait_lists[name][index]
                wait_lists[name][index]["rank"], wait_lists[name][index + 1]["rank"] = wait_lists[name][index + 1]["rank"], wait_lists[name][index]["rank"]
        elif request.form["submit_button"] == "Edit":
            index = int(request.form["index"])
            item_name = request.form["name"]
            wait_lists[name][index]["name"] = item_name
        elif request.form["submit_button"] == "Delete":
            index = int(request.form["index"])
            wait_lists[name].pop(index)
            for i in range(index, len(wait_lists[name])):
                wait_lists[name][i]["rank"] -= 1
    return render_template("wait_list.html", name=name, wait_list=wait_lists[name])

if __name__ == "__main__":
    app.run()

