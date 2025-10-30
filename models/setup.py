import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database


from models.feedback_model import FeedbackModel

feedback = FeedbackModel()

# Sample Traveller feedbacks
feedback.add_feedback(1, "traveller", "Alice Johnson", "alice@example.com", "Loved the Auckland trip itinerary!")
feedback.add_feedback(2, "traveller", "Mark Lee", "mark@example.com", "The booking feature was a bit slow.")

# Sample Provider feedbacks
feedback.add_feedback(1, "provider", "OceanView Tours", "info@oceanview.com", "We’d like better dashboard analytics.")
feedback.add_feedback(2, "provider", "Kiwi Rides", "support@kiwirides.nz", "Unable to view traveller feedback replies.")

print("✅ Sample feedback data inserted successfully!")
