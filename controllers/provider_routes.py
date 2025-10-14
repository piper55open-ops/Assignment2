from flask import Blueprint, render_template, redirect, url_for, session, flash, request,jsonify
import os
from werkzeug.utils import secure_filename
from models.provider_model import ProviderModel
from models.property_model import PropertyModel
from models.promotion_model import PromotionModel


# Initialize Blueprint
provider_bp = Blueprint("provider", __name__, template_folder="../templates/provider")

# Initialize model
provider_model = ProviderModel()
property_model = PropertyModel()
promotion_model = PromotionModel()


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

#------------------------------PROPERTY ----------------------------------------------
@provider_bp.route("/properties")
def properties():
    if session.get("role") != "provider":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) 
    properties = property_model.get_properties_by_provider(user_id)
    return render_template(
        "provider/properties.html",
        properties=properties,
        provider=provider  
    )

@provider_bp.route("/properties/add", methods=["POST"])
def add_property():
    if "provider_id" not in session:
        return jsonify({"message": "Unauthorized"}), 403

    provider_id = session["provider_id"]
    name = request.form.get("name")
    description = request.form.get("description")
    property_type = request.form.get("property_type")
    location = request.form.get("location")
    price_per_day = request.form.get("price_per_day")
    max_guests = request.form.get("max_guests")
    food_available = request.form.get("food_available")
    facilities = request.form.get("facilities")

    # Handle image upload
    image = request.files.get("image")
    filename = None
    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join("static", "images", filename))

    property_model.add_property(
        provider_id, name, description, property_type, location,
        price_per_day, max_guests, food_available, facilities, filename
    )

    return jsonify({"message": "Property added successfully!"})

@provider_bp.route("/properties/update", methods=["POST"])
def update_property():
    if "provider_id" not in session:
        return jsonify({"message": "Unauthorized"}), 403

    property_id = request.form.get("id")
    name = request.form.get("name")
    property_type = request.form.get("property_type")
    location = request.form.get("location")
    price_per_day = request.form.get("price_per_day")
    max_guests = request.form.get("max_guests")
    food_available = request.form.get("food_available")
    facilities = request.form.get("facilities")
    status = request.form.get("status")

    property_model.update_property(
        property_id, name, property_type, location,
        price_per_day, max_guests, food_available,
        facilities, status
    )

    return jsonify({"message": "Property updated successfully!"})

@provider_bp.route("/properties/delete/<int:property_id>", methods=["POST"])
def delete_property(property_id):
    if "provider_id" not in session:
        return jsonify({"message": "Unauthorized"}), 403

    property_model.delete_property(property_id)
    return jsonify({"message": "Property deleted successfully!"})


#------------------------------PROMOTION --------------------------------------------

@provider_bp.route('/promotions')
def promotions():
    if session.get("role") != "provider":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) 
    promotions = promotion_model.get_promotions_by_provider(user_id)
    return render_template('provider/promotions.html', promotions=promotions,provider=provider )

@provider_bp.route('/promotions/add', methods=['POST'])
def add_promotion():
    if "provider_id" not in session:
        return jsonify({"message": "Unauthorized"}), 403
    provider_id = session["provider_id"]
    title = request.form.get('title')
    description = request.form.get('description')
    image_file = request.files.get('image')
    image_name = None
    if image_file:
        image_name = image_file.filename
        image_file.save(f"static/images/{image_name}")

    promotion_model.add_promotion(provider_id, title, description, image_name)
    return jsonify({'message': 'Promotion added successfully!'})

@provider_bp.route('/promotions/update', methods=['POST'])
def update_promotion():
    promo_id = request.form.get('id')
    title = request.form.get('title')
    description = request.form.get('description')
    image_file = request.files.get('image')
    image_name = None
    if image_file and image_file.filename != "":
        image_name = image_file.filename
        image_file.save(f"static/images/{image_name}")

    promotion_model.update_promotion(promo_id, title, description, image_name)
    return jsonify({'message': 'Promotion updated successfully!'})

@provider_bp.route('/promotions/delete/<int:promo_id>', methods=['POST'])
def delete_promotion(promo_id):
    promotion_model.delete_promotion(promo_id)
    return jsonify({'message': 'Promotion deleted successfully!'})

#--------------------------------PROFILE ---------------------------------
@provider_bp.route("/profile", methods=["GET"])
def profile():
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) # fetch from session or DB
    return render_template("provider/provider_profile.html", provider=provider)

@provider_bp.route("/profile/update", methods=["POST"])
def update_profile():
    # handle hotel_address + image update
    # save changes to DB
    return redirect(url_for("provider.profile"))

@provider_bp.route("/profile/theme", methods=["POST"])
def update_theme():
    # update provider.theme_color in DB
    return redirect(url_for("provider.profile"))


@provider_bp.route("/profile/language", methods=["POST"])
def update_language():
    # update provider.language in DB
    return redirect(url_for("provider.profile"))


