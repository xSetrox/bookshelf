![Bookshelf logo](https://github.com/xSetrox/bookshelf/blob/main/bookshelf.png?raw=true)
# bookshelf
Bookshelf is a Python 3.8 GUI tool for automatically gathering needed materials for your courses using the internal API from bkstr.com. It will automatically do all the heavy-lifting for you and organize everything you need into a neat list that you can export to a spreadsheet with one click as well as a button to instantly open Amazon results for the ISBN's to make shopping for the books easy.  
## Setup
1. Clone the repo or download a release.  
2. Open a command prompt and CD into wherever you installed Bookshelf
3. install requirements with `pip install -r requirements.txt`
### Requirements  
```
requests==2.24.0
fake_headers==1.0.2
beautifulsoup4==4.10.0
Pillow==8.4.0
```
### College not found
This tool is designed to work with bkstr.com. If your college does not use bkstr.com, you cannot use this tool. 
