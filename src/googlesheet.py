import gspread
import json

auth_file = "auth.json"
gc = gspread.service_account(filename=auth_file)
sheet_url = "https://docs.google.com/spreadsheets/d/10NkfXVm8WYel4GTTTIaFyPxmVy52ODjda0WNpl70dF8/edit?gid=0#gid=0"

sheet_file = gc.open_by_url(sheet_url)
# sheet = sheet_file.sheet1

# with open("data/zara_data_extended.json", "r") as f:
#     products = json.load(f)

# # Prepare data for the sheet: header row + product rows
# sheet_data = [
#     ["ID", "Description", "Price", "ImageURL", "ColorHEX", "ProductURL", "ColorName", "DetailDescription", "Type", "PersonalColorType"]
# ]  # Header row
# for product in products:
#     sheet_data.append(
#         [
#             product.get("id"),
#             product.get("description", ""),
#             product.get("price", ""),
#             product.get("imageUrl", ""),
#             product.get("colorHex", ""),
#             product.get("productUrl", ""),
#             product.get("colorName", ""),
#             product.get("detailDescription", ""),
#             product.get("type", ""),
#             product.get("personalColorType", ""),
#         ]
#     )

# # Update the sheet starting from A1
# sheet.update("A1", sheet_data)

sheet = sheet_file.worksheet("Outfits")
with open("data/outfit.json", "r") as f:
    outfits = json.load(f)

sheet_data = [
    ["ID", "Season", "OutfitID", "Occasion", "TemperatureC", "Items"]
]  # Header row

# "season": "autumn_soft",
# "outfit_id": "autumn_soft_03",
# "occasion": "casual coffee date",
# "temperatureC": 15,
# "items": []

counter = 0
for outfit in outfits:
    sheet_data.append(
        [
            counter,
            outfit.get("season"),
            outfit.get("outfit_id"),
            outfit.get("occasion"),
            outfit.get("temperatureC"),
            json.dumps(outfit.get("items")),
        ]
    )
    counter += 1
sheet.update("A1", sheet_data)