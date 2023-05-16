from pymongo.mongo_client import MongoClient
from urllib.parse import quote_plus
import configparser
import enchant

from flavours import create_flavor_combination, ingredients_profile
from rnn import generate_combinations, words_to_string, model
import json


d = enchant.Dict("en_US")

config = configparser.ConfigParser()
config.read('server/settings.ini')

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
    
    
    def find_recipe_by_ingredient(self, ingredient):
        
        d.check(ingredient.lower())
        
        similiar_ingredients = d.suggest(ingredient.lower())
        similiar_ingredients.append(ingredient)
        
        found = find_by_keyword(similiar_ingredients, self.coll)
        
        if found is None:
        
            combos = create_flavor_combination(similiar_ingredients)
            title = words_to_string(ingredient, combos)
            result = generate_combinations(model, [title], 0.5)
            fill_db(result, self.coll, len(title.split(" ")))
            created = find_by_keyword(similiar_ingredients, self.coll)
            
            if created is not None:
                return created
        
        else:
            return found
        
        return None
        

def isFound(arr):
    return arr != None

def find_by_keyword(ingredients, db):
    for ing in ingredients:
            query_keywords = db.find_one({"keywords": ing})
            if query_keywords is not None:
                return query_keywords
    

def fill_db(recipes, db, title_length):
    
    for recipe in recipes:
        
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
        
        recipe_title = recipe_title.rstrip().lstrip().replace("_", "")
        recipe_ingredients = recipe_ingredients.rstrip().lstrip().replace("_", "")
        recipe_instructions = recipe_instructions.rstrip().lstrip().replace("_", "")
        
        if len(recipe_instructions) <= 1:
            recipe_instructions = " ".join(recipe_title.split()[title_length:])
            recipe_title = " ".join(recipe_title.split()[:title_length]) 
        
        if sum([len(recipe_title), len(recipe_ingredients), len(recipe_instructions)]) < 20:
            continue
        
        text = recipe.lower()
        words = text.split()
        words = [word.strip('.,!;•▪︎()[]') for word in words]
        unique = []
        
        for word in words:
            if word not in unique:
                unique.append(word)
        
        db.insert_one({
            "title": recipe_title, 
            "ingredients": recipe_ingredients, 
            "instructions": recipe_instructions,
            "keywords": unique})


if __name__ == "__main__":
    con = DatabaseConnector(uri)
    con.return_record_in_array(["tomato"])

    con.coll.insert_one({
        "title": "mlirge ot onion servion",
        "ingredients": "5 tablespoons chopped cheese",
        "instructions": "Pround thick bowl ingredients to boil lowl cook top the roffer ele creams in a large stirring of a 3-large bowl and pap entich and the Corn to cratbage sprightle, cream in saucepan and stir temperature and corkiened oil to bowl. Cook until browe bronby 1/4 cups woth garnish with salt and pecpart, and plave oncasing oil and cold water, 35 to 2 minutes (easone pepper. Season tarr to classer. Drain mixture 1 minute. Stor to a bowl. Mix water and to simmer, notstoo and simmer, cold rimmed, about 30 minutes, about 12 minutes. Add while furns the in onion, cut to combined an upplese. Cook until the heat. Add fook in a bakn-pere. Reped until heavy sheas with the cooking occasionally."
    })
    con.coll.insert_one({
        "title": "hesperrie or Casiffed shyrFace",
        "ingredients": "8 thiss; beach cup (a sárap of cut butter and milks",
        "instructions": "If remove fromele. Seanon over lide stirring dissardwises iconts and salt, until large bowl. Gratum betomet stematise with inchester atal until broth in blutctir. Mean let been or botw ruffing in course, 5 te peppers. Add Garlic on bat seeces. line onions glaves and vightly add 2 minutes. Sotarn gacontis (we)t asoll to roostely supfer and bach waters ase crivies, and gour courker babon paste of prepere salted and seeds and nut a 3 1/3-inch flams Trpame harbon mixture deges. Dill, noil, tease, indreding smoot in mold. Serve."})