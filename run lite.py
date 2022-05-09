import PySimpleGUI as sg
import json, datetime, os

# layouts
title_text = ("_ 20")
listbox_text = ("_ 12")

sg.theme("DarkGrey9")

world_info = {
    "name":"New Entry",
    "keys":[],
    "entry":"",
    "novelai": {
        "enabled": True,
        "search range":1000,
        "force activation":False,
        "key-relative insertion":False,
        "cascading activation":False,
        "prefix":"",
        "suffix":"\n",
        "token budget":2048,
        "reserved tokens":0,
        "insertion order":400,
        "insertion position":-1,
        "trim direction":"trimBottom",
        "max trim type":"sentence",
        "insertion type":"newline",
        "lorebook bias":[]
    },
    "meta": {
        "source": "This Program",
        "date created": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "date updated": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    }
}

folders_layout = [[sg.Text("Folders", font = title_text, expand_x = True, justification = "center")],
[sg.Listbox([], font = listbox_text, k = "-FOLDERLIST-", enable_events = True, select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, expand_x = True, expand_y = True)],
[sg.Button("New folder", k = "-ADDFOLDER-", expand_x = True), sg.Button("Rename Folder", k = "-RENAMEFOLDER-", expand_x = True), sg.Button("Delete Folder", k = "-DELETEFOLDER-",expand_x = True)]]

entries_layout = [[sg.Text("Entries", font = title_text, expand_x = True, justification = "center")],
[sg.Listbox(["No entries"], font = listbox_text, k = "-ENTRYLIST-", select_mode = sg.LISTBOX_SELECT_MODE_EXTENDED, enable_events = True, expand_x = True, expand_y = True)],
[sg.Button("New Entry", k = "-ADDENTRY-", expand_x = True), sg.Button("Move Selected", k = "-MOVEENTRY-", expand_x = True), sg.Button("Delete Selected", k = "-DELETEENTRY-", expand_x = True)]]

extras_layout = [[sg.Text("Extras", font = title_text, expand_x = True)],
[sg.Text("Source: (none)", expand_x = True, k = "-SOURCE-")],
[sg.Text("Date Added: (none)", expand_x = True, k = "-DATEADDED-")],
[sg.Text("Last Edited: (none)", expand_x = True, k = "-DATEEDITED-")],
[sg.Button("NovelAI LB Settings", k = "-NAISETTINGS-", expand_x = True)]]

export_layout = [[sg.Text("Export", font = title_text)],
[sg.Button("NAI .lorebook", k = "-EXPORTLB-")],
[sg.Button("AID .json", k = "-AIDJSON-")],
[sg.Button("Direct to AID", k = "-AIDAPI-", disabled = True)],
[sg.Button("Save to Library", k = "-SAVEENTRY-", expand_x = True)]]

details_layout = [[sg.Text("Details", font = title_text, expand_x = True, justification = "center")],
[sg.Text("Name")],
[sg.Input("", k = "-NAME-", expand_x = True)],
[sg.Text("Keys (Seperate with commas)")],
[sg.Input("", k = "-KEYS-", expand_x = True)],
[sg.Text("Entry - 0 tokens", k = "-TKNCOUNT-")],
[sg.Multiline("", k = "-ENTRY-", enable_events = True, expand_x = True, expand_y = True)],
[sg.Column(extras_layout, element_justification = "left", expand_x = True, k = "-META-"), sg.Column(export_layout, element_justification = "right", expand_x = True)]]

main_layout = [[sg.Column(folders_layout, expand_x = True, expand_y = True, k = "-FOLDERS-"), sg.Column(entries_layout, expand_x = True, expand_y = True, k = "-ENTRIES-"), sg.Column(details_layout, expand_x = True, expand_y = True, k = "-DETAILS-")]]

# utility functions
def keys_to_string(keys:list):
    keystr = ""
    for k in range(len(keys)):
        keystr += f"{keys[k]},"
    keystr = keystr.rstrip(",")
    return keystr

def string_to_keys(string:str):
    keys = string.split(",")
    return keys

def count_tokens(text:str):
    # estimation only in lite version
    if text:
        return int(len(text)/4.5)
    else:
        return 0

# library functions
def load_library():
    if os.path.isfile("library.json"):
        with open("library.json", "r") as f:
            lib = json.load(f)
    else:
        sg.Popup("No library.json found, starting with blank", title = "No library found")
        lib = {"No Folder":[]}
    return lib

def save_library():
    with open("library.json", "w+") as f:
        json.dump(library, f)

def remove_folder_by_name(name):
    if name == "No Folder": # not allowing deletion of No Folder, that would break things
        sg.Popup('Can\'t delete "No Folder"', title = "Error deleting folder")
    else:
        # ask to move content to "No Folder" first, if there's any
        if len(library[name]) > 0:
            keep = sg.popup_yes_no('Keep content from folder? It will be moved to "No Folder"')
            if keep == "Yes":
                indexes = []
                for i in range(len(library[name])):
                    indexes.append(i)
                move_entries_to_folder(indexes, name, "No Folder")
        library.pop(name) # delete folder

def add_folder_by_name(folder_name:str):
    # add folder to library if there isn't already one with the same name
    if folder_name in library:
        sg.Popup("Can't have two folders with the same name", title = "Error adding folder")
        return False
    else:
        library.update({folder_name:[]})
        return True

def rename_folder(folder_name:str, new_folder_name:str):
    if new_folder_name in library:
        sg.Popup("Can't have two folders with the same name", title = "Error renaming folder")
    elif folder_name == "No Folder":
        sg.Popup('Can\'t rename from or to "No Folder"', title = "Error renaming folder")
    else:
        # provided it's a valid folder name, create a new folder with the contents of the old one as we remove the old one
        library.update({new_folder_name:library.pop(folder_name)})

def delete_entries_from_folder(indexes:list, folder:str):
    # reverse, so i don't start deleting the wrong indexes because later ones would shift position if i deleted earlier ones first
    indexes.reverse()
    # and pop each one
    for i in range(len(indexes)):
        library[folder].pop(indexes[i])

def move_entries_to_folder(indexes:list, source_folder:str, destination_folder:str):
    # copy each entry from source folder to destination
    for i in range(len(indexes)):
        library[destination_folder].append(library[source_folder][indexes[i]].copy())
    # then delete the originals
    delete_entries_from_folder(indexes, source_folder)

def get_entry_names(folder:dict):
    entrylist = []
    for entry in range(len(library[folder])):
        entrylist.append(f"{library[folder][entry]['name']} ({keys_to_string(library[folder][entry]['keys'])})")
    return entrylist

def get_main_entry_details(folder:str, index:int):
    return library[folder][index]

def save_entry_to_index(entry:dict, index:int, folder:str):
    library[folder][index] = entry

def add_new_entry_to_folder(entry:dict, folder:str):
    library[folder].append(entry)

def import_json_entries_to_folder(filepath:str, folder:str):
    with open(filepath, "r") as f:
        json_entries = json.load(f) # loads the list of WI from worldInfo.json
    imported_wi = []
    for i in range(len(json_entries)):
        # copy WI template and edit as appropriate with importing info
        imported_wi.append(world_info.copy())
        # add name as name if there is one...
        if json_entries[i]['name']:
            imported_wi[i]['name'] = json_entries[i]['name']
        else: # ...otherwise, substitute in the first key
            imported_wi[i]['name'] = json_entries[i]['keys'].split(",")[0]
        # add keys if there are any...
        if json_entries[i]['keys']:
            imported_wi[i]['keys'] = json_entries[i]['keys'].split(",")
        else: # ...otherwise, substitute in the name
            imported_wi[i]['keys'] = [str(json_entries[i]['name'])]
        # add entry as entry if there is one...
        if json_entries[i]['entry']:
            imported_wi[i]['entry'] = json_entries[i]['entry']
        else: # ...otherwise, substitute in the description
            imported_wi[i]['entry'] = str(json_entries[i]['description'])
        # metadata
        imported_wi[i]['meta']['date created'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        imported_wi[i]['meta']['date updated'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        imported_wi[i]['meta']['source'] = "AI Dungeon"
        add_new_entry_to_folder(imported_wi[i], folder)
    sg.popup(f"Imported {len(imported_wi)} entries to folder: {folder}")

def import_lorebook_entries_to_folder(filepath:str, folder:str):
    with open(filepath, "r") as f:
        lorebook = json.load(f) # loads the list of LB entries from novelai .lorebook
        lorebook = lorebook['entries']
    imported_wi = []
    for i in range(len(lorebook)):
        # copy WI template and edit as appropriate with importing info
        imported_wi.append(world_info.copy())
        # get the details from the right place in the entry, converting to the library's universal format
        imported_wi[i]['name'] = lorebook[i]['displayName']
        imported_wi[i]['keys'] = lorebook[i]['keys']
        imported_wi[i]['entry'] = lorebook[i]['text']
        # the novelai specific ones all in one go
        imported_wi[i]['novelai'] = {
        "enabled":lorebook[i]['enabled'],
        "search range":lorebook[i]['searchRange'],
        "force activation":lorebook[i]['forceActivation'],
        "key-relative insertion":lorebook[i]['keyRelative'],
        "cascading activation":lorebook[i]['nonStoryActivatable'],
        "prefix":lorebook[i]['contextConfig']['prefix'],
        "suffix":lorebook[i]['contextConfig']['suffix'],
        "token budget":lorebook[i]['contextConfig']['tokenBudget'],
        "reserved tokens":lorebook[i]['contextConfig']['reservedTokens'],
        "insertion order":lorebook[i]['contextConfig']['budgetPriority'],
        "insertion position":lorebook[i]['contextConfig']['insertionPosition'],
        "trim direction":lorebook[i]['contextConfig']['trimDirection'],
        "max trim type":lorebook[i]['contextConfig']['maximumTrimType'],
        "insertion type":lorebook[i]['contextConfig']['insertionType'],
        "lorebook bias":lorebook[i]['loreBiasGroups']
    }
        # metadata
        imported_wi[i]['meta']['date created'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        imported_wi[i]['meta']['date updated'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        imported_wi[i]['meta']['source'] = "NovelAI"
        add_new_entry_to_folder(imported_wi[i], folder)
    sg.popup(f"Imported {len(imported_wi)} entries to folder: {folder}")

def export_entries_to_json(indexes:list, folder:str):
    json_output = []
    # convert all entries to the right format, add to json_output
    for index in range(len(indexes)):
        entry = get_main_entry_details(folder, indexes[index])
        #use WI .json format, fill in the blanks
        json_output.append({
            "description": None,
            "name": entry['name'],
            "genre": None,
            "tags": [],
            "type": "Active",
            "attributes": None,
            "keys": keys_to_string(entry['keys']),
            "entry": entry['entry']})
    # save to worldInfo.json
    with open("worldInfo.json", "w+") as f:
        json.dump(json_output, f)
    sg.popup(f"Saved {len(indexes)} entries to worldInfo.json")

def export_entries_to_lorebook(indexes:list, folder:str):
    # set up basic LB file structure
    lorebook_output = {
    "lorebookVersion": 4,
    "entries": [],
    "settings": {"orderByKeyLocations": False},
    "categories": []
    }
    # convert entries to the right format, add to lorebook_output
    for index in range(len(indexes)):
        entry = get_main_entry_details(folder, indexes[index])
        # drop it all in one go
        lorebook_output['entries'].append({
		"text": entry['entry'],
        "contextConfig": {
            "prefix": entry['novelai']['prefix'],
            "suffix": entry['novelai']['suffix'],
            "tokenBudget": entry['novelai']['token budget'],
            "reservedTokens": entry['novelai']['reserved tokens'],
            "budgetPriority": entry['novelai']['insertion order'],
            "trimDirection": entry['novelai']['trim direction'],
            "insertionType": entry['novelai']['insertion type'],
            "maximumTrimType": entry['novelai']['max trim type'],
            "insertionPosition": entry['novelai']['insertion position']
        },
        "displayName": entry['name'],
        "keys": entry['keys'],
        "searchRange": entry['novelai']['search range'],
        "enabled": entry['novelai']['enabled'],
        "forceActivation": entry['novelai']['force activation'],
        "keyRelative": entry['novelai']['key-relative insertion'],
        "nonStoryActivatable": entry['novelai']['cascading activation'],
        "category": "",
        "loreBiasGroups": entry['novelai']['lorebook bias']
        })
    # save to Exported Library.lorebook
    with open("Exported Library.lorebook", "w+") as f:
        json.dump(lorebook_output, f)
    sg.popup(f"Saved {len(indexes)} entries to Exported Library.lorebook")

# window functions
def move_entry_window():
    move_entry_layout = [[sg.Text("Move to where?", k = "-MOVEPROMPT-")],
    [sg.Combo(["No Folder"], default_value = "No Folder", readonly = True, k = "-DESTINATION-", expand_x = True)],
    [sg.Button("Move", k = "-CONFIRMMOVE-"), sg.Button("Cancel", k = "-CANCELMOVE-")]]
    move_entry_win = sg.Window("Move Entries", move_entry_layout, modal = True, finalize = True)
    return move_entry_win

def add_entry_window():
    add_entry_layout = [[sg.Text("How will you add an entry?")],
    [sg.Text("File path must be to worldInfo.json or .lorebook")],
    [sg.Input(k = "-FILEPATH-", expand_x = True), sg.FileBrowse(target = "-FILEPATH-", k = "-IMPORTBROWSE-")],
    [sg.Button("Manual Add", k = "-MANUALENTRY-"), sg.Button("Import File", k = "-CONFIRMIMPORT-"), sg.Button("Cancel", k = "-CANCELENTRY-")]]
    add_entry_win = sg.Window("Add Entry", add_entry_layout, modal = True)
    return add_entry_win

def rename_folder_window():
    # set layout, make window, return
    rename_folder_layout = [[sg.Text("Enter new name for folder")],
    [sg.Input(k = "-FOLDERRENAME-", expand_x = True)],
    [sg.Button("Rename", k = "-CONFIRMRENAME-"), sg.Button("Cancel", k = "-CANCELRENAME-")]]
    rename_win = sg.Window("Rename Folder", rename_folder_layout, modal = True)
    return rename_win

def add_folder_window():
    # set layout, make window, return
    add_folder_layout = [[sg.Text("Enter name of folder to add")],
[sg.Input(k = "-FOLDERNAME-", expand_x = True)],
[sg.Button("Add", k = "-ADD-"), sg.Button("Cancel", k = "-CANCELADD-")]]
    add_win = sg.Window("Add Folder", add_folder_layout, modal = True)
    return add_win

def nai_settings_window():
    # set layout, make window, return
    activation_layout = [[sg.Checkbox("Enabled", k = "-A_ENABLED-")],
    [sg.Checkbox("Force Activation", k = "-A_FORCEACTIVE-")],
    [sg.Checkbox("Key-Relative Insertion", k = "-A_KEYRELATIVE-")],
    [sg.Checkbox("Cascading Activation", k = "-A_CASCADING-")],
    [sg.Text("Search Range"), sg.Spin([i for i in range(1, 2049)], 1000, k = "-A_SEARCHRANGE-")]]
    trimming_layout = [[sg.Text("Maximum Trim Type"), sg.Combo(["sentence", "newline", "token"], default_value = "sentence", readonly = True, k = "-T_MAXTRIM-")],
    [sg.Text("Trim Direction"), sg.Combo(["trimTop", "trimBottom", "doNotTrim"], default_value = "trimBottom", readonly = True, k = "-T_TRIMDIR-")]]
    left_side_layout = [[sg.Frame("Activation", activation_layout, expand_x = True, element_justification = "right")],
    [sg.Frame("Trimming", trimming_layout, expand_x = True, expand_y = True, element_justification = "right")]]
    insertion_layout = [[sg.Text("Prefix"), sg.Input("", expand_x = True, k = "-I_PREFIX-")],
    [sg.Text("Suffix"), sg.Input("", expand_x = True, k = "-I_SUFFIX-")],
    [sg.Text("Token Budget"), sg.Spin([i for i in range(0, 2049)], 2048, k = "-I_TOKENBUDGET-")],
    [sg.Text("Reserved Tokens"), sg.Spin([i for i in range(0, 2049)], 0, k = "-I_RESERVEDTOKENS-")],
    [sg.Text("Insertion Order"), sg.Spin([i for i in range(-1000, 1000)], 400, k = "-I_INSERTIONORDER-")],
    [sg.Text("Insertion Position"), sg.Spin([i for i in range(-1000, 1000)], -1, k = "-I_INSERTIONPOSITION-")],
    [sg.Text("Insertion Type"), sg.Combo(["sentence", "newline", "token"], default_value = "newline", readonly = True, k = "-I_INSERTIONTYPE-")]]
    lore_bias_layout = [[sg.Text("This entry has - Lorebook biases.", k = "-BIASCOUNT-")]]
    right_side_layout = [[sg.Frame("Insertion", insertion_layout, expand_x = True, element_justification = "right")],
    [sg.Frame("LB Biases", lore_bias_layout, expand_x = True, element_justification = "center")]]
    nai_settings_layout = [[sg.Column(left_side_layout), sg.Column(right_side_layout)],
    [sg.Button("Save Changes", k = "-SAVENAISETTINGS-", expand_x = True), sg.Button("Discard Changes", k = "-DISCARDNAISETTINGS-", expand_x = True)]]
    nai_settings_win = sg.Window("NovelAI Settings", nai_settings_layout, element_justification = "center", finalize = True, modal = True)
    return nai_settings_win

def main_window():
    selected_wi = None
    win = sg.Window("Library", main_layout, resizable = True, size = (1024, 640), finalize = True)
    # update folder listbox with actual list of folders
    win['-FOLDERLIST-'].update(values = list(library.keys()), set_to_index = 0)
    # update entry listbox with actual list of entries
    win['-ENTRYLIST-'].update(values = get_entry_names(win["-FOLDERLIST-"].get()[0]))
    # event loop
    while True:
        # disable some buttons and stuff if the entry list is empty
        if not win['-ENTRYLIST-'].get():
            win['-NAME-'].update(value = "", disabled = True)
            win['-ENTRY-'].update(value = "", disabled = True)
            win['-KEYS-'].update(value = "", disabled = True)
            win['-SOURCE-'].update(value = "Source: (no entry selected)")
            win['-DATEADDED-'].update(value = "Date Added: (no entry selected)")
            win['-DATEEDITED-'].update(value = "Last Edited: (no entry selected)")
            win['-MOVEENTRY-'].update(disabled = True)
            win['-DELETEENTRY-'].update(disabled = True)
            win['-EXPORTLB-'].update(disabled = True)
            win['-AIDJSON-'].update(disabled = True)
            #win['-AIDAPI-'].update(disabled = True)
            win['-SAVEENTRY-'].update(disabled = True)
            win['-NAISETTINGS-'].update(disabled = True)
        else:
            win['-NAME-'].update(disabled = False)
            win['-ENTRY-'].update(disabled = False)
            win['-KEYS-'].update(disabled = False)
            win['-MOVEENTRY-'].update(disabled = False)
            win['-DELETEENTRY-'].update(disabled = False)
            win['-EXPORTLB-'].update(disabled = False)
            win['-AIDJSON-'].update(disabled = False)
            #win['-AIDAPI-'].update(disabled = False)
            win['-SAVEENTRY-'].update(disabled = False)
            win['-NAISETTINGS-'].update(disabled = False)
        # read, as usual. also, update entrybox token count
        win['-TKNCOUNT-'].update(value = f"Entry - ~{count_tokens(win['-ENTRY-'].get())} GPT-2 token(s) (Estimated)")
        event, values = win.read()
        if event == sg.WIN_CLOSED:
            break
        # folder list
        elif event == "-FOLDERLIST-":
            win['-ENTRYLIST-'].update(values = get_entry_names(values['-FOLDERLIST-'][0]))
        elif event == "-DELETEFOLDER-":
            remove_folder_by_name(values['-FOLDERLIST-'][0])
            win['-FOLDERLIST-'].update(values = list(library.keys()), set_to_index = 0)
            win['-ENTRYLIST-'].update(values = get_entry_names(win["-FOLDERLIST-"].get()[0]))
        elif event == "-ADDFOLDER-":
            # make "add folder" window
            add_folder_win = add_folder_window()
            # event loop for add window
            while True:
                event, _values = add_folder_win.read()
                # end event loop if window gets closed or user clicks cancel
                if event == sg.WIN_CLOSED or event == "-CANCELADD-":
                    break
                elif event == "-ADD-":
                    # add folder if it's got characters that aren't just whitespace
                    foldername_no_whitespace = _values['-FOLDERNAME-'].replace(" ", "")
                    if foldername_no_whitespace:
                        successful_add = add_folder_by_name(_values['-FOLDERNAME-'])
                        if successful_add:
                            win['-FOLDERLIST-'].update(values = list(library.keys()), set_to_index = win["-FOLDERLIST-"].get_indexes()[0])
                            win['-ENTRYLIST-'].update(values = get_entry_names(values['-FOLDERLIST-'][0]))
                        break
                    else:
                        sg.Popup("Please type a folder name. Folder names cannot consist of just whitespace.", title = "Error adding folder")
            # close this win once done
            add_folder_win.close()
        elif event == "-RENAMEFOLDER-":
            # make "rename folder" window
            rename_folder_win = rename_folder_window()
            # event loop for rename window
            while True:
                _event, _values = rename_folder_win.read()
                if _event == sg.WIN_CLOSED or _event == "-CANCELRENAME-":
                    break
                elif _event == "-CONFIRMRENAME-":
                    selected_folder = win["-FOLDERLIST-"].get_indexes()[0]
                    if _values['-FOLDERRENAME-'].replace(" ", ""):
                        rename_folder(values['-FOLDERLIST-'][0], _values['-FOLDERRENAME-'])
                        win['-FOLDERLIST-'].update(values = list(library.keys()), set_to_index = selected_folder)
                        break
                    else:
                        sg.Popup('Please type a folder name. Folder names cannot consist of just whitespace.', title = "Error renaming folder")
            rename_folder_win.close()
        # entry list
        elif event == "-ENTRYLIST-" and values['-ENTRYLIST-']:
            indexes = list(win['-ENTRYLIST-'].get_indexes())
            # get details of selected WI
            selected_wi = get_main_entry_details(values['-FOLDERLIST-'][0], indexes[0])
            # update the details shown in the WI details section
            win['-NAME-'].update(value = selected_wi['name'])
            win['-KEYS-'].update(value = keys_to_string(selected_wi['keys']))
            win['-ENTRY-'].update(value = selected_wi['entry'])
            win['-SOURCE-'].update(value = f"Source: {selected_wi['meta']['source']}")
            win['-DATEADDED-'].update(value = f"Date Added: {selected_wi['meta']['date created']}")
            win['-DATEEDITED-'].update(value = f"Last Edited: {selected_wi['meta']['date updated']}")
        elif event == "-SAVEENTRY-":
            keys = string_to_keys(values['-KEYS-'])
            # set selected_wi stuff to the new values
            selected_wi['name'] = values['-NAME-']
            selected_wi['keys'] = keys
            selected_wi['entry'] = values['-ENTRY-']
            selected_wi['meta']['date updated'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            # save new selected_wi to library
            save_entry_to_index(selected_wi, win['-ENTRYLIST-'].get_indexes()[0], values['-FOLDERLIST-'][0])
            save_library()
            win['-ENTRYLIST-'].update(values = get_entry_names(values['-FOLDERLIST-'][0]))
        elif event == "-DELETEENTRY-":
            # grab selected indexes
            indexes = list(win['-ENTRYLIST-'].get_indexes())
            # if bulk deleting, ask to confirm
            confirm = "Yes"
            if len(indexes) > 1:
                confirm = sg.popup_yes_no(f"Are you sure you want to delete {len(indexes)} entries?", title = "Confirm bulk delete")
            if confirm == "Yes":
                # delete entries at indexes, save and update listbox
                delete_entries_from_folder(indexes, values['-FOLDERLIST-'][0])
            save_library()
            win['-ENTRYLIST-'].update(values = get_entry_names(values['-FOLDERLIST-'][0]))
        elif event == "-ADDENTRY-":
            # make "add entry" window
            add_entry_win = add_entry_window()
            # event loop for entry window
            while True:
                event, _values = add_entry_win.read()
                # end event loop if window gets closed or user clicks cancel
                if event == sg.WIN_CLOSED or event == "-CANCELENTRY-":
                    break
                elif event == "-MANUALENTRY-": # manual entry, user writes it themself
                    new_wi = world_info.copy()
                    new_wi['meta']['date updated'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    new_wi['meta']['date created'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    new_wi['meta']['source'] = "This Program"
                    add_new_entry_to_folder(new_wi, values['-FOLDERLIST-'][0])
                    break
                elif event == "-CONFIRMIMPORT-":
                    filepath = _values['-FILEPATH-']
                    if filepath[-5:] == ".json":
                        import_json_entries_to_folder(filepath, values['-FOLDERLIST-'][0])
                        break
                    elif filepath[-9:] == ".lorebook":
                        import_lorebook_entries_to_folder(filepath, values['-FOLDERLIST-'][0])
                        break
                    else:
                        sg.popup("Please select a worldInfo.json or .lorebook file to import entries from", title = "Error importing")
            add_entry_win.close()
            save_library()
            win['-ENTRYLIST-'].update(values = get_entry_names(values['-FOLDERLIST-'][0]))
        elif event == "-MOVEENTRY-":
            # grab selected indexes and folder list from library.keys()
            indexes = list(win['-ENTRYLIST-'].get_indexes())
            valid_destinations = list(library.keys())
            # make "move entry" window, set things that need to be set before it's displayed
            move_entry_win = move_entry_window()
            move_entry_win['-DESTINATION-'].update(values = valid_destinations, set_to_index = 0)
            move_entry_win['-MOVEPROMPT-'].update(value = f"Entries to move: {len(indexes)} - Where to?")
            # event loop for entry window
            while True:
                _event, _values = move_entry_win.read()
                if _event == sg.WIN_CLOSED or _event == "-CANCELMOVE-":
                    break
                elif _event == "-CONFIRMMOVE-":
                    move_entries_to_folder(indexes, values['-FOLDERLIST-'][0], _values["-DESTINATION-"])
                    break
            move_entry_win.close()
            save_library()
            win['-ENTRYLIST-'].update(values = get_entry_names(values['-FOLDERLIST-'][0]))
        # exports
        elif event == "-EXPORTLB-":
            indexes = win['-ENTRYLIST-'].get_indexes()
            # if there's anything selected, export
            if indexes:
                export_entries_to_lorebook(indexes, values['-FOLDERLIST-'][0])
            else:
                sg.popup("Please select entries to export", title = "Error Exporting")
        elif event == "-AIDJSON-":
            indexes = win['-ENTRYLIST-'].get_indexes()
            # if there's anything selected, export
            if indexes:
                export_entries_to_json(indexes, values['-FOLDERLIST-'][0])
            else:
                sg.popup("Please select entries to export", title = "Error Exporting")
        # nai settings window
        elif event == "-NAISETTINGS-":
            # get info of currently selected entry
            selected = win['-ENTRYLIST-'].get_indexes()[0]
            viewed_entry = get_main_entry_details(values['-FOLDERLIST-'][0], selected)
            # open NAI settings window
            nai_settings_win = nai_settings_window()
            # pass in settings from entry. starting with activation...
            nai_settings_win['-A_ENABLED-'].update(value = viewed_entry["novelai"]["enabled"])
            nai_settings_win['-A_FORCEACTIVE-'].update(value = viewed_entry["novelai"]["force activation"])
            nai_settings_win['-A_KEYRELATIVE-'].update(value = viewed_entry["novelai"]["key-relative insertion"])
            nai_settings_win['-A_CASCADING-'].update(value = viewed_entry["novelai"]["cascading activation"])
            nai_settings_win['-A_SEARCHRANGE-'].update(value = viewed_entry["novelai"]["search range"])
            # trimming...
            nai_settings_win['-T_MAXTRIM-'].update(value = viewed_entry["novelai"]["max trim type"])
            nai_settings_win['-T_TRIMDIR-'].update(value = viewed_entry["novelai"]["trim direction"])
            # insertion...
            nai_settings_win['-I_PREFIX-'].update(value = viewed_entry["novelai"]["prefix"].replace("\n", "\\n"))
            nai_settings_win['-I_SUFFIX-'].update(value = viewed_entry["novelai"]["suffix"].replace("\n", "\\n"))
            nai_settings_win['-I_TOKENBUDGET-'].update(value = viewed_entry["novelai"]["token budget"])
            nai_settings_win['-I_RESERVEDTOKENS-'].update(value = viewed_entry["novelai"]["reserved tokens"])
            nai_settings_win['-I_INSERTIONORDER-'].update(value = viewed_entry["novelai"]["insertion order"])
            nai_settings_win['-I_INSERTIONPOSITION-'].update(value = viewed_entry["novelai"]["insertion position"])
            nai_settings_win['-I_INSERTIONTYPE-'].update(value = viewed_entry["novelai"]["insertion type"])
            # ... and lorebook bias count.
            nai_settings_win['-BIASCOUNT-'].update(value = f"This entry has {len(viewed_entry['novelai']['lorebook bias'])} Lorebook biases.")
            # finally to the event loop
            while True:
                _event, _values = nai_settings_win.read()
                if _event == sg.WIN_CLOSED or _event == "-DISCARDNAISETTINGS-":
                    break
                # save all changes... lotsa similar lines. maybe i could lump it into one big viewed_entry['nai'] = {bigdict} at some point
                elif _event == "-SAVENAISETTINGS-":
                    # saving activation...
                    viewed_entry["novelai"]["enabled"] = _values['-A_ENABLED-']
                    viewed_entry["novelai"]["force activation"] = _values['-A_FORCEACTIVE-']
                    viewed_entry["novelai"]["key-relative insertion"] = _values['-A_KEYRELATIVE-']
                    viewed_entry["novelai"]["cascading activation"] = _values['-A_CASCADING-']
                    viewed_entry["novelai"]["search range"] = _values['-A_SEARCHRANGE-']
                    # trimming...
                    viewed_entry["novelai"]["max trim type"] = _values['-T_MAXTRIM-']
                    viewed_entry["novelai"]["trim direction"] = _values['-T_TRIMDIR-']
                    # ...and insertion. replace verbatim "\n"s from input box with newline, because that is what people would use
                    viewed_entry["novelai"]["prefix"] = _values['-I_PREFIX-']
                    if viewed_entry["novelai"]["prefix"] == "\\n": viewed_entry["novelai"]["prefix"] = "\n"
                    viewed_entry["novelai"]["suffix"] = _values['-I_SUFFIX-']
                    if viewed_entry["novelai"]["suffix"] == "\\n": viewed_entry["novelai"]["suffix"] = "\n"
                    viewed_entry["novelai"]["token budget"] = _values['-I_TOKENBUDGET-']
                    viewed_entry["novelai"]["reserved tokens"] = _values['-I_RESERVEDTOKENS-']
                    viewed_entry["novelai"]["insertion order"] =  _values['-I_INSERTIONORDER-']
                    viewed_entry["novelai"]["insertion position"] =  _values['-I_INSERTIONPOSITION-']
                    viewed_entry["novelai"]["insertion type"] = _values['-I_INSERTIONTYPE-']
                    viewed_entry['meta']['date updated'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    break
            nai_settings_win.close()
            win['-ENTRYLIST-'].update(values = get_entry_names(values['-FOLDERLIST-'][0]))
    # save and close when event loop breaks (on window close)
    win.close()
    save_library()

def main():
    main_window()

if __name__ == "__main__":
    library = load_library()
    main()