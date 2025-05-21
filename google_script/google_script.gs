/*!
  * © Thinkledger, 2025
  *
  * You are free to modify, use this file as needed.
  * However, by editing this file, you accept full responsibility for any
  * consequences, bugs, or unexpected behavior that may result from those changes.
  *
  * This file is provided "as is", without warranty of any kind.
  */

function onOpen() {
  // SpreadsheetApp.getUi()
  // .createMenu('Script')
  //  .addItem('Show Alert', 'testScript')
  //  .addToUi();
  // Setup sheets
  setupSheets();
}

function testScript() {
  SpreadsheetApp.getUi().alert('Hello from the scripted menu!');
}

function setupSheets() {
  const activeSpreadSheet = SpreadsheetApp.getActiveSpreadsheet();
  // ----- Setup transactions sheet -----
  setupTransactionSheet(activeSpreadSheet);
}

/* ----------------------------------------*/
/* ---------- Transaction sheet ---------- */
/* ----------------------------------------*/
function setupTransactionSheet(activeSpreadsheet) {
  const sheetName = "Transactions";
  let sheet = activeSpreadsheet.getSheetByName(sheetName);
  if (!sheet) {
    // ----- Create sheet ----
    sheet = activeSpreadsheet.insertSheet(sheetName);

    // ----- Create main header -----
    const startRow = 1;
    const startCol = 1;
    const numRows = 4;
    const numCols = 6;

    try {
      const range = sheet.getRange(startRow, startCol, numRows, numCols);
      range.setValue(sheetName);
      range.merge()
      range.setHorizontalAlignment("center")
      range.setVerticalAlignment("middle")
    } catch(error) {
      SpreadsheetApp.getUi().alert(error);
    }

      //----- Create table -----
      const headers = ["ID", "Date", "Amount", "Institution", "Institution Account Name",
        "Institution Account Type", "Category", "Payment Channel", "Merchant Name", "Currency"];
    }
  }