import gspread
import json

auth_file = 'auth.json'
gc = gspread.service_account(filename=auth_file)
sheet_url = 'https://docs.google.com/spreadsheets/d/10NkfXVm8WYel4GTTTIaFyPxmVy52ODjda0WNpl70dF8/edit?gid=0#gid=0'

sheet_file = gc.open_by_url(sheet_url)
sheet = sheet_file.sheet1
data = sheet.get_all_records()
print(data)

with open('data/products.json', 'r') as f:
    products = json.load(f).get('products', [])

    
# Prepare data for the sheet: header row + product rows
sheet_data = [['ID','Name', 'Price', 'Category', 'Color', 'ColorHEX', 'Season', 'URL', 'Image']]  # Header row
for product in products:
    sheet_data.append([
        product.get('id'),
        product.get('name', ''),
        product.get('price', ''),
        product.get('category', ''),
        product.get('colorText', ''),
        product.get('colorHex', ''),
        product.get('season', ''),
        product.get('productUrl', ''),
        product.get('imageUrl', ''),
    ])

# Update the sheet starting from A1
sheet.update('A1', sheet_data)