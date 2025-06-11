import openpyxl

def load_startups_excel(filename):
    sheet = openpyxl.load_workbook(filename)["AISL2025"]
    return sheet

def create_results_file():    
    # Save the results to a new Excel file
    output_wb = openpyxl.Workbook()
    output_sheet = output_wb.active
    output_sheet.title = "AI Use Cases"

    return output_sheet, output_wb