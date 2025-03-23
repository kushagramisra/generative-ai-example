import asyncio
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMContentFilter, DefaultMarkdownGenerator
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, ContentRelevanceFilter
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


async def main():
    browser_config = BrowserConfig(
    browser_type="chromium",
    headless=True,
    text_mode=True
    )

    # Create a visible browser config for debugging
    debug_browser = browser_config.clone(
        headless=False,
        verbose=True
    )
    run_config = CrawlerRunConfig(
        # Content filtering
        word_count_threshold=10,
        excluded_tags=['form', 'header'],
        exclude_external_links=True,

        # Content processing
        process_iframes=True,
        remove_overlay_elements=True,

        # Cache control
        cache_mode=CacheMode.ENABLED  # Use cache if available
    )

    # Create a content relevance filter
    relevance_filter = ContentRelevanceFilter(
        query="get name and url of all the mutual funds",
        threshold=0.7  # Minimum similarity score (0.0 to 1.0)
    )

    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=1,
            filter_chain=FilterChain([relevance_filter])
        )
    )

    # 2) Example LLM content filtering

    gemini_config = LLMConfig(
        provider="openai/gpt-4o-mini",
        api_token = ""
    )

    # Initialize LLM filter with specific instruction
    filter = LLMContentFilter(
        llm_config=gemini_config,  # or your preferred provider
        instruction="""
            **Prompt:**  
            
            Extract all mutual fund names and their detailed information from the **"Explore All Funds"** section on the Moneycontrol website. The mutual funds are categorized under the following types:  
            
            - **Equity**  
            - **Equity-Focused**  
            - **Debt Long Term**  
            - **Debt Short Term**  
            - **Hybrid**  
            - **Tax-saving**  
            
            For each mutual fund, retrieve the following details (if available):  
            
            - **Fund Name**  
            - **Fund URL** (extract the href link associated with the fund name)  
            - **Category** (one of the categories mentioned above)  
            - **NAV (Net Asset Value)**  
            - **Expense Ratio**  
            - **AUM (Assets Under Management in Cr)**  
            - **Fund Manager(s)**  
            - **1-Year Return (%)**  
            - **3-Year Return (%)**  
            - **5-Year Return (%)**  
            - **Benchmark Index**  
            - **Risk Level**  
            - **Fund Objective**  
            - **Crisil Rank**  
            
            Return the extracted data in **JSON format** with the following structure:  
            
            ```json
            {
              "mutual_funds": [
                {
                  "fund_name": "XYZ Mutual Fund",
                  "fund_url": "https://www.moneycontrol.com/mf/xyz-fund",
                  "category": "Equity",
                  "nav": "₹123.45",
                  "expense_ratio": "1.25%",
                  "aum": "₹10,000 Cr",
                  "crisil_rank": "4",
                  "returns": {
                    "1_year": "12.5%",
                    "3_year": "18.2%",
                    "5_year": "22.3%"
                  },
                  "benchmark_index": "Nifty 50",
                  "risk_level": "High",
                  "fund_objective": "Long-term capital appreciation through equity investments."
                }
              ]
            }
            ```
            
            Ensure that:  
            - All fund categories are covered.  
            - The **Fund URL** is extracted from the hyperlink associated with the fund name.  
            - The **AUM (Cr)** is captured correctly.  
            - The **Crisil Rank** is included.  
            - If any information is unavailable, return `"N/A"`.  
            
            The final JSON output should be properly structured and formatted.
           """,
        chunk_token_threshold=500,  # Adjust based on your needs
        verbose=True
    )

    md_generator = DefaultMarkdownGenerator(
        content_filter=filter,
        options={"ignore_links": True}
    )

    # 4) Crawler run config: skip cache, use extraction
    run_conf = CrawlerRunConfig(
        markdown_generator=md_generator,
        # extraction_strategy=extraction,
        cache_mode=CacheMode.BYPASS,
    )

    async with AsyncWebCrawler(config=debug_browser) as crawler:
        result = await crawler.arun(
            url="https://www.moneycontrol.com/mutual-funds/find-fund/returns?&amc=IIFLMF,BIRMUTF,AOMF,AXMF,BFMF,ANZGRMUTF,BAXMF,BOBMUF,CANMUTF,DSPMLMF,EDELWMF,TEMMUFT,INDIABMF,HDFCMUTF,HMF,HSBCMUTF,PRUICM,ILFSMF,LIMF,ITIMF,JMMTFN,KMFLAMC,LICAMCL,MAHMF,MIRAEMF,MOMF,PEERMF,RELCAPM,NJMF,OBMF,PMF,PPFMF,ESCOMUF,QMF,SAMCOMF,SBIMUTF,SHMF,SUNMUTF,TATMUTF,TAUMUTF,TMF,UMF,UKBCMF,UTIMUTFD,YESMF,ZMF&invtype=Equity&category=Multi%20Cap%20Fund,Large%20Cap%20Fund,Large%20%26%20Mid%20Cap%20Fund,Mid%20Cap%20Fund,Small%20Cap%20Fund,ELSS,Dividend%20Yield%20Fund,Sectoral%2FThematic,Contra%20Fund,Focused%20Fund,Value%20Fund,Flexi%20Cap%20Fund&rank=1,2&MATURITY_TYPE=OPEN%20ENDED&SHOWAUM=Y&ASSETSIZE=100",
            config=run_conf
        )

        print(result.markdown)
        print('=======================================================================')


if __name__ == "__main__":
    asyncio.run(main())