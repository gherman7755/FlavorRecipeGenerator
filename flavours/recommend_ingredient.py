import json
from . import load_db
import random


df0, _, _ = load_db()

with open("flavours\\ingredients.json") as f:
    ingredients_profile = json.loads(f.read())

categories = df0['category'].unique()

def get_five_categories(useless):
    filtered_categories = list(categories)
    filtered_categories.remove(useless)
    return random.sample(filtered_categories, 4)
    

def create_flavor_combination(ingredient_familiar):
        
    found_id = -1
    
    combos_ingredients = []
    
    for ing in ingredient_familiar:
        if ing.lower() in ingredients_profile.keys():
            
            found_id = ingredients_profile[ing]
            break
    
    if found_id != -1:
        ing_molecules_set = df0['molecules'][found_id]
        ing_category = df0['category'][found_id]
        
        final_categories = get_five_categories(ing_category)
        max_combos_by_categories = dict.fromkeys(final_categories, [0, 0])
        
        filtered_df = df0[df0['category'].isin(final_categories)]
        
        for index, _ in filtered_df.iterrows():
            data_set = df0['molecules'][index]
            
            selected_category = df0['category'][index]
            number_combos = len(ing_molecules_set.intersection(data_set))
            
            if number_combos > max_combos_by_categories[selected_category][0]:

                max_combos_by_categories[selected_category] = [number_combos, df0['entity id'][index]]
        
        
        for ingredient, ingredient_id in ingredients_profile.items():
            for _, values in max_combos_by_categories.items():
                if ingredient_id == values[1]:
                    combos_ingredients.append(ingredient)
        return combos_ingredients
    
    else:
        return None


if __name__ == "__main__":
    result = create_flavor_combination(['mushroom'])
    print(result)