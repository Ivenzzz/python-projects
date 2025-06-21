from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    links = []
    if request.method == 'POST':
        url = request.form['url']
        max_pages = 5  # Limit to avoid deep or infinite crawling
        visited = set()
        to_visit = [url]
        links = []

        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue
            try:
                response = requests.get(current_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                visited.add(current_url)

                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']

                    # Convert relative links to full URLs
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        href = urljoin(current_url, href)

                    # Filter only http/https links
                    if href.startswith('http'):
                        links.append(href)
                        if href not in visited and href not in to_visit:
                            to_visit.append(href)

            except Exception as e:
                links.append(f"Error visiting {current_url}: {e}")
    return render_template('index.html', links=links)

if __name__ == '__main__':
    app.run(debug=True)
    

