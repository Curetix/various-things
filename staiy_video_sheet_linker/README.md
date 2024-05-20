# Staiy Video Sheet Linker

Add LiveArchive links (with timestamps) to the spreadsheet about videos watched by Staiy.

## Requirements

* [Bun](https://bun.sh)
* Google Sheets API access using your own credentials, see [Google Docs](https://developers.google.com/sheets/api/quickstart/nodejs)

## Running

To install dependencies:

```bash
bun install
```

To run:

```bash
bun run linker.ts [spreadsheet id] [sheet name]

# Example:
bun run linker.ts "1ng49vYM-iSdg6hRHwDirPM-AcWBaZ2P7ekFHiJdj_xU" "Tabellenblatt1"
```

The Google OAuth consent screen will open the first time the script is run, use an account that you added in the Google Cloud console and has write access to the spreadsheet.
