import requests
import sys
import os

# Global variable to store favorite articles
favorite_articles = []

def search_wikipedia(query):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract search results
        search_results = data["query"]["search"]
        return search_results

    except requests.RequestException as e:
        print("Error fetching data:", e)
        return []

def get_article_summary(article_title):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "titles": article_title,
        "exintro": True,
        "explaintext": True,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract page id and summary
        page_id = list(data["query"]["pages"].keys())[0]
        summary = data["query"]["pages"][page_id]["extract"]
        return summary

    except requests.RequestException as e:
        print("Error fetching data:", e)
        return None

def get_related_articles(article_title):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "links",
        "titles": article_title,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract links to related articles
        page_id = list(data["query"]["pages"].keys())[0]
        related_articles = [link["title"] for link in data["query"]["pages"][page_id]["links"]]
        return related_articles

    except requests.RequestException as e:
        print("Error fetching data:", e)
        return []

def save_favorite_article(article_title):
    favorite_articles.append(article_title)
    save_favorite_articles_to_file()
    print(f"'{article_title}' has been added to favorites.")

def load_favorite_articles_from_file():
    if os.path.exists("favorite_articles.txt"):
        with open("favorite_articles.txt", "r") as file:
            return [line.strip() for line in file.readlines()]
    else:
        return []

def save_favorite_articles_to_file():
    with open("favorite_articles.txt", "w") as file:
        for article in favorite_articles:
            file.write(article + "\n")

def show_favorite_articles():
    if not favorite_articles:
        print("You haven't saved any favorite articles yet.")
    else:
        print("\nYour Favorite Articles:")
        for i, article_title in enumerate(favorite_articles, start=1):
            print(f"{i}. {article_title}")

def export_article_to_file(article_title, summary):
    file_name = article_title.replace(" ", "_") + ".txt"
    with open(file_name, "w") as file:
        file.write(summary)
    print(f"Article summary has been exported to '{file_name}'.")

def main():
    global favorite_articles
    favorite_articles = load_favorite_articles_from_file()

    if len(sys.argv) < 2:
        print("Usage: python wikipedia_cli.py <search_query>")
        sys.exit(1)

    search_query = " ".join(sys.argv[1:])
    search_results = search_wikipedia(search_query)

    if not search_results:
        print("\nNo results found.")
    elif len(search_results) == 1:
        article_title = search_results[0]["title"]
        print(f"\nSummary of '{article_title}':")
        summary = get_article_summary(article_title)
        print(summary)
        choice = input("\nDo you want to save this article to favorites? (yes/no): ")
        if choice.lower() == "yes":
            save_favorite_article(article_title)
        choice = input("\nDo you want to export this article summary to a text file? (yes/no): ")
        if choice.lower() == "yes":
            export_article_to_file(article_title, summary)
    else:
        print("\nMultiple results found. Please choose one:")
        for i, result in enumerate(search_results, start=1):
            print(f"{i}. {result['title']}")

        try:
            choice = int(input("\nEnter the number of the article you want to read: "))
            if choice < 1 or choice > len(search_results):
                print("Invalid choice.")
            else:
                article_title = search_results[choice - 1]["title"]
                print(f"\nSummary of '{article_title}':")
                summary = get_article_summary(article_title)
                print(summary)
                choice = input("\nDo you want to save this article to favorites? (yes/no): ")
                if choice.lower() == "yes":
                    save_favorite_article(article_title)
                choice = input("\nDo you want to export this article summary to a text file? (yes/no): ")
                if choice.lower() == "yes":
                    export_article_to_file(article_title, summary)
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Prompt to show favorite articles
    show_favorite_articles()

if __name__ == "__main__":
    main()
