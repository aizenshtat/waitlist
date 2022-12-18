from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

wait_list = []

@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    if request.form["submit_button"] == "Add to Wait List":
      name = request.form["name"]
      timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      wait_list.append({"name": name, "timestamp": timestamp, "rank": len(wait_list) + 1})
    elif request.form["submit_button"] == "Next in Wait List":
      next_item = wait_list[0]
      wait_list.pop(0)
      for i in range(len(wait_list)):
        wait_list[i]["rank"] -= 1
    elif request.form["submit_button"] == "Move Up":
      index = int(request.form["index"])
      if index > 0:
        wait_list[index], wait_list[index - 1] = wait_list[index - 1], wait_list[index]
        wait_list[index]["rank"], wait_list[index - 1]["rank"] = wait_list[index - 1]["rank"], wait_list[index]["rank"]
    elif request.form["submit_button"] == "Move Down":
      index = int(request.form["index"])
      if index < len(wait_list) - 1:
        wait_list[index], wait_list[index + 1] = wait_list[index + 1], wait_list[index]
        wait_list[index]["rank"], wait_list[index + 1]["rank"] = wait_list[index + 1]["rank"], wait_list[index]["rank"]
    elif request.form["submit_button"] == "Edit":
      index = int(request.form["index"])
      name = request.form["name"]
      wait_list[index]["name"] = name
    elif request.form["submit_button"] == "Delete":
      index = int(request.form["index"])
      wait_list.pop(index)
      for i in range(index, len(wait_list)):
        wait_list[i]["rank"] -= 1
  return render_template("index.html", wait_list=wait_list)

if __name__ == "__main__":
  app.run()
