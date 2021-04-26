# Import Splinter and Beautiful Soup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = mars_hemispheres(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title":news_title,
        "news_paragraph":news_paragraph,
        "featured_image":featured_image(browser),
        "facts":mars_facts(),
        "last_modified":dt.datetime.now(),
        "hemispheres":hemisphere_image_urls
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quite the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first <a> tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent eleent to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p

# ### Featured Images

def featured_image(browser):
    
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL t ocreate an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():

    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

# Challenge Portion
# Function to retrieve hemisphere image urls and titles
def mars_hemispheres(browser):

    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Create list to hold images and titles
    hemisphere_image_urls = []

    # Click through image links for each hemisphere
    for i in range(0,4):
        hemisphere_dict = {}
    
        links = browser.find_by_tag('h3')
        links[i].click()
    
        # Parse HTML
        html = browser.html
        hemisphere_soup = soup(html, 'html.parser')
    
        # Get the image URL
        hemisphere_url = hemisphere_soup.find('a', text='Sample').get('href')
    
        # Get the image title
        hemisphere_title_html = hemisphere_soup.find('h2', class_='title')
        hemisphere_title = hemisphere_title_html.text
    
        # Write items to dictionary
        hemisphere_dict = {
            'img_url':hemisphere_url,
            'title':hemisphere_title
        }
    
        hemisphere_image_urls.append(hemisphere_dict)
    
        browser.back()

    return hemisphere_image_urls

if __name__ == '__main__':
    # If running as script, print scraped data
    print(scrape_all())




