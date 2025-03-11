import openpyxl

def load_startups_excel(startups_file):
    sheet = openpyxl.load_workbook(startups_file)["Sheet1"]
    return sheet

def create_results_file():    
    # Save the results to a new Excel file
    output_wb = openpyxl.Workbook()
    output_sheet = output_wb.active
    output_sheet.title = "AI Use Cases"

    return output_sheet, output_wb