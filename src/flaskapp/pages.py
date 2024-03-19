from flask import Blueprint, redirect, render_template, request, url_for

from . import models

bp = Blueprint("pages", __name__)


@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/api/demo")
def hello_api():
    return {
        "message": "Hello, World!",
    }

@bp.get("/about")
def about():
    return render_template("about.html")


@bp.get("/destinations")
def destinations():
    all_destinations = models.Destination.objects.all()

    return render_template("destinations.html", destinations=all_destinations)


@bp.get("/destination/<pk>")
def destination_detail(pk):
    destination = models.Destination.objects.get(pk=pk)

    return render_template(
        "destination_detail.html",
        destination=destination,
        cruises=models.Cruise.objects(destinations__in=[destination]),
    )


@bp.get("/cruise/<pk>")
def cruise_detail(pk: int):
    cruise = models.Cruise.objects.get(pk=pk)

    return render_template(
        "cruise_detail.html",
        cruise=cruise,
        destinations=cruise.destinations,
    )


@bp.get("/info_request")
def info_request():
    all_cruises = models.Cruise.objects.all()

    return render_template("info_request_create.html", cruises=all_cruises, message=request.args.get("message"))


@bp.post("/info_request")
def create_info_request():
    name = request.form["name"]
    db_info_request = models.InfoRequest(
        name=name,
        email=request.form["email"],
        notes=request.form["notes"],
        cruise=request.form["cruise_id"],
    )
    db_info_request.save()
    success_message = f"Thank you, {name}! We will email you when we have more information!"
    return redirect(url_for("pages.info_request", message=success_message))
