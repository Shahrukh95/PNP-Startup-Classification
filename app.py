# Standard Library
import os

import time


# Third-Party Library
import pandas as pd


from dotenv import load_dotenv
from openai import OpenAI

# Local Imports
from Classes import ChatGPT, Prompts, WebScraper, TextExtractor

# Load environment variables
load_dotenv()

# Constants
TOTAL_PAGE_CRAWLS = 4



def content_shortener(content_shortener_model, prompts_obj, page_content):
    chat_shorten_page_obj = ChatGPT(content_shortener_model, prompts_obj.shorten_page_content(page_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
    chat_shorten_page_response, input_tokens, output_tokens = chat_shorten_page_obj.chat_model()
    # print(f"Shortened Page Content: {chat_shorten_page_response}")

    return chat_shorten_page_response, input_tokens, output_tokens


def traverse_links(web_scraper_obj, links, model_name, content_shortener_model, ai_use_cases, prompts_obj):
    if links is None:  # Check if links is None
        return ai_use_cases
    
    try:
        # Traverse the important links
        for link in links:
            web_scraper_obj.set_url(link)
            # print(f"Going into relavant link: {link}")
            web_scraper_obj.load_page()
            page_content = web_scraper_obj.get_page_content(model_name)

            # Shorten the content
            shortened_content, input_tokens, output_tokens = content_shortener(content_shortener_model, prompts_obj, page_content)
            # Update token cost
            web_scraper_obj.set_token_cost(input_tokens, output_tokens, content_shortener_model)


            chat_use_case_obj = ChatGPT(model_name, prompts_obj.update_startup_summary(f"\n\n".join(ai_use_cases), shortened_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
            chat_use_case_response, input_tokens, output_tokens = chat_use_case_obj.chat_model()

            # Update token cost
            web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
            
            ai_use_cases.append(chat_use_case_response)
    
    except Exception as e:
        # Return error message only
        ai_use_cases.append(f"Page Error - Error in traversing links")

    return ai_use_cases



def save_to_excel(output_sheet, output_wb, startup_name, raw_homepage_url, web_scraper_obj, additional_urls, all_ai_use_cases, use_cases_combined, output_filename):
    headers = ["Startup Name", "Homepage URL", "Redirected URL (for logging only)", "Additional URLs"] + [f"Page {i+1}" for i in range(TOTAL_PAGE_CRAWLS)] + ["Combined AI Use Cases" , "Total Token Cost ($)"]
    # Write headers if not present
    if output_sheet.max_row < 2:
        output_sheet.append(headers)

    # When additional_urls is None
    urls_string = ", ".join(additional_urls) if additional_urls is not None else ""

    # Ensure all_ai_use_cases is padded to match the maximum number of columns
    use_cases_padded = all_ai_use_cases + [""] * (TOTAL_PAGE_CRAWLS - len(all_ai_use_cases))

    # Write data
    row = [startup_name, raw_homepage_url, web_scraper_obj.get_redirected_url(), urls_string] + use_cases_padded[:TOTAL_PAGE_CRAWLS] + [use_cases_combined, web_scraper_obj.get_token_cost()]
    output_sheet.append(row)

    output_wb.save(f"{output_filename}")  



def prompt_approach(model_name, classification_model_name, content_shortener_model, sheet, output_sheet, output_wb, output_filename):
    # Initialize the objects
    web_scraper_obj = WebScraper()

    # sheet.max_row + 1
    for row in range(2, sheet.max_row + 1):
        url = sheet.cell(row=row, column=2).value
        startup_name = sheet.cell(row=row, column=1).value

        if pd.isnull(url):
            continue

        prompts_obj = Prompts(TOTAL_PAGE_CRAWLS)
        ai_use_cases = []

        # First set the URL (this cleans the URL), then get the cleaned URL
        web_scraper_obj.set_url(url)
        raw_homepage_url = web_scraper_obj.get_url()
        # print(f"URL: {web_scraper_obj.get_url()}")
        time.sleep(1)
        print(f"Row {row}: {startup_name}")
        
        # Load page, get the content and links
        web_scraper_obj.load_page()

        # Get the content and links
        page_content = web_scraper_obj.get_page_content(model_name)
        page_links = web_scraper_obj.get_page_links()

        # Use chat model to get relavant links
        chat_links_obj = ChatGPT(model_name, prompts_obj.get_important_links(page_links), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_links_response, input_tokens, output_tokens = chat_links_obj.chat_model()
        chat_links_response = extract_list(chat_links_response)

        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
        
        # print(f"Important Links: {chat_links_response}")

        # Use a smaller model to remove cookie and unrelated text - reduces chance of classification error
        shortened_content, input_tokens, output_tokens = content_shortener(content_shortener_model, prompts_obj, page_content)
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, content_shortener_model)
        # print(f"Shortened Content: {shortened_content}")


        # Use chat model to get the use cases
        chat_use_cases_obj = ChatGPT(model_name, prompts_obj.startup_summary(startup_name, shortened_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_use_cases_response, input_tokens, output_tokens = chat_use_cases_obj.chat_model()
        # print(f"AI Use Cases: {chat_use_cases_response}")
        ai_use_cases.append(chat_use_cases_response)

        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)

        # Update the startup use cases with the important links
        # Also return the updated token count
        all_ai_use_cases = traverse_links(web_scraper_obj, chat_links_response, model_name, content_shortener_model, ai_use_cases, prompts_obj)


        # Process all the AI use cases into a single string
        use_cases_combiner_obj = ChatGPT(model_name, prompts_obj.combine_use_cases(all_ai_use_cases), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        use_cases_combined, input_tokens, output_tokens = use_cases_combiner_obj.chat_model()
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)

        save_to_excel(output_sheet, output_wb, startup_name, raw_homepage_url, web_scraper_obj, chat_links_response, all_ai_use_cases, use_cases_combined, output_filename)

        # --- Finishing calls ---
        # Reset token cost, redirected URL
        web_scraper_obj.reset_token_cost()
        web_scraper_obj.reset_redirect_url()


if __name__ == "__main__":
    startups_file = "Local Input/local-startups-input.xlsx"
    sheet = load_startups_excel(startups_file)

    output_sheet, output_wb = create_results_file()

    output_filename = "Local Output/Results.xlsx"

    prompt_approach(model_name='chatgpt-4o-latest', classification_model_name='chatgpt-4o-latest', content_shortener_model='gpt-4o-mini', sheet=sheet, output_sheet=output_sheet, output_wb=output_wb, output_filename=output_filename)
    


