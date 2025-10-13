from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models.provider_model import ProviderModel
from models.property_model import PropertyModel
from models.promotion_model import PromotionModel


# Initialize Blueprint
provider_bp = Blueprint("provider", __name__, template_folder="../templates/provider")

# Initialize model
provider_model = ProviderModel()


@provider_bp.route("/dashboard")
def provider_dashboard():
    """Provider main dashboard"""
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)
    if not provider:
        flash("Provider profile not found.", "warning")
        return redirect(url_for("login"))

    provider_id = provider["id"]
    total_properties = provider_model.count_properties(user_id)
    total_promotions = provider_model.count_promotions(user_id)
    profile_completion = provider_model.calculate_profile_completion(provider)

    return render_template(
        "provider/provider_dashboard.html",
        provider=provider,
        total_properties=total_properties,
        total_promotions=total_promotions,
        profile_completion=profile_completion
    )


@provider_bp.route("/add_property")
def add_property():
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    return render_template("provider/add_property.html")


@provider_bp.route("/add_promotion")
def add_promotion():
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    return render_template("provider/add_promotion.html")


@provider_bp.route("/properties")
def properties():
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    # later you can add real data here
    return render_template("provider/properties.html")


@provider_bp.route("/promotions")
def promotions():
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    # later you can add real data here
    return render_template("provider/promotions.html")
