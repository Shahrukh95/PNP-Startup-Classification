class Prompts():
    def __init__(self, total_use_cases):
        self.__total_use_cases = total_use_cases
        self.__use_english_prompt = f"Respond in English.\n\n"
    
    def shorten_page_content(self, full_page_content):
        shortened_content = f"{self.__use_english_prompt}Analyze the following page content and extract only the most relevant information about:\n1. What the company does and how they do it\n2. Any AI/ML technologies, capabilities, or features mentioned\n3. Their products, services, or solutions\n4. Their industry and target market\n\nRemove all other content including navigation menus, footers, contact information, legal text, and general website elements.\nIf the company name is mentioned, include it at the start.\nIf no relevant information is found, respond with 'No relevant content found'.\n\nPage Content:\n{full_page_content}"
        
        return shortened_content

    def startup_summary(self, pages_content_string):
        startup_summary = f"{self.__use_english_prompt}The following are the contents of some of the pages of a company's website.\n\nYour task is to generate a comprehensive description of the company with special focus on:\n1. What AI/ML technologies or capabilities they use or develop (e.g., machine learning, deep learning, NLP, computer vision, etc.)\n2. How AI/ML is integrated into their products/services (provide specific examples)\n3. Whether AI/ML is a core component of their offering and to what extent\n4. The specific industry and business model\n5. Any information about their development approach.\n\nStart the description with the name of the company if its provided in the contents. Be specific about AI/ML aspects - if they're not mentioned, explicitly state that. If AI/ML is mentioned but details are unclear, note this uncertainty.\n\nContents of the pages:\n{pages_content_string}"

        return startup_summary
    

    def get_important_links(self, page_links):
        important_links = f"The following are all the links available on the homepage of a company's website. Your task is to find the most relevant pages that would contain information about:\n1. What the company does and their core offerings\n2. Their AI/ML technologies and capabilities\n3. Their products, services, or solutions\n4. Their industry focus and business model\n\nSelect a maximum of {self.__total_use_cases - 1} links that are most likely to contain this information.\nExclude these types of pages:\n- Contact, About Us, Team, Careers\n- Legal, Privacy, Terms, Cookie Policy\n- Blog, News, Press Releases (unless they seem to contain product/technology information)\n- Login, Sign Up, Support pages\n\nReturn only a list of links, no other text. If no relevant links are found, return an empty list.\n\nLinks: {page_links}"
        
        return important_links

    def check_ai(self, full_description):
        ai_prompt = f"{self.__use_english_prompt}The following is a comprehensive description of a company. Your task is to evaluate if the company is an AI company or uses AI significantly in their operations. Consider these criteria:\n1. They develop AI/ML technologies as their core product\n2. They heavily integrate AI/ML into their main products/services\n3. They provide AI-powered solutions as their primary offering\n4. They use AI/ML as a significant component of their operations\n\nRespond with either 'Yes' or 'No'.\n- 'Yes' if they meet any of the above criteria (either primary AI focus or significant AI usage)\n- 'No' if they don't meet any criteria\n\nIf the information is unclear, respond with 'No'.\n\nThe comprehensive description of the company:\n{full_description}"
        
        return ai_prompt
