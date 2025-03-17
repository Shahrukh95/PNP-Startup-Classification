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
        important_links = f"The following are all the links available on the homepage of a company's website. Use your best judgement to find a maximum of {self.__total_use_cases - 1} links which when opened will have the most relavant content about what the company does and how it does it. Also include links that could tell which industry the company operates in, and about their revenue model. This should not include any pages that are similar to contact us, about us, pricing, impressum, privacy, terms-and-conditions or cookie related pages. Return only a list of links and no other text. If you can not find any relavant links, then return an empty list only.\n\nLinks: {page_links}"
        
        return important_links
    

    def get_all_details(self, full_description):
        
        # Robotics is purposely left out
        industries_list = f"Agriculture\nForestry\nFishing\nManufacturing\nAutomotive\nWater Supply\nFood Services\nEnergy & Environment\nWaste Management\nConstruction\nRetail Trade and E-commerce\nRepair Services\nLogistics and Supply Chain Management\nHospitality & Tourism\nTelecommunications\nFinance, Investment & Venture Capital\nInsurance\nReal Estate\nPublic Services and Administration\nDefense\nSocial Services\nEducation\nHealth\nArts, Entertainment and Recreation\nConsulting Services\nMining and Quarrying\nBiotechnology & Life Sciences\nMedia & Publishing\nCybersecurity\nAviation\nSpace Exploration\nNanotechnology\nPetrochemical\nLegal Services\nHuman Resources\nSports\nGaming & Esports\nEvent Management\nFashion & Apparel\nCrowdfunding & Alternative Finance\nSpiritual & Religious Services\nAnimal Care & Veterinary Services\nHome Services & Maintenance\nOther"

        revenue_models = f"Product Based\nService Based\nSubscriptions\nCommissions\nLicensing\nAdvertising\nAffiliate\nFreemium\nAsset Sharing\nTraining & Workshops\nCrowdfunding\nGrants & Subsidies\nWhite & Private Labeling"

        all_details = f"Respond only in JSON format. The following is a comprehensive description of a company. Your task is to find the following information from it:\n\n1. A summarized description of the company but covering all aspects mentioned in the comprehensive one (except funding and revenues). Start this description by naming the company.\n2. Is their primary focus more on 'Software' or 'Hardware'?\n3. What are the primary industries this company operates in? Choose a maximum of 3 from **this list only**, in descending preferential order:\n{industries_list}\n\n4. What is most likely their revenue model? Choose a maximum of 3 from **this list only**, in descending preferential order:\n{revenue_models}\n\n\n\nThe values in the JSON should be short_description, focus_type, industry (keep this as a string), revenue_model (keep this as a string too).\n\nThe comprehensive description of the company:\n{full_description}"
        
        return all_details



    def check_robotics(self, full_description):
        robotics_prompt = f"{self.__use_english_prompt}The following is a comprehensive description of a company. Your task is to find out if the company is related to Robotics. Respond with either 'Yes' or 'No'.\n\nThe comprehensive description of the company:\n{full_description}"
        
        return robotics_prompt
