import pycountry
from flask import Flask
from mongoengine import connect
from xlrd import open_workbook

from models import Country

app = Flask(__name__)

db = 'mongodb://user:password@ds133340.mlab.com:33340/comp9321-db'


# Import the worldbank world development indicator data
# Downloaded from http://databank.worldbank.org/data/reports.aspx?source=2
def worldbank_import():
    book = open_workbook('./data/worldbank.xlsx')
    sheet = book.sheet_by_name('Data')

    # start at cell 4 in row, find biggest column with a value which is most recent value
    def get_most_recent(row_index):
        row = sheet.row(row_index)
        most_recent = None
        for col in range(4, len(row)):
            if row[col].value and not row[col].value == '..':
                most_recent = row[col].value

        return most_recent

    # given a starting row in the sheet, make a Country object
    def make_country(start_row):
        name = sheet.cell(start_row, 0).value
        try:
            code = pycountry.countries.get(name=name).alpha_2 if pycountry.countries.get(name=name) else None
        except:
            code = None

        population = get_most_recent(start_row)
        area = get_most_recent(start_row + 1)
        pop_density = get_most_recent(start_row + 2)
        life_expectancy = get_most_recent(start_row + 3)
        gdp = get_most_recent(start_row + 4)
        gdp_growth = get_most_recent(start_row + 5)
        poverty = get_most_recent(start_row + 6)
        literacy = get_most_recent(start_row + 7)
        birth_rate = get_most_recent(start_row + 8)
        death_rate = get_most_recent(start_row + 9)
        co2_emissions = get_most_recent(start_row + 10)

        return Country(name, code, population, area, pop_density, life_expectancy, gdp, gdp_growth,
                       poverty, literacy, birth_rate, death_rate, co2_emissions)

    # make and save all the country objects from the sheet
    connect(host=db)
    for row in range(1, sheet.nrows, 11):
        country = make_country(row)
        country.save()


# Import the UN human development data
# Downloaded from http://data.un.org/DocumentData.aspx?q=human+development+index&id=378
def un_hdi_import():
    book = open_workbook('./data/un_hdi.xlsx')
    sheet = book.sheet_by_name('Table 2')

    connect(host=db)
    for row in range(7, sheet.nrows):
        name = sheet.cell(row, 1).value
        hdi_score = sheet.cell(row, 14).value
        hdi_rank = sheet.cell(row, 0).value

        Country.objects(name=name).update(hdi_score=hdi_score, hdi_rank=hdi_rank)


# Import Kaggle world happiness report data
# Downloaded from https://www.kaggle.com/unsdsn/world-happiness
def happiness_import():
    book = open_workbook('./data/kaggle_happiness.xlsx')
    sheet = book.sheet_by_name('2017')

    connect(host=db)
    for row in range(1, sheet.nrows):
        name = sheet.cell(row, 0).value
        happiness_score = sheet.cell(row, 2).value
        happiness_rank = sheet.cell(row, 1).value

        Country.objects(name=name).update(
            happiness_score=happiness_score,
            happiness_rank=happiness_rank)


if __name__ == '__main__':
    # Uncomment below to run data import
    # worldbank_import()
    # un_hdi_import()
    # happiness_import()
    pass
