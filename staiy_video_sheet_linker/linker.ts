import path from "path";
import { parseArgs } from "util";

import { authenticate } from "@google-cloud/local-auth";
import { google, type sheets_v4, type Auth } from "googleapis";

// If modifying these scopes, delete token.json.
const SCOPES = ["https://www.googleapis.com/auth/spreadsheets"];
const TOKEN_PATH = path.join(process.cwd(), "token.json");
const CREDENTIALS_PATH = path.join(process.cwd(), "credentials.json");

/**
 * Reads previously authorized credentials from the save file.
 */
async function loadSavedCredentialsIfExist() {
  try {
    const credentials = await Bun.file(TOKEN_PATH).json();
    return google.auth.fromJSON(credentials);
  } catch (err) {
    return null;
  }
}

/**
 * Serializes credentials to a file compatible with GoogleAuth.fromJSON.
 */
async function saveCredentials(client: Auth.OAuth2Client) {
  const keys = await Bun.file(CREDENTIALS_PATH).json();
  const key = keys.installed || keys.web;
  const payload = JSON.stringify({
    type: "authorized_user",
    client_id: key.client_id,
    client_secret: key.client_secret,
    refresh_token: client.credentials.refresh_token,
  });
  await Bun.write(TOKEN_PATH, payload);
}

/**
 * Load or request or authorization to call APIs.
 */
async function authorize() {
  //@ts-expect-error
  let client: Auth.OAuth2Client | null = await loadSavedCredentialsIfExist();
  if (client) {
    return client;
  }
  client = await authenticate({
    scopes: SCOPES,
    keyfilePath: CREDENTIALS_PATH,
  });
  if (client.credentials) {
    await saveCredentials(client);
  }
  return client;
}

/**
 * Get LiveArchive videos
 */
async function getVideos(): Promise<Array<Array<string>>> {
  return (
    await fetch("https://api.livearchive.net/video/getVideos.php?c=staiy")
  ).json();
}

/**
 * Main function: get spreadsheet and LiveArchive videos, figure out which cells to create links on, and update the spreadsheet.
 * @param spreadsheetId ID of the spreadsheet
 * @param sheetName name of the sheet within the spreadsheet
 * @param sheetIndex index of the sheet within the spreadsheet, probably 0 for the first sheet
 * @param force force update all cells, even when might already have the correct links
 */
async function updateRows(
  spreadsheetId: string,
  sheetName: string,
  sheetIndex = 0,
  force = false
) {
  // Get videos from LiveArchive
  const videos = await getVideos();

  if (!videos) {
    throw new Error("Oopsie woopsie, no videos :(");
  }

  console.log("Getting sheet data");
  // See https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/get
  const response = await sheets.spreadsheets.get({
    spreadsheetId,
    // Select all rows of the first column
    ranges: [`${sheetName}!A1:A10000`],
    // Select sheet properties and these row fields: raw value, formatted value and hyperlink
    fields:
      "sheets(properties,data/rowData/values(userEnteredValue,userEnteredFormat,formattedValue,hyperlink))",
  });

  if (!response.data.sheets || !response.data.sheets[0]) {
    throw new Error("No spreadsheet data returned");
  }

  const sheet = response.data.sheets[0];

  if (!sheet.data || !sheet.data[0] || !sheet.data[0].rowData) {
    throw new Error("No spreadsheet data returned");
  }

  const rows = sheet.data[0].rowData;

  // These will be the updates to execute on the cells
  const updates: sheets_v4.Schema$RowData[] = [];
  // Currently active VOD date
  let currentDate = null;
  // Currently active VOD ID (LiveArchive)
  let currentVideo = null;

  // Process all rows and their cell values
  for (const row of rows) {
    // Skip empty rows
    if (!row.values || row.values.length === 0) {
      updates.push({});
      continue;
    }

    const cellText = row.values[0].formattedValue;
    const cellLink = row.values[0].hyperlink;

    // Skip empty rows
    if (!cellText) {
      updates.push({});
      continue;
    }

    // Match dates in the form of yyyy-mm-dd, e.g.: "2024-05-20"
    const datePattern = /\d{4}-\d{2}-\d{2}/gi;
    // Match timestamps: "2h" or "2h 32min" or "48min"
    const timePattern =
      /(?:(\d+)\s?h)\s?(?:(\d+)\s?min)|(?:(\d)\s?h)|(?:(\d+)\s?min)/gi;
    const dateMatch = cellText.match(datePattern);
    const timeMatch = cellText
      .match(timePattern)
      // This Regex has potential false matches, filter out all matches that are just empty strings
      ?.filter((r: string) => r.trim() !== "");

    const cellUpdate: sheets_v4.Schema$RowData = {};

    if (dateMatch && dateMatch.length > 0) {
      // Find VOD for the matched date
      const video = videos.find((video) => video[2].startsWith(dateMatch[0]));
      if (video) {
        currentDate = dateMatch[0];
        currentVideo = video[0];

        // If the cell already has the correct link, break loop
        if (cellLink && cellLink.startsWith(`https://livearchive.net/video/${currentVideo}`) && !force) {
          console.log("Encountered cell that already has the correct link, stopping the check here. If you want to force an update, pass the --force flag.")
          break;
        }

        // Add link to VOD
        // See https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells
        cellUpdate.values = [
          {
            userEnteredFormat: {
              textFormat: {
                link: {
                  uri: `https://livearchive.net/video/${currentVideo}`,
                },
              },
            },
          },
        ];
      } else {
        currentDate = null;
        currentVideo = null;
      }
    } else if (
      currentDate &&
      timeMatch &&
      timeMatch.length > 0 &&
      timeMatch[0] !== ""
    ) {
      const time = timeMatch[0].trim().replaceAll(" ", "");
      // Add link to VOD with the timestamp
      cellUpdate.values = [
        {
          userEnteredFormat: {
            textFormat: {
              link: {
                uri: `https://livearchive.net/video/${currentVideo}?t=${time}`,
              },
            },
          },
        },
      ];
    }

    updates.push(cellUpdate);
  }

  console.log("Updating cells");
  // See https://developers.google.com/sheets/api/guides/batchupdate
  // and https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate
  sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: {
      requests: [
        {
          // See https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#updatecellsrequest
          updateCells: {
            start: {
              sheetId: sheetIndex,
              rowIndex: 0,
              columnIndex: 0,
            },
            fields: "userEnteredFormat/textFormat",
            rows: updates,
          },
        },
      ],
    },
  });
}

const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  strict: true,
  allowPositionals: true,
  options: {
    force: {
      type: "boolean",
    }
  }
});

if (positionals.length < 2) {
  throw new Error(
    "Missing positional parameter(s): [spreadsheet id] [sheet name]"
  );
}

const [spreadsheetId, sheetName] = positionals;

console.log("Authenticating with the Google API");
const auth = await authorize();
const sheets = google.sheets({ version: "v4", auth });

await updateRows(spreadsheetId, sheetName, 0, values.force);

console.log("Done")
