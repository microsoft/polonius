import os

import mongoengine as engine
from azure.monitor.opentelemetry import configure_azure_monitor
from flask import Flask
from flask_bootstrap import Bootstrap4


def create_app(test_config=None):
    # create and configure the app
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        configure_azure_monitor()

    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    bootstrap = Bootstrap4(app) # noqa: F841
    
    # Load configuration for prod vs. dev
    is_prod_env = "RUNNING_IN_PRODUCTION" in os.environ
    
    if not is_prod_env:
        app.config.from_object("flaskapp.config.development")
    else:
        app.config.from_object("flaskapp.config.production")

    # Configure the database
    if test_config is not None:
        app.config.update(test_config)

    db = engine.connect(host=app.config.get("DATABASE_URI"))  # noqa: F841

    from . import pages

    app.register_blueprint(pages.bp)

    # @app.cli.command("seed")
    # @click.option("--drop", is_flag=True, default=False)
    # @click.option("--filename", default="seed_data.json")
    # def seed_data(filename, drop):
    #     from . import seeder

    #     seeder.seed_data(filename, drop=drop)
    #     click.echo("Database seeded!")

    return app
