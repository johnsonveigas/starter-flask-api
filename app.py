from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

app = Flask(__name__)

MAX_RETRIES = 3  # Maximum number of retries for video URL request

def get_response_with_retries(url, headers):
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    response = session.get(url, headers=headers)
    return response

def get_video_url(download_link, headers):
    for retry_count in range(MAX_RETRIES):
        url = 'https://dood.pm' + download_link
        response = get_response_with_retries(url, headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            #print(soup)
            a_tag = soup.find('a')
            if a_tag and 'onclick' in a_tag.attrs:
                onclick_value = a_tag['onclick']
                start_index = onclick_value.find("'") + 1
                end_index = onclick_value.rfind("'")
                video_url = 'https://doraemonapp-18102.firebaseapp.com/index.html?video=' + onclick_value[start_index:end_index]
                return video_url  # Return the video URL if found
    return None  # Return None if video URL not found after retries

@app.route('/', methods=['GET'])
def get_url_content():
    url = request.args.get('url')
    if not url:
        return "Error: URL parameter is missing", 400

    try:
        headers ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8','Referer':'https://google.com/'}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            #print(soup)
            download_div = soup.find('div', class_='download-content')
            if download_div:
                download_link = download_div.find('a')['href']
                print(download_link)
                download_link='https://dood.pm/download/1e9ppywd0b2w5sjxv2v9ryka/n/40850365-103-89-1693497377-33bbf60f6550cb50bf553b428e3c9287'
                video_url = get_video_url(download_link, headers)
                if video_url:
                    response_data = {"video_url": video_url}
                    return jsonify(response_data), 200
                else:
                    error_data = {"error": "Unable to fetch valid video URL after retries"}
                    return jsonify(error_data), 500
            else:
                
                error_data = {"error": "Error: Download content not found"}
                return jsonify(error_data), 500

        else:
            
            error_data = {"error": "Error: Unable to fetch URL content"}
            return jsonify(error_data), 500
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
