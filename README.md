## Creppl - C++ REPL (Read, Evaluate, Print, Loop)

---

### Description: 
Are you sick of the hassle of creating your C++ projects, when you just get going and write some code? Have you ever wanted a C++ experience similar to that of the Python Interpreter? Then, look no further!

Creppl is a REPL for C++ that works in a terminal! Coupled with additional commands, Creppl can also be a light-weight text editor to quickly add, modify, or remove existing code. Enter any valid C++ code and view the results instantly, in true REPL fashion.


### Instructions
To install, enter ```pip install creppl``` in a command line. Then just run ```creppl``` and get coding; Creppl will take care of the rest.

Currently, Creppl will only work on Linux. However, future plans aim to make it available to other platforms.

---
#### TODO:
* If a selected line contains text, allow user to modify 
* ~~If the file contains data, ask if the user would like to overwrite~~ 
* ~~Save files to a specified directory. Ex: /home/creppl/, /home/creppl/bin, etc.. Create a new folder for different filenames~~
* Create .crepplrc that the program will use for default values, such as filename, boilerplate, includes, externs, etc.
* Get ```extern``` working and the ability to link external libraries (This could be achieved by the aforementioned .crepplrc to provide a path.)
* Port Creppl to additional operating systems:
  * Windows
  * MacOS