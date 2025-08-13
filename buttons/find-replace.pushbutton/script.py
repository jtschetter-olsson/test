import clr
import math
from time import sleep
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('System')
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.ApplicationServices import Application
from System.Collections.Generic import List
from pyrevit import forms

ui_doc = __revit__.ActiveUIDocument  # Replace with your UI document instance
doc = ui_doc.Document

#Code Architecture
#steps
#1. get selected items
#2. create a sublist of groups
#3. create a sublist of components
#4. create a sublist of text notes
#5. create a sublist of tags
#6. find and replace each liste seperately

find_text = forms.ask_for_string(
    prompt='Find Text:',
    title='Find',
    default=''
)
replace_text = forms.ask_for_string(
    prompt='Replace Text:',
    title='Replace',
    default=''
)

def get_selected_ids():
    return ui_doc.Selection.GetElementIds()

def get_nongrouped_ids(full_list):
    nongrouped_ids = []
    grouped_ids = []

    for elem_id in full_list:
        element = doc.GetElement(elem_id)
        if isinstance(element, Group) or element.GroupId != ElementId.InvalidElementId:
            grouped_ids.append(elem_id)
        else:
            nongrouped_ids.append(elem_id)
    
    return nongrouped_ids, grouped_ids

def get_text_note_ids(full_list):
    text_note_ids = []

    for elem_id in full_list:
        element = doc.GetElement(elem_id)
        if isinstance(element, TextNote):
            text_note_ids.append(elem_id)
    
    return text_note_ids

def get_unique_groups(element_list):
    group_ids = set()  # Using a set to ensure uniqueness

    for elem_id in element_list:
        element = doc.GetElement(elem_id)
        if isinstance(element, Group):
            group_ids.add(elem_id)  # If the element itself is a group, add it
        elif element.GroupId != ElementId.InvalidElementId:
            group_ids.add(element.GroupId)  # If the element is inside a group, add the group's ID
    
    return list(group_ids)  # Convert set to list for final output


def find_and_replace_model_elements(element_ids, find, replace):  #Finds and replaces text within all parameters of the given elements.
    changes = 0
    with Transaction(doc, "Find and Replace Text") as t:
        t.Start()
        for elem_id in element_ids:
            element = doc.GetElement(elem_id)
            if element:
                for param in element.Parameters:
                    try:
                        if param:
                            if not param.IsReadOnly:
                                if param.StorageType == StorageType.String and (not param.AsString() == None):
                                    param_value = param.AsString()
                                    if param.Definition.Name != "Mark":
                                        if find in param_value:
                                            new_value = param_value.replace(find, replace)
                                            param.Set(new_value)
                                            changes = changes + 1
                    except:
                        continue
        t.Commit()
    return changes
'''
def get_non_grouped_element_ids():
    """
    Retrieves all element IDs in the model that are not part of a group.
    """
    collector = FilteredElementCollector(doc).WhereElementIsNotElementType()
    non_grouped_element_ids = [elem.Id for elem in collector if not elem.GroupId or elem.GroupId == ElementId.InvalidElementId]
    return non_grouped_element_ids
'''
'''
def get_electrical_equipment_ids():
    """
    Retrieves all electrical equipment element IDs in the model that are not part of a group.
    """
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType()
    electrical_equipment_ids = [elem.Id for elem in collector if not elem.GroupId or elem.GroupId == ElementId.InvalidElementId]
    return electrical_equipment_ids

def get_group_ids():
    """
    Retrieves all unique group IDs in the model.
    """
    collector = FilteredElementCollector(doc).WhereElementIsNotElementType()
    group_ids = {elem.GroupId for elem in collector if elem.GroupId and elem.GroupId != ElementId.InvalidElementId}
    return list(group_ids)

print(get_group_ids())

def get_elements_in_group(group_id):
    """
    Retrieves all element IDs that belong to a given group ID.
    """
    collector = FilteredElementCollector(doc).WhereElementIsNotElementType()
    group_elements = [elem.Id for elem in collector if elem.GroupId == group_id]
    return group_elements


def edit_group(group_id):
    """
    Edits elements within a group by:
    1. Storing locations of all instances.
    2. Deleting all but one instance.
    3. Ungrouping the remaining instance and deleting the group definition.
    4. Allowing modifications.
    5. Regrouping elements and renaming to the original name.
    6. Placing instances back at original locations.
    """
    t = Transaction(doc, "Edit Group")
    t.Start()
    
    # Get the group by ID
    group = doc.GetElement(group_id)
    if not isinstance(group, Group):
        t.RollBack()
        print("Invalid Group ID")
        return
    
    # Store group name and type ID
    group_type = group.GroupType
    group_name_param = group_type.LookupParameter("Name")
    group_name = group_name_param.AsString() if group_name_param else "Unnamed Group"
    group_type_id = group.GroupType.Id
    
    # Get all instances of the group
    group_instances = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_IOSModelGroups).WhereElementIsNotElementType()
    group_instances = [g for g in group_instances if g.GroupId == group_id]
    
    # Store locations of all instances
    group_locations = [g.Location.Point for g in group_instances]
    
    # Keep one instance, delete the rest
    #if len(group_instances) > 1:
    #    for i in range(1, len(group_instances)):  
    #        doc.Delete(group_instances[i].Id)
    
    # Ungroup the last remaining instance
    print(group_instances)
    last_group = group_instances[0]
    ungrouped_elements = last_group.UngroupMembers()
    
    # Delete the old group type
    doc.Delete(group_type_id)
    
    # Allow user to edit elements here
    print("Make your modifications now.")
    
    find_and_replace_text(ungrouped_elements, find_text, replace_text)
    
    # Regroup elements
    new_group = doc.Create.NewGroup(ungrouped_elements)
    
    # Rename the new group
    new_group.GroupType.Name = group_name
    
    # Replace instances
    for loc in group_locations[1:]:  # Skip the first instance since it's already placed
        doc.Create.PlaceGroup(loc, new_group.GroupType)
    
    t.Commit()
    print("Group edited successfully.")
'''

def find_and_replace_text_notes(full_list, find, replace):
    t = Transaction(doc, "Find and Replace TextNotes")
    t.Start()

    for elem_id in full_list:
        element = doc.GetElement(elem_id)
        if isinstance(element, TextNote):
            current_text = element.Text
            new_text = current_text.replace(find, replace)
            element.Text = new_text  # Updating the text
        
    t.Commit()

''' this contains an attempt at editing groups but it doen't work yet
def edit_groups(group_ids):
    with Transaction(doc, "Edit Groups") as t:
        t.Start()

        original_groups = []

        # Process each specified group ID
        for group_id in group_ids:
            group = doc.GetElement(group_id)
            if isinstance(group, Group):
                group_name = group.Name
                elements = group.GetMemberIds()
                instances = [g for g in group.GetDependentElements(None) if isinstance(doc.GetElement(g), Group)]
                
                locations = []
                for instance_id in instances:
                    instance = doc.GetElement(instance_id)
                    if instance and instance.Id != group_id and instance.Location:
                        locations.append(instance.Location)  # Store entire Location object
                        doc.Delete(instance.Id)  # Delete other instances

                original_groups.append({
                    "name": group_name,
                    "elements": elements,
                    "original_location": group.Location if group.Location else None,
                    "instance_locations": locations
                })

        # Ungroup and gather element IDs
        element_id_map = {}
        element_locations = {}  # Store original locations before ungrouping

        for group_data in original_groups:
            group = doc.GetElement(group_ids[original_groups.index(group_data)])
            if isinstance(group, Group):
                element_ids = group.GetMemberIds()
                element_id_map[group_data["name"]] = element_ids

                # Store original positions for each element before ungrouping
                element_locations[group_data["name"]] = {
                    elem_id: doc.GetElement(elem_id).Location.Point
                    for elem_id in element_ids if doc.GetElement(elem_id).Location
                }

                group.UngroupMembers()

        # ** Blank section for editing modify elements as needed **
        for group_name, element_ids in element_id_map.items():
            print(element_ids)  # Modify elements as needed
            ungrouped_list, not_used_grouped_list = get_nongrouped_ids(element_ids)
            text_ids = get_text_note_ids(initial_list)
            
            for elem_id in ungrouped_list:
                element = doc.GetElement(elem_id)
                if element:
                    for param in element.Parameters:
                        #try: find
                        if param:
                            if not param.IsReadOnly:
                                if param.StorageType == StorageType.String and (not param.AsString() == None):
                                    param_value = param.AsString()
                                    if find_text in param_value:
                                        new_value = param_value.replace(find_text, replace_text)
                                        param.Set(new_value)
                                        print("replacement made")
                        #except:
                        #    print("not replaced",param)
            
                for elem_id in text_ids:
                    element = doc.GetElement(elem_id)
                    if isinstance(element, TextNote):
                        current_text = element.Text
                        new_text = current_text.replace(find_text, replace_text)
                        element.Text = new_text  # Updating the text
            
            
            
            

        # Regroup and restore instances
        for group_data in original_groups:
            new_group = doc.Create.NewGroup(group_data["elements"])
            #new_group.GroupType.Name = group_data["name"]  # Renaming is not allowed

            # Restore original element positions
            for elem_id in group_data["elements"]:
                if elem_id in element_locations[group_data["name"]]:
                    original_position = element_locations[group_data["name"]][elem_id]
                    current_position = doc.GetElement(elem_id).Location.Point
                    translation_vector = original_position - current_position
                    ElementTransformUtils.MoveElement(doc, elem_id, translation_vector)

            # Restore additional instances
            for location in group_data["instance_locations"]:
                new_instance = new_group.Group()
                if isinstance(location, LocationPoint):
                    translation_vector = location.Point - new_instance.Location.Point
                    ElementTransformUtils.MoveElement(doc, new_instance.Id, translation_vector)

        t.Commit()
#    print(elements_in_group)
'''

initial_list = get_selected_ids()
ungrouped_list, grouped_list = get_nongrouped_ids(initial_list)
text_ids = get_text_note_ids(initial_list)
groups = get_unique_groups(grouped_list)

text_replacements = find_and_replace_model_elements(ungrouped_list, find_text, replace_text)
find_and_replace_text_notes(ungrouped_list, find_text, replace_text)


#print(initial_list)
#print(ungrouped_list)
#print(grouped_list)


print("Made {} changes, close this window".format(text_replacements))