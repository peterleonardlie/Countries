from mongoengine import StringField, IntField, Document, FloatField


class Country(Document):
    name = StringField(required=True, primary_key=True)
    code = StringField()
    population = IntField()
    area = IntField()
    pop_density = FloatField()
    life_expectancy = FloatField()
    gdp = FloatField()
    gdp_growth = FloatField()
    poverty = FloatField()
    literacy = FloatField()
    birth_rate = FloatField()
    death_rate = FloatField()
    co2_emissions = FloatField()

    happiness_score = FloatField()
    happiness_rank = IntField()

    hdi_score = FloatField()
    hdi_rank = IntField()

    def __init__(self, name, code, population, area, pop_density, life_expectancy, gdp, gdp_growth,
                 poverty, literacy, birth_rate, death_rate, co2_emissions, happiness_score=None, happiness_rank=None,
                 hdi_score=None, hdi_rank=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.code = code
        self.population = population
        self.area = area
        self.pop_density = pop_density
        self.life_expectancy = life_expectancy
        self.gdp = gdp
        self.gdp_growth = gdp_growth
        self.poverty = poverty
        self.literacy = literacy
        self.birth_rate = birth_rate
        self.death_rate = death_rate
        self.co2_emissions = co2_emissions
        self.happiness_score = happiness_score
        self.happiness_rank = happiness_rank
        self.hdi_score = hdi_score
        self.hdi_rank = hdi_rank
