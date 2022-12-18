from flask import Flask, render_template, request

app = Flask(__name__)

wait_list = []

@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    if request.form["submit_button"] == "Add to Wait List":
      name = request.form["name"]
      wait_list.append(name)
    elif request.form["submit_button"] == "Next in Wait List":
      next_item = wait_list[0]
      wait_list.pop(0)
  return render_template("index.html", wait_list=wait_list)

if __name__ == "__main__":
  app.run()
