import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig, LLMContentFilter, \
    DefaultMarkdownGenerator
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, ContentRelevanceFilter

# Constants
BROWSER_TYPE = "chromium"
QUERY_TEXT = "get name and url of all the mutual funds"
LLM_PROVIDER = "openai/gpt-4o-mini"
API_TOKEN = ""
CACHE_MODE_ENABLED = CacheMode.ENABLED
CACHE_MODE_BYPASS = CacheMode.BYPASS
WORD_COUNT_THRESHOLD = 10
EXCLUDED_TAGS = ['form', 'header']
EXCLUDE_EXTERNAL_LINKS = True
PROCESS_IFRAMES = True
REMOVE_OVERLAY_ELEMENTS = True
DEEP_CRAWL_MAX_DEPTH = 1
RELEVANCE_THRESHOLD = 0.7
CHUNK_TOKEN_THRESHOLD = 500
VERBOSE_MODE = True
MUTUAL_FUNDS_URL = "https://www.moneycontrol.com/mutual-funds/find-fund/returns?..."

LLM_INSTRUCTION = """
    Extract all mutual fund names and their details from Moneycontrol's "Explore All Funds" section.
    Ensure JSON output with structured data, including Fund Name, URL, Category, NAV, AUM, Returns, etc.
"""


def get_browser_config(debug=False):
    return BrowserConfig(
        browser_type=BROWSER_TYPE,
        headless=not debug,
        text_mode=True,
        verbose=debug
    )


def get_crawler_run_config():
    return CrawlerRunConfig(
        word_count_threshold=WORD_COUNT_THRESHOLD,
        excluded_tags=EXCLUDED_TAGS,
        exclude_external_links=EXCLUDE_EXTERNAL_LINKS,
        process_iframes=PROCESS_IFRAMES,
        remove_overlay_elements=REMOVE_OVERLAY_ELEMENTS,
        cache_mode=CACHE_MODE_ENABLED
    )


def get_relevance_filter():
    return ContentRelevanceFilter(
        query=QUERY_TEXT,
        threshold=RELEVANCE_THRESHOLD
    )


def get_llm_config():
    return LLMConfig(
        provider=LLM_PROVIDER,
        api_token=API_TOKEN
    )


def get_llm_content_filter():
    return LLMContentFilter(
        llm_config=get_llm_config(),
        instruction=LLM_INSTRUCTION,
        chunk_token_threshold=CHUNK_TOKEN_THRESHOLD,
        verbose=VERBOSE_MODE
    )


def get_markdown_generator():
    return DefaultMarkdownGenerator(
        content_filter=get_llm_content_filter(),
        options={"ignore_links": True}
    )


async def main():
    browser_config = get_browser_config(debug=True)
    run_config = get_crawler_run_config()
    deep_crawl_config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=DEEP_CRAWL_MAX_DEPTH,
            filter_chain=FilterChain([get_relevance_filter()])
        )
    )
    markdown_generator = get_markdown_generator()

    final_run_config = CrawlerRunConfig(
        markdown_generator=markdown_generator,
        cache_mode=CACHE_MODE_BYPASS
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=MUTUAL_FUNDS_URL,
            config=final_run_config
        )

        print(result.markdown)
        print('=' * 80)


if __name__ == "__main__":
    asyncio.run(main())
