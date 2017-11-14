# diffbotpy

## Abstract

serveral library offers diffbot API wrapper for Python (e.g. https://github.com/diffbot/diffbot-python-client or https://github.com/andreypopp/diffbot ), but these library has several limits.
The library diffbotpy supports various kinds of API.

## Installation

```bash
pip install -e git+ssh://git@github.com/wacul/diffbotpy.git@master#egg=diffbotpy-0.1
```

## Scope

diffbotpy supports almost all diffbot APIs below (except for account API):

+ Analyze API, Article API, Discussion API, Image API, Product API, Video API

+ Crawlbot API, Bulk API, Search API

## How to use

### Analyze/Article/Discussion/Video/Product/Image API 

```python
import diffbot
token = "aaa"
fetcher = diffbot.SingleFetcher(token=token)
target_url = "https://aaa.co.jp/"

# simplely fetch
#extractors = fetcher.fetch_analyze_extractors(
#    target_url = target_url,
#)

extractors = fetcher.fetch_article_extractors(
    target_url = "http://google.co.jp",
    args=diffbot.SingleFetcher.generate_article_args(
        fields = "meta",
    ) 
)


for extractor in extractors:
    print(extractor)
    print(extractor.get_raw_data())
    data = extractor.get_raw_data()
    description = data["meta"]["description"]
    keyword_list = data["meta"]["keywords"].split(",")
    print(extractor.get_title())
    
    print(description)
    print(keyword_list)
```

### Bulk/Crawling API, Search API

#### only Bulk/Crawling API

```python
import diffbot

job_operator = diffbot.BulkJobOperator(
    token=token,
    job_name = "topPageUrl_12751"
)


# send request to bulk/data and get response data
data = job_operator.fetch_raw_data()
## get list of extractor object.
# extractors = job_operator.fetch_extractors()
print(data[0])

for ext in extractors:
    print(ext.get_title())
```


#### only Search API

```python
searcher = diffbot.Searcher(
    token,
    job_name,
)

#raw_data = searcher.fetch_raw_data(query = "type:article")
#print(raw_data)


extractors = searcher.fetch_search_extractors(query = "type:article")
for ext in extractors:
    # print(ext.get_raw_data())
    print(ext.get_title())
    print(ext.get_page_url())
```


#### both Bulk/Crawlbot API and Search API

```python
import diffbot
job_name = "topPageUrl_12751"

job_operator = diffbot.BulkJobOperator(
    token=token
)

# for new bot name
job_operator.start_job(
    target_url_list=new_url_lst,
    apiurl = job_operator.generate_apiurl("article"), # https://api.diffbot.com/v3/article
)

# fetch object using search API
searcher = job_operator.fetch_completed_searcher()
```

## Errors

Some Errors raise in paticular cases:

1. DiffbotTokenError
=> You may put the invalid username. Confirm your settings. See also `Settings` Section.

2. DiffbotResponseError
=> The response error occurs. see also https://www.diffbot.com/dev/docs/error/.

3. DiffbotJobStatusError
=> Some jobs are not completed in Bulk or Crawl API. Wait until the jobs completed, see also status code list, https://www.diffbot.com/dev/docs/bulk/api.jsp.



