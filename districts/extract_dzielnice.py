import geojson

converter = {
    "dzielnica vii zwierzyniec": "Zwierzyniec",
    "dzielnica x swoszowice": "Swoszowice",
    "dzielnica viii dębniki": "Dębniki",
    "dzielnica xii biezanow-prokocim": "Bieżanow-Prokocim",
    "dzielnica xiii podgórze": "Podgórze",
    "dzielnica xviii nowa huta": "Nowa Huta",
    "dzielnica xvi bieńczyce": "Bieńczyce",
    "dzielnica ix łagiewniki-borek fałęcki": "Łagiewniki-Borek Fałęcki",
    "dzielnica i stare miasto": "Stare miasto",
    "dzielnica ii grzegórzki": "Grzegórzki",
    "dzielnica iii prądnik czerwony": "Prądnik Czerwony",
    "dzielnica iv prądnik biały": "Prądnik Biały",
    "dzielnica v krowodrza": "Krowodrza",
    "dzielnica vi bronowice": "Bronowice",
    "dzielnica xi podgórze duchackie": "Podgórze Duchackie",
    "dzielnica xiv czyżyny": "Czyżyny",
    "dzielnica xv mistrzejowice": "Mistrzejowice",
    "dzielnica xvii wzgórza krzeszławickie": "Wzgórza Krzeszławickie",
}


city_districts = None
with open('./krakow-dzielnice.geojson', 'r', encoding="utf8") as F:
    city_districts = geojson.loads(F.read())

for district in city_districts.features:
    district_name = district.properties.get('name').lower()
    final_district_name = converter[district_name]
    with open(u'{}.geojson'.format(final_district_name), 'w') as WF:
        WF.write(geojson.dumps(district.geometry))
