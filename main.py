"""
Program Name: SalesTrax
Version: 0.1.5
Status: Prototype
Created on: 2023-04-09
Last updated: 2023-04-30
Created with: Python 3.11.2
Author: Danny Fleenor
Contributors:
    - Alex Clark, Fredrik Lundh, Secret Labs AB: _PIL_ image processing library
    - Anonymous Contributors: Python standard _OS_ library
    - DaedalicEntertainment: _Tktooltip_ tooltip module
    - Danny Fleenor: Program design and development; logo image
    - Fredrik Lundh, Guido van Rossum, Steen Lumholt: _Tkinter_ GUI library
    - Georg Brandl: _Webbrowser_ browser interface library
    - Isarra (Wikimedia Commons): Question mark image
    - J. D. Hunter: _Matplotlib_ figure generation library
    - Mockaroo LLC: Generation of large mock datasets
    - Wes McKinney: _Pandas_ file import library
    - www.aha-soft.com: Shortcut bar images

Description:
    As a Disclaimer™, I find it worth mentioning that this is a college project begun after only three weeks of learning
    Python. In absolutely no way will I claim it is perfect. By choosing to use this program, you accept responsibility
    for the fallout of potentially clumsy coding. It is not designed to be harmful, of course, but I cannot attest to
    how your system may or may not react to it; I'm not well-versed enough in Python programming to know that.

    Having said that, at this time, SalesTrax functions as a simple file merger and data visualizer for tabular
    financial documents. It reads CSV, ODS, and Excel documents, removes duplicate records, and provides a framework for
    manual record exclusions in the output file, which include CSV, ODS, and XLSX format. Note that any imported
    documents should have consistent column ordering between files, but there are no other solid requirements for file
    content.

NOTES regarding PyCharm:
    When editing this file in PyCharm, the program will raise a total of 33 warnings and 4 light warnings, none of which
    are legitimate problems. I've pointed most of them out in comments where they occur, but I thought I should go ahead
    and mention them here as well. Most of them stem from PyCharm incorrectly recognizing dictionaries as lists, some
    fail to recognize lists as lists, and others warn about direct object references that are intentional. In any case,
    all 33 warnings and 4 light warning are illegitimate, and attempting to correct them WILL break the program (trust
    me, I tried it). Just do your best to ignore them, or better yet, view the file in Visual Studio Code, which doesn't
    throw any warnings at all.
"""
# Section: Imports
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
from PIL import Image, ImageTk
from tktooltip import ToolTip


# Section: Variable class
# * This isn't actually needed for the list variables, but other datatypes can't be modified in functions without either
# * global or class definition. I chose class definition, as nearly every source I've found on the topic specifically
# * warns against global variables in almost all cases.
class StVars:
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
    # Validation strings for the 'Department' field
    valid_departments = list()
    # Validation strings for the 'Employee' field
    valid_employees = list()
    # Validation strings for the 'Location' field
    valid_locations = list()

    # The path for most recently imported document with temp records still active:
    current_file = str()
    # Whether a filter and/or sort is currently active:
    filter_toggle = bool()
    # The width of the primary monitor (used for positioning popups):
    monitor_width = int()
    # The height of the primary monitor (used for positioning popups):
    monitor_height = int()
    # Whether the Validation Control window is visible (used for updating validation lists):
    notebook_on = bool()
    # Whether or not 'odfpy' is installed
    odf_installed = bool()
    # The column by which to sort records:
    sort_column = str()
    # Whether to sort 'sort_column' in ascending or descending order:
    sort_descending = bool(True)
    # Empty list to store references for dynamically created total bar entry boxes:
    total_refs = list()
    # Empty list to store the values of the items inserted into 'total_refs':
    total_values = list()


# HEADLINE: Function definitions
# Updated: All good for now.
def bar_definition():
    """
    Opens a window for selecting the requirements for generating and viewing bar charts.
    """
    # Define the base toplevel:
    window = tk.Toplevel(root, padx=5, pady=5)
    # Set the title bar contents:
    window.title("Bar Chart")
    window.iconbitmap("Images/salestrax_icon_bw.ico")
    # Set the window size based on the user's monitor size and center it:
    window.geometry(
        (
            # 70% monitor width:
            str(int(StVars.monitor_width * 0.7))
            + "x"
            # 80% monitor height:
            + str(int(StVars.monitor_height * 0.8))
            + "+"
            # Center horizontally:
            + str(
                int((StVars.monitor_width / 2) - ((StVars.monitor_width * 0.35) + 25))
            )
            + "+"
            # Center vertically:
            + str(
                int((StVars.monitor_height / 2) - ((StVars.monitor_height * 0.4) + 25))
            )
        )
    )
    # Define the base layout frames for organizational setup:
    # Ensure the frame that holds the bar chart is visible even when empty (otherwise, the window looks incomplete):
    top_frame = tk.Frame(window, bg="white", border=2, relief="groove")
    bottom_frame = tk.Frame(window)
    # Define the frames for the 'matplotlib' toolbar and the axis choice area:
    tool_frame = tk.Frame(bottom_frame)
    button_frame = tk.Frame(bottom_frame)
    # Define the frame for the labels and entry boxes:
    left_frame = tk.Frame(button_frame)
    # Define the frame for the control buttons:
    right_frame = tk.Frame(button_frame)
    # Define the frame for the x-axis label and entry box:
    x_frame = tk.Frame(left_frame)
    # Define the frame for the x-axis label and entry box:
    y_frame = tk.Frame(left_frame)
    # X-axis label:
    x_label = tk.Label(x_frame, text="X-Axis")
    # Combo box for defining the x-axis to use in the bar chart:
    x_combo = ttk.Combobox(x_frame, values=list(base_tree["columns"]))
    # Y-axis label:
    y_label = tk.Label(y_frame, text="Y-Axis")
    # Combo box for defining the y-axis to use in the bar chart:
    y_combo = ttk.Combobox(y_frame, values=list(base_tree["columns"]))
    # Define the "OK" button:
    ok_button = tk.Button(
        right_frame,
        text="OK",
        width=10,
        command=lambda: [
            top_frame.winfo_children()[0].destroy()
            if len(top_frame.winfo_children()) > 0
            else do_nothing(),
            tool_frame.winfo_children()[0].destroy()
            if len(tool_frame.winfo_children()) > 0
            else do_nothing(),
            bar_generation(x_combo.get(), y_combo.get(), top_frame, tool_frame),
        ]
        if x_combo.get() != ""
        and y_combo.get() != ""
        and x_combo.get() != y_combo.get()
        and type(StVars.records_master[0][y_combo.get()]) != str
        else [
            log_msg("SalesTrax cannot visualize non-numerical data."),
            window.focus_force(),
        ],
    )
    # Define the "Cancel" button:
    cancel_button = tk.Button(
        right_frame, text="Cancel", width=10, command=window.destroy
    )
    # Place all the objects in their respective frames:
    top_frame.pack(side="top", fill="both", expand=True, padx=2, pady=(2, 0))
    bottom_frame.pack(side="bottom", fill="x")
    tool_frame.pack(side="left", padx=(10, 0), pady=(0, 80), anchor="nw")
    button_frame.pack(side="right", anchor="se")
    left_frame.pack(side="left", padx=(0, 10), pady=(30, 40))
    right_frame.pack(side="right", padx=(10, 40), pady=(30, 40))
    x_frame.pack(side="top")
    y_frame.pack(side="bottom")
    x_label.pack(side="left")
    x_combo.pack(side="right")
    y_label.pack(side="left")
    y_combo.pack(side="right")
    ok_button.pack(side="top")
    cancel_button.pack(side="bottom")
    # If there is an active sort, auto-populate the x-axis combobox with it:
    if StVars.sort_column != "":
        x_combo.set(StVars.sort_column)
    else:
        # Otherwise, use "Timestamp", if possible (don't auto-populate the x-axis combobox if no sort or "Timestamp"):
        if "Timestamp" in list(base_tree["columns"]):
            x_combo.set("Timestamp")


# Updated: All good for now.
def bar_generation(x: str, y: str, chart, bar):
    """
    Populates the "Bar Chart" window viewport with a bar chart as defined in 'bar_definition()'.

    Args:
        x (str): The name of the table column to use for the x-axis.
        y (str): The name of the table column to use for the y-axis.
        chart (_type_): The parent widget in which to place the bar chart.
        bar (_type_): The parent widget in which to place the 'matplotlib' toolbar.
    """
    # Initialize empty lists to store the x-axis and y-axis data:
    x_data = list()
    y_data = list()
    # Initialize an empty list for bar width definitions:
    w_data = list()
    # Decide which record list to use:
    # * PyCharm throws a light warning on this line, saying 'list_used' value is not used, even though it absolutely is.
    list_used = list()
    if len(StVars.records_filter) > 0:
        list_used = StVars.records_filter
    else:
        list_used = StVars.records_master
    # Add the values to the appropriate data lists:
    for record in list_used:
        if record in StVars.records_saved:
            if x == "Timestamp":
                x_data.append(pd.Timestamp(record[x]).round(freq="d"))
            elif x == "Cost" or x == "Total":
                x_data.append(int(record[x]))
            else:
                x_data.append(record[x])
            y_data.append(record[y])
    # Stop processing if there was no data:
    if len(x_data) > 0:
        # When working with numerical data, collect sums instead of individual data points:
        if type(y_data[0]) == float or type(y_data[0]) == int:
            # Iterate through the x data in both ascending and descending order simultaneously:
            iter8 = 0
            while iter8 < len(x_data):
                duplic8 = len(x_data) - 1
                while duplic8 > iter8:
                    # If a duplicate x-value is found, add its y-value to the first instance's y-value and remove the
                    # second instance from both x and y lists:
                    if x_data[iter8] == x_data[duplic8]:
                        if y != "Cost":
                            y_data[iter8] += y_data[duplic8]
                        x_data.remove(x_data[duplic8])
                        y_data.remove(y_data[duplic8])
                    duplic8 -= 1
                iter8 += 1
        iter8 = 0
        while iter8 < len(x_data):
            if len(x_data) > 31:
                w_data.append(0.5)
            else:
                w_data.append(0.8)
            iter8 += 1
        # Define a blank canvas on which to draw the line chart, ~65% of the monitor's height and width:
        chart_frame = Figure(
            figsize=(
                root.winfo_screenmmwidth() * 0.025,
                root.winfo_screenmmheight() * 0.025,
            ),
            dpi=90,
        )
        # Add a chart to the frame:
        plot = chart_frame.add_subplot()
        # Plot the data points onto the chart:
        plot.bar(x=x_data, height=y_data, width=w_data)
        # plot.plot(x_data, y_data)
        # Add a light gray grid to the chart:
        plot.grid(axis="y", color="0.7", linestyle=":")
        # Minimize the external margins around the chart:
        chart_frame.subplots_adjust(left=0.045, bottom=0.04, right=0.99, top=0.98)
        # Minimize the internal margins on the chart, but leave enough room for long x-labels:
        plot.margins(x=0.025, y=0.05)
        # Assign the chart frame to a 'tkinter'-compatible canvas-type widget:
        canvas = FigureCanvasTkAgg(chart_frame, master=chart)
        # Draw the chart to the canvas:
        canvas.draw()
        # Define a new instance of the 'matplotlib' toolbar and assign it to the canvas:
        toolbar = NavigationToolbar2Tk(canvas, bar, pack_toolbar=False)
        # Place the canvas inside the "Line Chart" window in its designated frame:
        canvas.get_tk_widget().pack(fill="both", expand=True)
        # Place the toolbar inside the "Line Chart" window in its designated frame:
        toolbar.pack()


# Updated: All good for now.
def check_temp_count():
    """
    Check that 'StVars.records_temp' is empty before attempting to load a file.
    """
    if len(StVars.records_temp) == 0:
        # All records are either saved or rejected. Proceed to open the file selection window:
        load_file()
    else:
        # There are still some temporary records. Ask the user what to do:
        commit_popup()


# Updated: All good for now.
def clear_all_data():
    """
    Clears all loaded data from all persistent lists EXCEPT 'StVars.datalog_msgs'. It allows the user to continue using
    the program to work on another document set without needing to close the program to do so.
    """
    # Ensure any selected rows are deselected:
    if len(base_tree.selection()) > 0:
        base_tree.selection_remove(base_tree.selection()[0])
    # Clear all records from all record lists:
    iter8 = 0
    while len(StVars.records_saved) > 0:
        StVars.records_saved.remove(StVars.records_saved[0])
    while len(StVars.records_deleted) > 0:
        StVars.records_deleted.remove(StVars.records_deleted[0])
    while len(StVars.records_filter) > 0:
        StVars.records_filter.remove(StVars.records_filter[0])
    while len(StVars.records_invalid) > 0:
        StVars.records_invalid.remove(StVars.records_invalid[0])
    while len(StVars.records_temp) > 0:
        StVars.records_temp.remove(StVars.records_temp[0])
    while len(StVars.records_master) > 0:
        StVars.records_master.remove(StVars.records_master[0])
        # Since all the other record lists are inside this one, only count its records:
        iter8 += 1
    # Don't log this action if the record lists were already empty.
    if iter8 > 0:
        log_msg(msg=(str(iter8) + " records were cleared from memory."))
    # Clear all user-defined field validation lists:
    iter8 = 0
    while len(StVars.valid_departments) > 0:
        StVars.valid_departments.remove(StVars.valid_departments[0])
        iter8 += 1
    while len(StVars.valid_employees) > 0:
        StVars.valid_employees.remove(StVars.valid_employees[0])
        iter8 += 1
    while len(StVars.valid_locations) > 0:
        StVars.valid_locations.remove(StVars.valid_locations[0])
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
    Moves all temp records from the temp record list into the saved records list.
    """
    # Only run this function if there are temporary records:
    # * This shouldn't be necessary, since the buttons and menu options for this are disabled,
    # * but it's here as a failsafe. Better safe than sorry.
    if len(StVars.records_temp) > 0:
        # Deselect any currently selected rows:
        # * This is in place because if a record is still selected when 'Status' values are modified,
        # * it causes an infinite loop in the 'get_selection()' function.
        if len(base_tree.selection()) > 0:
            base_tree.selection_remove(base_tree.selection()[0])
        iter8 = 0
        while len(StVars.records_temp) > 0:
            # Change the status of each record from "Temporary" to "Saved", for treeview color sorting:
            StVars.records_temp[0]["Status"] = "Saved"
            # Add each record to 'StVars.records_saved' in the same order they appear in 'StVars.records_temp':
            StVars.records_saved.append(StVars.records_temp[0])
            # Then delete the 'StVars.records_temp' copy of the record:
            StVars.records_temp.remove(StVars.records_temp[0])
            # As always, keep count of the number of records changed, for logging purposes:
            iter8 += 1
        if iter8 > 0:
            # Sort by timestamp if one is present:
            if len(StVars.records_saved) > 0:
                heading = list(StVars.records_saved[0].keys())[0]
                StVars.records_saved.sort(
                    key=lambda d: (d[heading] == "", d[heading]), reverse=False
                )
            # Log the record changes:
            log_msg(msg=(str(iter8) + " valid records were committed to memory."))
            # Only refresh the tree if there were changes made by this function:
            refresh_table(master_log=True)


# Updated: All good for now.
def commit_popup():
    """
    Displays a top-level popup asking how the user wishes to handle temporary records. Options are: "Commit All",
    "Reject All", and "Review Temporary".
    """
    # Create toplevel 'tkinter' window:
    popup = tk.Toplevel(root)
    # Set the size and position of the popup (centered to the primary monitor):
    popup.geometry(
        "400x150+"
        + str(int((StVars.monitor_width / 2) - 250))
        + "+"
        + str(int((StVars.monitor_height / 2) - 125))
    )
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
        + str(len(StVars.records_temp))
        + " temporary records. SalesTrax cannot load new data until all records"
        + " are either saved or rejected. Would you like to commit them all,"
        + " reject them all, or cancel loading to review them?"
    )
    # Create a label to hold the above message and apply line wrapping to it:
    warn_label = tk.Label(top_frame, text=msg, wraplength=275, justify="left")
    # Define the three buttons used for the user's decision. All three should re-enable access to the root window:
    btn_commit_all = tk.Button(
        popup,
        text="Commit All",
        font="sans 10 bold",
        # Have the 'Commit All' button actually commit all temp records before opening the 'Open File' dialog:
        command=lambda: [
            root.attributes("-disabled", False),
            root.focus_force(),
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
            root.focus_force(),
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
            root.focus_force(),
            # Turn off any currently active filters and/or sorting:
            toggle_filter(),
            # Turn on all 'Hide *' filters except 'Hide Temporary Records':
            view_menu.invoke("Hide Saved Records"),
            view_menu.invoke("Hide Deleted Records"),
            view_menu.invoke("Hide Invalid Records"),
            popup.destroy(),
        ],
    )
    # Place the frame in the first row of the toplevel window:
    top_frame.grid(row=0, column=0, columnspan=3, padx=25, pady=(15, 10))
    # Place the icon on the left side of the frame:
    icon.grid(row=0, column=0)
    # Place the body message on the right side of the frame:
    warn_label.grid(row=0, column=1, padx=(25, 0))
    # Place the three decision buttons under the frame:
    btn_commit_all.grid(row=1, column=0, padx=(30, 0), pady=(10, 15))
    btn_reject_all.grid(row=1, column=1, pady=(10, 15))
    btn_review_temp.grid(row=1, column=2, padx=(0, 30), pady=(10, 15))
    btn_review_temp.focus_set()


# Updated: All good for now.
def commit_selection():
    """
    Adds selected temp records to the saved records list and restores deleted records. Supports single and multiple
    selections.
    """
    # Get record list info for all the selected rows:
    data_address = get_selection(stop_select=True)
    if data_address is not None:
        row = 0
        iter8 = 0
        invalid8 = 0
        while row < len(data_address[0]):
            if data_address[0][row] == "Temporary":
                # Change the status of the record to "Saved":
                # Notes: The next code line raises a warning in PyCharm, but it isn't an error.
                # * The problem stems from PyCharm not recognizing that 'StVars.records_temp[data_address[1][row]]'
                # * refers to a dictionary, not a list. It's not a big deal, but I thought I should mention it in case
                # * someone takes over the code, tries to fix it, and breaks the program. Don't fix it. It's not broken.
                StVars.records_temp[data_address[1][row]]["Status"] = "Saved"
                # Add the record to the saved records list:
                StVars.records_saved.append(StVars.records_temp[data_address[1][row]])
                # Count successes:
                iter8 += 1
            elif data_address[0][row] == "Deleted":
                # Check for validation errors:
                if "" in StVars.records_deleted[data_address[1][row]].values():
                    # Change the status of the record to "Invalid":
                    # * See the 'Notes' above for why this raises a warning in PyCharm.
                    StVars.records_deleted[data_address[1][row]]["Status"] = "Invalid"
                    # Add the record to the invalid record list:
                    StVars.records_invalid.append(
                        StVars.records_deleted[data_address[1][row]]
                    )
                    # Count invalid successes:
                    invalid8 += 1
                else:
                    # Change the status of the record to "Saved":
                    # * See the 'Notes' above for why this raises a warning in PyCharm.
                    StVars.records_deleted[data_address[1][row]]["Status"] = "Saved"
                    # Add the record to the saved records list:
                    StVars.records_saved.append(
                        StVars.records_deleted[data_address[1][row]]
                    )
                    # Count successes:
                    iter8 += 1
            row += 1
        # Remove each record from its previous record list from the bottom up:
        # * This can't be done top down because it will modify the indexes of lower records, leading to indexing errors.
        row = len(data_address[0]) - 1
        while row >= 0:
            if data_address[0][row] == "Temporary":
                # Remove from the temp records list:
                StVars.records_temp.remove(StVars.records_temp[data_address[1][row]])
            elif data_address[0][row] == "Deleted":
                # Remove from the deleted records list:
                StVars.records_deleted.remove(
                    StVars.records_deleted[data_address[1][row]]
                )
            row -= 1
        if (iter8 > 0) or (invalid8 > 0):
            # Only refresh the table if changes were made:
            refresh_table(repop_tree=True)
            # Print a customized Datalog message for each combination of valid and invalid records:
            if (iter8 > 0) and (invalid8 > 0):
                if (iter8 > 1) and (invalid8 > 1):
                    log_msg(
                        str(iter8)
                        + " valid records and "
                        + str(invalid8)
                        + " invalid records were committed to memory.",
                        popup=False,
                    )
                elif (iter8 > 1) and (invalid8 == 1):
                    log_msg(
                        str(iter8)
                        + " valid records and 1 invalid record were committed to memory.",
                        popup=False,
                    )
                else:
                    log_msg(
                        "1 valid record and "
                        + str(invalid8)
                        + " invalid records were committed to memory.",
                        popup=False,
                    )
            elif (iter8 > 1) and (invalid8 == 0):
                log_msg(
                    str(iter8) + " valid records were committed to memory.", popup=False
                )
            elif (iter8 == 0) and (invalid8 > 1):
                log_msg(
                    str(invalid8) + " invalid records were committed to memory.",
                    popup=False,
                )
            elif (iter8 == 1) and (invalid8 == 0):
                log_msg("1 valid record was committed to memory.", popup=False)
            else:
                log_msg("1 invalid record was committed to memory.", popup=False)
            row = 0
            while row < len(data_address[2]) and data_address[2][row] < len(base_tree.get_children()):
                # Since performing this operation deselects the rows, reselect them:
                base_tree.selection_add(base_tree.get_children()[data_address[2][row]])
                row += 1
            # Refocus the cursor on the topmost record:
            if data_address[2][0] < len(base_tree.get_children()):
                base_tree.focus(base_tree.get_children()[data_address[2][0]])


# Updated: All good for now.
def disable_resize_cursor(event):
    """
    Prevents the resizing cursor graphic by interrupting the default behavior of mouse motion when the mouse is
    positioned over a column separator.

    Args:
        event (tkinter.Event): A standard tkinter keybinding event. In this case, '<Motion>' (mouse movement), but
            it should not be manually declared.
    Returns:
        (str): This returns "break" back to the calling event, preventing it from performing its default behavior.
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
    """
    pass


# Updated: All good for now.
def edit_record(event):
    """
    Creates a toplevel window for editing existing records.

    Args:
        event (tkinter.Event): A standard tkinter keybinding event. In this case, '<Double-Button-1>' (mouse double
            left-click), but it should not be manually declared.
    """
    # Only perform the function if the user double-clicked a cell in the table:
    if base_tree.identify_region(event.x, event.y) == "cell":
        # Get the record list location information for the current selection:
        data_address = get_selection(stop_select=True)
        # Stop if the location information comes back empty:
        if data_address is not None:
            # Store the location of the record for later:
            if data_address[0][0] == "Temporary":
                record = StVars.records_temp[data_address[1][0]]
            elif data_address[0][0] == "Saved":
                record = StVars.records_saved[data_address[1][0]]
            elif data_address[0][0] == "Deleted":
                record = StVars.records_deleted[data_address[1][0]]
            elif data_address[0][0] == "Invalid":
                record = StVars.records_invalid[data_address[1][0]]
            # Get a list of dictionary keys to use as labels:
            # * PyCharm raises a warning for the following line because it is a direct object reference. This is
            # * intentional, though, so don't fix it.
            keys = list(record.keys())
            # Get a list of values to use for populating the entry boxes:
            values = list(record.values())
            # Create the toplevel window:
            window = tk.Toplevel(root)
            # Define the title bar:
            window.title("Edit Record")
            window.iconbitmap("Images/salestrax_icon_bw.ico")
            # Set the window as a toolwindow to prevent minimizing and maximizing:
            window.attributes("-toolwindow", True)
            # Turn the "X" button on the popup into a "Cancel" button, not accepting any options but re-enabling 'root':
            window.protocol(
                "WM_DELETE_WINDOW",
                func=lambda: [root.attributes("-disabled", False), window.destroy()],
            )
            # Prevent the user from switching back to the root window without first closing the toplevel:
            root.attributes("-disabled", True)
            # Make a single frame to hold everything:
            main_frame = tk.Frame(window, padx=15, pady=15)
            # Place the frame:
            main_frame.pack(fill="both", expand=True)
            # Initialize an empty list to hold references to the dynamically created entry boxes:
            entry_refs = list()
            column = 0
            while column < len(keys):
                # Create a label and entry box for each key-value pair:
                label = tk.Label(main_frame, text=keys[column], anchor="w")
                entry = tk.Entry(main_frame)
                # Make the final column span two columns (because two buttons will be placed under it):
                if (column + 1) == len(keys):
                    label.grid(row=0, column=column, columnspan=2)
                    entry.grid(row=1, column=column, columnspan=2)
                # All the other columns should only span one column:
                else:
                    label.grid(row=0, column=column)
                    entry.grid(row=1, column=column)
                # Populate each entry box with the value of its respective box in the table:
                entry.insert(0, values[column])
                # If any fields are invalid, color them light red, just like in the viewport table:
                if values[column] == "":
                    entry.configure(bg="#FFD8CF")
                if (
                    keys[column] == "Employee"
                    and len(StVars.valid_employees) > 0
                    and values[column] not in StVars.valid_employees
                ):
                    entry.configure(bg="#FFD8CF")
                elif (
                    keys[column] == "Location"
                    and len(StVars.valid_locations) > 0
                    and values[column] not in StVars.valid_locations
                ):
                    entry.configure(bg="#FFD8CF")
                elif (
                    keys[column] == "Department"
                    and len(StVars.valid_departments) > 0
                    and values[column] not in StVars.valid_departments
                ):
                    entry.configure(bg="#FFD8CF")
                elif keys[column] == "Status":
                    entry.configure(state="disabled")
                # Add the entry reference to the reference list:
                entry_refs.append(entry)
                column += 1
            # Reverse direction after all key-value pairs have been placed:
            column -= 1
            # Define the "Accept" and "Cancel" buttons and tie them to functions:
            btn_accept = tk.Button(
                main_frame,
                text="Accept",
                width=7,
                command=lambda: [
                    update_record(record, entry_refs),
                    root.attributes("-disabled", False),
                    window.destroy(),
                    root.focus_force(),
                ],
            )
            btn_cancel = tk.Button(
                main_frame,
                text="Cancel",
                width=7,
                command=lambda: [
                    root.attributes("-disabled", False),
                    window.destroy(),
                    root.focus_force(),
                ],
            )
            # Place both buttons under the final key-value pair:
            btn_accept.grid(row=2, column=column, pady=(15, 0))
            column += 1
            btn_cancel.grid(row=2, column=column, pady=(15, 0))
            # Allow the user to press "<Return>" to accept the data or "<Escape>" to cancel:
            window.bind("<Return>", func=lambda event: btn_accept.invoke())
            window.bind("<Escape>", func=lambda event: btn_cancel.invoke())
            # Schedule a recalculation of the window's size for 5 frames from now, and then center it using the updated
            # window size information:
            # * This has to be a scheduled task because attempting to run it in the same frame as the object definitions
            # * causes it to read the window size before the size is changed by its contents, returning a default window
            # * geometry of "200x200".
            window.after(
                5,
                func=lambda: [
                    window.geometry(
                        str(window.winfo_width())
                        + "x"
                        + str(window.winfo_height())
                        + "+"
                        # Center horizontally:
                        + str(
                            int(
                                (StVars.monitor_width / 2)
                                - ((window.winfo_width() * 0.5) + 25)
                            )
                        )
                        + "+"
                        # Center vertically:
                        + str(
                            int(
                                (StVars.monitor_height / 2)
                                - ((window.winfo_height() * 0.5) + 25)
                            )
                        )
                    ),
                    window.focus_force(),
                ],
            )


# Updated: All good for now.
def exit_functions():
    """
    Postpones exiting the program to perform obligatory exit functions such as saving the Datalog and exporting saved
    records that are yet to be exported.
    """
    if len(StVars.records_saved) > 0:
        # Get a list of Datalog indexes containing the word "export":
        last_export = [
            index for index, sub in enumerate(StVars.datalog_msgs) if "export" in sub
        ]
        if len(last_export) > 0:
            # Trim the list down to the most recent index only:
            last_export = last_export[-1]
        else:
            # If there are no indexes containing the word "export", set 'last_export' to -1 (no file exports):
            last_export = -1
        # Get a list of Datalog indexes containing the word "commit":
        last_save = list(
            [index for index, sub in enumerate(StVars.datalog_msgs) if "commit" in sub]
        )
        while len(last_save) > 0:
            # Only trim the list to the most recent index if the index contains the word "valid" (but not "invalid"):
            if " valid " in StVars.datalog_msgs[last_save[-1]]:
                last_save = last_save[-1]
                # Break the loop once one has been found:
                break
            else:
                # If the index only contains messages relating to "invalid" records, remove that index and move to the
                # next most recent index with "commit" in it:
                last_save.remove(last_save[-1])
        # If all "commit" indexes are removed from the list, set 'last_save' to -1 (no saved records):
        # * Technically, this should never actually happen, since 'records_saved' must have a length of at least 1 for
        # * this function to even do anything. Still, better safe than sorry.
        if not last_save:
            last_save = -1
        if last_save > last_export:
            # Display the "Save Work?" dialog only if there are records that have been saved following the most recent
            # file export:
            answer = messagebox.askyesnocancel(
                title="Unsaved Work",
                message="You have saved records that have not been exported to disk. Would you like to export them?",
            )
            # If the user clicks "Cancel", prevent the program from closing, but don't do anything else:
            if answer is None:
                pass
            # If the user clicks "Yes", open the "Save File As..." dialog:
            elif answer:
                export_file()
                # If the user exports the file, it will be recorded in the most recent Datalog message. If it isn't, the
                # user clicked "Cancel" in the "Save File As..." dialog, so prevent the program from closing, but don't
                # do anything else:
                if "export" in StVars.datalog_msgs[-1]:
                    # If the user exports a file successfully, save a Datalog file and quit SalesTrax:
                    save_log()
                    root.quit()
            # If the user clicks "No", just save a Datalog file and quit SalesTrax without exporting:
            else:
                save_log()
                root.quit()
        # If the user hasn't saved any records since the most recent export, save a Datalog file and quit SalesTrax:
        else:
            save_log()
            root.quit()
    # If there are no saved records, just save a Datalog file (if necessary) and quit SalesTrax:
    else:
        save_log()
        root.quit()


# Updated: All good for now.
def export_file():
    """
    This opens the 'Save File As...' dialog to export an Excel, ODS, or CSV file to disk. When successful, passes the
    file info to 'write_file()' for use.
    """
    # Define filetypes that are accepted for writing, based on whether or not 'odfpy' is installed:
    if StVars.odf_installed:
        # With 'odfpy', allow '.ods' exports:
        table_docs = [
            ("Excel Worksheet", "*.xlsx"),
            ("Comma-Separated Values", "*.csv"),
            ("Open Office Spreadsheet", "*.ods"),
        ]
        # Now define them again as a normal list to double-check against the user's input:
        format_list = ["csv", "ods", "xlsx"]
    else:
        # Without 'odfpy', don't allow '.ods' exports:
        table_docs = [
            ("Excel Worksheet", "*.xlsx"),
            ("Comma-Separated Values", "*.csv"),
        ]
        # Now define them again as a normal list to double-check against the user's input:
        format_list = ["csv", "xlsx"]
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
    Grabs the contents of the currently selected lines in the viewport table and uses that information to locate the
    records in their respective record lists.

    Args:
        stop_select (bool, optional): Whether to clear the row selection on the chosen record when finding the record's
            list location. When used for record modifications, this should always be set to True, but for purposes that
            don't change the record values, set it to False. Defaults to False.
    Returns:
        (list): When successful, this returns a list that can be used by another function to locate and access the item
            more easily.
    """
    # Ensure that a record is selected at all:
    if len(base_tree.selection()) > 0:
        # Create a series of lists to hold relevant information for locating records:
        rec_status = [None] * len(base_tree.selection())
        rec_index = [None] * len(base_tree.selection())
        tree_index = [None] * len(base_tree.selection())
        # Create a master list to hold the three lists from above:
        select_data = [[] * len(base_tree.selection())] * 3
        row = 0
        while row < len(base_tree.selection()):
            # Add the tree indexes of selected records to the corresponding list:
            tree_index[row] = base_tree.index(base_tree.selection()[row])
            row += 1
        # Grab the list of column headers to use as dictionary keys:
        keys = list(base_tree["columns"])
        # Initialize an empty list for each record's values:
        values = [None] * len(base_tree.selection())
        row = 0
        while row < len(base_tree.selection()):
            # Store the records in the empty values list, one record at a time:
            # Notes: PyCharm recognizes 'row' as a TypeError for some reason, even though it is just an index number.
            # * This same warning is raised by PyCharm in several other places throughout this file, but it isn't
            # * actually a problem, so don't fix it.
            values[row] = base_tree.item(base_tree.selection()[row])["values"]
            row += 1
        # Initialize another empty list to store dictionaries for each record:
        selection = [None] * len(base_tree.selection())
        row = 0
        while row < len(values):
            # Build a dictionary using the keys and values from above:
            # * See the "Notes" section above for why this throws a warning in PyCharm.
            selection[row] = dict(zip(keys, values[row]))
            # Ensure "Timestamp" values are reformatted as timestamps (they're stored in Treeview as strings):
            if "Timestamp" in selection[row]:
                # * This is yet another false warning raised by PyCharm, in which it fails to recognize that
                # * 'selection[row]' is a dictionary, and thus doesn't understand why I'm using a key reference. More
                # * frustrating still, the exact same warning repeats ten times in this function alone. As with all
                # * PyCharm warning that I left un-addressed, don't fix this one either. It's not broken.
                selection[row]["Timestamp"] = pd.Timestamp(selection[row]["Timestamp"])
            # Ensure "Cost" values are reformatted as floats (they're stored in Treeview as strings):
            if "Cost" in selection[row]:
                if selection[row]["Cost"] != "":
                    selection[row]["Cost"] = float(selection[row]["Cost"])
            # Ensure "Total" values are reformatted as floats (they're stored in Treeview as strings):
            if "Total" in selection[row]:
                if selection[row]["Total"] != "":
                    selection[row]["Total"] = float(selection[row]["Total"])
            if selection[row]["Status"] == "Saved":
                record = 0
                iter8 = 0
                while record < len(StVars.records_saved):
                    # Compare the selected record to records in the saved records list:
                    if selection[row] == StVars.records_saved[record]:
                        # When a match is found, store the "Status" and record list index:
                        rec_status[row] = selection[row]["Status"]
                        # * See the "Notes" section above for why this throws a warning in PyCharm.
                        rec_index[row] = record
                    else:
                        iter8 += 1
                    record += 1
                # If no match is found, a record was incorrectly recorded; report this to the Datalog and user:
                if iter8 == len(StVars.records_saved):
                    log_msg(
                        "Something went wrong. A memory address for the selected record could not be found. Try "
                        + "refreshing the table and then try again.",
                        popup=True,
                    )
                    # Clear the selection whenever this happens, to prevent infinite looping of 'log_msg()':
                    base_tree.selection_remove(base_tree.selection()[0])
            elif selection[row]["Status"] == "Temporary":
                record = 0
                iter8 = 0
                while record < len(StVars.records_temp):
                    # Compare the selected record to records in the temp records list:
                    if selection[row] == StVars.records_temp[record]:
                        # When a match is found, store the "Status" and record list index:
                        rec_status[row] = selection[row]["Status"]
                        # * See the "Notes" section above for why this throws a warning in PyCharm.
                        rec_index[row] = record
                    else:
                        iter8 += 1
                    record += 1
                # If no match is found, a record was incorrectly recorded; report this to the Datalog and user:
                if iter8 == len(StVars.records_temp):
                    log_msg(
                        "Something went wrong. A memory address for the selected record could not be found. Try "
                        + "refreshing the table and then try again.",
                        popup=True,
                    )
                    # Clear the selection whenever this happens, to prevent infinite looping of 'log_msg()':
                    base_tree.selection_remove(base_tree.selection()[0])
            elif selection[row]["Status"] == "Invalid":
                record = 0
                iter8 = 0
                while record < len(StVars.records_invalid):
                    # Compare the selected record to records in the invalid records list:
                    if selection[row] == StVars.records_invalid[record]:
                        # When a match is found, store the "Status" and record list index:
                        rec_status[row] = selection[row]["Status"]
                        # * See the "Notes" section above for why this throws a warning in PyCharm.
                        rec_index[row] = record
                    else:
                        iter8 += 1
                    record += 1
                # If no match is found, a record was incorrectly recorded; report this to the Datalog and user:
                if iter8 == len(StVars.records_invalid):
                    log_msg(
                        "Something went wrong. A memory address for the selected record could not be found. Try "
                        + "refreshing the table and then try again.",
                        popup=True,
                    )
                    # Clear the selection whenever this happens, to prevent infinite looping of 'log_msg()':
                    base_tree.selection_remove(base_tree.selection()[0])
            elif selection[row]["Status"] == "Deleted":
                record = 0
                iter8 = 0
                while record < len(StVars.records_deleted):
                    # Compare the selected record to records in the deleted records list:
                    if selection[row] == StVars.records_deleted[record]:
                        # When a match is found, store the "Status" and record list index:
                        rec_status[row] = selection[row]["Status"]
                        # * See the "Notes" section above for why this throws a warning in PyCharm.
                        rec_index[row] = record
                    else:
                        iter8 += 1
                    record += 1
                # If no match is found, a record was incorrectly recorded; report this to the Datalog and user:
                if iter8 == len(StVars.records_deleted):
                    log_msg(
                        "Something went wrong. A memory address for the selected record could not be found. Try "
                        + "refreshing the table and then try again.",
                        popup=True,
                    )
                    # Clear the selection whenever this happens, to prevent infinite looping of 'log_msg()':
                    base_tree.selection_remove(base_tree.selection()[0])
            row += 1
        # Store all the collected data in the master info list:
        select_data[0] = rec_status
        select_data[1] = rec_index
        select_data[2] = tree_index
        # If the record is going to be modified, deselect it in the treeview to prevent looping errors:
        if stop_select:
            while len(base_tree.selection()) > 0:
                base_tree.selection_remove(base_tree.selection()[0])
        # As long as there were no writing errors, send the selection info back to the function that called for it:
        if select_data[0] is not None:
            return select_data


# Updated: All good for now.
def hide_toggle():
    """
    Used to set the appearance of toggle buttons used to hide records with a specific status.
    """
    # Check to see if any filters or sorts are currently active:
    if (
        toggle_deleted.get()
        or toggle_invalid.get()
        or toggle_saved.get()
        or toggle_temp.get()
        or (StVars.sort_column != "")
    ):
        # If so, turn on the primary filter and sink its button:
        StVars.filter_toggle = True
        btn_filter.configure(relief="sunken")
    else:
        # If not, turn off the primary filter and raise its button:
        StVars.filter_toggle = False
        btn_filter.configure(relief="raised")
    # Do the same with the "Hide Deleted" button:
    if toggle_deleted.get():
        btn_hide_deleted.configure(relief="sunken")
    else:
        btn_hide_deleted.configure(relief="raised")
    # Do the same with the "Hide Invalid" button:
    if toggle_invalid.get():
        btn_hide_invalid.configure(relief="sunken")
    else:
        btn_hide_invalid.configure(relief="raised")
    # Do the same with the "Hide Saved" button:
    if toggle_saved.get():
        btn_hide_saved.configure(relief="sunken")
    else:
        btn_hide_saved.configure(relief="raised")
    # Do the same with the "Hide Temporary" button:
    if toggle_temp.get():
        btn_hide_temp.configure(relief="sunken")
    else:
        btn_hide_temp.configure(relief="raised")
    # Refresh the table contents:
    refresh_table()


# Updated: All good for now.
def line_definition():
    """
    Opens a window for selecting the axes for generating and viewing line charts.
    """
    # Define the base toplevel:
    window = tk.Toplevel(root, padx=5, pady=5)
    # Set the title bar contents:
    window.title("Line Chart")
    window.iconbitmap("Images/salestrax_icon_bw.ico")
    # Set the window size based on the user's monitor size and center it:
    window.geometry(
        (
            # 70% monitor width:
            str(int(StVars.monitor_width * 0.7))
            + "x"
            # 80% monitor height:
            + str(int(StVars.monitor_height * 0.8))
            + "+"
            # Center horizontally:
            + str(
                int((StVars.monitor_width / 2) - ((StVars.monitor_width * 0.35) + 25))
            )
            + "+"
            # Center vertically:
            + str(
                int((StVars.monitor_height / 2) - ((StVars.monitor_height * 0.4) + 25))
            )
        )
    )
    # Define the base layout frames for organizational setup:
    # Ensure the frame that holds the line chart is visible even when empty (otherwise, the window looks incomplete):
    top_frame = tk.Frame(window, bg="white", border=2, relief="groove")
    bottom_frame = tk.Frame(window)
    # Define the frames for the 'matplotlib' toolbar and the axis choice area:
    tool_frame = tk.Frame(bottom_frame)
    button_frame = tk.Frame(bottom_frame)
    # Define the frame for the labels and entry boxes:
    left_frame = tk.Frame(button_frame)
    # Define the frame for the control buttons:
    right_frame = tk.Frame(button_frame)
    # Define the frame for the x-axis label and entry box:
    x_frame = tk.Frame(left_frame)
    # Define the frame for the x-axis label and entry box:
    y_frame = tk.Frame(left_frame)
    # X-axis label:
    x_label = tk.Label(x_frame, text="X-Axis")
    # Combo box for defining the x-axis to use in the line chart:
    x_combo = ttk.Combobox(x_frame, values=list(base_tree["columns"]))
    # Y-axis label:
    y_label = tk.Label(y_frame, text="Y-Axis")
    # Combo box for defining the y-axis to use in the line chart:
    y_combo = ttk.Combobox(y_frame, values=list(base_tree["columns"]))
    # Define the "OK" button:
    ok_button = tk.Button(
        right_frame,
        text="OK",
        width=10,
        command=lambda: [
            top_frame.winfo_children()[0].destroy()
            if len(top_frame.winfo_children()) > 0
            else do_nothing(),
            tool_frame.winfo_children()[0].destroy()
            if len(tool_frame.winfo_children()) > 0
            else do_nothing(),
            line_generation(x_combo.get(), y_combo.get(), top_frame, tool_frame),
        ]
        if x_combo.get() != ""
        and y_combo.get() != ""
        and x_combo.get() != y_combo.get()
        and type(StVars.records_master[0][y_combo.get()]) != str
        else [
            log_msg("SalesTrax cannot visualize non-numerical data."),
            window.focus_force(),
        ],
    )
    # Define the "Cancel" button:
    cancel_button = tk.Button(
        right_frame, text="Cancel", width=10, command=window.destroy
    )
    # Place all the objects in their respective frames:
    top_frame.pack(side="top", fill="both", expand=True, padx=2, pady=(2, 0))
    bottom_frame.pack(side="bottom", fill="x")
    tool_frame.pack(side="left", padx=(10, 0), pady=(0, 80), anchor="nw")
    button_frame.pack(side="right", anchor="se")
    left_frame.pack(side="left", padx=(0, 10), pady=(30, 40))
    right_frame.pack(side="right", padx=(10, 40), pady=(30, 40))
    x_frame.pack(side="top")
    y_frame.pack(side="bottom")
    x_label.pack(side="left")
    x_combo.pack(side="right")
    y_label.pack(side="left")
    y_combo.pack(side="right")
    ok_button.pack(side="top")
    cancel_button.pack(side="bottom")
    # If there is an active sort, auto-populate the x-axis combobox with it:
    if StVars.sort_column != "":
        x_combo.set(StVars.sort_column)
    else:
        # Otherwise, use "Timestamp", if possible (don't auto-populate the x-axis combobox if no sort or "Timestamp"):
        if "Timestamp" in list(base_tree["columns"]):
            x_combo.set("Timestamp")


# Updated: All good for now.
def line_generation(x: str, y: str, chart: tk.Widget, bar: tk.Widget):
    """
    Populates the "Line Chart" window viewport with a line chart as defined in 'line_definition()'.

    Args:
        x (str): The name of the table column to use for the x-axis.
        y (str): The name of the table column to use for the y-axis.
        chart (_type_): The parent widget in which to place the line chart.
        bar (_type_): The parent widget in which to place the 'matplotlib' toolbar.
    """
    # Initialize empty lists to store the x-axis and y-axis data:
    x_data = list()
    y_data = list()
    # Decide which record list to use:
    # * As in 'bar_generation()', PyCharm throws a light warning on the next line, claiming that 'list_used' is not used
    # * when it is very clearly used three times.
    list_used = list()
    if len(StVars.records_filter) > 0:
        list_used = sorted(
            list(StVars.records_filter), key=lambda d: (d[x] == "", d[x])
        )
    else:
        list_used = sorted(
            list(StVars.records_master), key=lambda d: (d[x] == "", d[x])
        )
    # Add the values to the appropriate data lists:
    for record in list_used:
        if record in StVars.records_saved:
            if x == "Timestamp":
                x_data.append(pd.Timestamp(record[x]).round(freq="d"))
            elif x == "Cost" or x == "Total":
                x_data.append(int(record[x]))
            else:
                x_data.append(record[x])
            y_data.append(record[y])
    # Stop processing if there was no data:
    if len(x_data) > 0:
        # When working with numerical data, collect sums instead of individual data points:
        if type(y_data[0]) == float or type(y_data[0]) == int:
            # Iterate through the x data in both ascending and descending order simultaneously:
            iter8 = 0
            while iter8 < len(x_data):
                duplic8 = len(x_data) - 1
                avg_div = 1
                while duplic8 > iter8:
                    # If a duplicate x-value is found, add its y-value to the first instance's y-value and remove the
                    # second instance from both x and y lists:
                    if x_data[iter8] == x_data[duplic8]:
                        # When y is "Cost", average the cost instead of summing it:
                        if y == "Cost":
                            avg_div += 1
                        y_data[iter8] += y_data[duplic8]
                        x_data.remove(x_data[duplic8])
                        y_data.remove(y_data[duplic8])
                    duplic8 -= 1
                y_data[iter8] /= avg_div
                iter8 += 1
        # Define a blank canvas on which to draw the line chart, ~65% of the monitor's height and width:
        chart_frame = Figure(
            figsize=(
                root.winfo_screenmmwidth() * 0.025,
                root.winfo_screenmmheight() * 0.025,
            ),
            dpi=90,
        )
        # Add a chart to the frame:
        plot = chart_frame.add_subplot()
        # Plot the data points onto the chart:
        plot.plot(x_data, y_data)
        # Add a light gray grid to the chart:
        plot.grid(color="0.9")
        # Minimize the external margins around the chart:
        chart_frame.subplots_adjust(left=0.045, bottom=0.04, right=0.99, top=0.98)
        # Minimize the internal margins on the chart, but leave enough room for long x-labels:
        plot.margins(x=0.025, y=0.05)
        # Assign the chart frame to a 'tkinter'-compatible canvas-type widget:
        canvas = FigureCanvasTkAgg(chart_frame, master=chart)
        # Draw the chart to the canvas:
        canvas.draw()
        # Define a new instance of the 'matplotlib' toolbar and assign it to the canvas:
        toolbar = NavigationToolbar2Tk(canvas, bar, pack_toolbar=False)
        # Place the canvas inside the "Line Chart" window in its designated frame:
        canvas.get_tk_widget().pack(fill="both", expand=True)
        # Place the toolbar inside the "Line Chart" window in its designated frame:
        toolbar.pack()


# Updated: All good for now.
def link_to_github(page: str = ""):
    """
    Opens a link to the SaleTrax repository on GitHub.

    Args:
        page (str): Specific GitHub navigation information (e.g. "issues/", "wiki/", etc.). Defaults to "".
    """
    # Define the page link:
    url = "https://www.github.com/Apellonyx/salestrax/" + page
    # Open the link in the user's default browser:
    webbrowser.open(url, new=0, autoraise=True)


# Updated: All good for now.
def load_file():
    """
    This opens the file select dialog to load an Excel, ODS, or CSV file from disk. When successful, passes this file
    to 'pop_temp()' for use.
    """
    # Define filetypes that are accepted for reading, based on whether or not 'odfpy' is installed:
    if StVars.odf_installed:
        table_docs = [
            ("All Supported", "*.csv;*.ods;*.xls;*.xlsb;*.xlsm;*.xlsx"),
            ("Excel Worksheet", "*.xls;*.xlsb;*.xlsm;*.xlsx"),
            ("Open Office Spreadsheet", "*.ods"),
            ("Comma-Separated Values", "*.csv"),
        ]
        # Now define them again as a normal list for comparison with the actual file loaded:
        format_list = ["csv", "ods", "xls", "xlsb", "xlsm", "xlsx"]
    else:
        # Remove '.ods' file reading if 'odfpy' is not installed:
        table_docs = [
            ("All Supported", "*.csv;*.ods;*.xls;*.xlsb;*.xlsm;*.xlsx"),
            ("Excel Worksheet", "*.xls;*.xlsb;*.xlsm;*.xlsx"),
            ("Comma-Separated Values", "*.csv"),
        ]
        # Now define them again as a normal list for comparison with the actual file loaded:
        format_list = ["csv", "xls", "xlsb", "xlsm", "xlsx"]
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
    """
    # Get the number of messages that have already been logged during this session:
    messages = len(StVars.datalog_msgs)
    # Grab a timestamp for the exact time when the message was sent to this function:
    time_now = pd.Timestamp.now().round(freq="s")
    # Compose the Datalog message using the information above and the contents of 'msg':
    full_msg = "%4s" % str(messages) + ": " + str(time_now) + ": " + msg + "\n"
    # Add the entire message to the 'dataLogged' list for backup:
    StVars.datalog_msgs.append(full_msg)
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


# Updated: All good for now.
def notebook_update():
    """
    Updates the Validation Control window on a 100 ms loop whenever the window is open.
    """
    if employees_entry.get() != "":
        # Toggle on the "Add New Entry" button when the entry field has text in it:
        if employees_add.cget("state") == "disabled":
            employees_add.configure(state="normal")
        # Enable the "<Return>" keybinding if the user is currently entering text into the entry field:
        if (
            employees_add.cget("state") == "normal"
            and val_control.focus_get() == employees_entry
        ):
            val_control.bind("<Return>", func=lambda event: employees_add.invoke())
        # Disable the "<Return>" keybinding if the user leaves the entry field or deletes its contents:
        else:
            val_control.unbind("<Return>")
    else:
        # Toggle off the "Add New Entry" button when the entry field is empty:
        if employees_add.cget("state") == "normal":
            employees_add.configure(state="disabled")
    # Enable the "Auto-Populate" button when its required data is present:
    if (len(base_tree.get_children()) > 0) and ("Employee" in base_tree["columns"]):
        if employees_auto.cget("state") == "disabled":
            employees_auto.configure(state="normal")
    # Disable the "Auto-Populate" button if its requirements are not met:
    else:
        if employees_auto.cget("state") == "normal":
            employees_auto.configure(state="disabled")
    # Copy the contents of the currently selected listbox item into the entry field when the user selects something new:
    if len(
        employees_box.curselection()
    ) > 0 and employees_selection.get() != employees_box.get(
        employees_box.curselection()[0]
    ):
        employees_selection.configure(state="normal")
        employees_selection.delete(0, "end")
        employees_selection.insert(
            0, employees_box.get(employees_box.curselection()[0])
        )
        employees_selection.configure(state="disabled")
    # Enable the "Delete Entry" button when a listbox item is selected:
    if employees_selection.get() != "":
        if employees_delete.cget("state") == "disabled":
            employees_delete.configure(state="normal")
    # Disable the "Delete Entry" when no entries are selected:
    else:
        if employees_delete.cget("state") == "normal":
            employees_delete.configure(state="disabled")

    if locations_entry.get() != "":
        # Toggle on the "Add New Entry" button when the entry field has text in it:
        if locations_add.cget("state") == "disabled":
            locations_add.configure(state="normal")
        # Enable the "<Return>" keybinding if the user is currently entering text into the entry field:
        if (
            locations_add.cget("state") == "normal"
            and val_control.focus_get() == locations_entry
        ):
            val_control.bind("<Return>", func=lambda event: locations_add.invoke())
        # Disable the "<Return>" keybinding if the user leaves the entry field or deletes its contents:
        else:
            val_control.unbind("<Return>")
    else:
        # Toggle off the "Add New Entry" button when the entry field is empty:
        if locations_add.cget("state") == "normal":
            locations_add.configure(state="disabled")
    # Enable the "Auto-Populate" button when its required data is present:
    if (len(base_tree.get_children()) > 0) and ("Location" in base_tree["columns"]):
        if locations_auto.cget("state") == "disabled":
            locations_auto.configure(state="normal")
    # Disable the "Auto-Populate" button if its requirements are not met:
    else:
        if locations_auto.cget("state") == "normal":
            locations_auto.configure(state="disabled")
    # Copy the contents of the currently selected listbox item into the entry field when the user selects something new:
    if len(
        locations_box.curselection()
    ) > 0 and locations_selection.get() != locations_box.get(
        locations_box.curselection()[0]
    ):
        locations_selection.configure(state="normal")
        locations_selection.delete(0, "end")
        locations_selection.insert(
            0, locations_box.get(locations_box.curselection()[0])
        )
        locations_selection.configure(state="disabled")
    # Enable the "Delete Entry" button when a listbox item is selected:
    if locations_selection.get() != "":
        if locations_delete.cget("state") == "disabled":
            locations_delete.configure(state="normal")
    # Disable the "Delete Entry" when no entries are selected:
    else:
        if locations_delete.cget("state") == "normal":
            locations_delete.configure(state="disabled")

    if departments_entry.get() != "":
        # Toggle on the "Add New Entry" button when the entry field has text in it:
        if departments_add.cget("state") == "disabled":
            departments_add.configure(state="normal")
        # Enable the "<Return>" keybinding if the user is currently entering text into the entry field:
        if (
            departments_add.cget("state") == "normal"
            and val_control.focus_get() == departments_entry
        ):
            val_control.bind("<Return>", func=lambda event: departments_add.invoke())
        # Disable the "<Return>" keybinding if the user leaves the entry field or deletes its contents:
        else:
            val_control.unbind("<Return>")
    else:
        # Toggle off the "Add New Entry" button when the entry field is empty:
        if departments_add.cget("state") == "normal":
            departments_add.configure(state="disabled")
    # Enable the "Auto-Populate" button when its required data is present:
    if (len(base_tree.get_children()) > 0) and ("Department" in base_tree["columns"]):
        if departments_auto.cget("state") == "disabled":
            departments_auto.configure(state="normal")
    # Disable the "Auto-Populate" button if its requirements are not met:
    else:
        if departments_auto.cget("state") == "normal":
            departments_auto.configure(state="disabled")
    # Copy the contents of the currently selected listbox item into the entry field when the user selects something new:
    if len(
        departments_box.curselection()
    ) > 0 and departments_selection.get() != departments_box.get(
        departments_box.curselection()[0]
    ):
        departments_selection.configure(state="normal")
        departments_selection.delete(0, "end")
        departments_selection.insert(
            0, departments_box.get(departments_box.curselection()[0])
        )
        departments_selection.configure(state="disabled")
    # Enable the "Delete Entry" button when a listbox item is selected:
    if departments_selection.get() != "":
        if departments_delete.cget("state") == "disabled":
            departments_delete.configure(state="normal")
    # Disable the "Delete Entry" when no entries are selected:
    else:
        if departments_delete.cget("state") == "normal":
            departments_delete.configure(state="disabled")
    # Schedule another loop of this function if the window is still open:
    if StVars.notebook_on:
        root.after(100, notebook_update)


# Updated: All good for now.
def pop_filter(clear: bool = False):
    """
    This populates the filtered record list based on active filters and sorting options, with optional stacking.
    Alternatively, it can also clear the filtered record list, enforcing the use of the standard master list in
    populating the viewport table instead.

    Args:
        clear (bool, optional): Set to True to bypass the use of filters and sorting. Defaults to False.
    """
    # Regardless of the value of 'clear', the record list needs to be emptied in order to refresh accurately:
    while len(StVars.records_filter) > 0:
        StVars.records_filter.remove(StVars.records_filter[0])
    if not clear:
        while len(StVars.total_refs) > 0:
            # Properly destroy the entry boxes in the total bar:
            StVars.total_refs[0].destroy()
            # Then remove the references to those entry boxes in the total references list:
            StVars.total_refs.remove(StVars.total_refs[0])
        while len(StVars.total_values) > 0:
            # Then remove the values in the total values list:
            StVars.total_values.remove(StVars.total_values[0])
        # In the case where 'clear' is False, add the contents of 'StVars.records_master', which should have already
        # been sorted by timestamp prior to calling this function:
        for record in StVars.records_master:
            StVars.records_filter.append(record)
        # If the "Hide Deleted" toggle is on, remove all deleted records from the filtered list:
        # * This is performed from the bottom up to prevent indexing errors:
        if toggle_deleted.get():
            iter8 = len(StVars.records_filter) - 1
            while iter8 >= 0:
                if StVars.records_filter[iter8]["Status"] == "Deleted":
                    StVars.records_filter.remove(StVars.records_filter[iter8])
                iter8 -= 1
        # Remove invalid records if "Hide Invalid" is toggled on:
        if toggle_invalid.get():
            iter8 = len(StVars.records_filter) - 1
            while iter8 >= 0:
                if StVars.records_filter[iter8]["Status"] == "Invalid":
                    StVars.records_filter.remove(StVars.records_filter[iter8])
                iter8 -= 1
        # Remove saved records if "Hide Saved" is toggled on:
        if toggle_saved.get():
            iter8 = len(StVars.records_filter) - 1
            while iter8 >= 0:
                if StVars.records_filter[iter8]["Status"] == "Saved":
                    StVars.records_filter.remove(StVars.records_filter[iter8])
                iter8 -= 1
        # Remove temp records if "Hide Temporary" is toggled on:
        if toggle_temp.get():
            iter8 = len(StVars.records_filter) - 1
            while iter8 >= 0:
                if StVars.records_filter[iter8]["Status"] == "Temporary":
                    StVars.records_filter.remove(StVars.records_filter[iter8])
                iter8 -= 1
        if (StVars.sort_column != "") and (len(StVars.records_filter) > 0):
            # If a sorting option is active, sort the filtered records using the chosen column:
            # * The 'lambda' function in this prevents empty cells from throwing TypeErrors.
            StVars.records_filter.sort(
                key=lambda d: (d[StVars.sort_column] == "", d[StVars.sort_column]),
                reverse=StVars.sort_descending,
            )
            # Sorting must also be applied to all the component record lists to prevent indexing errors when
            # modifying sorted records:
            if len(StVars.records_deleted) > 0:
                StVars.records_deleted.sort(
                    key=lambda d: (d[StVars.sort_column] == "", d[StVars.sort_column]),
                    reverse=StVars.sort_descending,
                )
            if len(StVars.records_invalid) > 0:
                StVars.records_invalid.sort(
                    key=lambda d: (d[StVars.sort_column] == "", d[StVars.sort_column]),
                    reverse=StVars.sort_descending,
                )
            # * TypeErrors can only be raised by invalid records, so only the master filtered list, the invalid record
            # * list, and the deleted record list need to account for them.
            if len(StVars.records_saved) > 0:
                StVars.records_saved.sort(
                    key=lambda d: d[StVars.sort_column], reverse=StVars.sort_descending
                )
            if len(StVars.records_temp) > 0:
                StVars.records_temp.sort(
                    key=lambda d: d[StVars.sort_column], reverse=StVars.sort_descending
                )
        # In the case where all records have been filtered out of the table, create a single record informing the user:
        if len(StVars.records_filter) == 0:
            StVars.records_filter.append({"Status": "All Records Hidden"})
            # Also create an empty placeholder entry box to fill out the total bar:
            total_ref_0 = tk.Entry(total_bar, state="disabled")
            # Add it to the total reference list so it can be properly destroyed when the table updates:
            StVars.total_refs.append(total_ref_0)
            # Draw the entry box to the screen:
            total_ref_0.pack(side="left", fill="x", expand=True)
        else:
            box = 0
            keys = list(StVars.records_filter[0].keys())
            # Create one total bar entry box for each column in the table:
            while box < len(keys):
                col_total_box = tk.Entry(total_bar)
                index = 0
                # Ensure that empty cells are skipped:
                while StVars.records_filter[index][keys[box]] == "":
                    index += 1
                    # If all cells in the column are empty (all invalid records), just set 'index' back to zero and
                    # break out of the loop.
                    if index == len(StVars.records_filter):
                        index = 0
                        break
                # Only total numeric fields:
                if (
                    type(StVars.records_filter[index][keys[box]]) == float
                    or type(StVars.records_filter[index][keys[box]]) == int
                ):
                    # Add a new value to the end of the list, initialized at zero:
                    StVars.total_values.append(0)
                    for record in StVars.records_filter:
                        # Skip empty cells, but add the values of all valid cells in the column:
                        if record[keys[box]] != "":
                            StVars.total_values[box] += record[keys[box]]
                    # Round float values to 2 decimal places:
                    # * I'm not sure why this happens, but floats sometimes gather random bits during the summing
                    # * process, somehow taking '100.00 + 2.35' and returning a result of '102.350000001'.
                    if type(StVars.total_values[box]) == float:
                        StVars.total_values[box] = round(StVars.total_values[box], 2)
                # If the field is non-numeric (or all invalid), just make its entry box empty:
                else:
                    StVars.total_values.append("")
                # Add the resulting value to the entry box:
                col_total_box.insert(0, str(StVars.total_values[box]))
                # Make the entry box read-only:
                col_total_box.configure(state="readonly")
                # Place it in the total bar, packing left to right and expanding to fill the row:
                # * This ensures that the entry boxes are the same size as their respective table rows.
                col_total_box.pack(side="left", fill="x", expand=True)
                # Add the reference for the entry box to a persistent list so it can be properly destroyed when updated:
                StVars.total_refs.append(col_total_box)
                box += 1


# Updated: All good for now.
def pop_listbox(tab: str):
    """
    Populates the list-boxes in the Validation Control window when the "Auto-Populate" button is pressed.

    Args:
        tab (str): The name of the tab to populate ("Employee", "Location", or "Department").
    """
    # Direct the program to the correct StVars list based on the value of 'tab':
    if tab == "Employee":
        list_picked = StVars.valid_employees
    elif tab == "Location":
        list_picked = StVars.valid_locations
    elif tab == "Department":
        list_picked = StVars.valid_departments
    # Only update lists when they are included in the currently loaded records:
    if tab in base_tree["columns"]:
        # Check for active filters and sorts first. If yes, load the list values from the filtered records:
        if len(StVars.records_filter) > 0:
            for record in StVars.records_filter:
                # * PyCharm throws a "Local variable 'list_picked' might be referenced before assignment" warning for
                # * this line, and again for the one 6 lines down from it. Don't fix either of them. The variable IS
                # * referenced before assignment, but that is intentional.
                list_picked.append(record[tab])
            # Refresh all validation lists to remove duplicates:
            refresh_lists()
        # If there aren't any filters or sorts active, load values from the master list instead:
        elif len(StVars.records_master) > 0:
            for record in StVars.records_master:
                list_picked.append(record[tab])
            # Refresh all validation lists to remove duplicates:
            refresh_lists()


# Updated: All good for now.
def pop_master(send_log: bool = False):
    """
    This clears the current master record list and repopulates it with data from the saved, deleted, invalid, and temp
    record lists. It is called any time the component record lists are modified, refreshing of the viewport table.

    Args:
        send_log (bool, optional): When True, a Datalog entry is sent to 'log_msg' containing an updated total record
            count. Note that this does NOT result in a popup, only a log entry. Defaults to False.
    """
    iter8 = 0
    while len(StVars.records_master) > 0:
        # Empty the contents of 'StVars.records_master' first:
        StVars.records_master.remove(StVars.records_master[0])
    while len(StVars.total_refs) > 0:
        # Properly destroy each entry box in the total bar:
        StVars.total_refs[0].destroy()
        # Then clear the references from the total references list:
        StVars.total_refs.remove(StVars.total_refs[0])
    while len(StVars.total_values) > 0:
        # Then clear the values from the total values list:
        StVars.total_values.remove(StVars.total_values[0])
    # Ensure that 'StVars.records_deleted' is sorted by its first column before importing its contents:
    if len(StVars.records_deleted) > 0:
        heading = list(StVars.records_deleted[0].keys())[0]
        StVars.records_deleted.sort(
            key=lambda d: (d[heading] == "", d[heading]), reverse=False
        )
    for record in StVars.records_deleted:
        # Next, add the entire contents of 'StVars.records_deleted' to the empty 'StVars.records_master':
        StVars.records_master.append(record)
        # Keep track of the number of records added to 'StVars.records_master' from this list:
        iter8 += 1
    # Ensure that 'StVars.records_invalid' is sorted by its first column before importing its contents:
    if len(StVars.records_invalid) > 0:
        heading = list(StVars.records_invalid[0].keys())[0]
        StVars.records_invalid.sort(
            key=lambda d: (d[heading] == "", d[heading]), reverse=False
        )
    for record in StVars.records_invalid:
        # Do the same for the other three lists:
        StVars.records_master.append(record)
        iter8 += 1
    # Ensure that 'StVars.records_saved' is sorted by its first column before importing its contents:
    if len(StVars.records_saved) > 0:
        heading = list(StVars.records_saved[0].keys())[0]
        StVars.records_saved.sort(
            key=lambda d: (d[heading] == "", d[heading]), reverse=False
        )
    for record in StVars.records_saved:
        StVars.records_master.append(record)
        iter8 += 1
    # Ensure that 'StVars.records_temp' is sorted by its first column before importing its contents:
    if len(StVars.records_temp) > 0:
        heading = list(StVars.records_temp[0].keys())[0]
        StVars.records_temp.sort(
            key=lambda d: (d[heading] == "", d[heading]), reverse=False
        )
    for record in StVars.records_temp:
        StVars.records_master.append(record)
        iter8 += 1
    # As long as at least one record was added to 'StVars.records_master', print a message to a popup and to the Datalog
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
        if len(StVars.records_temp) > 0:
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
            root.unbind(sequence="<Return>")
            root.unbind(sequence="<Delete>")
            root.unbind(sequence="<Shift-Return>")
            root.unbind(sequence="<Shift-Delete>")
        # Only enable data export menu option and shortcut button if there is at least one "Saved" record:
        if len(StVars.records_saved) > 0:
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
        if len(StVars.records_deleted) > 0:
            view_menu.entryconfig("Hide Deleted Records", state="normal")
            btn_hide_deleted.config(state="normal")
        # Otherwise, disable them:
        else:
            view_menu.entryconfig("Hide Deleted Records", state="disabled")
            btn_hide_deleted.config(state="disabled")
        # Enable batch actions for invalid records if there are any invalid records:
        if len(StVars.records_invalid) > 0:
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
        # Finally, sort the contents of 'StVars.records_master' by its first column:
        if len(StVars.records_master) > 0:
            heading = list(StVars.records_master[0].keys())[0]
            StVars.records_master.sort(
                key=lambda d: (d[heading] == "", d[heading]), reverse=False
            )
        box = 0
        keys = list(StVars.records_master[0].keys())
        # Create one total bar entry box for each column in the table:
        while box < len(keys):
            col_total_box = tk.Entry(total_bar)
            index = 0
            # Ensure that empty cells are skipped:
            while StVars.records_master[index][keys[box]] == "":
                index += 1
                # If all cells in the column are empty (all invalid records), just set 'index' back to zero and break
                # out of the loop.
                if index == len(StVars.records_master):
                    index = 0
                    break
            # Only total numeric fields:
            if (
                type(StVars.records_master[index][keys[box]]) == float
                or type(StVars.records_master[index][keys[box]]) == int
            ):
                # Add a new value to the end of the list, initialized at zero:
                StVars.total_values.append(0)
                for record in StVars.records_master:
                    # Skip empty cells, but add the values of all valid cells in the column:
                    if record[keys[box]] != "":
                        StVars.total_values[box] += record[keys[box]]
                # Round float values to 2 decimal places:
                # * I'm not sure why this happens, but floats sometimes gather random bits during the summing process,
                # * somehow taking '100.00 + 2.35' and returning a result of '102.350000001'.
                if type(StVars.total_values[box]) == float:
                    StVars.total_values[box] = round(StVars.total_values[box], 2)
            # If the field is non-numeric (or all invalid), just make its entry box empty:
            else:
                StVars.total_values.append("")
            # Add the resulting value to the entry box:
            col_total_box.insert(0, str(StVars.total_values[box]))
            # Make the entry box read-only:
            col_total_box.configure(state="readonly")
            # Place it in the total bar, packing left to right and expanding to fill the row:
            # * This ensures that the entry boxes are the same size as their respective table rows.
            col_total_box.pack(side="left", fill="x", expand=True)
            # Add the reference for the entry box to a persistent list so it can be properly destroyed when updated:
            StVars.total_refs.append(col_total_box)
            box += 1
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
    """
    # Open the selected file as a DataFrame first. Read data from '.csv' files using 'pd.read_csv()':
    if path.split(".")[-1] == "csv":
        # Fill any blank cells with empty strings instead of 'NaN':
        data_loaded = pd.DataFrame(pd.read_csv(path)).fillna("")
    # Read data from all other supported file types using 'pd.read_excel()':
    else:
        data_loaded = pd.DataFrame(pd.read_excel(path)).fillna("")
    # Add a status key to define the record in the 'StVars.records_temp' department:
    data_loaded["Status"] = "Temporary"
    # Convert the DataFrame to a list of dictionaries for more flexible manipulation:
    data_loaded = data_loaded.to_dict(orient="records")
    # Pass the entire list of records into 'StVars.records_temp' for persistent storage:
    iter8 = 0
    while len(data_loaded) > 0:
        StVars.records_temp.append(data_loaded[0])
        data_loaded.remove(data_loaded[0])
        # Keep count of how many records were loaded into 'StVars.records_temp':
        iter8 += 1
    if iter8 > 0:
        # Pass the tallied record count into the Datalog:
        log_msg(
            msg=(str(iter8) + ' records loaded from "' + str(path) + '".'),
            popup=False,
        )
        StVars.current_file = str(path)
        # Only pass on to the next step if there are records left to validate:
        validate_temp()


# Updated: All good for now.
def pop_table():
    """
    Populates the viewport table (Treeview widget) with data. If any filter or sort is active, it will populate with
    the contents of the filtered record list; otherwise, it will populate with the contents of the master record list.
    """
    # Initialize an empty list variable to hold either 'StVars.records_filter' or 'StVars.records_master':
    list_used = list()
    # If there are any records selected in the treeview widget, deselect them:
    if len(base_tree.selection()) > 0:
        base_tree.selection_remove(base_tree.selection()[0])
    # 'StVars.records_filter' will only have records in it if a filter or sort is active. If so, use
    # 'StVars.records_filter' to name the column headers:
    if len(StVars.records_filter) > 0:
        base_tree["columns"] = tuple(StVars.records_filter[0].keys())
        list_used = StVars.records_filter
    # If 'StVars.records_filter' is empty, use 'StVars.records_master' to name the column headers instead:
    elif len(StVars.records_master) > 0:
        base_tree["columns"] = tuple(StVars.records_master[0].keys())
        list_used = StVars.records_master
    # If both 'StVars.records_filter' and 'StVars.records_master' are empty, don't provide any column headers:
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
def refresh_lists():
    """
    Sorts validation lists, and removes any duplicate entries, and refreshes the list-boxes in the "Validation Control"
    window.
    """
    # Empty the listbox in the "Employees" tab:
    while employees_box.size() > 0:
        employees_box.delete(0)
    # Iterate through the employee validation list from the bottom up, removing any duplicates:
    if len(StVars.valid_employees) > 1:
        invalid8 = len(StVars.valid_employees) - 1
        while invalid8 >= 0:
            iter8 = 0
            while iter8 < invalid8:
                if StVars.valid_employees[invalid8] == StVars.valid_employees[iter8]:
                    StVars.valid_employees.remove(StVars.valid_employees[invalid8])
                    break
                iter8 += 1
            invalid8 -= 1
    # Sort the validation list:
    if len(StVars.valid_employees) > 0:
        StVars.valid_employees.sort()
    # Repopulate the listbox with the refreshed validation list:
    if len(StVars.valid_employees) > 0:
        iter8 = 0
        while iter8 < len(StVars.valid_employees):
            employees_box.insert("end", StVars.valid_employees[iter8])
            iter8 += 1
    # Empty the listbox in the "Locations" tab:
    while locations_box.size() > 0:
        locations_box.delete(0)
    # Iterate through the location validation list from the bottom up, removing any duplicates:
    if len(StVars.valid_locations) > 1:
        invalid8 = len(StVars.valid_locations) - 1
        while invalid8 >= 0:
            iter8 = 0
            while iter8 < invalid8:
                if StVars.valid_locations[invalid8] == StVars.valid_locations[iter8]:
                    StVars.valid_locations.remove(StVars.valid_locations[invalid8])
                    break
                iter8 += 1
            invalid8 -= 1
    # Sort the validation list:
    if len(StVars.valid_locations) > 0:
        StVars.valid_locations.sort()
    # Repopulate the listbox with the refreshed validation list:
    if len(StVars.valid_locations) > 0:
        iter8 = 0
        while iter8 < len(StVars.valid_locations):
            locations_box.insert("end", StVars.valid_locations[iter8])
            iter8 += 1
    # Empty the listbox in the "Departments" tab:
    while departments_box.size() > 0:
        departments_box.delete(0)
    # Iterate through the department validation list from the bottom up, removing any duplicates:
    if len(StVars.valid_departments) > 1:
        invalid8 = len(StVars.valid_departments) - 1
        while invalid8 >= 0:
            iter8 = 0
            while iter8 < invalid8:
                if (
                    StVars.valid_departments[invalid8]
                    == StVars.valid_departments[iter8]
                ):
                    StVars.valid_departments.remove(StVars.valid_departments[invalid8])
                    break
                iter8 += 1
            invalid8 -= 1
    # Sort the validation list:
    if len(StVars.valid_departments) > 0:
        StVars.valid_departments.sort()
    # Repopulate the listbox with the refreshed validation list:
    if len(StVars.valid_departments) > 0:
        iter8 = 0
        while iter8 < len(StVars.valid_departments):
            departments_box.insert("end", StVars.valid_departments[iter8])
            iter8 += 1


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
    """
    # Clear the contents of the viewport table:
    clear_table()
    # Update validation for all records:
    validate_all()
    # Refresh the contents of 'StVars.records_master' (and optionally send a Datalog message):
    if master_log:
        pop_master(send_log=True)
    else:
        pop_master()
    if StVars.filter_toggle or StVars.sort_column != "":
        # Refresh the contents of 'StVars.records_filter' if any filters or sorts are toggled on:
        pop_filter()
    else:
        pop_filter(clear=True)
    if repop_tree:
        # Repopulate the viewport table with data:
        pop_table()
    else:
        # If the table is to remain empty, remove all the column headers.
        base_tree["columns"] = []


# Updated: All good for now.
def reject_all():
    """
    Rejects all temporary records in one batch action.
    """
    # Only do anything if there are temp records loaded:
    if len(StVars.records_temp) > 0:
        # If there are any selected rows in the viewport, deselect them:
        if len(base_tree.selection()) > 0:
            base_tree.selection_remove(base_tree.selection()[0])
        iter8 = 0
        while len(StVars.records_temp) > 0:
            # Change the status of each record:
            StVars.records_temp[0]["Status"] = "Deleted"
            # Add the record to the end of the deleted records list:
            StVars.records_deleted.append(StVars.records_temp[0])
            # Remove the record from the temp list:
            StVars.records_temp.remove(StVars.records_temp[0])
            iter8 += 1
        if iter8 > 0:
            # Sort all deleted records by the first column:
            if len(StVars.records_deleted) > 0:
                heading = list(StVars.records_deleted[0].keys())[0]
                StVars.records_deleted.sort(
                    key=lambda d: (d[heading] == "", d[heading]), reverse=False
                )
            # Pass a message to the Datalog if changes were made:
            log_msg(msg=(str(iter8) + " records were cleared from memory."))
            # Then refresh the table and have the master list pass its own message to the Datalog:
            refresh_table(master_log=True)


# Updated: All good for now.
def reject_selection():
    """
    Deletes the selected temp, saved, and invalid records, excluding them from export. Supports single and multiple
    selections.
    """
    # Send a call to 'get_selection()' for data on the currently selected Treeview rows:
    data_address = get_selection(stop_select=True)
    # Only proceed if valid information was returned:
    if data_address is not None:
        row = 0
        iter8 = 0
        while row < len(data_address[0]):
            # Compare the data from 'get_selection()' with the records in the saved records list:
            if data_address[0][row] == "Saved":
                # Modify the status to "Deleted":
                # * See the 'Notes' in 'commit_selection()' for why this raises a warning in PyCharm.
                StVars.records_saved[data_address[1][row]]["Status"] = "Deleted"
                # Add the record to the deleted records list:
                StVars.records_deleted.append(
                    StVars.records_saved[data_address[1][row]]
                )
                # Record successes:
                iter8 += 1
            elif data_address[0][row] == "Temporary":
                # Modify the status to "Deleted":
                # * See the 'Notes' in 'commit_selection()' for why this raises a warning in PyCharm.
                StVars.records_temp[data_address[1][row]]["Status"] = "Deleted"
                # Add the record to the deleted records list:
                StVars.records_deleted.append(StVars.records_temp[data_address[1][row]])
                # Record successes:
                iter8 += 1
            elif data_address[0][row] == "Invalid":
                # Modify the status to "Deleted":
                # * See the 'Notes' in 'commit_selection()' for why this raises a warning in PyCharm.
                StVars.records_invalid[data_address[1][row]]["Status"] = "Deleted"
                # Add the record to the deleted records list:
                StVars.records_deleted.append(
                    StVars.records_invalid[data_address[1][row]]
                )
                # Record successes:
                iter8 += 1
            row += 1
        # Remove each record from its previous record list from the bottom up:
        # * This can't be done top down because it will modify the indexes of lower records.
        row = len(data_address[0]) - 1
        while row >= 0:
            if data_address[0][row] == "Saved":
                # Remove record from the saved records list:
                StVars.records_saved.remove(StVars.records_saved[data_address[1][row]])
            elif data_address[0][row] == "Temporary":
                # Remove record from the temp records list:
                StVars.records_temp.remove(StVars.records_temp[data_address[1][row]])
            elif data_address[0][row] == "Invalid":
                # Remove record from the invalid records list:
                StVars.records_invalid.remove(
                    StVars.records_invalid[data_address[1][row]]
                )
            elif data_address[0][row] == "Deleted":
                # Permanently remove double-deleted records from the deleted records list:
                StVars.records_deleted.remove(
                    StVars.records_deleted[data_address[1][row]]
                )
                # Record double-deletions:
                iter8 += 1
            row -= 1
        if iter8 > 0:
            # Only refresh the table if changes were made:
            refresh_table(repop_tree=True)
            # Print the correct Datalog message for records (either singular or plural):
            if iter8 > 1:
                log_msg(str(iter8) + " records were removed from memory.", popup=False)
            else:
                log_msg("1 record was removed from memory.", popup=False)
            row = 0
            while row < len(data_address[2]) and data_address[2][row] < len(base_tree.get_children()):
                # Since performing this operation deselects the rows, reselect them:
                base_tree.selection_add(base_tree.get_children()[data_address[2][row]])
                row += 1
            # Refocus the cursor on the topmost record:
            if data_address[2][0] < len(base_tree.get_children()):
                base_tree.focus(base_tree.get_children()[data_address[2][0]])


# Updated: All good for now.
def root_update():
    """
    A recreation of a traditional main loop run every 100 ms, written as a partial redirection of the 'mainloop()'
    function from 'tkinter' to allow custom updates to be defined in this file without overriding 'mainloop'.
    """
    # Set the "Toggle Filter..." button to the correct state depending on the value of 'StVars.filter_toggle':
    if StVars.filter_toggle and btn_filter.cget("relief") == "raised":
        btn_filter.configure(relief="sunken")
    elif (not StVars.filter_toggle) and (btn_filter.cget("relief") == "sunken"):
        btn_filter.configure(relief="raised")
    # Toggle on the menu options and shortcut buttons associated with the record status of the selected row:
    if len(base_tree.selection()) > 0:
        select_toggle(state=True)
    # If no row is selected, toggle off menu options and shortcut buttons that rely on records:
    else:
        select_toggle(state=False)
    # If there are Datalog messages, enable the "Save Datalog Contents" menu option:
    if len(StVars.datalog_msgs) > 0:
        if view_menu.entrycget("Save Datalog Contents", option="state") == "disabled":
            view_menu.entryconfigure("Save Datalog Contents", state="normal")
    # If no Datalog contents, disable saving the Datalog:
    else:
        if view_menu.entrycget("Save Datalog Contents", option="state") == "normal":
            view_menu.entryconfigure("Save Datalog Contents", state="disabled")
    # Ensure the default treeview column stays hidden:
    base_tree.column("#0", width=0, stretch=False)
    # If all temp records have been accepted or rejected, reset the filename display to reflect this:
    if len(StVars.records_temp) == 0:
        status_file.configure(text="Unmanaged Records: None")
    else:
        # Make sure the status bar filename display updates when it changes:
        status_file.configure(
            text=(
                "Unmanaged Records: "
                + str(len(StVars.records_temp))
                + ' from "'
                + StVars.current_file
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
    Saves the contents of 'StVars.datalog_msgs' to a text file in the user's "My Documents/SalesTrax/Datalog" folder and
    clears the contents of 'StVars.datalog_msgs'. Log files end with the date in "YYYY-MM-DD" format and an iterative
    3-digit index number that allows multiple logs to be saved on the same date without overwriting earlier logs.
    """
    # Do nothing if there are no messages in the Datalog:
    if len(StVars.datalog_msgs) > 0:
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
        for msg in StVars.datalog_msgs:
            file.write(msg)
        # Close the file to save its contents:
        file.close()
        # Clear the contents of 'StVars.datalog_msgs' to prevent message doubling over multiple log files:
        # * This is really only necessary when the user manually saves the log.
        while len(StVars.datalog_msgs) > 0:
            StVars.datalog_msgs.remove(StVars.datalog_msgs[0])
        # Clear the contents of the 'datalog_body' Text object as well:
        datalog_body.delete("1.0", "end")


# Updated: All good for now.
def select_toggle(state: bool):
    """
    Enables and disables menu options, shortcut buttons, and keybindings based on the record status of the currently
    selected table row (or lack thereof).

    Args:
        state (bool): True when a row is selected, False when no row is selected.
    """
    if state:
        # Request information about which record is currently selected:
        data_address = get_selection(stop_select=False)
        # If the request comes back with no data, stop:
        if data_address is not None:
            # Add keybindings for selection-based edits:
            # * 'event' must be declared but *not* used here, or else it would need to be declared in the functions,
            # * despite not being used there, either. It's just a quirk of 'tkinter' keybinding, apparently.
            root.bind(sequence="<Return>", func=lambda event: commit_selection())
            root.bind(sequence="<Delete>", func=lambda event: reject_selection())
            if ("Saved" in data_address[0]) or ("Invalid" in data_address[0]):
                # When a saved or invalid record is selected, enable events relating to individual saved and invalid
                # records and disable those that only act on other record statuses:
                if (
                    edit_menu.entrycget("Reject Selection", option="state")
                    == "disabled"
                ):
                    edit_menu.entryconfig("Reject Selection", state="normal")
                btn_reject_s.config(state="normal")
                if ("Deleted" not in data_address[0]) and (
                    "Temporary" not in data_address[0]
                ):
                    if (
                        edit_menu.entrycget("Commit Selection", option="state")
                        == "normal"
                    ):
                        edit_menu.entryconfig("Commit Selection", state="disabled")
                    btn_commit_s.config(state="disabled")
                else:
                    if (
                        edit_menu.entrycget("Commit Selection", option="state")
                        == "disabled"
                    ):
                        edit_menu.entryconfig("Commit Selection", state="normal")
                    btn_commit_s.config(state="normal")
            if "Deleted" in data_address[0]:
                # When a deleted record is selected, enable events relating to individual deleted records and disable
                # those that only act on other record statuses:
                if (
                    edit_menu.entrycget("Commit Selection", option="state")
                    == "disabled"
                ):
                    edit_menu.entryconfig("Commit Selection", state="normal")
                btn_commit_s.config(state="normal")
                if (
                    ("Saved" not in data_address[0])
                    and ("Invalid" not in data_address[0])
                    and ("Temporary" not in data_address[0])
                ):
                    if (
                        edit_menu.entrycget("Reject Selection", option="state")
                        == "normal"
                    ):
                        edit_menu.entryconfig("Reject Selection", state="disabled")
                    btn_reject_s.config(state="disabled")
                else:
                    if (
                        edit_menu.entrycget("Reject Selection", option="state")
                        == "disabled"
                    ):
                        edit_menu.entryconfig("Reject Selection", state="normal")
                    btn_reject_s.config(state="normal")
            if "Temporary" in data_address[0]:
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
    else:
        # If there is no selected row, disable all events and keybindings that act on individual records:
        if edit_menu.entrycget("Commit Selection", option="state") == "normal":
            edit_menu.entryconfig("Commit Selection", state="disabled")
        btn_commit_s.config(state="disabled")
        if edit_menu.entrycget("Reject Selection", option="state") == "normal":
            edit_menu.entryconfig("Reject Selection", state="disabled")
        btn_reject_s.config(state="disabled")
        root.unbind(sequence="<Return>")
        root.unbind(sequence="<Delete>")


# Updated: All good for now.
def toggle_datalog(state: bool = False):
    """
    Handles the visibility of the Datalog window. Technically speaking, it does not actually close when SalesTrax is
    running; it only hides.

    Args:
        state (bool, optional): When True, the Datalog becomes visible, and when False, it is hidden. Defaults to False.
    """
    if state:
        # Reveal the Datalog window:
        datalog.deiconify()
    else:
        # Hide the Datalog window:
        datalog.withdraw()


# Updated: All good for now.
def toggle_filter():
    """
    This turns off all active filters and toggles when the user invokes it.
    """
    # Only do something if the filter toggle is already on:
    if StVars.filter_toggle:
        # Turn off the "Hide Deleted" toggle if it is on:
        if toggle_deleted.get():
            btn_hide_deleted.invoke()
        # Turn off the "Hide Invalid" toggle if it is on:
        if toggle_invalid.get():
            btn_hide_invalid.invoke()
        # Turn off the "Hide Saved" toggle if it is on:
        if toggle_saved.get():
            btn_hide_saved.invoke()
        # Turn off the "Hide Temporary" toggle if it is on:
        if toggle_temp.get():
            btn_hide_temp.invoke()
        # Clear the sorting variables:
        StVars.sort_column = str()
        StVars.sort_descending = True
        # Turn off the filter toggle itself:
        StVars.filter_toggle = False
        # Refresh the table contents using default sorting in the master records list:
        refresh_table()


# Updated: All good for now.
def toggle_notebook(state: bool = False, tab: str = "employees"):
    """
    Handles the visibility of the Validation Control window. Technically speaking, it does not actually close when
    SalesTrax is running; it only hides.

    Args:
        state (bool, optional): When True, the window becomes visible, and when False, it is hidden. Defaults to False.
        tab (str, optional): The name of the tab to open ("employees", "locations", or "departments"). Defaults to
            "employees".
    """
    if state:
        # Reveal the Validation Control window:
        val_control.deiconify()
        # Set it to the chosen tab:
        if tab == "employees":
            val_notebook.select(employees_tab)
        elif tab == "locations":
            val_notebook.select(locations_tab)
        elif tab == "departments":
            val_notebook.select(departments_tab)
        # Start the Validation Control update loop:
        StVars.notebook_on = True
        notebook_update()
        # Refresh the validation lists:
        refresh_lists()
        # Disable operations on 'root' window while the notebook is open:
        root.attributes("-disabled", True)
        # Direct keyboard focus to the Validation Control window:
        val_control.focus_set()
    else:
        # Hide the Validation Control window:
        val_control.withdraw()
        # Turn off the Validation Control update loop:
        StVars.notebook_on = False
        # Re-enable 'root' window processing:
        root.attributes("-disabled", False)
        # Re-focus on 'root' window:
        # * For some reason, the 'root' window hides behind other open windows without this command.
        root.focus_force()
        # Refresh the table, in case any record statuses have changed as a result of validation editing:
        refresh_table()


# Updated: All good for now.
def tree_click(event):
    """
    This determines which area of the Treeview object was clicked to determine which action it takes. If a separator was
    clicked, do nothing. If a column header was clicked, sort the contents of the tree based the column header.

    Args:
        event (tkinter.Event): A standard tkinter keybinding event. In this case, '<Button-1>' (mouse left-click), but
        it should not be manually declared.
    Returns:
        (str): This returns "break" back to the calling event, preventing it from performing its default behavior.
    """
    # Prevent column resizing by intercepting clicks on column separators:
    if base_tree.identify_region(event.x, event.y) == "separator":
        return "break"
    # If a column header was clicked, gather more information:
    elif base_tree.identify_region(event.x, event.y) == "heading":
        # Get the index of the column header clicked:
        heading = int(base_tree.identify_column(x=event.x)[1:]) - 1
        # Turn the gathered index into its actual text (for dictionary key comparisons):
        heading = base_tree["columns"][heading]
        # Only sort descending if the column is already sorted ascending:
        if (not StVars.sort_descending) and (StVars.sort_column == heading):
            StVars.sort_descending = True
        # Otherwise, sort ascending first:
        else:
            StVars.sort_descending = False
        # Store the gathered heading in a persistent variable:
        StVars.sort_column = heading
        # Turn on the filter toggle variable:
        StVars.filter_toggle = True
        # Refresh the contents of the table:
        refresh_table()


# Updated: All good for now.
def update_record(record: dict, values: list):
    """
    Performs direct record modifications based on criteria defined in 'edit_record()'.

    Args:
        record (dict): The record list address of the record to be modified. Note: This is an object reference.
        values (list): The new values to use in the record modification. Note: This is a list of object references.
    """
    # Change the record one key-value pair at a time:
    iter8 = 0
    while iter8 < len(values):
        # Ensure that Timestamps are properly formatted for sorting:
        if list(record.keys())[iter8] == "Timestamp":
            try:
                record[list(record.keys())[iter8]] = pd.Timestamp(values[iter8].get())
            except ValueError:
                # If the user only provides an empty entry field, delete the contents of that field:
                if values[iter8].get() == "":
                    record[list(record.keys())[iter8]] = ""
                # Otherwise, any other non-Timestamp datatypes should be ignored:
                else:
                    pass
        # Ensure that float values are properly formatted for sorting:
        elif (
            list(record.keys())[iter8] == "Cost"
            or list(record.keys())[iter8] == "Total"
        ):
            try:
                record[list(record.keys())[iter8]] = float(values[iter8].get())
            except ValueError:
                # If the user only provides an empty entry field, delete the contents of that field:
                if values[iter8].get() == "":
                    record[list(record.keys())[iter8]] = ""
                # Otherwise, any other non-numeric datatypes should be ignored:
                else:
                    pass
        # Ensure that integers are properly formatted for sorting:
        elif list(record.keys())[iter8] == "Count":
            try:
                record[list(record.keys())[iter8]] = int(values[iter8].get())
            except ValueError:
                # If the user only provides an empty entry field, delete the contents of that field:
                if values[iter8].get() == "":
                    record[list(record.keys())[iter8]] = ""
                # Otherwise, any other non-numeric datatypes should be ignored:
                else:
                    pass
        # String fields don't need any validation control; just copy them over:
        else:
            record[list(record.keys())[iter8]] = values[iter8].get()
        iter8 += 1
    # Refresh the table to ensure the update is immediately visible:
    refresh_table()


# Updated: All good for now.
def validate_all():
    """
    Iterates through the composite record lists to ensure their status hasn't been changed by validation control.
    Redistributes any records that have changed status according to their new status.
    """
    # Check saved records for newly invalid records:
    if len(StVars.records_saved) > 0:
        # Iterate in reverse order to prevent indexing errors:
        iter8 = len(StVars.records_saved) - 1
        while iter8 >= 0:
            # Create a sentinel value to prevent double-processing:
            invalid8 = 0
            # Invalidate saved records with missing values:
            if "" in StVars.records_saved[iter8].values():
                StVars.records_saved[iter8]["Status"] = "Invalid"
                StVars.records_invalid.append(StVars.records_saved[iter8])
                StVars.records_saved.remove(StVars.records_saved[iter8])
                # Set the sentinel value if any problems are found:
                invalid8 = 1
            if invalid8 == 0:
                # Only apply string invalidation if the validation lists are already defined:
                if (len(StVars.valid_employees) > 0) and (
                    "Employee" in StVars.records_saved[iter8].keys()
                ):
                    # Invalidate saved records with invalid "Employee" fields:
                    if (
                        StVars.records_saved[iter8]["Employee"]
                        not in StVars.valid_employees
                    ):
                        StVars.records_saved[iter8]["Status"] = "Invalid"
                        StVars.records_invalid.append(StVars.records_saved[iter8])
                        StVars.records_saved.remove(StVars.records_saved[iter8])
                        # Set the sentinel value if any problems are found:
                        invalid8 = 1
            if invalid8 == 0:
                # Only apply string invalidation if the validation lists are already defined:
                if (len(StVars.valid_locations) > 0) and (
                    "Location" in StVars.records_saved[iter8].keys()
                ):
                    # Invalidate saved records with invalid "Location" fields:
                    if (
                        StVars.records_saved[iter8]["Location"]
                        not in StVars.valid_locations
                    ):
                        StVars.records_saved[iter8]["Status"] = "Invalid"
                        StVars.records_invalid.append(StVars.records_saved[iter8])
                        StVars.records_saved.remove(StVars.records_saved[iter8])
                        # Set the sentinel value if any problems are found:
                        invalid8 = 1
            if invalid8 == 0:
                # Only apply string invalidation if the validation lists are already defined:
                if (len(StVars.valid_departments) > 0) and (
                    "Department" in StVars.records_saved[iter8].keys()
                ):
                    # Invalidate saved records with invalid "Department" fields:
                    if (
                        StVars.records_saved[iter8]["Department"]
                        not in StVars.valid_departments
                    ):
                        StVars.records_saved[iter8]["Status"] = "Invalid"
                        StVars.records_invalid.append(StVars.records_saved[iter8])
                        StVars.records_saved.remove(StVars.records_saved[iter8])
            iter8 -= 1
    if len(StVars.records_temp) > 0:
        iter8 = len(StVars.records_temp) - 1
        while iter8 >= 0:
            # Create a sentinel value to prevent double-processing:
            invalid8 = 0
            # Invalidate temp records with missing values:
            if "" in StVars.records_temp[iter8].values():
                StVars.records_temp[iter8]["Status"] = "Invalid"
                StVars.records_invalid.append(StVars.records_temp[iter8])
                StVars.records_temp.remove(StVars.records_temp[iter8])
                # Set the sentinel value if any problems are found:
                invalid8 = 1
            if invalid8 == 0:
                # Only apply string invalidation if the validation lists are already defined:
                if (len(StVars.valid_employees) > 0) and (
                    "Employee" in StVars.records_temp[iter8].keys()
                ):
                    # Invalidate temp records with invalid "Employee" fields:
                    if (
                        StVars.records_temp[iter8]["Employee"]
                        not in StVars.valid_employees
                    ):
                        StVars.records_temp[iter8]["Status"] = "Invalid"
                        StVars.records_invalid.append(StVars.records_temp[iter8])
                        StVars.records_temp.remove(StVars.records_temp[iter8])
                        # Set the sentinel value if any problems are found:
                        invalid8 = 1
            if invalid8 == 0:
                # Only apply string invalidation if the validation lists are already defined:
                if (len(StVars.valid_locations) > 0) and (
                    "Location" in StVars.records_temp[iter8].keys()
                ):
                    # Invalidate temp records with invalid "Location" fields:
                    if (
                        StVars.records_temp[iter8]["Location"]
                        not in StVars.valid_locations
                    ):
                        StVars.records_temp[iter8]["Status"] = "Invalid"
                        StVars.records_invalid.append(StVars.records_temp[iter8])
                        StVars.records_temp.remove(StVars.records_temp[iter8])
                        # Set the sentinel value if any problems are found:
                        invalid8 = 1
            if invalid8 == 0:
                # Only apply string invalidation if the validation lists are already defined:
                if (len(StVars.valid_departments) > 0) and (
                    "Department" in StVars.records_temp[iter8].keys()
                ):
                    # Invalidate temp records with invalid "Department" fields:
                    if (
                        StVars.records_temp[iter8]["Department"]
                        not in StVars.valid_departments
                    ):
                        StVars.records_temp[iter8]["Status"] = "Invalid"
                        StVars.records_invalid.append(StVars.records_temp[iter8])
                        StVars.records_temp.remove(StVars.records_temp[iter8])
            iter8 -= 1
    # Check the invalid records list last to ensure that everything there is supposed to be there:
    if len(StVars.records_invalid) > 0:
        # Iterate from the bottom up to prevent indexing errors:
        iter8 = len(StVars.records_invalid) - 1
        while iter8 >= 0:
            # Initialize variables for each field:
            employee = 0
            location = 0
            department = 0
            # Initialize a comparison variable:
            total = 0
            # Only set the "Employee" field's variable if it is being used for validation control:
            if (
                len(StVars.valid_employees) > 0
                and "Employee" in StVars.records_invalid[iter8].keys()
            ):
                employee = 1
            # Only set the "Location" field's variable if it is being used for validation control:
            if (
                len(StVars.valid_locations) > 0
                and "Location" in StVars.records_invalid[iter8].keys()
            ):
                location = 1
            # Only set the "Department" field's variable if it is being used for validation control:
            if (
                len(StVars.valid_departments) > 0
                and "Department" in StVars.records_invalid[iter8].keys()
            ):
                department = 1
            # Check the employee field if it's being used:
            if employee == 1:
                if StVars.records_invalid[iter8]["Employee"] in StVars.valid_employees:
                    total += 1
            # Check the location field if it's being used:
            if location == 1:
                if StVars.records_invalid[iter8]["Location"] in StVars.valid_locations:
                    total += 1
            # Check the department field if it's being used:
            if department == 1:
                if (
                    StVars.records_invalid[iter8]["Department"]
                    in StVars.valid_departments
                ):
                    total += 1
            # If all used fields pass validation AND there aren't any empty fields, turn the invalid record into a temp
            # record instead:
            if (total == (employee + location + department)) and (
                "" not in list(StVars.records_invalid[iter8].values())
            ):
                StVars.records_invalid[iter8]["Status"] = "Temporary"
                StVars.records_temp.append(StVars.records_invalid[iter8])
                StVars.records_invalid.remove(StVars.records_invalid[iter8])
            iter8 -= 1


# Updated: All good for now.
def validate_temp():
    """
    Processes every individual record in the temp record list after importing to ensure they meet the requirements of
    the program. This may include combining similar keys (such as "Date" and "Time" into "Timestamp"), renaming keys to
    match existing records, checking user-defined validation strings to locate misspelled or incorrect names, locations,
    or departments, etc.
    """
    # Define a dummy list for safer modification:
    data_loaded = list()
    # Loop through all records to ensure they are uniform in formatting:
    while len(StVars.records_temp) > 0:
        data_loaded.append(StVars.records_temp[0])
        StVars.records_temp.remove(StVars.records_temp[0])
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
    # Define a list of acceptable terms for "Department" columns:
    department_list = ["Product Category", "Category", "Product Type", "Type"]
    # If any of the list terms are used for column names, replace them with the default "Department":
    for item in department_list:
        if item in data_loaded[0].keys():
            data_loaded = pd.DataFrame.from_records(data_loaded)
            data_loaded = data_loaded.rename({item: "Department"}, axis="columns")
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
    for record in data_loaded:
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
        if "Total" in record.keys():
            if type(record["Total"]) != str:
                record["Total"] = round(record["Total"], 2)
    # Ensure the data is sorted by its first column, from oldest to most recent:
    # * Note that 'reverse' defaults to False, so this isn't actually needed, but I'm leaving it there anyway.
    if len(data_loaded) > 0:
        heading = list(data_loaded[0].keys())[0]
        data_loaded.sort(key=lambda d: (d[heading] == "", d[heading]), reverse=False)
    # Check to make sure the record isn't already loaded in a different list:
    iter8 = 0
    record = 0
    while record < len(data_loaded):
        rec = 0
        while rec < len(StVars.records_master):
            # Define a list of keys used in the record:
            keys = list(data_loaded[record].keys())
            # Remove the 'Status' key from the comparison list (because they WON'T match):
            keys.remove(keys[len(keys) - 1])
            # Now compare the key values from 'data_loaded' with the key values from 'StVars.records_master':
            if all(
                data_loaded[record].get(key) == StVars.records_master[rec].get(key)
                for key in keys
            ):
                # If they match, exclude the record and increment the exclusion counter:
                data_loaded.remove(data_loaded[record])
                iter8 += 1
            rec += 1
        # Now make sure the record didn't have a duplicate in the source file:
        while rec < len(StVars.records_temp):
            # In this case, the 'Status' keys would be the same, so we can just compare the entire dictionary:
            if data_loaded[record] == StVars.records_temp[rec]:
                # Again, if there's a match, exclude it from import and increment the exclusion counter.
                data_loaded.remove(data_loaded[record])
                iter8 += 1
            rec += 1
        record += 1
    if iter8 > 0:
        # Send any exclusion records to the Datalog along with a popup.
        log_msg(msg=(str(iter8) + " duplicate records were excluded from import."))
    # Move the records from the validation list into 'StVars.records_temp' for persistent storage:
    iter8 = 0
    invalid8 = 0
    while len(data_loaded) > 0:
        # If records contain empty cells, place them in the invalid records list:
        if "" in data_loaded[0].values():
            data_loaded[0]["Status"] = "Invalid"
            StVars.records_invalid.append(data_loaded[0])
            data_loaded.remove(data_loaded[0])
            # Count the number of invalid record imports:
            invalid8 += 1
        # Otherwise, add them to the temp records list:
        else:
            StVars.records_temp.append(data_loaded[0])
            data_loaded.remove(data_loaded[0])
            # Count the number of successful record imports:
            iter8 += 1
    # Send a grammatically correct count of successful and invalid records to the Datalog along with a popup:
    if (iter8 > 0) or (invalid8 > 0):
        if (iter8 > 1) and (invalid8 > 1):
            log_msg(
                msg=(
                    str(iter8)
                    + " valid records and "
                    + str(invalid8)
                    + " invalid records were successfully imported."
                )
            )
        elif (iter8 > 1) and (invalid8 == 1):
            log_msg(
                msg=(
                    str(iter8)
                    + " valid records and 1 invalid record were successfully imported."
                )
            )
        elif (iter8 == 1) and (invalid8 > 1):
            log_msg(
                msg=(
                    "1 valid record and "
                    + str(invalid8)
                    + " invalid records were successfully imported."
                )
            )
        elif (iter8 == 1) and (invalid8 == 1):
            log_msg(
                msg="1 valid record and 1 invalid record were successfully imported."
            )
        elif (iter8 > 1) and (invalid8 == 0):
            log_msg(msg=(str(iter8) + " valid records were successfully imported."))
        elif (iter8 == 1) and (invalid8 == 0):
            log_msg(msg="1 valid record was successfully imported.")
        elif (iter8 == 0) and (invalid8 > 1):
            log_msg(
                msg=(str(invalid8) + " invalid records were successfully imported.")
            )
        elif (iter8 == 0) and (invalid8 == 1):
            log_msg(msg="1 invalid record was successfully imported.")
    # Refresh the viewport table and log the number of records currently loaded.
    refresh_table(master_log=True)


# Incomplete: See "Task" comment in function body for details.
def write_file(path: str):
    """
    Writes all records with "Saved" status to a CSV, ODS, or XLSX file.

    Args:
        path (str): The filename and location of the new/updated file.
    """
    # Create a 'pandas' DataFrame object from the records in 'StVars.records_saved':
    data_frame = pd.DataFrame(StVars.records_saved)
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
    if len(StVars.records_saved) > 1:
        log_msg(
            str(len(StVars.records_saved)) + ' records were exported to "' + path + '"'
        )
    else:
        log_msg('1 record was exported to "' + path + '"')


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
# Store the width of the main monitor:
StVars.monitor_width = root.winfo_screenwidth()
# Store the height of the main monitor:
StVars.monitor_height = root.winfo_screenheight()

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
    command=hide_toggle,
)
view_menu.add_checkbutton(
    label="Hide Temporary Records",
    state="disabled",
    offvalue=0,
    onvalue=1,
    variable=toggle_temp,
    command=hide_toggle,
)
view_menu.add_checkbutton(
    label="Hide Invalid Records",
    offvalue=0,
    onvalue=1,
    variable=toggle_invalid,
    state="disabled",
    command=hide_toggle,
)
view_menu.add_checkbutton(
    label="Hide Deleted Records",
    offvalue=0,
    onvalue=1,
    variable=toggle_deleted,
    state="disabled",
    command=hide_toggle,
)
view_menu.add_separator()
view_menu.add_command(label="Open Datalog Window", command=lambda: toggle_datalog(True))
view_menu.add_command(label="Save Datalog Contents", state="disabled", command=save_log)
view_menu.add_separator()
view_menu.add_checkbutton(
    label="Toggle Filter...",
    offvalue=0,
    onvalue=1,
    state="disabled",
    command=toggle_filter,
)
# Finalize the contents of the "Edit" menu:
menu_bar.add_cascade(label="View", menu=view_menu)
# Define the "Lists" menu and its commands:
list_menu = tk.Menu(menu_bar, tearoff=0)
list_menu.add_command(
    label="Employees", command=lambda: toggle_notebook(state=True, tab="employees")
)
list_menu.add_command(
    label="Locations", command=lambda: toggle_notebook(state=True, tab="locations")
)
list_menu.add_command(
    label="Departments", command=lambda: toggle_notebook(state=True, tab="departments")
)
# Finalize the contents of the "Lists" menu:
menu_bar.add_cascade(label="Lists", menu=list_menu)
# Define the "Generate" menu and its commands:
data_menu = tk.Menu(menu_bar, tearoff=0)
data_menu.add_command(label="Line Chart", state="disabled", command=line_definition)
data_menu.add_command(label="Bar Chart", state="disabled", command=bar_definition)
data_menu.add_command(label="Pie Chart", state="disabled", command=log_msg)
# Finalize the contents of the "Generate" menu:
menu_bar.add_cascade(label="Generate", menu=data_menu)
# Define the "Help" menu and its commands:
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(
    label="Readme", command=lambda: link_to_github(page="blob/master/README.md")
)
help_menu.add_command(
    label="Changelog",
    command=lambda: link_to_github(page="blob/master/Docs/Changelog.txt"),
)
help_menu.add_separator()
help_menu.add_command(
    label="GitHub Wiki...", command=lambda: link_to_github(page="wiki/")
)
help_menu.add_command(
    label="GitHub Issues...", command=lambda: link_to_github(page="issues/")
)
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
img_refresh = ImageTk.PhotoImage(Image.open("Images/20/refresh_view.png"))
img_hide_saved = ImageTk.PhotoImage(Image.open("Images/20/hide_saved.png"))
img_hide_temp = ImageTk.PhotoImage(Image.open("Images/20/hide_temp.png"))
img_hide_invalid = ImageTk.PhotoImage(Image.open("Images/20/hide_invalid.png"))
img_hide_deleted = ImageTk.PhotoImage(Image.open("Images/20/hide_deleted.png"))
img_employee = ImageTk.PhotoImage(Image.open("Images/20/employees.png"))
img_location = ImageTk.PhotoImage(Image.open("Images/20/locations.png"))
img_department = ImageTk.PhotoImage(Image.open("Images/20/departments.png"))
img_filter = ImageTk.PhotoImage(Image.open("Images/20/filter.png"))
img_line = ImageTk.PhotoImage(Image.open("Images/20/chart_line.png"))
img_bar = ImageTk.PhotoImage(Image.open("Images/20/chart_bar.png"))
img_pie = ImageTk.PhotoImage(Image.open("Images/20/chart_pie.png"))
img_help = ImageTk.PhotoImage(Image.open("Images/20/help.png"))
img_logo = ImageTk.PhotoImage(Image.open("Images/Logo/salestrax_logo_24.png"))
# Define the container for the shortcut bar:
# * Note that the container is not actually visible. The "bar" behind the buttons is not actually a bar; it's just empty
# * background space that looks like a bar because of the surrounding objects.
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
btn_refresh = tk.Button(
    shortcut_bar, image=img_refresh, state="disabled", command=refresh_table
)
btn_hide_saved = tk.Button(
    shortcut_bar,
    image=img_hide_saved,
    state="disabled",
    command=lambda: view_menu.invoke("Hide Saved Records"),
)
btn_hide_temp = tk.Button(
    shortcut_bar,
    image=img_hide_temp,
    state="disabled",
    command=lambda: view_menu.invoke("Hide Temporary Records"),
)
btn_hide_invalid = tk.Button(
    shortcut_bar,
    image=img_hide_invalid,
    state="disabled",
    command=lambda: view_menu.invoke("Hide Invalid Records"),
)
btn_hide_deleted = tk.Button(
    shortcut_bar,
    image=img_hide_deleted,
    state="disabled",
    command=lambda: view_menu.invoke("Hide Deleted Records"),
)
btn_filter = tk.Button(
    shortcut_bar, image=img_filter, state="disabled", command=toggle_filter
)
btn_employee = tk.Button(
    shortcut_bar,
    image=img_employee,
    command=lambda: toggle_notebook(state=True, tab="employees"),
)
btn_location = tk.Button(
    shortcut_bar,
    image=img_location,
    command=lambda: toggle_notebook(state=True, tab="locations"),
)
btn_department = tk.Button(
    shortcut_bar,
    image=img_department,
    command=lambda: toggle_notebook(state=True, tab="departments"),
)
btn_line = tk.Button(
    shortcut_bar, image=img_line, state="disabled", command=line_definition
)
btn_bar = tk.Button(
    shortcut_bar, image=img_bar, state="disabled", command=bar_definition
)
btn_pie = tk.Button(shortcut_bar, image=img_pie, state="disabled", command=log_msg)
btn_help = tk.Button(
    shortcut_bar, image=img_help, command=lambda: link_to_github(page="wiki/")
)
# The logo button gets special treatment, because it includes both text and an image:
btn_logo = tk.Button(
    shortcut_bar,
    image=img_logo,
    text="SalesTrax v0.1.5 ",
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
btn_refresh.pack(side="left", padx=(8, 1), pady=2)
btn_hide_saved.pack(side="left", padx=1, pady=2)
btn_hide_temp.pack(side="left", padx=1, pady=2)
btn_hide_invalid.pack(side="left", padx=1, pady=2)
btn_hide_deleted.pack(side="left", padx=1, pady=2)
btn_filter.pack(side="left", padx=(1, 8), pady=2)
btn_employee.pack(side="left", padx=(8, 1), pady=2)
btn_location.pack(side="left", padx=1, pady=2)
btn_department.pack(side="left", padx=(1, 8), pady=2)
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
ToolTip(btn_refresh, msg="Refresh Table", delay=0.2, follow=True)
ToolTip(btn_hide_saved, msg="Hide Saved Records", delay=0.2, follow=True)
ToolTip(btn_hide_temp, msg="Hide Temporary Records", delay=0.2, follow=True)
ToolTip(btn_hide_invalid, msg="Hide Invalid Records", delay=0.2, follow=True)
ToolTip(btn_hide_deleted, msg="Hide Deleted Records", delay=0.2, follow=True)
ToolTip(btn_filter, msg="Toggle Filter...", delay=0.2, follow=True)
ToolTip(btn_employee, msg="Employee List", delay=0.2, follow=True)
ToolTip(btn_location, msg="Location List", delay=0.2, follow=True)
ToolTip(btn_department, msg="Department List", delay=0.2, follow=True)
ToolTip(btn_line, msg="Generate Line Chart", delay=0.2, follow=True)
ToolTip(btn_bar, msg="Generate Bar Chart", delay=0.2, follow=True)
ToolTip(btn_pie, msg="Generate Pie Chart", delay=0.2, follow=True)
ToolTip(btn_help, msg="GitHub Wiki...", delay=0.2, follow=True)
ToolTip(btn_logo, msg="SalesTrax on GitHub", delay=0.2, follow=True)

# Section: Primary viewport table
# Future: For now, only one record can be selected at a time.
# $ Try to find a way to include multiple selections in the 'get_selection()' function to support batch actions.
# $ Once that is figured out, set 'selectmode="extended"' to allow multiple record selection.
# Define the Treeview object:
base_tree = ttk.Treeview(root, selectmode="extended")
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
base_tree.bind("<Button-1>", func=tree_click)
# Also prevent the mouse from switching to the "resize" mouse image under the same circumstance:
base_tree.bind("<Motion>", func=disable_resize_cursor)
base_tree.bind("<Double-Button-1>", func=edit_record)

# Section: Total bar
# Define container frame for the total bar and status bar:
btm_container = tk.Frame(root)
# Define total bar frame:
total_bar = tk.Frame(btm_container)
# Define a placeholder total bar entry box:
total_ref_0 = tk.Entry(total_bar, state="disabled")
# Add the placeholder to 'StVars.total_refs' so it can be destroyed properly once data is loaded:
StVars.total_refs.append(total_ref_0)
# Pack the container frame at the bottom of the window:
btm_container.pack(side="bottom", fill="x")
# Pack the total bar in the top half of the container frame:
total_bar.pack(side="top", fill="x", padx=5, pady=(3, 0))
# Pack the placeholder entry box in the total bar:
total_ref_0.pack(side="left", fill="x", expand=True)

# Section: Status bar
# Define status bar frame:
status_bar = tk.Frame(btm_container)
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
# Assign the status bar to take up the full width of the bottom of 'btm_container'.
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

# Section: Validation Control window
# Define Validation Control window:
val_control = tk.Toplevel(root)
# Set the size and position of the window:
val_control.geometry(
    "500x400+"
    + str(int((StVars.monitor_width / 2) - 300))
    + "+"
    + str(int((StVars.monitor_height / 2) - 250))
)
# Set the contents of the window's title bar:
val_control.title("Validation Control")
val_control.iconbitmap("Images/salestrax_icon_bw.ico")
# Disable the minimize and maximize buttons by setting Validation Control as a toolwindow:
val_control.attributes("-toolwindow", True)
# Set the "X" button to withdraw the window instead of closing it:
val_control.protocol("WM_DELETE_WINDOW", toggle_notebook)
# Validation Control should be withdrawn by default:
val_control.withdraw()
# Define the base notebook for the Validation Control tabs:
val_notebook = ttk.Notebook(val_control)
# Define each tab as a Frame object:
employees_tab = tk.Frame(val_notebook)
locations_tab = tk.Frame(val_notebook)
departments_tab = tk.Frame(val_notebook)
# Add the tabs to the notebook:
val_notebook.add(employees_tab, text="Employees")
val_notebook.add(locations_tab, text="Locations")
val_notebook.add(departments_tab, text="Departments")

# Add an empty listbox to the "Employees" tab:
employees_box = tk.Listbox(employees_tab, height=18)
# Define a vertical scrollbar for the listbox:
employees_scroll = ttk.Scrollbar(
    employees_box, orient="vertical", command=employees_box.yview, cursor="arrow"
)
# Assign y-scrolling to the scrollbar:
employees_box.configure(yscrollcommand=employees_scroll.set)
# Define a container to hold the entry fields and buttons:
employees_frame_a = tk.Frame(employees_tab)
# Define a sub-container for the entry fields only:
employees_frame_b = tk.Frame(employees_frame_a)
# Define a sub-container for the buttons only:
employees_frame_c = tk.Frame(employees_frame_a)
# Define the active entry widget for manual entry:
employees_entry = tk.Entry(employees_frame_a, width=36)
# Define the read-only entry widget for selections:
employees_selection = tk.Entry(employees_frame_a, width=36, state="readonly")
# Define the "Add New Entry" button:
employees_add = tk.Button(
    employees_frame_c,
    text="Add New Entry",
    state="disabled",
    command=lambda: [
        StVars.valid_employees.append(employees_entry.get()),
        employees_entry.delete(0, "end"),
        refresh_lists(),
    ],
)
# Define the "Auto-Populate" button:
employees_auto = tk.Button(
    employees_frame_c,
    text="Auto-Populate",
    state="disabled",
    command=lambda: pop_listbox(tab="Employee"),
)
# Define the "Delete Entry" button:
employees_delete = tk.Button(
    employees_frame_c,
    text="Delete Entry",
    state="disabled",
    command=lambda: [
        StVars.valid_employees.remove(
            StVars.valid_employees[
                StVars.valid_employees.index(
                    employees_box.get(employees_box.curselection()[0])
                )
            ]
        ),
        refresh_lists(),
        employees_selection.configure(state="normal"),
        employees_selection.delete(0, "end"),
        employees_selection.configure(state="disabled"),
    ],
)

# Add an empty listbox to the "Locations" tab:
locations_box = tk.Listbox(locations_tab, height=18)
# Define a vertical scrollbar for the listbox:
locations_scroll = ttk.Scrollbar(
    locations_box, orient="vertical", command=locations_box.yview, cursor="arrow"
)
# Assign y-scrolling to the scrollbar:
locations_box.configure(yscrollcommand=locations_scroll.set)
# Define a container to hold the entry fields and buttons:
locations_frame_a = tk.Frame(locations_tab)
# Define a sub-container for the entry fields only:
locations_frame_b = tk.Frame(locations_frame_a)
# Define a sub-container for the buttons only:
locations_frame_c = tk.Frame(locations_frame_a)
# Define the active entry widget for manual entry:
locations_entry = tk.Entry(locations_frame_a, width=36)
# Define the read-only entry widget for selections:
locations_selection = tk.Entry(locations_frame_a, width=36, state="readonly")
# Define the "Add New Entry" button:
locations_add = tk.Button(
    locations_frame_c,
    text="Add New Entry",
    state="disabled",
    command=lambda: [
        StVars.valid_locations.append(locations_entry.get()),
        locations_entry.delete(0, "end"),
        refresh_lists(),
    ],
)
# Define the "Auto-Populate" button:
locations_auto = tk.Button(
    locations_frame_c,
    text="Auto-Populate",
    state="disabled",
    command=lambda: pop_listbox(tab="Location"),
)
# Define the "Delete Entry" button:
locations_delete = tk.Button(
    locations_frame_c,
    text="Delete Entry",
    state="disabled",
    command=lambda: [
        StVars.valid_locations.remove(
            StVars.valid_locations[
                StVars.valid_locations.index(
                    locations_box.get(locations_box.curselection()[0])
                )
            ]
        ),
        refresh_lists(),
        locations_selection.configure(state="normal"),
        locations_selection.delete(0, "end"),
        locations_selection.configure(state="disabled"),
    ],
)

# Add an empty listbox to the "Departments" tab:
departments_box = tk.Listbox(departments_tab, height=18)
# Define a vertical scrollbar for the listbox:
departments_scroll = ttk.Scrollbar(
    departments_box, orient="vertical", command=departments_box.yview, cursor="arrow"
)
# Assign y-scrolling to the scrollbar:
departments_box.configure(yscrollcommand=departments_scroll.set)
# Define a container to hold the entry fields and buttons:
departments_frame_a = tk.Frame(departments_tab)
# Define a sub-container for the entry fields only:
departments_frame_b = tk.Frame(departments_frame_a)
# Define a sub-container for the buttons only:
departments_frame_c = tk.Frame(departments_frame_a)
# Define the active entry widget for manual entry:
departments_entry = tk.Entry(departments_frame_a, width=36)
# Define the read-only entry widget for selections:
departments_selection = tk.Entry(departments_frame_a, width=36, state="readonly")
# Define the "Add New Entry" button:
departments_add = tk.Button(
    departments_frame_c,
    text="Add New Entry",
    state="disabled",
    command=lambda: [
        StVars.valid_departments.append(departments_entry.get()),
        departments_entry.delete(0, "end"),
        refresh_lists(),
    ],
)
# Define the "Auto-Populate" button:
departments_auto = tk.Button(
    departments_frame_c,
    text="Auto-Populate",
    state="disabled",
    command=lambda: pop_listbox(tab="Department"),
)
# Define the "Delete Entry" button:
departments_delete = tk.Button(
    departments_frame_c,
    text="Delete Entry",
    state="disabled",
    command=lambda: [
        StVars.valid_departments.remove(
            StVars.valid_departments[
                StVars.valid_departments.index(
                    departments_box.get(departments_box.curselection()[0])
                )
            ]
        ),
        refresh_lists(),
        departments_selection.configure(state="normal"),
        departments_selection.delete(0, "end"),
        departments_selection.configure(state="disabled"),
    ],
)

val_notebook.pack(expand=1, fill="both")
employees_box.pack(side="top", fill="both", padx=15, pady=15, expand=True)
# Assign the scrollbar to the entire right edge of the listbox:
employees_scroll.pack(side="right", fill="y")
# Place the containers under the listbox:
employees_frame_a.pack(side="bottom", fill="x")
employees_frame_b.pack(side="top", fill="x")
employees_frame_c.pack(side="bottom", fill="x")
# Place the employee entry widgets inside the top sub-container:
employees_entry.pack(side="left", padx=(15, 0), pady=(0, 15))
employees_selection.pack(side="right", padx=(0, 15), pady=(0, 15))
# Place the employee modification buttons inside the bottom sub-container:
employees_add.pack(side="left", ipadx=25, padx=(15, 32), pady=(0, 15))
employees_auto.pack(side="left", ipadx=25, pady=(0, 15))
employees_delete.pack(side="right", ipadx=25, padx=(0, 15), pady=(0, 15))

locations_box.pack(side="top", fill="both", padx=15, pady=15, expand=True)
# Assign the scrollbar to the entire right edge of the listbox:
locations_scroll.pack(side="right", fill="y")
# Place the containers under the listbox:
locations_frame_a.pack(side="bottom", fill="x")
locations_frame_b.pack(side="top", fill="x")
locations_frame_c.pack(side="bottom", fill="x")
# Place the location entry widgets inside the top sub-container:
locations_entry.pack(side="left", padx=(15, 0), pady=(0, 15))
locations_selection.pack(side="right", padx=(0, 15), pady=(0, 15))
# Place the location modification buttons inside the bottom sub-container:
locations_add.pack(side="left", ipadx=25, padx=(15, 32), pady=(0, 15))
locations_auto.pack(side="left", ipadx=25, pady=(0, 15))
locations_delete.pack(side="right", ipadx=25, padx=(0, 15), pady=(0, 15))

departments_box.pack(side="top", fill="both", padx=15, pady=15, expand=True)
# Assign the scrollbar to the entire right edge of the listbox:
departments_scroll.pack(side="right", fill="y")
# Place the containers under the listbox:
departments_frame_a.pack(side="bottom", fill="x")
departments_frame_b.pack(side="top", fill="x")
departments_frame_c.pack(side="bottom", fill="x")
# Place the department entry widgets inside the top sub-container:
departments_entry.pack(side="left", padx=(15, 0), pady=(0, 15))
departments_selection.pack(side="right", padx=(0, 15), pady=(0, 15))
# Place the department modification buttons inside the bottom sub-container:
departments_add.pack(side="left", ipadx=25, padx=(15, 32), pady=(0, 15))
departments_auto.pack(side="left", ipadx=25, pady=(0, 15))
departments_delete.pack(side="right", ipadx=25, padx=(0, 15), pady=(0, 15))

# Section: Misc objects
# Define images for popup windows:
img_question = ImageTk.PhotoImage(Image.open("Images/48/question.png"))
# Apply global window theme:
glb_theme = ttk.Style(root).theme_use("winnative")

# HEADLINE: Misc initializations
# Check if 'odfpy' module is installed and set its boolean accordingly:
try:
    import odf
    StVars.odf_installed = True
except ModuleNotFoundError:
    StVars.odf_installed = False

# HEADLINE: Program initiators
# Begin custom update loop:
root_update()
# Start the 'tkinter' mainloop() function:
root.mainloop()
