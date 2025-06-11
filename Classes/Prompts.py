class Prompts():
    def __init__(self, total_use_cases):
        self.__total_use_cases = total_use_cases
        self.__use_english_prompt = f"Respond in English.\n\n"
    
    def shorten_page_content(self, full_page_content):
        shortened_content = f"{self.__use_english_prompt}Remove any content from the following that doesn't directly describe what the company does and how it does it. Mention the name of the company if its available in the content.\n\nPage Content:\n{full_page_content}"
        
        return shortened_content

    def startup_summary(self, pages_content_string):
        startup_summary = f"{self.__use_english_prompt}The following are the contents of some of the pages of a company's website.\n\nYour task is to generate a comprehensive description of the company mentioning what the company is doing and how it is doing it. This should also inlcude information about is their focus more on software or hardware?, what is the specific industry this company operates in (not just by software/hardware, but in a more general sense), and what is most likely their revenue model. You can also use your own knowledge to help with this task. Do not guess the description, only use the contents and your own knowledge to generate the description. Start the description with the name of the company if its provided in the contents.\n\nContents of the pages:\n{pages_content_string}"

        return startup_summary
    

    def get_important_links(self, page_links):
        important_links = f"The following are all the links available on the homepage of a company's website. Use your best judgement to find a maximum of {self.__total_use_cases - 1} links which when opened will have the most relavant content about what the company does and how it does it. Also include links that could tell which industry the company operates in, and about their revenue model. This should not include any pages that are similar to contact us, about us, pricing, legal, impressum, privacy, terms-and-conditions or cookie related pages. Return only a list of links and no other text. If you can not find any relavant links, then return an empty list only.\n\nLinks: {page_links}"
        
        return important_links

    def check_ai(self, full_description):
        ai_prompt = f"{self.__use_english_prompt}The following is a comprehensive description of a company. Your task is to find out if the company is primarily an AI company or heavily uses AI in their core products/services. A company is considered an AI company if:\n1. They develop AI/ML technologies as their core product\n2. They heavily integrate AI/ML into their main products/services\n3. They provide AI-powered solutions as their primary offering\n\nRespond with either 'Yes' or 'No'.\n\nThe comprehensive description of the company:\n{full_description}"
        
        return ai_prompt
