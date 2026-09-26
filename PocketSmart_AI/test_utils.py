from gemini_utils import get_home_recommendations

result = get_home_recommendations(
    budget=15000,
    room_type="Living Room",
    items={"Wall Shelves": 2, "Floor Lamp": 1},
)
print("Home Planner Test JSON:")
print(result)