"""
Google Sheets operations - for syncing data to/from Google Sheets.
"""
import gspread
import json

auth_file = "auth.json"
gc = gspread.service_account(filename=auth_file)
sheet_url = "https://docs.google.com/spreadsheets/d/10NkfXVm8WYel4GTTTIaFyPxmVy52ODjda0WNpl70dF8/edit?gid=0#gid=0"

sheet_file = gc.open_by_url(sheet_url)


def sync_outfits_to_sheet(outfits_json_path: str = "data/outfit.json", worksheet_name: str = "Outfits"):
    """
    Sync outfit data from JSON file to Google Sheets.
    
    Args:
        outfits_json_path: Path to the outfit JSON file
        worksheet_name: Name of the worksheet to update
    """
    sheet = sheet_file.worksheet(worksheet_name)
    
    with open(outfits_json_path, "r") as f:
        outfits = json.load(f)

    sheet_data = [
        ["ID", "Season", "OutfitID", "Occasion", "TemperatureC", "Items"]
    ]  # Header row

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


def sync_products_to_sheet(products_json_path: str = "data/zara_data_extended.json", worksheet_name: str = "Main"):
    """
    Sync product data from JSON file to Google Sheets.
    
    Args:
        products_json_path: Path to the products JSON file
        worksheet_name: Name of the worksheet to update
    """
    sheet = sheet_file.worksheet(worksheet_name)
    
    with open(products_json_path, "r") as f:
        products = json.load(f)

    # Prepare data for the sheet: header row + product rows
    sheet_data = [
        ["ID", "Description", "Price", "ImageURL", "ColorHEX", "ProductURL", "ColorName", "DetailDescription", "Type", "PersonalColorType"]
    ]  # Header row
    
    for product in products:
        sheet_data.append(
            [
                product.get("id"),
                product.get("description", ""),
                product.get("price", ""),
                product.get("imageUrl", ""),
                product.get("colorHex", ""),
                product.get("productUrl", ""),
                product.get("colorName", ""),
                product.get("detailDescription", ""),
                product.get("type", ""),
                product.get("personalColorType", ""),
            ]
        )

    # Update the sheet starting from A1
    sheet.update("A1", sheet_data)


if __name__ == "__main__":
    # Example usage
    sync_outfits_to_sheet()

