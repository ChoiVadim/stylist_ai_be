import gspread
import json
import pandas as pd

auth_file = "auth.json"
gc = gspread.service_account(filename=auth_file)
sheet_url = "https://docs.google.com/spreadsheets/d/10NkfXVm8WYel4GTTTIaFyPxmVy52ODjda0WNpl70dF8/edit?gid=0#gid=0"

sheet_file = gc.open_by_url(sheet_url)

sheet = sheet_file.worksheet("Main")
data = sheet.get_all_records()
df = pd.DataFrame(data)

def __get_all_items():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def get_outfit_by_season(season):
    df = __get_all_items()
    df = df.loc[df['PersonalColorType'] == season]
    return df.to_dict(orient='records')


def get_outfit_by_category(category):
    df = __get_all_items()
    df = df.loc[df['Type'] == category]
    return df.to_dict(orient='records')

def get_outfit_by_season_and_category(season, category):
    df = __get_all_items()
    if season is not None:
        df = df.loc[df['PersonalColorType'] == season]
    if category is not None:
        df = df.loc[df['Type'] == category]
    if season is not None and category is not None:
        df = df.loc[(df['PersonalColorType'] == season) & (df['Type'] == category)]
        return df.to_dict(orient='records')
    return []

if __name__ == "__main__":
    print(get_outfit_by_season_and_category("Deep Autumn", "t-shirts"))