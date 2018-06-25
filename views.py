import math
import operator

from flask import Flask, render_template, redirect, url_for
from flask_restful import reqparse
from pymongo import MongoClient

from models import *

app = Flask(__name__)


# connect to Claire's Mlab
def connect_db():
    connection = MongoClient('ds133340.mlab.com', 33340)
    db = connection['comp9321-db']
    db.authenticate('user', 'password')

    return db


@app.route('/')
def index():
    return redirect(url_for("get_countries"))


# show a list of all countries
@app.route("/countries/", methods=['GET'])
def get_countries():
    query = []
    for country in countries:
        readable = convert_to_readable(country)
        query.append(readable)

    return render_template("home.html", countries=query, search='')


# show the information for a specific country
@app.route("/countries/<name>", methods=['GET'])
def get_single_country(name):
    no_data = False
    for country in countries:
        if name.lower() == country.name.lower():
            readable = convert_to_readable(country)
            query = readable
            country_name = country.name

            # check for gdp growth
            if (country.gdp_growth == 0):
                no_data = True

            # implement k-nearest neighbour algorithm
            for data in normalize:
                if data[0] == country.name:
                    neighbour_name = get_k_nearest_neighbours(normalize, data, 3)

            break

    # get chart data
    chart_data = []
    for country in normalize:
        if country_name == country[0]:
            for i in range(1, len(country)):
                if (i == 6 or i == 10) and country[i] != 0:
                    # lower value rate higher
                    chart_data.append(abs(country[i] - 1))
                else:
                    # normal rating
                    if (i == 5 and no_data):
                        chart_data.append(0)
                    else:
                        chart_data.append(country[i])
            break

    # get neighbour data
    neighbour = []
    for data in neighbour_name:
        for country in countries:
            if data == country.name:
                readable = convert_to_readable(country)
                neighbour.append(readable)

                # go to next neighbour
                break

    return render_template("profile_page.html", name=country_name,
                           country=query, chart_data=chart_data,
                           neighbour=neighbour, count=len(neighbour))


# search for countries by name
@app.route("/countries/search", methods=['GET'])
def search_countries():
    parser = reqparse.RequestParser()
    parser.add_argument('query', type=str)
    args = parser.parse_args()
    name = args.get('query')

    results = []
    for country in countries:
        if name.lower() in country.name.lower():
            readable = convert_to_readable(country)
            results.append(readable)

    return render_template("home.html", countries=results, search=name)


def get_parameters(data):
    # we put in parameters so that if data is None, it doesn't give error
    try:
        name = data['_id']
    except:
        name = None

    try:
        code = data['code']
    except:
        code = None
    try:
        population = data['population']
    except:
        population = 0

    try:
        area = data['area']
    except:
        area = 0

    try:
        pop_density = data['pop_density']
    except:
        pop_density = 0

    try:
        life_expectancy = data['life_expectancy']
    except:
        life_expectancy = 0

    try:
        gdp = data['gdp']
    except:
        gdp = 0

    try:
        gdp_growth = data['gdp_growth']
    except:
        gdp_growth = 0

    try:
        poverty = data['poverty']
    except:
        poverty = 0

    try:
        literacy = data['literacy']
    except:
        literacy = 0

    try:
        birth_rate = data['birth_rate']
    except:
        birth_rate = 0

    try:
        death_rate = data['death_rate']
    except:
        death_rate = 0

    try:
        co2_emissions = data['co2_emissions']
    except:
        co2_emissions = 0

    try:
        happiness_score = data['happiness_score']
    except:
        happiness_score = 0

    try:
        happiness_rank = data['happiness_rank']
    except:
        happiness_rank = None

    try:
        hdi_score = data['hdi_score']
    except:
        hdi_score = 0

    try:
        hdi_rank = data['hdi_rank']
    except:
        hdi_rank = None

    return name, code, population, area, pop_density, life_expectancy, \
           gdp, gdp_growth, poverty, literacy, birth_rate, \
           death_rate, co2_emissions, happiness_score, \
           happiness_rank, hdi_score, hdi_rank,


def format_number(number):
    suffix = ['', ' thousand', ' million', ' billion', ' trillion']
    n = float(number)
    index = max(0, min(len(suffix) - 1,
                       int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    if index != 0:
        return '{:.2f}{}'.format(n / 10 ** (3 * index), suffix[index])
    else:
        return number


def get_countries_data_from_mongoDB():
    db = connect_db()
    countries = []

    # list to be used to store value for normalize
    population_list = []
    pop_density_list = []
    life_list = []
    gdp_list = []
    gdp_growth_list = []
    poverty_list = []
    literacy_list = []
    birth_rate_list = []
    death_rate_list = []
    co2_list = []
    happiness_list = []
    hdi_list = []

    for data in db.country.find().sort("_id"):
        # get all the data from mongoDB, and put in params
        name, code, population, area, pop_density, life_expectancy, \
        gdp, gdp_growth, poverty, literacy, birth_rate, \
        death_rate, co2_emissions, happiness_score, \
        happiness_rank, hdi_score, hdi_rank = get_parameters(data)

        countries.append(Country(
            name,
            code,
            population,
            area,
            pop_density,
            life_expectancy,
            gdp,
            gdp_growth,
            poverty,
            literacy,
            birth_rate,
            death_rate,
            co2_emissions,
            happiness_score,
            happiness_rank,
            hdi_score,
            hdi_rank
        ))

        # create list with normalize values
        # firstly create list for each important data
        # population, area, life_expectancy, gdp, poverty, literacy, co2_emissions,
        # happiness_score, hdi_score
        population_list.append(population)
        pop_density_list.append(pop_density)
        life_list.append(life_expectancy)
        gdp_list.append(gdp)
        gdp_growth_list.append(gdp_growth)
        poverty_list.append(poverty)
        literacy_list.append(literacy)
        birth_rate_list.append(birth_rate)
        death_rate_list.append(death_rate)
        co2_list.append(co2_emissions)
        happiness_list.append(happiness_score)
        hdi_list.append(hdi_score)

    # create list with normalize values
    normalize = []
    for data in countries:
        temp = []
        temp.append(data.name)

        population = (data.population - min(population_list)) / (max(population_list) - min(population_list))
        temp.append(population)
        pop_density = (data.pop_density - min(pop_density_list)) / (max(pop_density_list) - min(pop_density_list))
        temp.append(pop_density)
        life = (data.life_expectancy - min(life_list)) / (max(life_list) - min(life_list))
        temp.append(life)
        gdp = (data.gdp - min(gdp_list)) / (max(gdp_list) - min(gdp_list))
        temp.append(gdp)
        gdp_growth = (data.gdp_growth - min(gdp_growth_list)) / (max(gdp_growth_list) - min(gdp_growth_list))
        temp.append(gdp_growth)
        poverty = (data.poverty - min(poverty_list)) / (max(poverty_list) - min(poverty_list))
        temp.append(poverty)
        literacy = (data.literacy - min(literacy_list)) / (max(literacy_list) - min(literacy_list))
        temp.append(literacy)
        birth_rate = (data.birth_rate - min(birth_rate_list)) / (max(birth_rate_list) - min(birth_rate_list))
        temp.append(birth_rate)
        death_rate = (data.death_rate - min(death_rate_list)) / (max(death_rate_list) - min(death_rate_list))
        temp.append(death_rate)
        co2_emissions = (data.co2_emissions - min(co2_list)) / (max(co2_list) - min(co2_list))
        temp.append(co2_emissions)
        happiness_score = (data.happiness_score - min(happiness_list)) / (max(happiness_list) - min(happiness_list))
        temp.append(happiness_score)
        hdi_score = (data.hdi_score - min(hdi_list)) / (max(hdi_list) - min(hdi_list))
        temp.append(hdi_score)

        normalize.append(temp)

    return countries, normalize


# K-Nearest Neighbour implementation for countries similar to features
def get_k_nearest_neighbours(training_set, test_instance, k):
    distances = []

    length = len(test_instance) - 1
    for x in range(len(training_set)):
        dist = euclidean_distance(test_instance, training_set[x], length)
        if dist != 0.0:
            distances.append((training_set[x], dist))

    distances.sort(key=operator.itemgetter(1))
    neighbours = []
    for x in range(k):
        neighbours.append(distances[x][0][0])

    return neighbours


def euclidean_distance(instance1, instance2, length):
    # the distance metric that will be used in this algorithm
    # basically the normal euclidean distance
    # sqrt(sum of all (xi - yi)2)
    distance = 0
    for x in range(1, length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)


def convert_to_readable(country):
    name = country.name
    code = country.code.lower() if country.code else None
    population = format_number(country.population)
    area = format_number(country.area)

    if country.pop_density:
        pop_density = '{:.2f}'.format(country.pop_density)
    else:
        pop_density = None
    life_expectancy = '{:.1f} years'.format(country.life_expectancy)

    if country.gdp != 0:
        gdp = format_number(country.gdp)
    else:
        gdp = None

    if country.gdp_growth:
        gdp_growth = '{:.2f}'.format(country.gdp_growth)
    else:
        gdp_growth = None

    if country.poverty:
        poverty = '{:.2f}'.format(country.poverty)
    else:
        poverty = None

    if country.literacy:
        literacy = '{:.2f}'.format(country.literacy)
    else:
        literacy = None

    if country.birth_rate:
        birth_rate = '{:.2f}'.format(country.birth_rate)
    else:
        birth_rate = None

    if country.death_rate:
        death_rate = '{:.2f}'.format(country.death_rate)
    else:
        death_rate = None

    if country.co2_emissions:
        co2_emissions = '{:.2f}'.format(country.co2_emissions)
    else:
        co2_emissions = None

    if country.happiness_score:
        happiness_score = '{:.2f}'.format(country.happiness_score)
    else:
        happiness_score = None

    happiness_rank = country.happiness_rank

    if country.hdi_score:
        hdi_score = '{:.2f}'.format(country.hdi_score)
    else:
        hdi_score = None

    hdi_rank = country.hdi_rank

    return Country(
        name,
        code,
        population,
        area,
        pop_density,
        life_expectancy,
        gdp,
        gdp_growth,
        poverty,
        literacy,
        birth_rate,
        death_rate,
        co2_emissions,
        happiness_score,
        happiness_rank,
        hdi_score,
        hdi_rank
    )


if __name__ == '__main__':
    countries, normalize = get_countries_data_from_mongoDB()
    app.run(debug=True)
