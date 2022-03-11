# wi-lb-library
stores all of your AI Dungeon world info and NovelAI lorebook entries in one place, with the option to import from and export to either file type. made for another latitude hackathon
## features
* ability to import AID worldInfo.json
* ability to import NAI .lorebook files
* ability to export entries to AID worldInfo.json
* ability to export entries to NAI .lorebook format
* nothing is lost (except for categories) when importing from and exporting back to NAI lorebook. try it yourself
* folders for keeping entries organised
* move, delete and export entries in bulk - as long as they're all in the same folder
* view, edit and create new entries ready for exporting to either platform (exception: lorebook biases)
## todo
* fix ocd-triggering alignment issue with extras and export column
* make NAI Settings window
* allow "Direct to AID" exporting via API (waiting until auth is reworked for this)
* figure out why newly imported entries, until the program is restarted, always have the same "updated at" date regardless of which ones you update
* come up with a better name for the app than "Library"
* make token counting functional
