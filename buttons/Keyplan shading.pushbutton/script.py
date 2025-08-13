from pyrevit import revit, DB, forms
import re

ui_doc = __revit__.ActiveUIDocument
doc = ui_doc.Document

def get_segment_from_sheet_name(sheet_name):
    # Match 'SEGMENT {X}' at the end of the name
    #print(sheet_name)
    #print(sheet_name.split(" - "))
    #print(sheet_name.split(" - ")[-1].split(" ")[1])
    return sheet_name.split(" - ")[-1].split(" ")[1]

def get_titleblock_instance(sheet):
    # Get all title block instances on the sheet
    collector = DB.FilteredElementCollector(doc, sheet.Id).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).WhereElementIsNotElementType()
    for tb in collector:
        return tb  # Assume only one title block per sheet
    return None

def set_keyplan_parameters(titleblock, segment_value):
    # Find all parameters that start with 'Keyplan Area'
    for param in titleblock.Parameters:
        if param.Definition.Name.startswith("Keyplan Area"):
            # Extract the segment from the parameter name
            area = param.Definition.Name.split(" ")[-1]
            #print(area)
            if area:
                #print("made it here2")
                if area == segment_value:
                    param.Set(1)  # Yes
                    #print("Set Keyplan Area {} to Yes".format(area))
                elif area == "OVERALL":
                    param.Set(1)
                else:
                    param.Set(0)  # No
                    #print("Set Keyplan Area {} to No".format(area))

selected_sheets = [doc.GetElement(elId) for elId in ui_doc.Selection.GetElementIds() if isinstance(doc.GetElement(elId), DB.ViewSheet)]

if not selected_sheets:
    forms.alert("No sheets selected.", exitscript=True)

with revit.Transaction("Update Keyplan Areas"):
    for sheet in selected_sheets:
        try:
            segment = get_segment_from_sheet_name(sheet.Name)
            if segment:
                titleblock = get_titleblock_instance(sheet)
                if titleblock:
                    set_keyplan_parameters(titleblock, segment)
                else:
                    print("No title block found on sheet: {}".format(sheet.Name))
        except:
            print("error processing sheet: {}".format(sheet.Name))




