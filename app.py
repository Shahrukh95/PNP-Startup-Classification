# Standard Library
import os
import re

# Third-Party Library
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

# Local Imports
from Classes import ChatGPT, Prompts, WebScraper, TextExtractor
from Utilities import *

# Load environment variables
load_dotenv()

# Constants
TOTAL_PAGE_CRAWLS = 7



def content_shortener(content_shortener_model, prompts_obj, page_content):
    chat_shorten_page_obj = ChatGPT(content_shortener_model, prompts_obj.shorten_page_content(page_content), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
    chat_shorten_page_response, input_tokens, output_tokens = chat_shorten_page_obj.chat_model()
    # print(f"Shortened Page Content: {chat_shorten_page_response}")

    return chat_shorten_page_response, input_tokens, output_tokens


# Get the content of all the pages and return a list
def get_pages_contents(web_scraper_obj, links, model_name, content_shortener_model, prompts_obj) -> list:
    pages_content = []
    
    if links is None:
        return ["Page Error - No Link Found"] * TOTAL_PAGE_CRAWLS

    try:
        # Traverse the important links
        for link in links:
            web_scraper_obj.set_url(link)
            web_scraper_obj.load_page()
            page_content = web_scraper_obj.get_page_content(model_name)

            # Shorten the content
            shortened_content, input_tokens, output_tokens = content_shortener(content_shortener_model, prompts_obj, page_content)
            # Update token cost
            web_scraper_obj.set_token_cost(input_tokens, output_tokens, content_shortener_model)

            pages_content.append(shortened_content)

    
    except Exception as e:
        # Return error message only
        pages_content = ["Page Error - Error in traversing link"] * TOTAL_PAGE_CRAWLS

    return pages_content


# Get the full description of the startup using the list of page contents
def get_full_description(web_scraper_obj, pages_content, model_name, prompts_obj):
    try:
        pages_content_string = "\n\n\n\n".join(pages_content)

        chat_description_obj = ChatGPT(model_name, prompts_obj.startup_summary(pages_content_string), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_description_response, input_tokens, output_tokens = chat_description_obj.chat_model()
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
        

    except Exception as e:
        chat_description_response = "Page Error - Error in combining descriptions"


    return chat_description_response





def save_to_excel(output_sheet, output_wb, startup_name, cleaned_url, redirected_url, web_scraper_obj, all_links, all_pages_content, full_description, all_details_dict, output_filename):
    headers = ["Startup Name", "Homepage URL", "Redirected URL (for logging only)", "Additional URLs"] + [f"Page {i+1}" for i in range(TOTAL_PAGE_CRAWLS)] + ["Full Description" ,"Short Description", "Focus Type", "Industry", "Revenue Models (Top 3)" ,"Total Token Cost ($)"]
    # Write headers if not present
    if output_sheet.max_row < 2:
        output_sheet.append(headers)

    # When all_links is None
    urls_string = ", ".join(all_links) if all_links is not None else ""

    # Ensure all_pages_content is padded to match the maximum number of columns
    all_pages_content_padded = all_pages_content[:TOTAL_PAGE_CRAWLS] + [""] * (TOTAL_PAGE_CRAWLS - len(all_pages_content))

    # Write data
    row = [startup_name, cleaned_url, redirected_url, urls_string] + all_pages_content_padded[:TOTAL_PAGE_CRAWLS] + [full_description, all_details_dict['short_description'],all_details_dict['focus_type'], all_details_dict['industry'], all_details_dict['revenue_model'], web_scraper_obj.get_token_cost()]

    output_sheet.append(row)
    output_wb.save(f"{output_filename}")  


def claude_api(prompt):
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_KEY")
    )
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=8192,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    message_content = message.content[0].text  # Extracts the actual message text
    input_tokens = message.usage.input_tokens  # Extracts input tokens
    output_tokens = message.usage.output_tokens  # Extracts output tokens

    return message_content, input_tokens, output_tokens


def get_relavant_links(web_scraper_obj, page_links, model_name, prompts_obj):
    chat_links_obj = ChatGPT(model_name, prompts_obj.get_important_links(page_links), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
    chat_links_response, input_tokens, output_tokens = chat_links_obj.chat_model()
    chat_links_response = extract_list(chat_links_response)
    # Update token cost
    web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)

    return chat_links_response



def prompt_approach(model_name, content_shortener_model, reasoning_model, sheet, output_sheet, output_wb, output_filename):
    # Initialize the objects
    web_scraper_obj = WebScraper()

    # sheet.max_row + 1
    for row in range(2, sheet.max_row + 1):
        startup_name = sheet.cell(row=row, column=2).value
        url = sheet.cell(row=row, column=4).value
        
        if pd.isnull(url):
            continue

        prompts_obj = Prompts(TOTAL_PAGE_CRAWLS)

        # First set the URL (this cleans the URL), then get the cleaned URL
        web_scraper_obj.set_url(url)
        cleaned_url = web_scraper_obj.get_url()
        print(f"Row {row}: {startup_name}")

        # Load page
        web_scraper_obj.load_page()
        # Get redirected startup url (this will be for homepage)
        redirected_url = web_scraper_obj.get_redirected_url()

        # Get the content and links
        # page_content = web_scraper_obj.get_page_content(model_name)
        page_links = web_scraper_obj.get_page_links()

        # Use chat-gpt model to get relavant links (seems to be better than claude for this task)
        chat_links_response = get_relavant_links(web_scraper_obj, page_links, model_name, prompts_obj)
        for i in range(0,6):
            if not chat_links_response:
                print("No relavant links found. Trying again.")
                chat_links_response = get_relavant_links(web_scraper_obj, page_links, model_name, prompts_obj)


        chat_links_response.insert(0, web_scraper_obj.get_url())
        # print(f"All Important Links: {chat_links_response}")
        
        # Get the content of all the pages
        all_pages_content = get_pages_contents(web_scraper_obj, chat_links_response, model_name, content_shortener_model, prompts_obj)
        # print(f"All Pages Content: {all_pages_content}\n\n\n\n")

        # Get the full description of the startup
        full_description = get_full_description(web_scraper_obj, all_pages_content, model_name, prompts_obj)
        # print(f"Full Description: {full_description}\n\n\n\n")
        


        # Use chat-gpt to get all details
        chat_all_deatils_obj = ChatGPT(reasoning_model, prompts_obj.get_all_details(full_description), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_all_details_response, input_tokens, output_tokens = chat_all_deatils_obj.chat_model_reasoning()
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, reasoning_model)

        
        # #use claude to get all details
        # claude_all_details_response, input_tokens, output_tokens = claude_api(prompts_obj.get_all_details(full_description))
        # # Update token cost
        # web_scraper_obj.set_token_cost(input_tokens, output_tokens, "claude-3-7-sonnet-20250219")



        # Regular expression to extract key-value pairs from the JSON (may not be exactly valid JSON)
        json_matches = re.findall(r'"(.*?)":\s*"(.*?)"', chat_all_details_response, re.DOTALL)
        all_details_dict = dict(json_matches)

        
        save_to_excel(output_sheet, output_wb, startup_name, cleaned_url, redirected_url, web_scraper_obj, chat_links_response, all_pages_content, full_description, all_details_dict, output_filename)

        # --- Finishing calls ---
        # Reset token cost, redirected URL
        web_scraper_obj.reset_token_cost()
        web_scraper_obj.reset_redirect_url()




if __name__ == "__main__":
    startups_file = "robotics_companies.xlsx"
    sheet = load_startups_excel(startups_file)

    output_sheet, output_wb = create_results_file()

    output_filename = "robotics_output.xlsx"

    prompt_approach(model_name='chatgpt-4o-latest', content_shortener_model='gpt-4o-mini', reasoning_model='o3-mini', sheet=sheet, output_sheet=output_sheet, output_wb=output_wb, output_filename=output_filename)
    


