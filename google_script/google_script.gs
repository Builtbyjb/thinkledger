/**
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
      .addItem('Setup', 'setup')
      .addToUi();
  } catch (error) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
  }
  
  // Check the if the spreadsheet has been set previous and display a message showing the user the user that a setup been completed previously
  // Only display this message if this the first time the user is opening the spreadsheet.
  if (DEBUG < 2) {
    SpreadsheetApp.getUi().alert("Hi there! Complete the setup process by clicking on the 'Setup' button in the 'Thinkledger' menu");
  }
}

/* ----- Setup sheets ----- */
function setup() {
  // Check the if the spreadsheet has been set previous and display a message showing the user the user that a setup been completed previously
  // const setupDone = SCRIPT_PROPERTIES.getProperty('initialSetupDone');
  // if (!setupDone) {
    // setupSheets();
  // }
  const activeSpreadSheet = SpreadsheetApp.getActiveSpreadsheet();
  // Add onChange Trigger
  // ScriptApp.newTrigger('onChange').forSpreadsheet(activeSpreadSheet).onChange().create();

  // setupTimeBasedTrigger();

  setupDashboardSheet(activeSpreadSheet);
  setupTransactionSheet(activeSpreadSheet);
  setupJournalEntrySheet(activeSpreadSheet);
  setupTAccounts(activeSpreadSheet);
  setupTrialBalance(activeSpreadSheet);
  setupIncomeStatement(activeSpreadSheet);
  setupOwnersEquityStatement(activeSpreadSheet);
  setupBalanceSheet(activeSpreadSheet);
  setupCashflowStatement(activeSpreadSheet);

  if (DEBUG < 2) {
    SpreadsheetApp.getUi().alert('Just got done setting your spreadsheet, give me a moment to fetch your transactions');
    notify('SpreadsheetSetupCompleted');
    // SCRIPT_PROPERTIES.setProperty('initialSetupDone', 'true');
  }
}

/* ----- Dashboard Sheet ----- */
function setupDashboardSheet(activeSpreadSheet) {
  const name = "Dashboard"
  try {
    let sheetName = activeSpreadSheet.getSheetByName("Sheet1");
    if(sheetName) sheetName.setName(name);
    const sheet = activeSpreadSheet.getSheetByName(name);
    setupMainHeader(sheet, name);
  } catch (error) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error)
  }
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
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
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
              .requireNumberBetween(-1e300, 1e300)
              .setAllowInvalid(false)
              .setHelpText("Please enter  a numerical amount.")
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

          // TODO: Add checks for For "ID", "Institution", "Institution Account Name", "Merchant Name"
        }
      });
      // Apply conditional format rules
      if (conditionalFormatRules.length > 0) {
        transactionSheet.setConditionalFormatRules(conditionalFormatRules);
      }

      // setDynamicRow(transactionSheet, validationRowStart, headers.length);

    } catch (error) {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error)
    }
  }
}

/* ----- Journal Entry sheet ----- */
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
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
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
              .requireNumberBetween(-1e300, 1e300)
              .setAllowInvalid(false)
              .setHelpText("Please enter a numerical amount.")
              .build();
            columnRange.setDataValidation(rule);
            columnRange.setNumberFormat("$#,##0.00;$(#,##0.00)");
            break;
          
          case "Credit":
            rule = SpreadsheetApp.newDataValidation()
              .requireNumberBetween(-1e300, 1e300)
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
    
      // setDynamicRow(journalEntrySheet, validationRowStart, headers.length);

    } catch (error) {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error)
    }
  }
}

/* ----- T-accounts sheet ----- */
function setupTAccounts(activeSpreadSheet) {
  const sheetName = "T-Accounts";
  let tAccountSheet = activeSpreadSheet.getSheetByName(sheetName);
  if (!tAccountSheet) {
    // Create a new t - accounts sheet
    tAccountSheet = activeSpreadSheet.insertSheet(sheetName, 3);
    // Create main header
    try {
      setupMainHeader(tAccountSheet, sheetName);
    } catch (error) {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error);
    }
 
    /* Start with an empty list, update the list with unique values as the new values are added to the journal entry sheet 
    * Move this into a function that is called everytime the journal entries sheet changes. Will time based triggers work?
    */

    // Create dropdown
    tAccountSheet.getRange("A5").setValue("Select an account name").setFontStyle("italic");
    const columnCValues = getUniqueValues("C5:C", "Journal Entries");
 
    rule = SpreadsheetApp.newDataValidation()
      .requireValueInList(columnCValues, true)
      .setAllowInvalid(false)
      .setHelpText("Select an account name")
      .build();
    tAccountSheet.getRange("A6").setDataValidation(rule);

    // Create a function that is trigged when a dropdown item is clicked
  }
}

/* ----- Setup trial balance ----- */
function setupTrialBalance(activeSpreadSheet) {
  const sheetName = "Trial Balance";
  let trialBalanceSheet = activeSpreadSheet.getSheetByName(sheetName);
  if (!trialBalanceSheet) {
    // Create a new trial balance sheet
    trialBalanceSheet = activeSpreadSheet.insertSheet(sheetName, 4);
    // Create main header
    try {
      setupMainHeader(trialBalanceSheet, sheetName);
    } catch (error) {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error);
    }

    // Setup trial balance table
    buildTrialBalance();
  }
}

/* ----- Setup income statement ----- */
function setupIncomeStatement(activeSpreadSheet) {
  const sheetName = "Income Statement";
  let incomeStatementSheet = activeSpreadSheet.getSheetByName(sheetName);
  if (!incomeStatementSheet) {
    // Create a new trial balance sheet
    incomeStatementSheet = activeSpreadSheet.insertSheet(sheetName, 5);
    // Create main header
    try {
      setupMainHeader(incomeStatementSheet, sheetName);
    } catch (error) {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error);
    }
  }
}

/* ----- Setup owners equity statement ----- */
function setupOwnersEquityStatement(activeSpreadSheet) {
  const sheetName = "Owner's Equity Statement";
  let ownersEquityStatement = activeSpreadSheet.getSheetByName(sheetName);
  if (!ownersEquityStatement) {
    // Create a new trial balance sheet
    ownersEquityStatement = activeSpreadSheet.insertSheet(sheetName, 6);
    // Create main header
    try {
      setupMainHeader(ownersEquityStatement, sheetName);
    } catch (error) {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error);
    }
  }
}

/* ----- Setup balance sheet ----- */
function setupBalanceSheet(activeSpreadSheet) {
  const sheetName = "Balance Sheet";
  let balanceSheet = activeSpreadSheet.getSheetByName(sheetName);
  if (!balanceSheet) {
    // Create a new trial balance sheet
    balanceSheet = activeSpreadSheet.insertSheet(sheetName, 7);
    // Create main header
    try {
      setupMainHeader(balanceSheet, sheetName);
    } catch (error) {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error);
    }
  }
}

/* ----- Setup cashflow statement ----- */
function setupCashflowStatement(activeSpreadSheet) {
  const sheetName = "Cashflow Statement";
  let cashflowStatement = activeSpreadSheet.getSheetByName(sheetName);
  if (!cashflowStatement) {
    // Create a new trial balance sheet
    cashflowStatement = activeSpreadSheet.insertSheet(sheetName, 8);
    // Create main header
    try {
      setupMainHeader(cashflowStatement, sheetName);
    } catch (error) {
      if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
      Logger.log(error);
    }
  }
}

/* ----- Setup time based trigger ----- */
function setupTimeBasedTrigger(){
  try {
    // Delete existing triggers
    ScriptApp.getProjectTriggers().forEach(trigger => ScriptApp.deleteTrigger(trigger));
    // Setup new trigger
    ScriptApp.newTrigger("handleUpdates").timeBased().everyMinutes(1).create();
  } catch (error) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
  }
}

/* ----- Handles changes in the spreadsheet ----- */
function handleUpdates() {
  SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Transactions").getRange("L1").setValue("Alert triggered at: " + new Date())
}

/* ----- On change trigger ----- */
function onChange(e) {
  try {
    const sheet = e.source.getActiveSheet();
    const editedRange = e.range;
    const changeType = e.changeType
    if (changeType === "INSERT_ROW") {
      SpreadsheetApp.getUi().alert("Row inserted")
    } else if (changeType === "EDIT") {
      // SpreadsheetApp.getUi().alert("Cell edited")
    }
  } catch (error) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error);
  }
}

/* ----- On edit trigger ----- */
function onEdit(e) {
  try {
    const sheet = e.source.getActiveSheet();
    const editedRange = e.range;
    const editedColumn = editedRange.getColumn();
    const value = e.value;

    // Auto-resize the edited column
    sheet.autoResizeColumn(editedColumn);
    // Add padding
    const currentWidth = sheet.getColumnWidth(editedColumn);
    sheet.setColumnWidth(editedColumn, currentWidth + 20);
    
  
  // Handle dropdown selection in T-Accounts sheet
  if (sheet.getName() === "T-Accounts" && editedRange.getA1Notation() === "A6") {
    createTAccountTable(value, sheet);
  }
  
  // Handle Journal Entries updates to refresh dropdown
  if (sheet.getName() === "Journal Entries" && editedColumn === 3) {
    updateTAccountDropdown();
  }

  } catch (error) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert(error)
  }
}

/* ----- Create t-account table ----- */
function createTAccountTable(selectedAccount, sheet) {
  if (!selectedAccount || selectedAccount === "") {
    clearTAccountTable(sheet);
    return;
  }
  
  // Get journal entries data
  const journalSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Journal Entries");
  const allData = journalSheet.getDataRange().getValues();
  const headerRow = allData[3];

  // Get column indices
  const accountCol =  2; // column C
  const debitCol = 4; // column E
  const creditCol = 5; // column F
  const dateCol = 0; // column A

  // Filter entries for selected account
  const accountEntries = allData.slice(1).filter(row => 
    row[accountCol] && row[accountCol].toString().trim() === selectedAccount.trim()
  );

  if (accountEntries.length === 0) {
    displayNoDataMessage(sheet, selectedAccount);
    return;
  }
  
  // Clear previous table
  clearTAccountTable(sheet);
  
  // Create table header
  createTableHeader(sheet, selectedAccount);
  
  // Separate debits and credits
  const debits = [];
  const credits = [];
  
  accountEntries.forEach(row => {
    const date = row[dateCol] || '';
    const debitAmount = parseFloat(row[debitCol]) || 0;
    const creditAmount = parseFloat(row[creditCol]) || 0;
    
    if (debitAmount > 0) {
      debits.push({
        // date: date,
        // description: description,
        amount: debitAmount
      });
    }
    
    if (creditAmount > 0) {
      credits.push({
        // date: date,
        // description: description,
        amount: creditAmount
      });
    }
  });
  
  // Fill the T-Account table
  fillTAccountTable(sheet, debits, credits);
}

/* ----- Create t-account table header ----- */
function createTableHeader(sheet, accountName) {
  // Account name header
  sheet.getRange("B8").setValue(accountName).setFontSize(14);
  sheet.getRange("B8:C8").merge().setHorizontalAlignment("center");
  
  // T-Account structure
  sheet.getRange("B9").setValue("Debit").setHorizontalAlignment("center");
  sheet.getRange("C9").setValue("Credit").setHorizontalAlignment("center");
  
  // // Column headers
  // sheet.getRange("A10:E10").setValues([["Amount", "Amount"]]);
  // sheet.getRange("A10:E10").setFontWeight("bold").setBackground("#f0f0f0");
  
  // Add borders for T-Account look
  const headerRange = sheet.getRange("B8:C9");
  headerRange.setBorder(false, false, true, false, false, false);
}

/* ----- Fill the t-account table with data ----- */
function fillTAccountTable(sheet, debits, credits) {
  const startRow = 10;
  const maxRows = Math.max(debits.length, credits.length);
  
  // Fill debit and credit data
  for (let i = 0; i < maxRows; i++) {
    const currentRow = startRow + i;
    
    // Fill debit side (left)
    if (i < debits.length) {
      const debit = debits[i];
      // sheet.getRange(currentRow, 1).setValue(formatDate(debit.date));
      // sheet.getRange(currentRow, 2).setValue(debit.description);
      sheet.getRange(currentRow, 2).setValue(debit.amount).setNumberFormat("$#,##0.00");
    }
    
    // Fill credit side (right)
    if (i < credits.length) {
      const credit = credits[i];
      // sheet.getRange(currentRow, 4).setValue(credit.description);
      sheet.getRange(currentRow, 3).setValue(credit.amount).setNumberFormat("$#,##0.00");
    }
  }
  
  // Calculate and display totals
  const totalRow = startRow + maxRows + 1;
  
  const debitTotal = debits.reduce((sum, debit) => sum + debit.amount, 0);
  const creditTotal = credits.reduce((sum, credit) => sum + credit.amount, 0);
  const balance = debitTotal - creditTotal;
  
  // Total labels and amounts
  sheet.getRange(totalRow, 1).setValue("Total").setFontWeight("bold").setHorizontalAlignment("right");
  sheet.getRange(totalRow, 2).setValue(debitTotal).setNumberFormat("$#,##0.00").setFontWeight("bold");
  
  // sheet.getRange(totalRow, 4).setValue("TOTAL CREDITS:").setFontWeight("bold");
  sheet.getRange(totalRow, 3).setValue(creditTotal).setNumberFormat("$#,##0.00").setFontWeight("bold");
  
  // Balance
  const balanceRow = totalRow + 1;
  sheet.getRange(balanceRow, 1).setValue("Balance").setFontWeight("bold").setHorizontalAlignment("right");
  sheet.getRange(balanceRow, 2).setValue(Math.abs(balance)).setNumberFormat("$#,##0.00").setFontWeight("bold");
  
  if (balance > 0) {
    // sheet.getRange(balanceRow, 2).setValue("DEBIT BALANCE:").setFontWeight("bold");
  } else if (balance < 0) {
    // sheet.getRange(balanceRow, 4).setValue("CREDIT BALANCE:").setFontWeight("bold");
    sheet.getRange(balanceRow, 3).setValue(Math.abs(balance)).setNumberFormat("$#,##0.00").setFontWeight("bold");
    sheet.getRange(balanceRow, 2).clearContent();
  } else {
    sheet.getRange(balanceRow, 2).setValue("BALANCED").setFontWeight("bold");
    sheet.getRange(balanceRow, 3).clearContent();
  }
  
  // Add table borders
  // const tableRange = sheet.getRange();
  // tableRange.setBorder(false, false, false, false, true, false);
  
  // Add center line for T-Account visual
  // const centerLineRange = sheet.getRange(9, 2, maxRows + 3, 1);
  // centerLineRange.setBorder(null, true, null, true, null, null);
}

/* ----- Update t-account dropdown ---- */
function updateTAccountDropdown() {
  const activeSpreadSheet = SpreadsheetApp.getActiveSpreadsheet();
  const tAccountSheet = activeSpreadSheet.getSheetByName("T-Accounts");
  const journalEntrySheet = activeSpreadSheet.getSheetByName("Journal Entries");
  
  const columnCValues = journalEntrySheet.getRange("C:C").getValues()
    .flat()
    .filter(value => value !== "" && value != null)
    .filter((value, index, self) => self.indexOf(value) === index);
  
  if (columnCValues.length > 0) {
    const rule = SpreadsheetApp.newDataValidation()
      .requireValueInList(columnCValues, true)
      .setAllowInvalid(false)
      .setHelpText("Select an account name")
      .build();
    
    tAccountSheet.getRange("A6").setDataValidation(rule);
  }
}

/* ----- Clear the t-account table ----- */
function clearTAccountTable(sheet) {
  // Clear content from row 8 downwards
  sheet.getRange("A8:E50").clearContent().clearFormat();
  console.log("Cleared T-Account table");
}

/* ----- Display message when no data found ----- */
function displayNoDataMessage(sheet, accountName) {
  clearTAccountTable(sheet);
  sheet.getRange("B10").setValue(`No entries found for account: ${accountName}`);
  sheet.getRange("B10").setFontStyle("italic").setFontColor("red");
}

/* ----- Build trial balance ----- */
function buildTrialBalance() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const journalSheet = spreadsheet.getSheetByName('Journal Entries');
  const trialBalanceSheet = spreadsheet.getSheetByName('Trial Balance');
  
  if (!journalSheet || !trialBalanceSheet) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert('Error: Make sure both sheets exist');
    return;
  }

  // TODO: Add title
  // TODO: Add date

  // Get journal entries data
  const journalData = journalSheet.getDataRange().getValues();
  
  const accountCol = 2;
  const debitCol = 4;
  const creditCol = 5;

  // Get all unique accounts.
  const accounts = getUniqueValues("C5:C", "Journal Entries");
  // TODO: Reorder accounts in order of liquidity
  
  // Aggregate balances
  const accountBalances = {};

  try {
    accounts.forEach(account => {
        let credit = 0;
        let debit = 0;
        for (let i = 4; i < journalData.length; i++) {
          const row = journalData[i];
          if (account === row[accountCol]) {
            debit += parseFloat(row[debitCol]) || 0;
            credit += parseFloat(row[creditCol]) || 0;
          }
        }

        // Calculate normal balance
        const balance = debit - credit
        if (Math.sign(balance) === 1) {
          debit = balance;
          credit = "";
        } else {
          credit = Math.abs(balance);
          debit = "";
        }

        accountBalances[account] = {debit: debit, credit: credit};
    })

    // Rebuild trial balance
    const header = ['Account Name', 'Debit', 'Credit'];
    setupTableHeader(trialBalanceSheet, header, 4)
    
    const trialBalanceData = [];
    
    Object.keys(accountBalances).forEach(account => {
      trialBalanceData.push([
        account,
        accountBalances[account].debit,
        accountBalances[account].credit
      ]);
    });
    
    // Write new data
    if (trialBalanceData.length > 1) {
      trialBalanceSheet.getRange(5, 1, trialBalanceData.length, 3).setValues(trialBalanceData);
    }

    // Write total
    const lastRow = trialBalanceSheet.getLastRow() + 1;
    let totalDebit = 0;
    let totalCredit = 0;
    Object.keys(accountBalances).forEach(account => {
      totalDebit += parseFloat(accountBalances[account].debit) || 0;
      totalCredit += parseFloat(accountBalances[account].credit) || 0;
    })

    alert(totalDebit);
    alert(totalCredit);
 
    const total = ["Total", totalDebit, totalCredit]
    trialBalanceSheet.getRange(lastRow, 1, 1, 3).setValues([total]).setFontWeight("bold");
  } catch (err) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert(err)
  } 
}

/* ----- Update trial balance ----- */
function updateTrialBalance() {
  // Get the spreadsheet and sheets
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const journalSheet = spreadsheet.getSheetByName('Journal Entries'); // Adjust sheet name as needed
  const trialBalanceSheet = spreadsheet.getSheetByName('Trial Balance'); // Adjust sheet name as needed
  
  if (!journalSheet || !trialBalanceSheet) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert('Error: Make sure both "Journal Entries" and "Trial Balance" sheets exist');
    return;
  }
  
  // Get journal entries data (assuming columns: Date, Account, Description, Debit, Credit)
  const journalData = journalSheet.getDataRange().getValues();
  const journalHeaders = journalData[0];
  
  // Find column indices
  const accountCol = journalHeaders.indexOf('Account');
  const debitCol = journalHeaders.indexOf('Debit');
  const creditCol = journalHeaders.indexOf('Credit');
  
  if (accountCol === -1 || debitCol === -1 || creditCol === -1) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert('Error: Could not find required columns (Account, Debit, Credit) in Journal Entries sheet');
    return;
  }
  
  // Aggregate balances by account
  const accountBalances = {};
  
  // Process journal entries (skip header row)
  for (let i = 1; i < journalData.length; i++) {
    const row = journalData[i];
    const account = row[accountCol];
    const debit = parseFloat(row[debitCol]) || 0;
    const credit = parseFloat(row[creditCol]) || 0;
    
    if (account && account.toString().trim() !== '') {
      if (!accountBalances[account]) {
        accountBalances[account] = { debit: 0, credit: 0 };
      }
      accountBalances[account].debit += debit;
      accountBalances[account].credit += credit;
    }
  }
  
  // Get trial balance data
  const trialBalanceData = trialBalanceSheet.getDataRange().getValues();
  const trialBalanceHeaders = trialBalanceData[0];
  
  // Find column indices in trial balance
  const tbAccountCol = trialBalanceHeaders.indexOf('Account');
  const tbDebitCol = trialBalanceHeaders.indexOf('Debit');
  const tbCreditCol = trialBalanceHeaders.indexOf('Credit');
  
  if (tbAccountCol === -1 || tbDebitCol === -1 || tbCreditCol === -1) {
    if (DEBUG >= 1) SpreadsheetApp.getUi().alert('Error: Could not find required columns in Trial Balance sheet');
    return;
  }
  
  // Update existing accounts in trial balance
  for (let i = 1; i < trialBalanceData.length; i++) {
    const account = trialBalanceData[i][tbAccountCol];
    if (account && accountBalances[account]) {
      // Update the row with new balances
      trialBalanceSheet.getRange(i + 1, tbDebitCol + 1).setValue(accountBalances[account].debit);
      trialBalanceSheet.getRange(i + 1, tbCreditCol + 1).setValue(accountBalances[account].credit);
      
      // Mark this account as processed
      delete accountBalances[account];
    }
  }
  
  // Add new accounts that weren't in the trial balance
  const newAccounts = Object.keys(accountBalances);
  if (newAccounts.length > 0) {
    const lastRow = trialBalanceSheet.getLastRow();
    const newRowsData = [];
    
    newAccounts.forEach(account => {
      const newRow = new Array(trialBalanceHeaders.length).fill('');
      newRow[tbAccountCol] = account;
      newRow[tbDebitCol] = accountBalances[account].debit;
      newRow[tbCreditCol] = accountBalances[account].credit;
      newRowsData.push(newRow);
    });
    
    // Add new rows to trial balance
    const range = trialBalanceSheet.getRange(lastRow + 1, 1, newRowsData.length, trialBalanceHeaders.length);
    range.setValues(newRowsData);
  }
}

/* ----- Helper function to format dates ----- */
function formatDate(date) {
  if (!date) return '';
  if (date instanceof Date) {
    return Utilities.formatDate(date, Session.getScriptTimeZone(), "MM/dd/yyyy");
  }
  return date.toString();
}

// TODO: Ensure the sheet setup notification is only sent once, Using propertiesService.
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

  sheet.getRange(headerStartRow, 1, 1, headers.length)
    .setValues([headers])
    .setFontWeight("medium")
    .setBackground(HEADER_BACKGROUND_COLOR)
    .setFontColor(HEADER_FONT_COLOR)
    .setHorizontalAlignment("center");
  sheet.setFrozenRows(headerStartRow);
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
  sheet.getRange(1, 1, 2, 4)
    .setValue(sheetName)
    .setFontWeight("medium")
    .setFontSize(16)
    .merge()
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle")
}

/**
* Filter a range of values and returns only a list of unique values 
*
*@param {string} The range to get the values from
*@param {string} The name of sheet to get the values from
*@return A list of strings
*/
function getUniqueValues(range, sheetName) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName)
  const values = sheet.getRange(range).getValues()
    .flat()
    .filter(value => value !== "" && value !== null) // Remove empty values
    .filter((value, index, self) => self.indexOf(value) === index) // Remove duplicates
  return values
}

/**
* Helper alert function
*
*@customfunction
*/
function alert(value) {
  SpreadsheetApp.getUi().alert(value);
}