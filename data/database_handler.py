from pymongo.mongo_client import MongoClient
from urllib.parse import quote_plus
import configparser
# from recipe_generator import model, generate_combinations

config = configparser.ConfigParser()
config.read('data/settings.ini')

USERNAME = quote_plus(config['DEFAULT']['username'])
PASSWORD = quote_plus(config['DEFAULT']['password'])

uri = "mongodb+srv://" + USERNAME + ":" + PASSWORD + "@cluster0.5uhe4wh.mongodb.net/?retryWrites=true&w=majority"

class DatabaseConnector:
    def __init__(self, uri="mongodb+srv://" + USERNAME + ":" + PASSWORD + "@cluster0.5uhe4wh.mongodb.net/?retryWrites=true&w=majority"):

        # Create a new client and connect to the server
        self.client = MongoClient(uri)
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            
            self.db = self.client.server
            self.coll = self.db.recipes
            
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
    
        
    def ingredient_found(self, ingredient):
        results = self.find({ "instructions": { "$regex": ingredient } })
        for res in results:
            print(res)
    
    def return_record_in_array(self, arr):
        query = {"ingredients": {"$in": arr}}
        results = self.coll.find(query)
        for result in results:
            print(result)
        
        
def fill_db(db):
    
    # res = generate_combinations(model, ["Apple", "Orange"], 0.2)
    res = ''
    for recipe in res:
        
        recipe_title = ''
        recipe_instructions = ''
        recipe_ingredients = ''
        section_marker = ''
        sections = {'*': 'title', '▪︎': 'instructions', '•': 'ingredients'}

        for symbol in recipe:
            if symbol in sections:
                section_marker = symbol
            elif section_marker:
                if sections[section_marker] == 'title':
                    recipe_title += symbol
                elif sections[section_marker] == 'instructions':
                    recipe_instructions += symbol
                elif sections[section_marker] == 'ingredients':
                    recipe_ingredients += symbol
            elif symbol == '_':
                break
        
        recipe_title = recipe_title.rstrip().lstrip()
        recipe_ingredients = recipe_ingredients.rstrip().lstrip()
        recipe_instructions = recipe_instructions.rstrip().lstrip()
        
        if sum([recipe_title, recipe_ingredients, recipe_instructions]) < 20:
            continue
        
        db.insert_one({"title": recipe_title, "ingredients": recipe_ingredients, "instructions": recipe_instructions})


if __name__ == "__main__":
    con = DatabaseConnector(uri)
    con.return_record_in_array(["tomato"])
    # con.fill_db()

    con.coll.insert_one({
        "title": "mlirge ot onion servion",
        "ingredients": "5 tablespoons chopped cheese",
        "instructions": "Pround thick bowl ingredients to boil lowl cook top the roffer ele creams in a large stirring of a 3-large bowl and pap entich and the Corn to cratbage sprightle, cream in saucepan and stir temperature and corkiened oil to bowl. Cook until browe bronby 1/4 cups woth garnish with salt and pecpart, and plave oncasing oil and cold water, 35 to 2 minutes (easone pepper. Season tarr to classer. Drain mixture 1 minute. Stor to a bowl. Mix water and to simmer, notstoo and simmer, cold rimmed, about 30 minutes, about 12 minutes. Add while furns the in onion, cut to combined an upplese. Cook until the heat. Add fook in a bakn-pere. Reped until heavy sheas with the cooking occasionally."
    })
    con.coll.insert_one({
        "title": "hesperrie or Casiffed shyrFace",
        "ingredients": "8 thiss; beach cup (a sárap of cut butter and milks",
        "instructions": "If remove fromele. Seanon over lide stirring dissardwises iconts and salt, until large bowl. Gratum betomet stematise with inchester atal until broth in blutctir. Mean let been or botw ruffing in course, 5 te peppers. Add Garlic on bat seeces. line onions glaves and vightly add 2 minutes. Sotarn gacontis (we)t asoll to roostely supfer and bach waters ase crivies, and gour courker babon paste of prepere salted and seeds and nut a 3 1/3-inch flams Trpame harbon mixture deges. Dill, noil, tease, indreding smoot in mold. Serve."})