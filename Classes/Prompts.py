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
        industries_list = "Agriculture, forestry and fishing\nManufacturing\nElectricity, gas, steam and air conditioning supply\nWater supply; sewerage, waste management and remediation activities\nConstruction\nWholesale and retail trade; repair of motor vehicles\nTransportation and storage\nAccommodation and food service activities\nInformation and communication technologies\nFinancial and insurance activities\nReal estate activities\nProfessional, scientific and technical activities\nAdministrative and support service activities\nPublic administration and defense and compulsory social security\nEducation\nHuman health and social work activities\nArts, entertainment and recreation\nOther service activities\nCross Industry\nAerospace\nRetail & E-commerce\nOther"

        revenue_models = "Direct Sales\nE-commerce Sales\nRetail Sales\nCommission Revenue Model\nAdvertising Revenue Model\nSubscription Revenue Model\nSoftware as a Service (SaaS)\nLicensing Revenue Model\nFreemium with Upsell\nProfessional Services\nTraining & Workshops\nCrowdfunding\nGrants & Subsidies\nWhite & Private Labeling\nArbitrage Revenue Model"


        all_details = f"Respond only in JSON format. The following is a comprehensive description of a company. Your task is to find the following information from it:\n\n1. A moderate length description of the company focusing on what the company is doing and how it is doing it. Start this description by naming the company.\n\n2. Is their primary focus more on 'Software' or 'Hardware'?\n\n3. What is the specific industry this company operates in? Choose only one from this list:\n{industries_list}\n\n4. What is most likely their revenue model? Choose a maximum of 3 from the following list:\n{revenue_models}\n\n\n\nThe values in the JSON should be short_description, focus_type, industry, revenue_model (keep this as a string).\n\nThe comprehensive description of the company:\n{full_description}"
        
        return all_details


