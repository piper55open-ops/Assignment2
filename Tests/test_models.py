import os
import pytest
import sqlite3
from models.database import Database
from models.blog_model import BlogModel
from models.event_model import EventModel
from models.promotion_model import PromotionModel
from models.property_model import PropertyModel
from models.provider_model import ProviderModel
from models.journey_models import JourneyModel


# ---------------- FIXTURE: Temporary test DB ----------------
@pytest.fixture(scope="module", autouse=True)
def setup_test_db(tmp_path_factory):
    """Use a temporary database for testing."""
    test_db_path = tmp_path_factory.mktemp("data") / "test.db"


    Database._instance = None
    db = Database()
    db.connection = sqlite3.connect(test_db_path)
    db.connection.row_factory = sqlite3.Row

    yield db  

    db.close_connection()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


# ---------------- BLOG MODEL TESTS ----------------
def test_blog_crud_operations(setup_test_db):
    blog = BlogModel()
    blog.create_table()

    # Add blog
    blog.add_blog("Trip to Auckland", "John", "2025-10-25", "Short desc", "Full desc", "image.jpg")
    assert blog.count_blogs() == 1

    # Get blog
    all_blogs = blog.get_all_blogs()
    assert len(all_blogs) == 1
    blog_id = all_blogs[0]["id"]

    # Update blog
    blog.update_blog(blog_id, "Trip to Wellington", "John", "2025-10-26", "Updated short", "Updated full", "new.jpg")
    updated = blog.get_blog_by_id(blog_id)
    assert updated["title"] == "Trip to Wellington"

    # Delete blog
    blog.delete_blog(blog_id)
    assert blog.count_blogs() == 0


# ---------------- EVENT MODEL TESTS ----------------
def test_event_crud_operations(setup_test_db):
    event = EventModel()
    event.create_table()

    event.add_event("Music Fest", "Live music", "2025-12-01", "img.jpg", "Auckland")
    assert event.count_events() == 1

    all_events = event.get_all_events()
    event_id = all_events[0]["id"]

    event.update_event(event_id, "Food Fest", "Food tasting", "2025-12-02", "img2.jpg", "Wellington")
    updated = event.get_event_by_id(event_id)
    assert updated["title"] == "Food Fest"

    event.delete_event(event_id)
    assert event.count_events() == 0


# ---------------- PROMOTION MODEL TESTS ----------------
def test_promotion_crud_operations(setup_test_db):
    promo = PromotionModel()
    promo.create_table()

    promo.add_promotion(1, "Summer Sale", "50% off", "promo.jpg", "2025-01-01", "2025-02-01")
    all_promos = promo.get_promotions_by_provider(1)
    assert len(all_promos) == 1

    promo_id = all_promos[0]["id"]
    promo.update_promotion(promo_id, "Winter Sale", "30% off", "promo2.jpg", "2025-03-01", "2025-04-01")
    updated = promo.get_promotion_by_id(promo_id)
    assert updated["title"] == "Winter Sale"

    promo.delete_promotion(promo_id)
    assert promo.get_promotions_by_provider(1) == []


# ---------------- PROPERTY MODEL TESTS ----------------
def test_property_crud_operations(setup_test_db):
    prop = PropertyModel()
    prop.create_table()

    prop.add_property(1, "Sea View", "Nice house", "House", "Auckland", 100.0, 2, 1, "WiFi, Pool", "house.jpg")
    all_props = prop.get_properties_by_provider(1)
    assert len(all_props) == 1

    prop_id = all_props[0]["id"]
    prop.update_property(prop_id, "Lake View", "Villa", "Rotorua", 200.0, 4, 1, "WiFi, Jacuzzi", "Active")
    updated = prop.get_property_by_id(prop_id)
    assert updated["name"] == "Lake View"

    prop.delete_property(prop_id)
    assert prop.get_properties_by_provider(1) == []


# ---------------- PROVIDER MODEL TESTS ----------------
def test_provider_add_and_fetch(setup_test_db):
    provider = ProviderModel()
    provider.create_table()

    result = provider.add_provider(1, "Sky Hotel", "123 Street", "www.sky.com", "hotel.jpg")
    assert result["success"] is True

    duplicate = provider.add_provider(1, "Sky Hotel", "123 Street", "www.sky.com", "hotel.jpg")
    assert duplicate["success"] is False

# ---------------- JOURNEY MODEL TESTS ----------------

def test_journey_crud_operations(setup_test_db):
    journey = JourneyModel()
    journey.create_table()

    journey.add_journey(
        user_id=1,
        title="South Island Road Trip",
        description="An amazing journey through Queenstown and Milford Sound.",
        location="Queenstown",
        lat=-45.0311,
        lng=168.6626,
        images=["img1.jpg", "img2.jpg"]
    )
    
    all_journeys = journey.get_journeys_by_user(1)
    assert len(all_journeys) == 1
    assert all_journeys[0]["title"] == "South Island Road Trip"
    journey_id = all_journeys[0]["id"]


    single_journey = journey.get_journey_by_id(journey_id)
    assert single_journey is not None
    assert isinstance(single_journey["images"], list)

    journey.delete_journey(journey_id)
    assert journey.count_journeys() == 0
