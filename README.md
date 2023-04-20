# SalesTrax v0.1.1

---

**Program Name**: SalesTrax
**Version**: 0.1.1
**Status**: Prototype
**Created on**: 2023-04-09
**Last updated**: 2023-04-18
**Created with**: Python 3.11.2
**Author**: Danny Fleenor
**Contributors**:
- Alex Clark, Fredrik Lundh, Secret Labs AB: _PIL_ image processing library
- Anonymous Contributors: Python standard _OS_ library
- DaedalicEntertainment: _Tktooltip_ tooltip module
- Danny Fleenor: Program design and development; logo image
- Fredrik Lundh, Guido van Rossum, Steen Lumholt: _Tkinter_ GUI library
- Georg Brandl: _Webbrowser_ browser interface library
- Wes McKinney: _Pandas_ file import library
- www.aha-soft.com: Shortcut bar images

**Description**:
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
elementary sorting and filtering, but _proper_ filtering will not be available until later. Record modification, too,
is planned for implementation at some point, but I cannot promise exactly when that will be.
