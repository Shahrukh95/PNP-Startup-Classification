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

    # Traverse the important links
    for link in links:
        try:
            web_scraper_obj.set_url(link)
            web_scraper_obj.load_page()
            
            # Check if page was loaded successfully
            if web_scraper_obj.get_body_text() == "Page Error - HTML Element not found" or web_scraper_obj.get_body_text() == "Page Error - Unexpected Error":
                print(f"Error accessing {link}: Page could not be loaded")
                pages_content.append("Page Error - Could not access page")
                continue
                
            page_content = web_scraper_obj.get_page_content(model_name)

            # Shorten the content
            shortened_content, input_tokens, output_tokens = content_shortener(content_shortener_model, prompts_obj, page_content)
            # Update token cost
            web_scraper_obj.set_token_cost(input_tokens, output_tokens, content_shortener_model)

            pages_content.append(shortened_content)
        except Exception as e:
            print(f"Error accessing {link}: {str(e)}")
            pages_content.append("Page Error - Could not access page")

    # Ensure we always return TOTAL_PAGE_CRAWLS number of items
    if len(pages_content) < TOTAL_PAGE_CRAWLS:
        pages_content.extend(["Page Error - No additional pages found"] * (TOTAL_PAGE_CRAWLS - len(pages_content)))
    elif len(pages_content) > TOTAL_PAGE_CRAWLS:
        pages_content = pages_content[:TOTAL_PAGE_CRAWLS]

    return pages_content


# Get the full description of the startup using the list of page contents
def get_full_description(web_scraper_obj, pages_content, model_name, prompts_obj):
    try:
        # Check if all pages had errors
        if all("Page Error" in content for content in pages_content):
            return "Page Error - Could not access any pages of the website"

        pages_content_string = "\n\n\n\n".join(pages_content)

        chat_description_obj = ChatGPT(model_name, prompts_obj.startup_summary(pages_content_string), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_description_response, input_tokens, output_tokens = chat_description_obj.chat_model()
        
        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, model_name)
        
        return chat_description_response

    except Exception as e:
        print(f"Error in generating full description: {str(e)}")
        return "Page Error - Error in combining descriptions"





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



def prompt_approach(model_name, content_shortener_model, reasoning_model, sheet, output_sheet, output_wb, output_filename, startup_name_col, start_index, stop_index):
    # Initialize the objects
    web_scraper_obj = WebScraper()
    prompts_obj = Prompts(TOTAL_PAGE_CRAWLS)

    # Process rows from start_index to stop_index
    for main_loop_index, row in enumerate(range(start_index, stop_index + 1), start=1):
        startup_name = sheet.cell(row=row, column=startup_name_col).value
        url = sheet.cell(row=row, column=4).value
        
        if pd.isnull(url):
            continue

        print(f"Row {row}: {startup_name}")

        try:
            # First set the URL (this cleans the URL), then get the cleaned URL
            web_scraper_obj.set_url(url)
            cleaned_url = web_scraper_obj.get_url()

            # Load page and check if it's accessible
            if not web_scraper_obj.load_page():
                print(f"Website not accessible for {startup_name}")
                save_to_excel_check(output_sheet, output_wb, startup_name, cleaned_url, 
                                  "Page Error - Website not accessible", "No", web_scraper_obj, output_filename)
                continue

            # Get redirected startup url (this will be for homepage)
            redirected_url = web_scraper_obj.get_redirected_url()
            
            # Use redirected URL if available, otherwise use cleaned URL
            final_url = redirected_url if redirected_url else cleaned_url

            # Get the content and links
            # page_content = web_scraper_obj.get_page_content(model_name)
            page_links = web_scraper_obj.get_page_links()

            # Use chat-gpt model to get relevant links with retry logic
            chat_links_response = get_relavant_links(web_scraper_obj, page_links, model_name, prompts_obj)
            retry_count = 0
            while not chat_links_response and retry_count < 10:  # Try up to 10 times
                print(f"No relevant links found. Retry attempt {retry_count + 1}")
                chat_links_response = get_relavant_links(web_scraper_obj, page_links, model_name, prompts_obj)
                retry_count += 1

            if not chat_links_response:
                print(f"No additional relevant links found for {startup_name} after {retry_count} attempts, proceeding with homepage only")
                chat_links_response = [web_scraper_obj.get_url()]  # Just use the homepage
            else:
                chat_links_response.insert(0, web_scraper_obj.get_url())
                print(f"All Important Links: {chat_links_response}")
            
            # Get the content of all the pages
            all_pages_content = get_pages_contents(web_scraper_obj, chat_links_response, model_name, content_shortener_model, prompts_obj)

            # Get the full description of the startup
            full_description = get_full_description(web_scraper_obj, all_pages_content, model_name, prompts_obj)

            # Check if it's an AI company
            chat_ai_obj = ChatGPT(reasoning_model, prompts_obj.check_ai(full_description), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
            chat_ai_response, input_tokens, output_tokens = chat_ai_obj.chat_model()
            # Update token cost
            web_scraper_obj.set_token_cost(input_tokens, output_tokens, reasoning_model)

            # Save results
            save_to_excel_check(output_sheet, output_wb, startup_name, final_url, full_description, chat_ai_response, web_scraper_obj, output_filename)

        except Exception as e:
            print(f"Error processing {startup_name}: {str(e)}")
            save_to_excel_check(output_sheet, output_wb, startup_name, url, 
                              "Page Error - Unexpected error occurred", "No", web_scraper_obj, output_filename)

        finally:
            # --- Finishing calls ---
            # Reset token cost, redirected URL
            web_scraper_obj.reset_token_cost()
            web_scraper_obj.reset_redirect_url()

            # Reset the web scraper object after every 8 rows
            if main_loop_index % 4 == 0:
                web_scraper_obj.quit_driver()
                web_scraper_obj = WebScraper()
                print(f"Resetting the selenium driver")


def save_to_excel_check(output_sheet, output_wb, startup_name, url, full_description, answer, web_scraper_obj, output_filename):
    headers = ["Startup Name", "Homepage URL", "Full Description", "Is AI Startup?", "Total Token Cost ($)"]
    # Write headers if not present
    if output_sheet.max_row < 2:
        output_sheet.append(headers)

    # Handle page errors
    if "Page Error" in full_description:
        answer = "Uncertain"  # Set to "Uncertain" for page errors
        token_cost = 0  # Set token cost to 0 for page errors
    else:
        token_cost = web_scraper_obj.get_token_cost()

    # Write data
    row = [startup_name, url, full_description, answer, token_cost]
    output_sheet.append(row)
    
    # Save after each row
    output_wb.save(output_filename)
    print(f"Saved results for {startup_name}")


def get_domain_from_email(email):
    if pd.isnull(email):
        return None
    try:
        return f"https://{email.split('@')[1]}"
    except:
        return None

def check_ai_company(model_name, reasoning_model, sheet, output_sheet, output_wb, output_filename):
    # Initialize the objects
    web_scraper_obj = WebScraper()

    for main_loop_index, row in enumerate(range(2, sheet.max_row + 1), start=1):
        startup_name = sheet.cell(row=row, column=1).value
        url = sheet.cell(row=row, column=2).value
        full_description = sheet.cell(row=row, column=13).value

        if pd.isnull(url):
            continue

        print(f"Row {row}: {startup_name}")

        prompts_obj = Prompts(TOTAL_PAGE_CRAWLS)
    
        chat_ai_obj = ChatGPT(reasoning_model, prompts_obj.check_ai(full_description), [], OpenAI(api_key=os.getenv("MY_KEY"), max_retries=5))
        chat_ai_response, input_tokens, output_tokens = chat_ai_obj.chat_model()

        # Update token cost
        web_scraper_obj.set_token_cost(input_tokens, output_tokens, reasoning_model)

        save_to_excel_check(output_sheet, output_wb, startup_name, url, full_description, chat_ai_response, web_scraper_obj, output_filename)

        # --- Finishing calls ---
        # Reset token cost
        web_scraper_obj.reset_token_cost()
        web_scraper_obj.reset_redirect_url()




if __name__ == "__main__":
    startups_file = "Philip.xlsx"
    sheet = load_startups_excel(startups_file)
    output_sheet, output_wb = create_results_file()
    output_filename = "PNP Results_output.xlsx"

    # Find the required columns
    email_col = None
    startup_name_col = None
    for col in range(1, sheet.max_column + 1):
        header = sheet.cell(row=1, column=col).value
        if header == 'Email':
            email_col = col
        elif header == "Startups's business name":
            startup_name_col = col

    if email_col is None:
        raise ValueError("Email column not found in the Excel file")
    if startup_name_col is None:
        raise ValueError("Startups's business name column not found in the Excel file")

    # Get start and stop indices
    start_index = int(input("Enter start row index (default 2): ") or "2")
    stop_index = int(input("Enter stop row index (default is last row): ") or str(sheet.max_row))
    
    # Validate indices
    if start_index < 2:
        start_index = 2
    if stop_index > sheet.max_row:
        stop_index = sheet.max_row
    if start_index > stop_index:
        raise ValueError("Start index cannot be greater than stop index")

    print(f"Processing rows from {start_index} to {stop_index}")

    # Extract URLs from email domains
    for row in range(start_index, stop_index + 1):
        email = sheet.cell(row=row, column=email_col).value
        domain_url = get_domain_from_email(email)
        if domain_url:
            sheet.cell(row=row, column=4).value = domain_url  # Store URL in column 4

    prompt_approach(model_name='chatgpt-4o-latest', content_shortener_model='chatgpt-4o-latest', reasoning_model='o3', 
                  sheet=sheet, output_sheet=output_sheet, output_wb=output_wb, output_filename=output_filename, 
                  startup_name_col=startup_name_col, start_index=start_index, stop_index=stop_index)

    
    


