import random

title_words = ["sprikled with", "under", "seasoned with"]

def words_to_string(ingredient, combos):
    title = str(ingredient).capitalize()
    
    for combo in combos:
        random_word = random.choice(title_words)
        title += " " + random_word + " " + combo

    return title


if __name__ == "__main__":
    print(words_to_string("letuce", ["cheese", "coffee", "potato", "banana"]))