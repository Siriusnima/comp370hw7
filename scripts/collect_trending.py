import json
import argparse
import requests_cache
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(
    description = "Collecting trending articles from Montreal Gazette"
)

parser.add_argument(
    "-o",
    "--output",
    default = "data/raw_data/trending.json",
    help = "Path to the output JSON file"
)

args = parser.parse_args()


url = "https://montrealgazette.com/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

session = requests_cache.CachedSession(
    "gazette_cache",
    expire_after = 3600
)
response = session.get(
    url,
    headers=headers,
    timeout=15
)
print("Status", response.status_code)
print("From cache", response.from_cache)

"""
 #check scrapper failed message
print("Status", response.status_code)
print("Final URL", response.url)
print("Server", response.headers.get("Server"))
print("Content Type", response.headers.get("Content-Type"))
print("Response preview", response.text[:500])
"""



if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    trending_nav = soup.select_one(
        'nav[aria-label = "Secondary Navigation"]'
    )
    if trending_nav is not None:

        print("Trending navigation found")
        # print(trending_nav.prettify())

        links = trending_nav.select(
            "ul.secondary-navigation__list li a"
        )
        print("Number of links:", len(links))

        articles = []

        for link in links:
            #print(link.get_text(strip = True))
            article_url = link.get("href")
            #print("Article URL:", article_url)

            article_response = session.get(
                article_url,
                headers=headers,
                timeout=15
            )
            #print("Article status:", article_response.status_code)
            #print("Article from cache:", article_response.from_cache)

            if article_response.status_code == 200:
                article_soup = BeautifulSoup(
                    article_response.text,
                    "html.parser"
                )

                # Find title
                headline_tag = article_soup.select_one("h1")

                if headline_tag is not None:
                    title = headline_tag.get_text(strip=True)
                    #print("Article title:", title)
                else:
                    print("Article title not found")

                # Find date
                date_tag = article_soup.select_one(
                    "time.author-meta__date"
                )
                if date_tag is not None:
                    publication_date = date_tag.get("datetime")
                    #print("Publication date:", publication_date)
                else:
                    print("Publication date not found")
                
                #find author
                author_tag = article_soup.select_one(
                    "a.author-meta__author"
                )

                if author_tag is not None:
                    author_name = author_tag.get_text(strip = True)
                    #print("Author Name:", author_name)
                    # print(author_tag.prettify())
                else:
                    print("Author not found")

                # find blurb
                blurb_tag = article_soup.select_one(
                    "p.postmedia-article-topper__excerpt"
                )

                if blurb_tag is not None:
                    blurb = blurb_tag.get_text(strip=True)
                    #print("Blurb:", blurb)
                else:
                    blurb = None
                    print("Blurb not found")

                article_data = {
                    "title": title,
                    "publication date": publication_date,
                    "author": author_name,
                    "blurb": blurb
                }
                articles.append(article_data)

        print("Total article collected:", len(articles))

        #for article in articles:
            #print(article)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent = 4, ensure_ascii = False)

        print ("Results was saved to trending.json")


    else:
        print("Trending navigation not found.")
else:
    print("Request failed")



