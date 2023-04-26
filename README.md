# SalesTrax v0.1.3

---

**Program Name**: SalesTrax  
**Version**: 0.1.3  
**Status**: Prototype  
**Created on**: 2023-04-09  
**Last updated**: 2023-04-26  
**Created with**: Python 3.11.2  
**Author**: Danny Fleenor  
**Contributors**:
- Alex Clark, Fredrik Lundh, Secret Labs AB: _PIL_ image processing library
- Anonymous Contributors: Python standard _OS_ library
- DaedalicEntertainment: _Tktooltip_ tooltip module
- Danny Fleenor: Program design and development; logo image
- Fredrik Lundh, Guido van Rossum, Steen Lumholt: _Tkinter_ GUI library
- Georg Brandl: _Webbrowser_ browser interface library
- Isarra (Wikimedia Commons): Question mark image
- Wes McKinney: _Pandas_ file import library
- www.aha-soft.com: Shortcut bar images

**Description**:  
As a Disclaimer™, I find it worth mentioning that this is a college project begun after only three weeks of learning
Python. In absolutely no way will I claim it is perfect. By choosing to use this program, you accept responsibility
for the fallout of potentially clumsy coding. It is not designed to be harmful, of course, but I cannot attest to
how your system may or may not react to it; I'm not well-versed enough in Python programming to know that.

Having said that, at this time, SalesTrax functions as a simple file merger for tablular financial documents. It
reads CSV, ODS, and Excel documents, removes duplicate records, and provides a framework for manual record
exclusions in the output file, which include CSV, ODS, and XLSX format. Note that any imported documents should have
consistent column ordering between files, but there are no other solid requirements for file content.

As of update 0.1.2, more than one record can now be selected at once, allowing CTRL and SHIFT clicking for multiple
selection. Clicking on a column header will sort the table using that column as the sort criterion, and the "Hide
Saved," "Hide Temp," "Hide Invalid," and "Hide Deleted" shortcut buttons (along with their respective "View" menu
counterparts) are now functional. Any active sorting or filtering can be reset back to program defaults by pressing
either the "Toggle Filter..." button on the shortcut bar or its counterpart in the "View" menu cascade.

As of update 0.1.3, basic user-defined validation control is now available. By clicking any of the options under the
"Lists" menu cascade, users can enter strings to check for in specific fields, and any record that doesn't have one
of the defined strings will be invalidated, excluding it from export. There is an "Auto-Populate" button for each
field, which will take all of the values from the currently loaded records (filter-aware) and fill the listbox with
those values. Individual values can then be deleted from the list to exclude them. Alternatively, this blacklist
functionality can be reversed into a whitelist by only adding those strings that you wish to keep, which can be done
manually with the "Add New Entry" button. This whitelist/blacklist system is meant to be used as a placeholder for
proper filtering algorithms for the time being, as proper filtering is as yet still unimplemented. Note that if a
blacklisted value is added BACK to a validation list, any matching records will become valid again, but they will be
classified as "Temporary" records, regardless of their previous status. I am unsure of how to remedy this. If at any
point, you wish to no longer use validation control for a field, simply delete all of the entries in that field's
Validation Control tab, and the entire system will ignore that field in subsequent validation checks.

The next update will focus on implementing the generation of line charts at least, but it may also introduce bar
and/or pie charts, depending on how well I manage my time.

PROPER filtering will not be available until a later update. Record modification, too, is planned for implementation
at some point, but I cannot promise exactly when that will be.
