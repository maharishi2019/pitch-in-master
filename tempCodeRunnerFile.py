
                items = i["checklist"]
            
    return render_template("visiting_page.html", items=items)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))



