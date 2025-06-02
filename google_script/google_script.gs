/*!
* © Thinkledger, 2025
*
* You are free to modify, use this file as needed.
* However, by editing this file, you accept full responsibility for any
* consequences, bugs, or unexpected behavior that may result from those changes.
*
* This file is provided "as is", without warranty of any kind.
*
*
* @OnlyCurrentDoc
*/

const DEBUG = SET_DEBUG__();
const TMP_USER_ID = SET_TMP_USER_ID__();
const BACKEND_URL = SET_BACKEND_URL__();
const SPREADSHEET_ID = SpreadsheetApp.getActiveSpreadsheet().getId();
const SCRIPT_PROPERTIES = PropertiesService.getDocumentProperties();

// const userProperties = PropertiesService.getUserProperties();
// const notificationSent = userProperties.getProperty('permissionNotificationSent');
// userProperties.setProperty('permissionNotificationSent', 'true');

// PropertiesService.getUserProperties().deleteProperty('permissionNotificationSent');

function onOpen() {
  try {
    SpreadsheetApp.getUi()
      .createMenu('Thinkledger')
      .addItem('Setup', 'setupSheets')
      .addToUi();
  } catch (error) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
  }
  // Check the if the spreadsheet has been set previous and display a message showing the user the user that a setup been completed previously
  // Only display this message if this the first time the user is opening the spreadsheet.
  SpreadsheetApp.getUi().alert("Hi there! Complete the setup process by clicking on the 'Setup' button in the 'Thinkledger' menu");
}

function setupSheets() {
  // Check the if the spreadsheet has been set previous and display a message showing the user the user that a setup been completed previously
  // Setup sheets
  // const setupDone = SCRIPT_PROPERTIES.getProperty('initialSetupDone');
  // if (!setupDone) {
    // setupSheets();
  // }
  const activeSpreadSheet = SpreadsheetApp.getActiveSpreadsheet();
  setupDashboardSheet(activeSpreadSheet);
  setupTransactionSheet(activeSpreadSheet);
  setupJournalEntrySheet(activeSpreadSheet);
  SpreadsheetApp.getUi().alert('Just got done setting your spreadsheet, give me a moment to fetch your transactions');
  notify('SpreadsheetSetupCompleted');
  // SCRIPT_PROPERTIES.setProperty('initialSetupDone', 'true');
}

/* ----- Dashboard Sheet ---- */
function setupDashboardSheet(activeSpreadSheet) {
  Logger.log("TODO: setupDashboardSheet");
  // TODO: Rename sheet
  // Create main header
}

/* ----- Transaction sheet ----- */
function setupTransactionSheet(activeSpreadsheet) {
  const sheetName = "Transactions";
  let transactionSheet = activeSpreadsheet.getSheetByName(sheetName);
  // Instead of checking if sheet write a more robust error handling
  if (!transactionSheet) {
    // Create transaction sheet
    transactionSheet = activeSpreadsheet.insertSheet(sheetName, 1); // Second value is the sheet position

    // Create main header
    try {
      setupMainHeader(transactionSheet, sheetName);
    } catch (error) {
      if (DEBUG === 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error)
    }

    // Transaction sheet styles
    const CATEGORY_COLORS = {
      "TRANSPORTATION_TAXIS_AND_RIDE_SHARES": "#FFDDC1", // Light Orange
      "TRAVEL_FLIGHTS": "#C9DAF8", // Light Blue
      "FOOD_AND_DRINK_FAST_FOOD": "#FFF2CC", // Light Yellow
      "FOOD_AND_DRINK_COFFEE": "#D9EAD3", // Light Green
      "GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE": "#EAD1DC", // Light Purple
      "INCOME_WAGES": "#A2D9A2", // Brighter Green for income
      "LOAN_PAYMENTS_CREDIT_CARD_PAYMENT": "#F4CCCC", // Light Red
      // Add more categories and their desired background colors
      "Groceries": "#D0E0E3",
      "Utilities": "#B4A7D6",
      "Rent/Mortgage": "#A4C2F4",
      "Other Income": "#93C47D",
      "Other Expense": "#D5A6BD"
    };
    // TODO: Use green, blue, yellow, purple, do not use light grey
    const ACCOUNT_TYPE_COLORS = {
      "checking": "#EFEFEF", // Light Grey
      "savings": "#E2F0D9",  // Pale Green
      "credit card": "#FCE4D6", // Pale Orange
      "other": "#F2F2F2" // Lighter Grey
    };
    // TODO: Add color coding for payment channels

    //Create table 
    const headers = [
      "ID", "Date", "Amount", "Institution", "Institution Account Name", "Institution Account Type", 
      "Category", "Payment Channel", "Merchant Name", "Currency", "Pending", "Authorized Date"
    ];

    try {
      const headerStartRow = 4;
      setupTableHeader(transactionSheet, headers, headerStartRow);
      // Validate table rows
      const validationRowStart = headerStartRow + 1;
      const numRowsForValidation = transactionSheet.getMaxRows() - validationRowStart;

      let conditionalFormatRules = [];

      headers.forEach((h, i) => {
        const columnIndex = i + 1; // 1-based index
        const columnRange = transactionSheet.getRange(validationRowStart, columnIndex, numRowsForValidation, 1);

        let rule;
        switch (h) {
          case "Date":
            rule = SpreadsheetApp.newDataValidation()
              .requireDate()
              .setAllowInvalid(false) // Disallow invalid dates
              .setHelpText("Please enter a valid date (YYYY-MM-DD)")
              .build();
            columnRange.setDataValidation(rule);
            break;

          case "Amount":
            rule = SpreadsheetApp.newDataValidation()
              .requireNumberGreaterThan(-1)
              .setAllowInvalid(false)
              .setHelpText("Please enter a numerical amount.")
              .build();
            columnRange.setDataValidation(rule);
            columnRange.setNumberFormat("$#,##0.00;$(#,##0.00)");
            break;

          case "Institution Account Type":
            const accountTypes = Object.keys(ACCOUNT_TYPE_COLORS)
            rule = SpreadsheetApp.newDataValidation()
              .requireValueInList(["Checking", "Savings", "Credit Card", "Other"], true)
              .setAllowInvalid(false)
              .setHelpText("Select and account type from the list")
              .build();
            columnRange.setDataValidation(rule);
            // Add conditional formatting
            accountTypes.forEach(type => {
              if (ACCOUNT_TYPE_COLORS[type]) {
                const conditionalRule = SpreadsheetApp.newConditionalFormatRule()
                  .whenTextEqualTo(type)
                  .setBackground(ACCOUNT_TYPE_COLORS[type])
                  .setRanges([columnRange])
                  .build();
                conditionalFormatRules.push(conditionalRule);
              }
            });
            break;

          // case "Category":
          //   const categories = [
          //     "TRANSPORTATION_TAXIS_AND_RIDE_SHARES", "TRAVEL_FLIGHTS", "FOOD_AND_DRINK_FAST_FOOD",
          //     "FOOD_AND_DRINK_COFFEE", "GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE", "INCOME_WAGES",
          //     "LOAN_PAYMENTS_CREDIT_CARD_PAYMENT", "Groceries", "Utilities", "Rent/Mortgage",
          //     "Entertainment", "Healthcare", "Education", "Shopping", "Gifts/Donations", "Other Income", "Other Expense"
          //   ]; 
          //   rule = SpreadsheetApp.newDataValidation()
          //     .requireValueInList(categories.sort(), true)
          //     .setAllowInvalid(true)
          //     .setHelpText("Select a category or enter your own.")
          //     .build();
          //   columnRange.setDataValidation(rule);
          //   break;

          case "Payment Channel":
            rule = SpreadsheetApp.newDataValidation()
              .requireValueInList(["Online", "In Store", "Transfer", "ATM", "Other"], true)
              .setAllowInvalid(false)
              .setHelpText("Select the payment channel")
              .build();
            columnRange.setDataValidation(rule);
            break;

          case "Currency":
            rule = SpreadsheetApp.newDataValidation()
              .requireValueInList(["CAD", "USD"], true)
              .setAllowInvalid(false)
              .setHelpText("Select the currency code.")
              .build();
            columnRange.setDataValidation(rule);
            break;

          // TODO: Add require checks for For "ID", "Institution", "Institution Account Name", "Merchant Name"
        }
      });
      // Apply conditional format rules
      if (conditionalFormatRules.length > 0) {
        transactionSheet.setConditionalFormatRules(conditionalFormatRules);
      }

      setDynamicRow(transactionSheet, validationRowStart, headers.length);

    } catch (error) {
      if (DEBUG === 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error)
    }
  }
}

/* ----- Journal Entry sheet ---- */
function setupJournalEntrySheet(activeSpreadSheet) {
  const sheetName = "Journal Entries";
  let journalEntrySheet = activeSpreadSheet.getSheetByName(sheetName);
  if (!journalEntrySheet) {
    // Create a new journal entry sheet
    journalEntrySheet = activeSpreadSheet.insertSheet(sheetName, 2);
    // Create main header
    try {
      setupMainHeader(journalEntrySheet, sheetName);
    } catch (error) {
      if (DEBUG === 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error)
    }
    // Create table
    const headers = ["Date", "Description", "Account Name", "Account ID", "Debit", "Credit"];
    try {
      const headerStartRow = 4;
      setupTableHeader(journalEntrySheet, headers, headerStartRow);
      // Setup validation
      const validationRowStart = headerStartRow + 1;
      const numRowsForValidation = journalEntrySheet.getMaxRows() - validationRowStart;

      let conditionalFormatRules = [];

      headers.forEach((h, i) => {
        const columnIndex = i + 1; // 1-based index
        const columnRange = journalEntrySheet.getRange(validationRowStart, columnIndex, numRowsForValidation, 1);

        // TODO: wrap description at a certain length 
        // TODO: merge debit amount row and credit amount row for the description

        let rule;
        switch (h) {
          case "Date":
            rule = SpreadsheetApp.newDataValidation()
              .requireDate()
              .setAllowInvalid(false) // Disallow invalid dates
              .setHelpText("Please enter a valid date (YYYY-MM-DD)")
              .build();
            columnRange.setDataValidation(rule);
            break;

          case "Debit":
            rule = SpreadsheetApp.newDataValidation()
              .requireNumberGreaterThan(-1)
              .setAllowInvalid(false)
              .setHelpText("Please enter a numerical amount.")
              .build();
            columnRange.setDataValidation(rule);
            columnRange.setNumberFormat("$#,##0.00;$(#,##0.00)");
            break;
          
          case "Credit":
            rule = SpreadsheetApp.newDataValidation()
              .requireNumberGreaterThan(-1)
              .setAllowInvalid(false)
              .setHelpText("Please enter a numerical amount.")
              .build();
            columnRange.setDataValidation(rule);
            columnRange.setNumberFormat("$#,##0.00;$(#,##0.00)");
            break;

            // Set description wrap  
        }
      });
      // Apply conditional format rules
      if (conditionalFormatRules.length > 0) {
        journalEntrySheet.setConditionalFormatRules(conditionalFormatRules);
      }
    
      setDynamicRow(journalEntrySheet, validationRowStart, headers.length);

    } catch (error) {
      if (DEBUG === 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error)
    }
  }
}

/* ----- T-accounts sheet ----- */
function setupTAccounts(activeSpreadSheet) {

}

function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  const editedRange = e.range;
  const editedColumn = editedRange.getColumn();
  // Auto-resize the edited column
  sheet.autoResizeColumn(editedColumn);
  // Add padding
  const currentWidth = sheet.getColumnWidth(editedColumn);
  sheet.setColumnWidth(editedColumn, currentWidth + 20);
  // If the active sheet name is transactions and edited column == 1; pass

  // get t-account values
}

// Ensure the sheet setup notification is only sent once, Using propertiesService.
function notify(event) {
  const payload = {
    tmp_user_id: TMP_USER_ID,
    spreadsheet_id: SPREADSHEET_ID,
    event: event,
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    // headers: { 'X-API-Key': BACKEND_API_KEY},
    muteHttpExceptions: true,
  };

  try {
    const response = UrlFetchApp.fetch(BACKEND_URL, options);
    const responseCode = response.getResponseCode();

    if (responseCode === 200) {
      Logger.log('Successfully notified backend');
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert("Successfully notified backend. Status: " + responseCode)
    } else {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert("Error notifying backend. Status: " + responseCode)
      Logger.log('Error notifying backend. Status: ' + responseCode);
    }
  } catch (error) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error)
    Logger.log('Failed to send notification to backend: ' + error);
  }
}

function backgroundTask() {
1  // Trigger every hour
  ScriptApp.newTrigger('myBackgroundTask')
    .timeBased()
    .everyHours(1) // Can also be .everyDays(1), .everyWeeks(1), .onMonthDay(1), etc.
    // .atHour(3) // To run at a specific hour of the day
    .create();
  Logger.log("Time-driven trigger created for 'myBackgroundTask' to run every hour.");
}

// To monitor file edits
function createOnEditTrigger() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  // Delete existing triggers for this function to avoid duplicates
  const existingTriggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < existingTriggers.length; i++) {
    if (existingTriggers[i].getHandlerFunction() === "handleEditTrigger") {
      ScriptApp.deleteTrigger(existingTriggers[i]);
    }
  }

  ScriptApp.newTrigger('handleEditTrigger')
    .forSpreadsheet(ss)
    .onEdit()
    .create();
  Logger.log("Installable onEdit trigger created for 'handleEditTrigger'.");
}

/* ----- Set dynamic row colors ----- */
function setDynamicRow(sheet, validationRowStart, headerLength) {
  sheet.getRange(validationRowStart, 1, Math.max(1, sheet.getLastRow() - validationRowStart), headerLength)
    .applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY, true, false)
    .setHeaderRowColor(null)
    .setFirstRowColor("#FFFFFF") // White
    .setSecondRowColor("#F3F3F3"); // Gray
}

/* ----- Setup table header ----- */
function setupTableHeader(sheet, headers, headerStartRow) {
  const HEADER_BACKGROUND_COLOR = "#0065F2"; //"#4A86E8"; // A nice blue
  const HEADER_FONT_COLOR = "#FFFFFF"; // White
  /* ----- Range (startRow, startCol, numRows, numCols) ---- */
  sheet.getRange(headerStartRow, 1, 1, headers.length)
    .setValues([headers])
    .setFontWeight("medium")
    .setBackground(HEADER_BACKGROUND_COLOR)
    .setFontColor(HEADER_FONT_COLOR)
    .setHorizontalAlignment("center");
  sheet.setFrozenRows(headerStartRow);
  // sheet.setFrozenColumns(headers.length);
  sheet.autoResizeColumns(1, headers.length);
  const paddingPixels = 20; // Add 20 pixels of padding
  // Add extra padding to column values
  for (let col = 1; col <= headers.length; col++) {
    const currentWidth = sheet.getColumnWidth(col);
    sheet.setColumnWidth(col, currentWidth + paddingPixels);
  }
}

/* ----- Setup main header ----- */
function setupMainHeader(sheet, sheetName) {
  /* ----- Range (startRow, startCol, numRows, numCols) ----- */
  sheet.getRange(1, 1, 2, 4)
    .setValue(sheetName)
    .setFontWeight("medium")
    .setFontSize(16)
    .merge()
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle")
}