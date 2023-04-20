"""
Program Name: SalesTrax
Version: 0.1.1
Status: Prototype
Created on: 2023-04-09
Last updated: 2023-04-20
Created with: Python 3.11.2
Author: Danny Fleenor
Contributors:
    Alex Clark, Fredrik Lundh, Secret Labs AB: PIL image processing library
    Anonymous Contributors: Python OS library
    DaedalicEntertainment: Tktooltip tooltip module
    Danny Fleenor: Program design and development; logo image
    Fredrik Lundh, Guido van Rossum, Steen Lumholt: Tkinter GUI library
    Georg Brandl: Webbrowser browser interface library
    Wes McKinney: Pandas file import library
    www.aha-soft.com: Shortcut bar images

Description:
    As a Disclaimer™, I find it worth mentioning that this is a college project begun after only three weeks of learning
    Python. In absolutely no way will I claim it is perfect. By choosing to use this program, you accept responsibility
    for the fallout of potentially clumsy coding. It is not designed to be harmful, of course, but I cannot attest to
    how your system may or may not react to it; I'm not well-versed enough in Python programming to know that.

    Having said that, at this time, SalesTrax functions as a simple file merger for tablular financial documents. It
    reads CSV, ODS, and Excel documents, removes duplicate records, and provides a framework for manual record
    exclusions in the output file, which include CSV, ODS, and XLSX format. Note that any documents without a "Date" or
    "Timestamp" column WILL be rejected from being imported, but there are no other solid requirements for file content.
    
    Records can only be selected individually for now, so record status can only be updated one record at a time or all
    at once. Multiple selection is planned to be part of the next update, though. The plan for that update also includes
    elementary sorting and filtering, but PROPER filtering will not be available until later. Record modification, too,
    is planned for implementation at some point, but I cannot promise exactly when that will be.
"""
# Section: Imports
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from PIL import Image, ImageTk
from tktooltip import ToolTip


# Section: Variable class
# * This isn't actually needed for the list variables, but other datatypes can't be modified in functions without either
# * global or class definition. I chose class definition, as nearly every source I've found on the topic specifically
# * warns against global variables in almost all cases.
class stvars:
    # Keep a backup of all Datalog messages in iterable format
    datalog_msgs = list()
    # Saved records; base data list
    records_saved = list()
    # Deleted records; base data list
    records_deleted = list()
    # Filtered records from one or more of the base data lists
    records_filter = list()
    # Invalid records; base data list
    records_invalid = list()
    # Unfiltered records from all the base data lists
    records_master = list()
    # Temporary records; base data list
    records_temp = list()
    # Validation strings for the 'Category' field
    valid_categories = list()
    # Validation strings for the 'Employee' field
    valid_employees = list()
    # Validation strings for the 'Location' field
    valid_locations = list()
    current_file = str()


# HEADLINE: Function definitions
# Updated: All good for now.
def check_temp_count():
    """
    Check that 'stvars.records_temp' is empty before attempting to load a file.

    Args: None
    Raises: None
    Returns: None
    """
    if len(stvars.records_temp) == 0:
        # All records are either saved or rejected. Proceed to open the file selection window:
        load_file()
    else:
        # There are still some temporary records. Ask the user what to do:
        commit_popup()


# Updated: All good for now.
def clear_all_data():
    """
    Clears all loaded data from all persistent lists EXCEPT 'stvars.datalog_msgs'. It allows the user to continue using
    the program to work on another document set without needing to close the program to do so.

    Args: None
    Raises: None
    Returns: None
    """
    # Ensure any selected rows are deselected:
    if len(base_tree.selection()) > 0:
        base_tree.selection_remove(base_tree.selection()[0])
    # Clear all records from all record lists:
    iter8 = 0
    while len(stvars.records_saved) > 0:
        stvars.records_saved.remove(stvars.records_saved[0])
    while len(stvars.records_deleted) > 0:
        stvars.records_deleted.remove(stvars.records_deleted[0])
    while len(stvars.records_filter) > 0:
        stvars.records_filter.remove(stvars.records_filter[0])
    while len(stvars.records_invalid) > 0:
        stvars.records_invalid.remove(stvars.records_invalid[0])
    while len(stvars.records_temp) > 0:
        stvars.records_temp.remove(stvars.records_temp[0])
    while len(stvars.records_master) > 0:
        stvars.records_master.remove(stvars.records_master[0])
        # Since all the other record lists are inside this one, only count its records:
        iter8 += 1
    # Don't log this action if the record lists were already empty.
    if iter8 > 0:
        log_msg(msg=(str(iter8) + " records were cleared from memory."))
    # Clear all user-defined field validation lists:
    iter8 = 0
    while len(stvars.valid_categories) > 0:
        stvars.valid_categories.remove(stvars.valid_categories[0])
        iter8 += 1
    while len(stvars.valid_employees) > 0:
        stvars.valid_employees.remove(stvars.valid_employees[0])
        iter8 += 1
    while len(stvars.valid_locations) > 0:
        stvars.valid_locations.remove(stvars.valid_locations[0])
        iter8 += 1
    # Don't log this action if the validation lists were already empty.
    if iter8 > 0:
        log_msg(
            msg=(str(iter8) + " field validation definitions were cleared from memory.")
        )
    # Clear the viewport, but don't attempt to repopulate it:
    refresh_table(repop_tree=False)


# Updated: All good for now.
def clear_table():
    """
    Clears the contents of the primary viewport (typically used for updating the table contents).

    Args: None
    Raises: None
    Returns: None
    """
    # Deselect any currently selected rows:
    if len(base_tree.selection()) > 0:
        base_tree.selection_remove(base_tree.selection()[0])
    # Delete all the rows in the table:
    for record in base_tree.get_children():
        base_tree.delete(record)


# Updated: All good for now.
def commit_all():
    """
    Moves temp records from the temp record list into the saved records

    Args: None
    Raises: None
    Returns: None
    """
    # Only run this function if there are temporary records:
    # * This shouldn't be necessary, since the buttons and menu options for this are disabled,
    # * but it's here as a failsafe. Better safe than sorry.
    if len(stvars.records_temp) > 0:
        # Deselect any currently selected rows:
        # * This is in place because if a record is still selected when 'Status' values are modified,
        # * it causes an infinite loop in the 'get_selected()' function.
        if len(base_tree.selection()) > 0:
            base_tree.selection_remove(base_tree.selection()[0])
        iter8 = 0
        while len(stvars.records_temp) > 0:
            # Change the status of each record from "Temporary" to "Saved", for treeview color sorting:
            stvars.records_temp[0]["Status"] = "Saved"
            # Add each record to 'stvars.records_saved' in the same order they appear in 'stvars.records_temp':
            stvars.records_saved.append(stvars.records_temp[0])
            # Then delete the 'stvars.records_temp' copy of the record:
            stvars.records_temp.remove(stvars.records_temp[0])
            # As always, keep count of the number of records changed, for logging purposes:
            iter8 += 1
        if iter8 > 0:
            # Sort by timestamp if one is present:
            if "Timestamp" in stvars.records_saved[0].keys():
                stvars.records_saved.sort(key=lambda d: d["Timestamp"], reverse=False)
            # Log the record changes:
            log_msg(msg=(str(iter8) + " records were committed to memory."))
            # Only refresh the tree if there were changes made by this function:
            refresh_table(master_log=True)


# Updated: All good for now.
def commit_popup():
    """
    Displays a top-level popup asking how the user wishes to handle temporary records. Options are: "Commit All",
    "Reject All", and "Review Temporary".

    Args: None
    Raises: None
    Returns: None
    """
    # Create toplevel 'tkinter' window:
    popup = tk.Toplevel(root)
    # Assign the SalesTrax logo as the window icon:
    popup.iconbitmap("Images/salestrax_icon_bw.ico")
    # Assign a suitable title to the window header:
    popup.title("Temporary Records Remaining")
    # Remove the maximize and minimize buttons by defining the popup as a 'toolwindow':
    popup.attributes("-toolwindow", True)
    # Turn the "X" button on the popup into a "Cancel" button, not accepting any options, but re-enabling 'root':
    popup.protocol(
        "WM_DELETE_WINDOW",
        func=lambda: [root.attributes("-disabled", False), popup.destroy()],
    )
    # Open the toplevel window in the center of the screen:
    # * Note that this isn't precisely the center of the screen, because the window geometry isn't a fixed value set,
    # * but it is approximately centered, so the user should see it straight away.
    popup.tk.eval(f"tk::PlaceWindow {str(popup)} center")
    # Set the toplevel window as the window with user focus:
    popup.focus_set()
    # Play the Windows popup 'ding' when the window opens:
    popup.bell()
    # Prevent the user from switching back to the root window:
    root.attributes("-disabled", True)
    # Place a frame in the toplevel window to allow column width variation per row:
    top_frame = tk.Frame(popup)
    # Assign a 'Question' icon to the popup body and put it in the frame:
    icon = tk.Label(top_frame, image=img_question)
    # Compose the popup's text content to show how many temp records are still in the document:
    msg = (
        "You have "
        + str(len(stvars.records_temp))
        + " temporary records. SalesTrax cannot load new data until all records"
        + " are either saved or rejected. Would you like to commit them all,"
        + " reject them all, or cancel loading to review them?"
    )
    # Create a label to hold the above message and apply line wrapping to it:
    warn_label = tk.Label(top_frame, text=msg, wraplength=300)
    # Define the three buttons used for the user's decision. All three should re-enable access to the root window:
    btn_commit_all = tk.Button(
        popup,
        text="Commit All",
        font="sans 10 bold",
        # Have the 'Commit All' button actually commit all temp records before opening the 'Open File' dialog:
        command=lambda: [
            root.attributes("-disabled", False),
            commit_all(),
            load_file(),
            popup.destroy(),
        ],
    )
    btn_reject_all = tk.Button(
        popup,
        text="Reject All",
        font="sans 10 bold",
        # Have the 'Reject All' button reject all temp records before opening the 'Open File' dialog:
        command=lambda: [
            root.attributes("-disabled", False),
            reject_all(),
            load_file(),
            popup.destroy(),
        ],
    )
    btn_review_temp = tk.Button(
        popup,
        text="Review Temporary",
        font="sans 10 bold",
        # Have the 'Review Temporary' set the record filter to only show temp records:
        command=lambda: [
            root.attributes("-disabled", False),
            view_temp(),
            popup.destroy(),
        ],
    )
    # Place the frame in the first row of the toplevel window:
    top_frame.grid(row=0, column=0, columnspan=3, padx=25, pady=10)
    # Place the icon on the left side of the frame:
    icon.grid(row=0, column=0)
    # Place the body message on the right side of the frame:
    warn_label.grid(row=0, column=1, padx=(25, 0))
    # Place the three decision buttons under the frame:
    btn_commit_all.grid(row=1, column=0, padx=(40, 0), pady=(10, 25))
    btn_reject_all.grid(row=1, column=1, pady=(10, 25))
    btn_review_temp.grid(row=1, column=2, padx=(0, 40), pady=(10, 25))


# Idea: Remove restore and reject options altogether and replace them with 'Commit' and 'Delete' only.
# $ Essentially, restore and commit do the same thing anyway. Same with reject and delete. There's no need to recognize
# $ them as two separate functions when they use almost exactly the same code.
# Alternative: An even more slimmed-down option would be to remove 'Delete' as well.
# % There could potentially be just one function that handles moving records from one record list to another. It would
# % require a minor rewrite to 'get_selected()', but if that function passed the actual record list into the
# % 'data_address' list instead of passing the 'Status' key value, then the 'commit_selection()' function (or whatever
# % replaces it) would be able to dynamically build the record modification commands from that.
# Document: Add docstring and topline comments.
# ? I'm leaving the documentation incomplete for now in lieu of contemplating the changes above. If I decide to
# ? implement either change, the documentation would change anyway; no need to do it twice.
def commit_selection():
    data_address = get_selection(stop_select=True)
    if data_address is not None:
        if data_address[0] == "Temporary":
            # Notes: The next code line raises a warning in PyCharm, but it isn't an error.
            # * The problem stems from PyCharm not recognizing that 'stvars.records_temp[data_address[1]]' refers to a
            # * dictionary, not a list. It's not a big deal, but I thought I should mention it in case someone takes
            # * over the code, tries to fix it, and breaks the program in the process. Don't fix it. It's not broken.
            stvars.records_temp[data_address[1]]["Status"] = "Saved"
            stvars.records_saved.append(stvars.records_temp[data_address[1]])
            stvars.records_temp.remove(stvars.records_temp[data_address[1]])
            log_msg("1 record was committed to memory.", popup=False)
            refresh_table(repop_tree=True)
            base_tree.selection_set(base_tree.get_children()[data_address[2]])
            base_tree.focus(base_tree.get_children()[data_address[2]])


# Document: Add docstring and topline comments.
# ? See the documentation comments on 'commit_selection()' for why this function's documentation is pending.
def delete_selection():
    data_address = get_selection(stop_select=True)
    if data_address is not None:
        if data_address[0] == "Saved":
            # * See the 'Notes' in 'commit_selection()' for why this raises a warning in PyCharm.
            stvars.records_saved[data_address[1]]["Status"] = "Deleted"
            stvars.records_deleted.append(stvars.records_saved[data_address[1]])
            stvars.records_saved.remove(stvars.records_saved[data_address[1]])
            log_msg("1 record was deleted.", popup=False)
            refresh_table(repop_tree=True)
        if data_address[0] == "Invalid":
            # * See the 'Notes' in 'commit_selection()' for why this raises a warning in PyCharm.
            stvars.records_invalid[data_address[1]]["Status"] = "Deleted"
            stvars.records_deleted.append(stvars.records_invalid[data_address[1]])
            stvars.records_invalid.remove(stvars.records_invalid[data_address[1]])
            log_msg("1 record was deleted from memory.", popup=False)
            refresh_table(repop_tree=True)
        base_tree.selection_set(base_tree.get_children()[data_address[2]])
        base_tree.focus(base_tree.get_children()[data_address[2]])


# Updated: All good for now.
def disable_resize(event):
    """
    Prevents manual resizing of table column headers and its associated mouse graphic by interrupting the default
    behavior of left-clicking and mouse motion when the mouse is positioned over a column separator.

    Args:
        event (tkinter.Event): A standard tkinter keybinding event. In this case, it is either '<Button-1>' (left-click)
            or '<Motion>' (mouse movement), but should not be manually declared.

    Returns:
        str: This returns "break" back to the calling event, preventing it from performing its default behavior.
    """
    # Only interrupt mouse behavior if the mouse is positioned over a column header separator:
    if base_tree.identify_region(event.x, event.y) == "separator":
        return "break"


# Placeholder: This will eventually be replaced by other functions.
# << It serves the purpose of disabling certain behaviors during the design phase of the project, but those behaviors
# << should be tied to something more meaningful in the final project.
# Updated: All good for now.
def do_nothing():
    """
    Literally just does nothing. Used to disable default behavior on things like "Close Window" buttons, etc.

    Args: None
    Raises: None
    Returns: None
    """
    pass


# Incomplete: This should also prompt the user to export their work if any modified records are loaded.
def exit_functions():
    """
    Postpones exiting the program to perform obligatory exit functions such as saving the Datalog.

    Args: None
    Raises: None
    Returns: None
    """
    # Save the contents of the Datalog to file:
    save_log()
    # Then safely close the program
    root.quit()


# Updated: All good for now.
def export_file():
    """
    This opens the 'Save File As...' dialog to export an Excel, ODS, or CSV file to disk. When successful, passes the
    file info to 'write_file()' for use.

    Args: None
    Raises: None
    Returns: None
    """
    # Define filetypes that are accepted for writing:
    table_docs = [
        ("Excel Worksheet", "*.xlsx"),
        ("Comma-Separated Values", "*.csv"),
        ("Open Office Spreadsheet", "*.ods"),
    ]
    # Now define them again as a normal list to double-check against the user's input:
    format_list = ["csv", "ods", "xlsx"]
    # Get the path of the chosen file name and store it as 'filePath':
    file_path = filedialog.asksaveasfilename(
        filetypes=table_docs, defaultextension=".xlsx"
    )
    # Ensure the user didn't click 'Cancel' in the dialog:
    if len(file_path) > 0:
        # Ensure that the file type is writeable before passing to 'write_file()':
        # * The "Save As..." dialog doesn't actually prevent users from manually typing in file extensions that aren't
        # * in the filter list, so this guards against that behavior.
        if file_path.split(".")[-1] in format_list:
            write_file(path=file_path)
        else:
            log_msg(
                "SalesTrax does not support writing to the '."
                + file_path.split(".")[-1]
                + "' file format."
            )


# Updated: All good for now.
def get_selection(stop_select: bool = False):
    """
    Grabs the contents of the currently selected line in the viewport table and uses that information to locate the
    record in its respective record list.

    Args:
        stop_select (bool, optional): Whether to clear the row selection on the chosen record when finding the record's
            list location. When used for record modifications, this should always be set to True, but for purposes that
            don't change the record values, set it to False. Defaults to False.

    Raises: None
    Returns:
        list: When successful, this returns a list that can be used by another function to locate and access the item
            more easily.
    """
    # Ensure that a record is selected at all:
    if len(base_tree.selection()) > 0:
        # Initialize an empty list to store the location of the selected record:
        data_address = list()
        # Store the treeview index of the selected row, so it can be re-selected after a table refresh:
        tree_index = base_tree.index(base_tree.selection()[0])
        # Grab the list of column headers to use as key values:
        keys = list(base_tree["columns"])
        # Grab the values displayed in the selected row:
        values = base_tree.item(base_tree.selection()[0])["values"]
        # If the record is going to be modified, deselect it in the treeview to prevent looping errors:
        if stop_select:
            if len(base_tree.selection()) > 0:
                base_tree.selection_remove(base_tree.selection()[0])
        # Initialize an empty dictionary to store the keys and values gathered above:
        selection_dict = dict()
        # Populate the empty dictionary with key-value pairs in the same format as found in the record list variables:
        iter8 = 0
        while iter8 < len(keys):
            selection_dict[keys[iter8]] = values[iter8]
            iter8 += 1
        # Timestamp objects and float values are stored as strings in Treeview, so convert them to their original
        # datatypes in the library:
        if "Timestamp" in selection_dict:
            selection_dict["Timestamp"] = pd.Timestamp(selection_dict["Timestamp"])
        if "Cost" in selection_dict:
            if selection_dict["Cost"] != "":
                selection_dict["Cost"] = float(selection_dict["Cost"])
        if "Total" in selection_dict:
            if selection_dict["Total"] != "":
                selection_dict["Total"] = float(selection_dict["Total"])
        # If the record status is "Temporary", search the 'stvars.records_temp' list for a matching record:
        if selection_dict["Status"] == "Temporary":
            index = 0
            iter8 = 0
            while index < len(stvars.records_temp):
                if selection_dict == stvars.records_temp[index]:
                    # Store the "Temporary" status in the return list:
                    data_address.append(selection_dict["Status"])
                    # Store the 'stvars.records_temp' index of the matching record:
                    data_address.append(index)
                    # And store the 'tree_index' from earlier, for reselection purposes:
                    data_address.append(tree_index)
                else:
                    # If the first record doesn't match, move on to the next, and so on, but store the number of
                    # non-matching records:
                    iter8 += 1
                index += 1
            # If the number of non-matching records matches the number of records, then no match was found:
            if iter8 == len(stvars.records_temp):
                # Display a messagebox and Datalog entry informing the user of the record error:
                log_msg(
                    msg="Something went wrong. A memory address for the selected record could not be found. Try "
                    "refreshing the table and then try again.",
                    popup=True,
                )
                # If an error does occur, deselect the selected row to prevent looping errors:
                base_tree.selection_remove(base_tree.selection()[0])
        # If the record status is "Saved", follow all the same steps from the "Temporary" option, but with the
        # 'stvars.records_saved' lists instead:
        elif selection_dict["Status"] == "Saved":
            index = 0
            iter8 = 0
            while index < len(stvars.records_saved):
                if selection_dict == stvars.records_saved[index]:
                    data_address.append(selection_dict["Status"])
                    data_address.append(index)
                    data_address.append(tree_index)
                else:
                    iter8 += 1
                index += 1
            if iter8 == len(stvars.records_saved):
                log_msg(
                    msg="Something went wrong. A memory address for the selected record could not be found. Try "
                    "refreshing the table and then try again.",
                    popup=True,
                )
                base_tree.selection_remove(base_tree.selection()[0])
        # If the record status is "Deleted", follow all the same steps from the "Temporary" option, but with the
        # 'stvars.records_deleted' lists instead:
        elif selection_dict["Status"] == "Deleted":
            index = 0
            iter8 = 0
            while index < len(stvars.records_deleted):
                if selection_dict == stvars.records_deleted[index]:
                    data_address.append(selection_dict["Status"])
                    data_address.append(index)
                    data_address.append(tree_index)
                else:
                    iter8 += 1
                index += 1
            if iter8 == len(stvars.records_deleted):
                log_msg(
                    msg="Something went wrong. A memory address for the selected record could not be found. Try "
                    "refreshing the table and then try again.",
                    popup=True,
                )
                base_tree.selection_remove(base_tree.selection()[0])
        # If the record status is "Invalid", follow all the same steps from the "Temporary" option, but with the
        # 'stvars.records_invalid' lists instead:
        elif selection_dict["Status"] == "Invalid":
            index = 0
            iter8 = 0
            while index < len(stvars.records_invalid):
                if selection_dict == stvars.records_invalid[index]:
                    data_address.append(selection_dict["Status"])
                    data_address.append(index)
                    data_address.append(tree_index)
                else:
                    iter8 += 1
                index += 1
            if iter8 == len(stvars.records_invalid):
                log_msg(
                    msg="Something went wrong. A memory address for the selected record could not be found. Try "
                    "refreshing the table and then try again.",
                    popup=True,
                )
                base_tree.selection_remove(base_tree.selection()[0])
        # As long as the record is found, pass its information back to the function that called for it:
        if len(data_address) > 0:
            return data_address


# Updated: All good for now.
def link_to_github():
    """
    Opens a link to the SaleTrax repository on GitHub.

    Args: None
    Raises: None
    Returns: None
    """
    # Define the page link:
    url = "https://www.github.com/Apellonyx/salestrax"
    # Open the link in the user's default browser:
    webbrowser.open(url, new=0, autoraise=True)


# Updated: All good for now.
def load_file():
    """
    This opens the file select dialog to load an Excel, ODS, or CSV file from disk. When successful, passes this file
    to 'pop_temp()' for use.

    Args: None
    Raises: None
    Returns: None
    """
    # Define filetypes that are accepted for reading:
    table_docs = [
        ("All Supported", "*.csv;*.ods;*.xls;*.xlsb;*.xlsm;*.xlsx"),
        ("Excel Worksheet", "*.xls;*.xlsb;*.xlsm;*.xlsx"),
        ("Open Office Spreadsheet", "*.ods"),
        ("Comma-Separated Values", "*.csv"),
    ]
    # Now define them again as a normal list for comparison with the actual file loaded:
    format_list = ["csv", "ods", "xls", "xlsb", "xlsm", "xlsx"]
    # Get the path of the selected file and store it as 'filePath':
    file_path = filedialog.askopenfilename(filetypes=table_docs)
    # Ensure the file is loaded:
    if len(file_path) > 0:
        # Ensure that the file is parsable before passing to 'popTemp()':
        # * Technically, this shouldn't be needed, since format filters were defined for the Open File dialog,
        # * but--as usual--better safe than sorry.
        if file_path.split(".")[-1] in format_list:
            pop_temp(path=file_path)


# Updated: All good for now.
# ^ While this function is technically complete, the Datalog itself is still not complete.
# ^ See 'To-Do List.txt' for more details.
def log_msg(msg: str = "This event is not functional yet.", popup: bool = True):
    """
    Logs changes to the record lists in the Datalog. Optionally displays a top-level messagebox to the user with the
    same message.

    Args:
        msg (str, optional): Message to record in the Datalog. Defaults to "This event is not functional yet."
        popup (bool, optional): If True, display a top-level messagebox with the message contents. Defaults to True.
    Raises: None
    Returns: None
    """
    # Get the number of messages that have already been logged during this session:
    messages = len(stvars.datalog_msgs)
    # Grab a timestamp for the exact time when the message was sent to this function:
    time_now = pd.Timestamp.now().round(freq="s")
    # Compose the Datalog message using the information above and the contents of 'msg':
    full_msg = "%4s" % str(messages) + ": " + str(time_now) + ": " + msg + "\n"
    # Add the entire message to the 'dataLogged' list for backup:
    stvars.datalog_msgs.append(full_msg)
    # Enable writing to the Datalog:
    datalog_body.configure(state="normal")
    # * Print the message to the Datalog, ensuring it appears at the top: The Datalog displays in reverse-order for
    # * convenience, because the 'Text' widget doesn't automatically scroll when its contents overflow the visible
    # * area. Displaying them in reverse-order ensures the most recent message is always immediately visible when
    # * opening the Datalog window.
    datalog_body.insert("1.0", full_msg)
    # Disable writing to the Datalog after the message has been written to it:
    datalog_body.configure(state="disabled")
    # When bulk record changes occur, show the Datalog message to the user in a popup:
    if popup:
        messagebox.showinfo("Message", msg)


# Placeholder:
def pop_filter():
    pass


# Updated: All good for now.
def pop_master(send_log: bool = False):
    """
    This clears the current master record list and repopulates it with data from the saved, deleted, invalid, and temp
    record lists. It is called any time the component record lists are modified, refreshing of the viewport table.

    Args:
        send_log (bool, optional): When True, a Datalog entry is sent to 'log_msg' containing an updated total record
            count. Note that this does NOT result in a popup, only a log entry. Defaults to False.
    Raises: None
    Returns: None
    """
    iter8 = 0
    while len(stvars.records_master) > 0:
        # Empty the contents of 'stvars.records_master' first:
        stvars.records_master.remove(stvars.records_master[0])
    for record in stvars.records_deleted:
        # Next, add the entire contents of 'stvars.records_deleted' to the empty 'stvars.records_master':
        stvars.records_master.append(record)
        # Keep track of the number of records added to 'stvars.records_master' from this list:
        iter8 += 1
    for record in stvars.records_invalid:
        # Do the same for the other three lists:
        stvars.records_master.append(record)
        iter8 += 1
    for record in stvars.records_saved:
        stvars.records_master.append(record)
        iter8 += 1
    for record in stvars.records_temp:
        stvars.records_master.append(record)
        iter8 += 1
    # As long as at least one record was added to 'stvars.records_master', print a message to a popup and to the Datalog
    # informing the user how many records are currently loaded.
    if iter8 > 0:
        if send_log:
            log_msg(
                msg=(
                    "--There are currently "
                    + str(iter8)
                    + " total records loaded to the program."
                ),
                popup=False,
            )
        # If there is at least one temp record, enable the menu options, shortcut buttons, and shortcut keybindings
        # that can modify temp records in bulk operations:
        if len(stvars.records_temp) > 0:
            edit_menu.entryconfig("Commit All", state="normal")
            edit_menu.entryconfig("Reject All", state="normal")
            view_menu.entryconfig("Hide Temporary Records", state="normal")
            btn_commit_a.config(state="normal")
            btn_reject_a.config(state="normal")
            btn_hide_temp.config(state="normal")
            root.bind(sequence="<Shift-Return>", func=lambda event: commit_all())
            root.bind(sequence="<Shift-Delete>", func=lambda event: reject_all())
        # If no temp files are loaded, disable menu options, shortcut buttons, and keybindings associated with them:
        else:
            edit_menu.entryconfig("Commit All", state="disabled")
            edit_menu.entryconfig("Reject All", state="disabled")
            view_menu.entryconfig("Hide Temporary Records", state="disabled")
            btn_commit_a.config(state="disabled")
            btn_reject_a.config(state="disabled")
            btn_hide_temp.config(state="disabled")
            root.unbind(sequence="<Shift-Return>")
            root.unbind(sequence="<Shift-Delete>")
        # Only enable data export menu option and shortcut button if there is at least one "Saved" record:
        if len(stvars.records_saved) > 0:
            file_menu.entryconfig("Export To...", state="normal")
            btn_export.config(state="normal")
            view_menu.entryconfig("Hide Saved Records", state="normal")
            btn_hide_saved.config(state="normal")
        # Otherwise, disable exporting (because only "Saved" records are written to files during export):
        else:
            file_menu.entryconfig("Export To...", state="disabled")
            btn_export.config(state="disabled")
            view_menu.entryconfig("Hide Saved Records", state="disabled")
            btn_hide_saved.config(state="disabled")
        # Enable batch actions that rely on deleted records if there are any deleted records:
        if len(stvars.records_deleted) > 0:
            view_menu.entryconfig("Hide Deleted Records", state="normal")
            btn_hide_deleted.config(state="normal")
        # Otherwise, disable them:
        else:
            view_menu.entryconfig("Hide Deleted Records", state="disabled")
            btn_hide_deleted.config(state="disabled")
        # Enable batch actions for invalid records if there are any invalid records:
        if len(stvars.records_invalid) > 0:
            view_menu.entryconfig("Hide Invalid Records", state="normal")
            btn_hide_invalid.config(state="normal")
        # Otherwise, disable them:
        else:
            view_menu.entryconfig("Hide Invalid Records", state="disabled")
            btn_hide_invalid.config(state="disabled")
        # Enable any other menu options and buttons that perform batch actions on all varieties of loaded data:
        file_menu.entryconfig("Clear All Data", state="normal")
        edit_menu.entryconfig("Refresh Table", state="normal")
        view_menu.entryconfig("Toggle Filter...", state="normal")
        data_menu.entryconfig("Line Chart", state="normal")
        data_menu.entryconfig("Bar Chart", state="normal")
        data_menu.entryconfig("Pie Chart", state="normal")
        btn_refresh.config(state="normal")
        btn_filter.config(state="normal")
        btn_line.config(state="normal")
        btn_bar.config(state="normal")
        btn_pie.config(state="normal")
        # Finally, sort the contents of 'stvars.records_master' by timestamp:
        if "Timestamp" in stvars.records_master[0]:
            stvars.records_master.sort(key=lambda d: d["Timestamp"], reverse=False)
    # If there are no records loaded to any of the record lists, disable all menu options, buttons, and keybindings
    # that rely on table data:
    else:
        file_menu.entryconfig("Export To...", state="disabled")
        file_menu.entryconfig("Clear All Data", state="disabled")
        edit_menu.entryconfig("Refresh Table", state="disabled")
        edit_menu.entryconfig("Commit All", state="disabled")
        edit_menu.entryconfig("Reject All", state="disabled")
        view_menu.entryconfig("Hide Temporary Records", state="disabled")
        view_menu.entryconfig("Hide Invalid Records", state="disabled")
        view_menu.entryconfig("Hide Deleted Records", state="disabled")
        view_menu.entryconfig("Toggle Filter...", state="disabled")
        data_menu.entryconfig("Line Chart", state="disabled")
        data_menu.entryconfig("Bar Chart", state="disabled")
        data_menu.entryconfig("Pie Chart", state="disabled")
        btn_export.config(state="disabled")
        btn_commit_a.config(state="disabled")
        btn_reject_a.config(state="disabled")
        btn_refresh.config(state="disabled")
        btn_hide_saved.config(state="disabled")
        btn_hide_temp.config(state="disabled")
        btn_hide_invalid.config(state="disabled")
        btn_hide_deleted.config(state="disabled")
        btn_filter.config(state="disabled")
        btn_line.config(state="disabled")
        btn_bar.config(state="disabled")
        btn_pie.config(state="disabled")
        root.unbind(sequence="<Shift-Return>")
        root.unbind(sequence="<Shift-Delete>")


# Updated: All good for now.
def pop_temp(path: str):
    """
    Converts a tabular source document into a list of dictionaries for the program to work from.

    Args:
        path (str): The file path to the source document.
    Raises: None
    Returns: None
    """
    # Open the selected file as a DataFrame first. Read data from '.csv' files using 'pd.read_csv()':
    if path.split(".")[-1] == "csv":
        # Fill any blank cells with empty strings instead of 'NaN':
        data_loaded = pd.DataFrame(pd.read_csv(path)).fillna("")
    # Read data from all other supported file types using 'pd.read_excel()':
    else:
        data_loaded = pd.DataFrame(pd.read_excel(path)).fillna("")
    # Add a status key to define the record in the 'stvars.records_temp' category:
    data_loaded["Status"] = "Temporary"
    # Convert the DataFrame to a list of dictionaries for more flexible manipulation:
    data_loaded = data_loaded.to_dict(orient="records")
    # Pass the entire list of records into 'stvars.records_temp' for persistent storage:
    iter8 = 0
    while len(data_loaded) > 0:
        stvars.records_temp.append(data_loaded[0])
        data_loaded.remove(data_loaded[0])
        # Keep count of how many records were loaded into 'stvars.records_temp':
        iter8 += 1
    if iter8 > 0:
        # Pass the tallied record count into the Datalog:
        log_msg(
            msg=(str(iter8) + ' records loaded from "' + str(path) + '".'),
            popup=False,
        )
        stvars.current_file = str(path)
        # Only pass on to the next step if there are records left to validate:
        validate_temp()


# Updated: All good for now.
def pop_table():
    """
    Populates the viewport table (Treeview widget) with data. If any filter or sort is active, it will populate with
    the contents of the filtered record list; otherwise, it will populate with the contents of the master record list.

    Args: None
    Raises: None
    Returns: None
    """
    # Initialize an empty list variable to hold either 'stvars.records_filter' or 'stvars.records_master':
    list_used = list()
    # If there are any records selected in the treeview widget, deselect them:
    if len(base_tree.selection()) > 0:
        base_tree.selection_remove(base_tree.selection()[0])
    # 'stvars.records_filter' will only have records in it if a filter or sort is active. If so, use
    # 'stvars.records_filter' to name the column headers:
    if len(stvars.records_filter) > 0:
        base_tree["columns"] = tuple(stvars.records_filter[0].keys())
        list_used = stvars.records_filter
    # If 'stvars.records_filter' is empty, use 'stvars.records_master' to name the column headers instead:
    elif len(stvars.records_master) > 0:
        base_tree["columns"] = tuple(stvars.records_master[0].keys())
        list_used = stvars.records_master
    # If both 'stvars.records_filter' and 'stvars.records_master' are empty, don't provide any column headers:
    else:
        base_tree["columns"] = tuple()
    # Define the default Treeview column and its header, ensuring that it stays hidden, as its functions aren't used
    # in SalesTrax:
    base_tree.column("#0", width=0, stretch=False)
    base_tree.heading("#0", text="", anchor="w")
    # Now set up the attributes for columns that are actually visible:
    for col_head in base_tree["columns"]:
        if col_head == "Timestamp":
            base_tree.column(
                col_head,
                anchor="w",
                # All columns should have a fixed width starting out, with approximately equal size:
                width=int((root.winfo_width() - 26) / len(base_tree["columns"])),
                # The 'Timestamp' column needs a higher minimum width than the other columns:
                minwidth=120,
            )
        else:
            base_tree.column(
                col_head,
                anchor="w",
                width=int((root.winfo_width() - 26) / len(base_tree["columns"])),
                minwidth=70,
            )
        # Name the column headers using the key values from the table used during import:
        base_tree.heading(col_head, text=col_head, anchor="w")
    for record in list_used:
        # Write all the records from the record list to the table, tagging each with its "Status" value:
        base_tree.insert(
            parent="",
            index="end",
            tags=[record["Status"]],
            values=tuple(record[x] for x in base_tree["columns"]),
        )
    # Don't apply any formatting to saved records:
    base_tree.tag_configure("Saved", background="white")
    # Apply a pale blue background to temp records:
    base_tree.tag_configure("Temporary", background="#E8F4FF")
    # Apply a pale orange background and gray text to deleted records:
    base_tree.tag_configure("Deleted", background="#FFEFDF", foreground="#AFAFAF")
    # Apply a light red background and bright red text to invalid records:
    base_tree.tag_configure("Invalid", background="#FFD8CF", foreground="#FF0000")


# Updated: All good for now.
def refresh_table(repop_tree: bool = True, master_log: bool = False):
    """
    Clears the contents of the viewport table, refreshes the contents of the master and filtered record lists, and then
    repopulates the viewport table with updated data.

    Args:
        repop_tree (bool, optional): Whether to repopulate the viewport table after clearing it. Set this to False for
            simply clearing the table. Defaults to True.
        master_log (bool, optional): Whether to send a Datalog message when repopulating the master record list. Set
            this to True when performing record modifications. Defaults to False.
    Raises: None
    Returns: None
    """
    # Clear the contents of the viewport table:
    clear_table()
    # Refresh the contents of 'stvars.records_master' (and optionally send a Datalog message):
    if master_log:
        pop_master(send_log=True)
    else:
        pop_master()
    # Refresh the contents of 'stvars.records_filter' using updated 'stvars.records_master' data:
    pop_filter()
    if repop_tree:
        # Repopulate the viewport table with data:
        pop_table()
    else:
        # If the table is to remain empty, remove all the column headers.
        base_tree["columns"] = []


# Updated: All good for now.
def reject_all():
    """
    Permanently removes all temporary records from the program.

    Args: None
    Raises: None
    Returns: None
    """
    # Only do anything if there are temp records loaded:
    if len(stvars.records_temp) > 0:
        # If there are any selected rows in the viewport, deselect them:
        if len(base_tree.selection()) > 0:
            base_tree.selection_remove(base_tree.selection()[0])
        iter8 = 0
        while len(stvars.records_temp) > 0:
            # Remove all records from the temp list:
            stvars.records_temp.remove(stvars.records_temp[0])
            iter8 += 1
        if iter8 > 0:
            # Pass a message to the Datalog if changes were made:
            log_msg(msg=(str(iter8) + " records were cleared from memory."))
            # Then refresh the table and have the master list pass its own message to the Datalog:
            refresh_table(master_log=True)


# Document: Add docstring and topline comments.
# ? See the 'Document' comment on 'commit_selection()' for why this function's documentation is pending.
def reject_selection():
    data_address = get_selection(stop_select=True)
    if data_address is not None:
        if data_address[0] == "Temporary":
            stvars.records_temp.remove(stvars.records_temp[data_address[1]])
            log_msg("1 record was cleared from memory.", popup=False)
            refresh_table(repop_tree=True)
            base_tree.selection_set(base_tree.get_children()[data_address[2]])
            base_tree.focus(base_tree.get_children()[data_address[2]])


# Document: Add docstring and topline comments.
# ? See the 'Document' comment on 'commit_selection()' for why this function's documentation is pending.
def restore_selection():
    data_address = get_selection(stop_select=True)
    if data_address is not None:
        if data_address[0] == "Deleted":
            if "" in stvars.records_deleted[data_address[1]].values():
                # * See the 'Notes' in 'commit_selection()' for why this raises a warning in PyCharm.
                stvars.records_deleted[data_address[1]]["Status"] = "Invalid"
                stvars.records_invalid.append(stvars.records_deleted[data_address[1]])
                stvars.records_deleted.remove(stvars.records_deleted[data_address[1]])
                log_msg("1 invalid record was restored to memory.", popup=False)
                refresh_table(repop_tree=True)
                base_tree.selection_set(base_tree.get_children()[data_address[2]])
                base_tree.focus(base_tree.get_children()[data_address[2]])
            else:
                # * See the 'Notes' in 'commit_selection()' for why this raises a warning in PyCharm.
                stvars.records_deleted[data_address[1]]["Status"] = "Saved"
                stvars.records_saved.append(stvars.records_deleted[data_address[1]])
                stvars.records_deleted.remove(stvars.records_deleted[data_address[1]])
                log_msg("1 record was restored to memory.", popup=False)
                refresh_table(repop_tree=True)
                base_tree.selection_set(base_tree.get_children()[data_address[2]])
                base_tree.focus(base_tree.get_children()[data_address[2]])


# Updated: All good for now.
def root_update():
    """
    A recreation of a traditional main loop run every 100 ms, written as a partial redirection of the 'mainloop()'
    function from 'tkinter' to allow custom updates to be defined in this file without overriding 'mainloop'.

    Args: None
    Raises: None
    Returns: None
    """
    # Toggle on the menu options and shortcut buttons associated with the record status of the selected row:
    if len(base_tree.selection()) > 0:
        select_toggle(state=True)
    # If no row is selected, toggle off menu options and shortcut buttons that rely on records:
    else:
        select_toggle(state=False)
    # If there are Datalog messages, enable the "Save Datalog Contents" menu option:
    if len(stvars.datalog_msgs) > 0:
        if view_menu.entrycget("Save Datalog Contents", option="state") == "disabled":
            view_menu.entryconfigure("Save Datalog Contents", state="normal")
    # If no Datalog contents, disable saving the Datalog:
    else:
        if view_menu.entrycget("Save Datalog Contents", option="state") == "normal":
            view_menu.entryconfigure("Save Datalog Contents", state="disabled")
    # Ensure the default treeview column stays hidden:
    base_tree.column("#0", width=0, stretch=False)
    # If all temp records have been accepted or rejected, reset the filename display to reflect this:
    if len(stvars.records_temp) == 0:
        status_file.configure(text="Unmanaged Records: None")
    else:
        # Make sure the status bar filename display updates when it changes:
        status_file.configure(
            text=(
                "Unmanaged Records: "
                + str(len(stvars.records_temp))
                + ' from "'
                + stvars.current_file
                + '"'
            )
        )
    # Make sure the status bar clock updates its timestamp:
    status_clock.configure(text=str(pd.Timestamp.now().round(freq="s")))
    # Schedule a call to 'root_update()' from 'mainloop()' after 100 ms:
    root.after(100, root_update)


# Updated: All good for now.
def save_log():
    """
    Saves the contents of 'stvars.datalog_msgs' to a text file in the user's "My Documents/SalesTrax/Datalog" folder and
    clears the contents of 'stvars.datalog_msgs'. Log files end with the date in "YYYY-MM-DD" format and an iterative
    3-digit index number that allows multiple logs to be saved on the same date without overwriting earlier logs.

    Args: None
    Raises: None
    Returns: None
    """
    # Do nothing if there are no messages in the Datalog:
    if len(stvars.datalog_msgs) > 0:
        # Get the path of the user's "C:/Users/{USERNAME}/" folder:
        path = str(os.path.expanduser("~\\"))
        # Add the leaf folders to the path:
        path = path + "Documents\\SalesTrax\\Datalog\\"
        # Create the "SalesTrax/Datalog/" directory if it doesn't already exist:
        if not os.path.exists(path=path):
            os.makedirs(name=path)
        # Get a timestamp for the time when this function was called:
        now = str(pd.Timestamp.now()).split(" ")
        # Add the date portion of the timestamp to the path to get a starting place for the filename:
        filename = path + "log_" + now[0]
        iter8 = 1
        # If a log file already exists for today, increment 'iter8' until it finds a filename that hasn't been used:
        while os.path.exists(path=(filename + "_" + "%03d" % iter8 + ".txt")):
            iter8 += 1
        # Once a unique filename has been found, finalize it:
        filename = filename + "_" + "%03d" % iter8 + ".txt"
        # Create the file and open it for writing:
        file = open(file=filename, mode="w")
        # Write each Datalog message to the file in chronological order:
        for msg in stvars.datalog_msgs:
            file.write(msg)
        # Close the file to save its contents:
        file.close()
        # Clear the contents of 'stvars.datalog_msgs' to prevent message doubling over multiple log files:
        # * This is really only necessary when the user manually saves the log.
        while len(stvars.datalog_msgs) > 0:
            stvars.datalog_msgs.remove(stvars.datalog_msgs[0])
        # Clear the contents of the 'datalog_body' Text object as well:
        datalog_body.delete("1.0", "end")


# Updated: All good for now.
def select_toggle(state: bool):
    """
    Enables and disables menu options, shortcut buttons, and keybindings based on the record status of the currently
    selected table row (or lack thereof).

    Args:
        state (bool): True when a row is selected, False when no row is selected.
    Raises: None
    Returns: None
    """
    if state:
        # Request information about which record is currently selected:
        data_address = get_selection(stop_select=False)
        # If the request comes back with no data, stop:
        if data_address is not None:
            if data_address[0] == "Temporary":
                # When a temp record is selected, enable events relating to individual temp records and disable those
                # that only act on other record statuses:
                if (
                    edit_menu.entrycget("Commit Selection", option="state")
                    == "disabled"
                ):
                    edit_menu.entryconfig("Commit Selection", state="normal")
                btn_commit_s.config(state="normal")
                if (
                    edit_menu.entrycget("Reject Selection", option="state")
                    == "disabled"
                ):
                    edit_menu.entryconfig("Reject Selection", state="normal")
                btn_reject_s.config(state="normal")
                if edit_menu.entrycget("Delete Selection", option="state") == "normal":
                    edit_menu.entryconfig("Delete Selection", state="disabled")
                btn_delete.config(state="disabled")
                if edit_menu.entrycget("Restore Selection", option="state") == "normal":
                    edit_menu.entryconfig("Restore Selection", state="disabled")
                btn_restore.config(state="disabled")
                # Reset keybindings that act on other record statuses and replace with relevant keybindings:
                root.unbind(sequence="<Return>")
                root.unbind(sequence="<Delete>")
                root.bind(sequence="<Return>", func=lambda event: commit_selection())
                root.bind(sequence="<Delete>", func=lambda event: reject_selection())
            elif (data_address[0] == "Saved") or (data_address[0] == "Invalid"):
                # When a saved or invalid record is selected, enable events relating to individual saved and invalid
                # records and disable those that only act on other record statuses:
                if edit_menu.entrycget("Commit Selection", option="state") == "normal":
                    edit_menu.entryconfig("Commit Selection", state="disabled")
                btn_commit_s.config(state="disabled")
                if edit_menu.entrycget("Reject Selection", option="state") == "normal":
                    edit_menu.entryconfig("Reject Selection", state="disabled")
                btn_reject_s.config(state="disabled")
                if (
                    edit_menu.entrycget("Delete Selection", option="state")
                    == "disabled"
                ):
                    edit_menu.entryconfig("Delete Selection", state="normal")
                btn_delete.config(state="normal")
                if edit_menu.entrycget("Restore Selection", option="state") == "normal":
                    edit_menu.entryconfig("Restore Selection", state="disabled")
                btn_restore.config(state="disabled")
                # Reset keybindings that act on other record statuses and replace with relevant keybindings:
                root.unbind(sequence="<Return>")
                root.unbind(sequence="<Delete>")
                root.bind(sequence="<Delete>", func=lambda event: delete_selection())
            elif data_address[0] == "Deleted":
                # When a deleted record is selected, enable events relating to individual deleted records and disable
                # those that only act on other record statuses:
                if edit_menu.entrycget("Commit Selection", option="state") == "normal":
                    edit_menu.entryconfig("Commit Selection", state="disabled")
                btn_commit_s.config(state="disabled")
                if edit_menu.entrycget("Reject Selection", option="state") == "normal":
                    edit_menu.entryconfig("Reject Selection", state="disabled")
                btn_reject_s.config(state="disabled")
                if edit_menu.entrycget("Delete Selection", option="state") == "normal":
                    edit_menu.entryconfig("Delete Selection", state="disabled")
                btn_delete.config(state="disabled")
                if (
                    edit_menu.entrycget("Restore Selection", option="state")
                    == "disabled"
                ):
                    edit_menu.entryconfig("Restore Selection", state="normal")
                btn_restore.config(state="normal")
                # Reset keybindings that act on other record statuses and replace with relevant keybindings:
                root.unbind(sequence="<Return>")
                root.unbind(sequence="<Delete>")
                root.bind(sequence="<Return>", func=lambda event: restore_selection())
    else:
        # If there is no selected row, disable all events and keybindings that act on individual records:
        if edit_menu.entrycget("Commit Selection", option="state") == "normal":
            edit_menu.entryconfig("Commit Selection", state="disabled")
        btn_commit_s.config(state="disabled")
        if edit_menu.entrycget("Reject Selection", option="state") == "normal":
            edit_menu.entryconfig("Reject Selection", state="disabled")
        btn_reject_s.config(state="disabled")
        if edit_menu.entrycget("Delete Selection", option="state") == "normal":
            edit_menu.entryconfig("Delete Selection", state="disabled")
        btn_delete.config(state="disabled")
        if edit_menu.entrycget("Restore Selection", option="state") == "normal":
            edit_menu.entryconfig("Restore Selection", state="disabled")
        btn_restore.config(state="disabled")
        root.unbind(sequence="<Return>")
        root.unbind(sequence="<Delete>")


# Updated: All good for now.
def toggle_datalog(state: bool = False):
    """
    Handles the visibility of the Datalog window. Technically speaking, it does not actually close when SalesTrax is
    running; it only hides.

    Args:
        state (bool, optional): When True, the Datalog becomes visible, and when False, it is hidden. Defaults to False.
    Raises: None
    Returns: None
    """
    if state:
        # Reveal the Datalog window:
        datalog.deiconify()
    else:
        # Hide the Datalog window:
        datalog.withdraw()


# Updated: All good for now.
def validate_temp():
    """
    Processes every individual record in the temp record list after importing to ensure they meet the requirements of
    the program. This may include combining similar keys (such as "Date" and "Time" into "Timestamp"), renaming keys to
    match existing records, checking user-defined validation strings to locate misspelled or incorrect names, locations,
    or product categories, etc.

    Args: None
    Raises: None
    Returns: None
    """
    # Define a dummy list for safer modification:
    data_loaded = list()
    # Loop through all records to ensure they are uniform in formatting:
    while len(stvars.records_temp) > 0:
        data_loaded.append(stvars.records_temp[0])
        stvars.records_temp.remove(stvars.records_temp[0])
    for record in data_loaded:
        # If the 'Time' column contains a data type other than Timedelta, convert it to a Timedelta:
        if "Time" in record.keys():
            if type(record["Time"]) != pd.Timedelta:
                record["Time"] = pd.Timedelta(str(record["Time"]))
        # If the 'Timestamp' or 'Date' column contains a datatype other than Timestamp, convert it to a Timestamp:
        if "Timestamp" in record.keys():
            if type(record["Timestamp"]) != pd.Timestamp:
                record["Timestamp"] = pd.Timestamp(record["Timestamp"])
        elif "Date" in record.keys():
            if type(record["Date"]) != pd.Timestamp:
                record["Date"] = pd.Timestamp(record["Date"])
        # If both 'Date' and 'Time' columns exist, combine them into a 'Date' column:
        if ("Date" in record.keys()) and ("Time" in record.keys()):
            record["Date"] = record["Date"] + record["Time"]
            # Now delete the 'Time' column:
            del record["Time"]
        # Ensure timestamps are not fractional by rounding to the nearest second ("freq='min'" for minute rounding):
        # * This *shouldn't* be necessary, but occasionally, timestamps are imported with additional milliseconds that
        # * aren't in the source document. It appears to occur when datetime values are auto-populated by Excel rather
        # * than having been manually entered. Note that this error is exclusive to Excel sheets, and does not occur in
        # * in CSV or ODS documents.
        if "Date" in record.keys():
            record["Date"] = pd.Timestamp(record["Date"]).round(freq="s")
        elif "Timestamp" in record.keys():
            record["Timestamp"] = pd.Timestamp(record["Timestamp"]).round(freq="s")
        # Ensure both currency fields are rounded to the nearest cent:
        # * Again, this *shouldn't* be necessary, but 'Net Total' occasionally has bits flipped that shouldn't be.
        # * This also appears to be a result of calculation errors in Excel, as it only happens in cells that either
        # * contain formulas or had their contents auto-filled with data in the source Excel document. And again, this
        # * doesn't happen at all in CSV or ODS documents--only in Excel.
        if "Cost" in record.keys():
            if type(record["Cost"]) != str:
                record["Cost"] = round(record["Cost"], 2)
        elif "Unit Cost" in record.keys():
            if type(record["Unit Cost"]) != str:
                record["Unit Cost"] = round(record["Unit Cost"], 2)
        if "Total" in record.keys():
            if type(record["Total"]) != str:
                record["Total"] = round(record["Total"], 2)
        elif "Net Total" in record.keys():
            if type(record["Net Total"]) != str:
                record["Net Total"] = round(record["Net Total"], 2)
    # If a 'Date' column exists, rename it to 'Timestamp' for later referencing. Since dictionary keys can't be
    # renamed without reordering them, do this through a DataFrame instead. Inefficient, yes, but it works with only
    # three lines instead of thirty for manual renaming and reordering.
    if "Date" in data_loaded[0].keys():
        data_loaded = pd.DataFrame.from_records(data_loaded)
        data_loaded = data_loaded.rename({"Date": "Timestamp"}, axis="columns")
        # Now turn it back into a dictionary list, since it doesn't need to be a DataFrame anymore.
        data_loaded = data_loaded.to_dict(orient="records")
    # Define a list of acceptable terms for "Location" columns:
    location_list = [
        "Area",
        "District",
        "Location ID",
        "Location Number",
        "Region",
        "Shop",
        "Site",
        "Store",
        "Store ID",
        "Store Number",
        "Venue",
    ]
    # If any of the list terms are used for column names, replace them with the default "Location":
    for item in location_list:
        if item in data_loaded[0].keys():
            data_loaded = pd.DataFrame.from_records(data_loaded)
            data_loaded = data_loaded.rename({item: "Location"}, axis="columns")
            # Now turn it back into a dictionary list, since it doesn't need to be a DataFrame anymore.
            data_loaded = data_loaded.to_dict(orient="records")
    # Define a list of acceptable terms for "Employee" columns:
    employee_list = [
        "Account",
        "Cashier",
        "Clerk",
        "Rep",
        "Representative",
        "Sales Rep",
        "Sales Representative",
        "Salesman",
        "Salesperson",
        "Worker",
    ]
    # If any of the list terms are used for column names, replace them with the default "Employee":
    for item in employee_list:
        if item in data_loaded[0].keys():
            data_loaded = pd.DataFrame.from_records(data_loaded)
            data_loaded = data_loaded.rename({item: "Employee"}, axis="columns")
            # Now turn it back into a dictionary list, since it doesn't need to be a DataFrame anymore.
            data_loaded = data_loaded.to_dict(orient="records")
    # Define a list of acceptable terms for "Product" columns:
    product_list = ["Description", "Item", "Merch", "Merchandise"]
    # If any of the list terms are used for column names, replace them with the default "Product":
    for item in product_list:
        if item in data_loaded[0].keys():
            data_loaded = pd.DataFrame.from_records(data_loaded)
            data_loaded = data_loaded.rename({item: "Product"}, axis="columns")
            # Now turn it back into a dictionary list, since it doesn't need to be a DataFrame anymore.
            data_loaded = data_loaded.to_dict(orient="records")
    # Define a list of acceptable terms for "Count" columns:
    count_list = ["Quantity", "Qty", "Units"]
    # If any of the list terms are used for column names, replace them with the default "Count":
    for item in count_list:
        if item in data_loaded[0].keys():
            data_loaded = pd.DataFrame.from_records(data_loaded)
            data_loaded = data_loaded.rename({item: "Count"}, axis="columns")
            # Now turn it back into a dictionary list, since it doesn't need to be a DataFrame anymore.
            data_loaded = data_loaded.to_dict(orient="records")
    # Define a list of acceptable terms for "Cost" columns:
    cost_list = ["Price", "Rate", "Unit Cost", "Unit Price"]
    # If any of the list terms are used for column names, replace them with the default "Cost":
    for item in cost_list:
        if item in data_loaded[0].keys():
            data_loaded = pd.DataFrame.from_records(data_loaded)
            data_loaded = data_loaded.rename({item: "Cost"}, axis="columns")
            # Now turn it back into a dictionary list, since it doesn't need to be a DataFrame anymore.
            data_loaded = data_loaded.to_dict(orient="records")
    # Define a list of acceptable terms for "Total" columns:
    total_list = [
        "Grand Total",
        "Gross",
        "Gross Total",
        "Net",
        "Net Total",
        "Result",
        "Sum",
    ]
    # If any of the list terms are used for column names, replace them with the default "Total":
    for item in total_list:
        if item in data_loaded[0].keys():
            data_loaded = pd.DataFrame.from_records(data_loaded)
            data_loaded = data_loaded.rename({item: "Total"}, axis="columns")
            # Now turn it back into a dictionary list, since it doesn't need to be a DataFrame anymore.
            data_loaded = data_loaded.to_dict(orient="records")
    # Ensure the data is sorted by timestamp, from oldest to most recent:
    # * Note that 'reverse' defaults to False, so this isn't actually needed, but I'm leaving it there anyway.
    if "Timestamp" in data_loaded[0].keys():
        data_loaded.sort(key=lambda d: d["Timestamp"], reverse=False)
    # Check to make sure the record isn't already loaded in a different list:
    iter8 = 0
    record = 0
    while record < len(data_loaded):
        rec = 0
        while rec < len(stvars.records_master):
            # Define a list of keys used in the record:
            keys = list(data_loaded[record].keys())
            # Remove the 'Status' key from the comparison list (because they WON'T match):
            keys.remove(keys[len(keys) - 1])
            # Now compare the key values from 'data_loaded' with the key values from 'stvars.records_master':
            if all(
                data_loaded[record].get(key) == stvars.records_master[rec].get(key)
                for key in keys
            ):
                # If they match, exclude the record and increment the exclusion counter:
                data_loaded.remove(data_loaded[record])
                iter8 += 1
            rec += 1
        # Now make sure the record didn't have a duplicate in the source file:
        while rec < len(stvars.records_temp):
            # In this case, the 'Status' keys would be the same, so we can just compare the entire dictionary:
            if data_loaded[record] == stvars.records_temp[rec]:
                # Again, if there's a match, exclude it from import and increment the exclusion counter.
                data_loaded.remove(data_loaded[record])
                iter8 += 1
            rec += 1
        record += 1
    if iter8 > 0:
        # Send any exclusion records to the Datalog along with a popup.
        log_msg(msg=(str(iter8) + " duplicate records were excluded from import."))
    # Move the records from the validation list into 'stvars.records_temp' for persistent storage:
    iter8 = 0
    invalid8 = 0
    while len(data_loaded) > 0:
        if "" in data_loaded[0].values():
            data_loaded[0]["Status"] = "Invalid"
            stvars.records_invalid.append(data_loaded[0])
            data_loaded.remove(data_loaded[0])
            # Count the number of successful record imports:
            invalid8 += 1
        else:
            stvars.records_temp.append(data_loaded[0])
            data_loaded.remove(data_loaded[0])
            # Count the number of successful record imports:
            iter8 += 1
    if iter8 > 0:
        # Send the success count to the Datalog along with a popup.
        log_msg(msg=(str(iter8) + " records were successfully imported."))
    if invalid8 > 0:
        # Send the success count to the Datalog along with a popup.
        log_msg(msg=(str(invalid8) + " invalid records were imported."))
    # Refresh the viewport table and log the number of records currently loaded.
    refresh_table(master_log=True)


# Placeholder:
def view_temp():
    pass


# Incomplete: See "Task" comment in function body for details.
def write_file(path: str):
    """
    Writes all records with "Saved" status to a CSV, ODS, or XLSX file.

    Args:
        path (str): The filename and location of the new/updated file.
    Raises: None
    Returns: None
    """
    # Create a 'pandas' DataFrame object from the records in 'stvars.records_saved':
    data_frame = pd.DataFrame(stvars.records_saved)
    # Remove the "Status" column from the DataFrame:
    data_frame = data_frame.drop(columns="Status")
    if path.split(".")[-1] == "csv":
        # Write the DataFrame to disk in CSV format:
        data_frame.to_csv(path, float_format="%.2f", index=False)
    elif path.split(".")[-1] == "ods":
        # Task: This is a temporary fix for how the ODS writer formats datetime objects when exporting.
        # & Create a question popup asking if the user wants it in string format or as an integer. Keep reading.
        # & In either case, they are still read in accurately as Timestamps in SalesTrax, but in OpenOffice, the
        # & 'Timestamp' column displays as an integer value by default, not a proper datetime. For example,
        # & '2021-01-23 00:00:00' writes to OpenOffice as '44219'. It converts back to its accurate timestamp if the
        # & cell is formatted as a date value, but the user won't necessarily know to do that. This is an issue with the
        # & 'openpyxl' Excel Writer, so it's not something I can fix, but it is a problem I can mitigate by informing
        # & the user of the issue and offering them both a choice and a bandaid.
        # Convert the contents of the "Timestamp" column to strings when writing to ODS:
        data_frame = data_frame.astype({"Timestamp": "string"})
        # Write the DataFrame to disk in ODS format:
        data_frame.to_excel(path, float_format="%.2f", index=False)
    else:
        # Write the DataFrame to disk in XLSX format:
        data_frame.to_excel(path, float_format="%.2f", index=False)


# HEADLINE: Object Definitions
# Section: Root 'tkinter' window
# Open base window
root = tk.Tk()
# Set default (restore) size:
root.geometry("1200x675")
# Set custom title bar icon:
root.iconbitmap("Images/salestrax_icon_bw.ico")
# Set title bar name:
root.title("SalesTrax")
# Maximize window:
root.state("zoomed")
# Redirect the "X" button to perform exit functions prior to closing the program:
root.protocol("WM_DELETE_WINDOW", func=exit_functions)

# Section: Menu-driven checkbox toggles
# Updated: All good for now.
toggle_saved = tk.IntVar(root)
toggle_temp = tk.IntVar(root)
toggle_invalid = tk.IntVar(root)
toggle_deleted = tk.IntVar(root)

# Section: Menu Bar
# Updated: All good for now.
# Define the menu bar itself:
menu_bar = tk.Menu(root)
# Define the "File" menu and its commands:
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Import From...", command=check_temp_count)
file_menu.add_command(label="Export To...", state="disabled", command=export_file)
file_menu.add_command(label="Clear All Data", state="disabled", command=clear_all_data)
file_menu.add_separator()
file_menu.add_command(label="Exit SalesTrax", command=exit_functions)
# Finalize the contents of the "File" menu:
menu_bar.add_cascade(label="File", menu=file_menu)
# Define the "Edit Menu" and its commands:
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Refresh Table", state="disabled", command=refresh_table)
edit_menu.add_separator()
edit_menu.add_command(
    label="Commit Selection", state="disabled", command=commit_selection
)
edit_menu.add_command(label="Commit All", state="disabled", command=commit_all)
edit_menu.add_command(
    label="Reject Selection", state="disabled", command=reject_selection
)
edit_menu.add_command(label="Reject All", state="disabled", command=reject_all)
edit_menu.add_separator()
edit_menu.add_command(
    label="Delete Selection", state="disabled", command=delete_selection
)
edit_menu.add_command(
    label="Restore Selection", state="disabled", command=restore_selection
)
# Finalize the contents of the "Edit" menu:
menu_bar.add_cascade(label="Edit", menu=edit_menu)
# Define the "View Menu" and its commands:
view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.add_checkbutton(
    label="Hide Saved Records",
    state="disabled",
    offvalue=0,
    onvalue=1,
    variable=toggle_saved,
    command=log_msg,
)
view_menu.add_checkbutton(
    label="Hide Temporary Records",
    state="disabled",
    offvalue=0,
    onvalue=1,
    variable=toggle_temp,
    command=log_msg,
)
view_menu.add_checkbutton(
    label="Hide Invalid Records",
    offvalue=0,
    onvalue=1,
    variable=toggle_invalid,
    state="disabled",
    command=log_msg,
)
view_menu.add_checkbutton(
    label="Hide Deleted Records",
    offvalue=0,
    onvalue=1,
    variable=toggle_deleted,
    state="disabled",
    command=log_msg,
)
view_menu.add_separator()
view_menu.add_command(label="Open Datalog Window", command=lambda: toggle_datalog(True))
view_menu.add_command(label="Save Datalog Contents", state="disabled", command=save_log)
view_menu.add_separator()
view_menu.add_checkbutton(
    label="Toggle Filter...", offvalue=0, onvalue=1, state="disabled", command=log_msg
)
# Finalize the contents of the "Edit" menu:
menu_bar.add_cascade(label="View", menu=view_menu)
# Define the "Lists" menu and its commands:
list_menu = tk.Menu(menu_bar, tearoff=0)
list_menu.add_command(label="Employees", command=log_msg)
list_menu.add_command(label="Locations", command=log_msg)
list_menu.add_command(label="Product Categories", command=log_msg)
# Finalize the contents of the "Lists" menu:
menu_bar.add_cascade(label="Lists", menu=list_menu)
# Define the "Generate" menu and its commands:
data_menu = tk.Menu(menu_bar, tearoff=0)
data_menu.add_command(label="Line Chart", state="disabled", command=log_msg)
data_menu.add_command(label="Bar Chart", state="disabled", command=log_msg)
data_menu.add_command(label="Pie Chart", state="disabled", command=log_msg)
# Finalize the contents of the "Generate" menu:
menu_bar.add_cascade(label="Generate", menu=data_menu)
# Define the "Help" menu and its commands:
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="User Manual", command=log_msg)
help_menu.add_command(label="Changelog", command=log_msg)
help_menu.add_separator()
help_menu.add_command(label="Online Docs...", command=log_msg)
help_menu.add_command(label="GitHub Issues...", command=log_msg)
# Finalize the contents of the "Help" menu:
menu_bar.add_cascade(label="Help", menu=help_menu)
# Assign the menu bar to 'root':
root.config(menu=menu_bar)

# Section: Shortcut bar
# Define button images for the shortcut bar:
img_import = ImageTk.PhotoImage(Image.open("Images/20/import.png"))
img_export = ImageTk.PhotoImage(Image.open("Images/20/export.png"))
img_commit_s = ImageTk.PhotoImage(Image.open("Images/20/commit_selection.png"))
img_commit_a = ImageTk.PhotoImage(Image.open("Images/20/commit_all.png"))
img_reject_s = ImageTk.PhotoImage(Image.open("Images/20/reject_selection.png"))
img_reject_a = ImageTk.PhotoImage(Image.open("Images/20/reject_all.png"))
img_delete = ImageTk.PhotoImage(Image.open("Images/20/delete_selection.png"))
img_restore = ImageTk.PhotoImage(Image.open("Images/20/restore_selection.png"))
img_refresh = ImageTk.PhotoImage(Image.open("Images/20/refresh_view.png"))
img_hide_saved = ImageTk.PhotoImage(Image.open("Images/20/hide_saved.png"))
img_hide_temp = ImageTk.PhotoImage(Image.open("Images/20/hide_temp.png"))
img_hide_invalid = ImageTk.PhotoImage(Image.open("Images/20/hide_invalid.png"))
img_hide_deleted = ImageTk.PhotoImage(Image.open("Images/20/hide_deleted.png"))
img_employee = ImageTk.PhotoImage(Image.open("Images/20/employees.png"))
img_location = ImageTk.PhotoImage(Image.open("Images/20/locations.png"))
img_category = ImageTk.PhotoImage(Image.open("Images/20/categories.png"))
img_filter = ImageTk.PhotoImage(Image.open("Images/20/filter.png"))
img_line = ImageTk.PhotoImage(Image.open("Images/20/chart_line.png"))
img_bar = ImageTk.PhotoImage(Image.open("Images/20/chart_bar.png"))
img_pie = ImageTk.PhotoImage(Image.open("Images/20/chart_pie.png"))
img_help = ImageTk.PhotoImage(Image.open("Images/20/help.png"))
img_logo = ImageTk.PhotoImage(Image.open("Images/Logo/salestrax_logo_24.png"))
# Define the container for the shortcut bar:
# * Note that the container is not actually visible. The "bar" behind the buttons is not actually a bar; it's just empty
# * background space that looks like a bar because of the objects around it.
shortcut_bar = tk.Frame(root, height=28)
# Define button attributes:
btn_import = tk.Button(shortcut_bar, image=img_import, command=check_temp_count)
btn_export = tk.Button(
    shortcut_bar, image=img_export, state="disabled", command=export_file
)
btn_commit_s = tk.Button(
    shortcut_bar, image=img_commit_s, state="disabled", command=commit_selection
)
btn_commit_a = tk.Button(
    shortcut_bar, image=img_commit_a, state="disabled", command=commit_all
)
btn_reject_s = tk.Button(
    shortcut_bar, image=img_reject_s, state="disabled", command=reject_selection
)
btn_reject_a = tk.Button(
    shortcut_bar, image=img_reject_a, state="disabled", command=reject_all
)
btn_delete = tk.Button(
    shortcut_bar, image=img_delete, state="disabled", command=delete_selection
)
btn_restore = tk.Button(
    shortcut_bar, image=img_restore, state="disabled", command=restore_selection
)
btn_refresh = tk.Button(
    shortcut_bar, image=img_refresh, state="disabled", command=refresh_table
)
btn_hide_saved = tk.Button(
    shortcut_bar, image=img_hide_saved, state="disabled", command=log_msg
)
btn_hide_temp = tk.Button(
    shortcut_bar, image=img_hide_temp, state="disabled", command=log_msg
)
btn_hide_invalid = tk.Button(
    shortcut_bar, image=img_hide_invalid, state="disabled", command=log_msg
)
btn_hide_deleted = tk.Button(
    shortcut_bar, image=img_hide_deleted, state="disabled", command=log_msg
)
btn_employee = tk.Button(shortcut_bar, image=img_employee, command=log_msg)
btn_location = tk.Button(shortcut_bar, image=img_location, command=log_msg)
btn_category = tk.Button(shortcut_bar, image=img_category, command=log_msg)
btn_filter = tk.Button(
    shortcut_bar, image=img_filter, state="disabled", command=log_msg
)
btn_line = tk.Button(shortcut_bar, image=img_line, state="disabled", command=log_msg)
btn_bar = tk.Button(shortcut_bar, image=img_bar, state="disabled", command=log_msg)
btn_pie = tk.Button(shortcut_bar, image=img_pie, state="disabled", command=log_msg)
btn_help = tk.Button(shortcut_bar, image=img_help, command=log_msg)
# The logo button gets special treatment, because it includes both text and an image:
btn_logo = tk.Button(
    shortcut_bar,
    image=img_logo,
    text="SalesTrax v0.1.0 ",
    font='"consolas" 12 italic bold',
    fg="gray",
    activebackground="black",
    activeforeground="white",
    compound="right",
    padx=8,
    border=0,
    command=link_to_github,
)
# Put the buttons in a logical order on the shortcut bar, separated by menu category:
shortcut_bar.pack(side="top", fill="x")
btn_import.pack(side="left", padx=(5, 1), pady=2)
btn_export.pack(side="left", padx=(1, 8), pady=2)
btn_commit_s.pack(side="left", padx=(8, 1), pady=2)
btn_commit_a.pack(side="left", padx=1, pady=2)
btn_reject_s.pack(side="left", padx=1, pady=2)
btn_reject_a.pack(side="left", padx=1, pady=2)
btn_delete.pack(side="left", padx=1, pady=2)
btn_restore.pack(side="left", padx=(1, 8), pady=2)
btn_refresh.pack(side="left", padx=(8, 1), pady=2)
btn_hide_saved.pack(side="left", padx=1, pady=2)
btn_hide_temp.pack(side="left", padx=1, pady=2)
btn_hide_invalid.pack(side="left", padx=1, pady=2)
btn_hide_deleted.pack(side="left", padx=1, pady=2)
btn_filter.pack(side="left", padx=(1, 8), pady=2)
btn_employee.pack(side="left", padx=(8, 1), pady=2)
btn_location.pack(side="left", padx=1, pady=2)
btn_category.pack(side="left", padx=(1, 8), pady=2)
btn_line.pack(side="left", padx=(8, 1), pady=2)
btn_bar.pack(side="left", padx=1, pady=2)
btn_pie.pack(side="left", padx=(1, 8), pady=2)
btn_help.pack(side="left", padx=(8, 1), pady=2)
btn_logo.pack(side="right", padx=(0, 5))
# Define button tooltips:
ToolTip(btn_import, msg="Import From...", delay=0.2, follow=True)
ToolTip(btn_export, msg="Export To...", delay=0.2, follow=True)
ToolTip(btn_commit_s, msg="Commit Selection", delay=0.2, follow=True)
ToolTip(btn_commit_a, msg="Commit All", delay=0.2, follow=True)
ToolTip(btn_reject_s, msg="Reject Selection", delay=0.2, follow=True)
ToolTip(btn_reject_a, msg="Reject All", delay=0.2, follow=True)
ToolTip(btn_delete, msg="Delete Selection", delay=0.2, follow=True)
ToolTip(btn_restore, msg="Restore Selection", delay=0.2, follow=True)
ToolTip(btn_refresh, msg="Refresh Table", delay=0.2, follow=True)
ToolTip(btn_hide_saved, msg="Hide Saved Records", delay=0.2, follow=True)
ToolTip(btn_hide_temp, msg="Hide Temporary Records", delay=0.2, follow=True)
ToolTip(btn_hide_invalid, msg="Hide Invalid Records", delay=0.2, follow=True)
ToolTip(btn_hide_deleted, msg="Hide Deleted Records", delay=0.2, follow=True)
ToolTip(btn_filter, msg="Toggle Filter...", delay=0.2, follow=True)
ToolTip(btn_employee, msg="Employee List", delay=0.2, follow=True)
ToolTip(btn_location, msg="Location List", delay=0.2, follow=True)
ToolTip(btn_category, msg="Product Category List", delay=0.2, follow=True)
ToolTip(btn_line, msg="Generate Line Chart", delay=0.2, follow=True)
ToolTip(btn_bar, msg="Generate Bar Chart", delay=0.2, follow=True)
ToolTip(btn_pie, msg="Generate Pie Chart", delay=0.2, follow=True)
ToolTip(btn_help, msg="User Manual", delay=0.2, follow=True)
ToolTip(btn_logo, msg="SalesTrax on GitHub", delay=0.2, follow=True)

# Section: Primary viewport table
# Future: For now, only one record can be selected at a time.
# $ Try to find a way to include multiple selections in the 'get_selection()' function to support batch actions.
# $ Once that is figured out, set 'selectmode="extended"' to allow multiple record selection.
# Define the Treeview object:
base_tree = ttk.Treeview(root, selectmode="browse")
# Ensure that the default Treeview column takes up the entire Treeview area:
base_tree.column("#0", width=(root.winfo_width() - 10))
base_tree.heading("#0", text="", anchor="w")
# Place the table and set its height and width to take up most of the space in 'root':
base_tree.pack(side="top", expand=True, fill="both", padx=5)
# Define a vertical scrollbar for the Treeview object:
scroll_tree = ttk.Scrollbar(base_tree, orient="vertical", command=base_tree.yview)
# Assign it to the entire right side of the viewport:
scroll_tree.pack(side="right", fill="y")
# Link the Treeview object's contents to the scrollbar:
base_tree.configure(yscrollcommand=scroll_tree.set)
# Disable manual column resizing by interrupting left-clicks when the mouse is positioned over a column separator:
base_tree.bind("<Button-1>", func=disable_resize)
# Also prevent the mouse from switching to the "resize" mouse image under the same circumstance:
base_tree.bind("<Motion>", func=disable_resize)

# Section: Status bar
# Incomplete: Replace status bar content with something actually useful.
# Define status bar frame:
status_bar = tk.Frame(root)
# Add a filename display to the status bar:
# * This will be populated with the filename of the most recently loaded file once one has been loaded.
status_file = tk.Label(
    status_bar, text="Unmanaged Records: None", anchor="w", padx=5, foreground="#585858"
)
# Add a clock to the status bar:
status_clock = tk.Label(
    status_bar,
    text=str(pd.Timestamp.now().round(freq="s")),
    anchor="e",
    padx=5,
    foreground="#585858",
)
# Assign the status bar to take up the full width of the bottom of 'root'.
status_bar.pack(side="bottom", fill="x")
# Place the filename display on the left side of the status bar:
status_file.pack(side="left")
# Place the clock on the right side of the status bar:
status_clock.pack(side="right")

# Section: Datalog window
# Define Datalog window:
datalog = tk.Toplevel(root)
# Set the size of the window:
datalog.geometry("800x400")
# Set the contents of the Datalog's title bar:
datalog.title("SalesTrax Datalog")
datalog.iconbitmap("Images/salestrax_icon_bw.ico")
# Give it a black background, so it looks like a command prompt:
datalog.configure(bg="black")
# Redirect the "X" button on the window to simply hide the Datalog instead of closing it:
datalog.protocol("WM_DELETE_WINDOW", toggle_datalog)
# Hide the Datalog by default when SalesTrax starts:
datalog.withdraw()
# Define a 'tkinter' Text object to display messages with the appearance of a command prompt:
datalog_body = tk.Text(datalog, bg="black", fg="white", border=0, wrap="word")
# Make the Text object take up the entire Datalog window:
datalog_body.pack(side="left", fill="both", expand=True)
# Define a scrollbar for the Text object:
scroll_log = ttk.Scrollbar(
    datalog_body, orient="vertical", command=datalog_body.yview, cursor="arrow"
)
# Assign the scrollbar to the entire right edge of the window:
scroll_log.pack(side="right", fill="y")
# Disable the user's ability to write to the Datalog themselves:
datalog_body.configure(yscrollcommand=scroll_log.set, state="disabled")

# Section: Misc objects
# Define images for popup windows:
img_question = ImageTk.PhotoImage(Image.open("Images/32/question.png"))
# Apply global window theme:
glb_theme = ttk.Style(root).theme_use("winnative")

# HEADLINE: Program initiators
# Begin custom update loop:
root_update()
# Start the 'tkinter' mainloop() function:
root.mainloop()
