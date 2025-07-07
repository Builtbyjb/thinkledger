import unittest
from unittest.mock import Mock, patch, ANY
from redis import Redis
from datetime import datetime
from googleapiclient.errors import HttpError
from google_core.google_sheet import GoogleSheet, JournalEntrySheet
from utils.types import JournalEntry, JournalAccount
import os


# TODO: Refactor
class TestGoogleSheet(unittest.TestCase):
  @patch.dict(os.environ, {
    "GOOGLE_SERVICE_CLIENT_ID": "client_id",
    "GOOGLE_SERVICE_CLIENT_SECRET": "client_secret"
  })
  def setUp(self) -> None:
    self.redis_mock = Mock(spec=Redis)
    self.user_id = "test_user"
    self.sheet = GoogleSheet(self.redis_mock, self.user_id, name="TestSheet")
    self.sheet.sheet_service = Mock()
    self.sheet.drive_service = Mock()
    self.sheet.script_service = Mock()

  @patch.dict(os.environ, {
    "GOOGLE_SERVICE_CLIENT_ID": "client_id",
    "GOOGLE_SERVICE_CLIENT_SECRET": "client_secret"
  })
  @patch('google_core.google_sheet.build')
  def test_create_service_success(self, mock_build) -> None:
    self.redis_mock.get.side_effect = lambda x: {
      f"service_access_token:{self.user_id}": b"access_token",
      f"service_refresh_token:{self.user_id}": b"refresh_token"
    }.get(x)

    mock_build.side_effect = [
      Mock(),  # sheets service
      Mock(),  # drive service
      Mock()   # script service
    ]

    sheet_service, drive_service, script_service = self.sheet._create_service()

    self.assertIsNotNone(sheet_service)
    self.assertIsNotNone(drive_service)
    self.assertIsNotNone(script_service)
    mock_build.assert_any_call("sheets", "v4", credentials=ANY)
    mock_build.assert_any_call("drive", "v3", credentials=ANY)
    mock_build.assert_any_call("script", "v1", credentials=ANY)

  @patch.dict(os.environ, {
    "GOOGLE_SERVICE_CLIENT_ID": "client_id",
    "GOOGLE_SERVICE_CLIENT_SECRET": "client_secret"
  })
  def test_create_service_no_access_token(self) -> None:
    self.redis_mock.get.return_value = None

    sheet_service, drive_service, script_service = self.sheet._create_service()

    self.assertIsNone(sheet_service)
    self.assertIsNone(drive_service)
    self.assertIsNone(script_service)

  def test_create_folder_new(self) -> None:
    folder_name = "test_folder"
    parent_id = "root"

    # Mock drive service response for no existing folder
    self.sheet.drive_service.files().list().execute.return_value = {'files': []}

    # Mock folder creation
    self.sheet.drive_service.files().create.return_value.execute.return_value = {'id': 'folder_id'}

    result = self.sheet._create_folder(folder_name, parent_id)

    self.assertEqual(result, 'folder_id')
    self.sheet.drive_service.files().create.assert_called_once()

  def test_create_folder_existing(self) -> None:
    folder_name = "test_folder"
    parent_id = "root"

    # Mock drive service response for existing folder
    self.sheet.drive_service.files().list().execute.return_value = {
      'files': [{'id': 'existing_folder_id'}]
    }

    result = self.sheet._create_folder(folder_name, parent_id)

    self.assertEqual(result, 'existing_folder_id')
    self.sheet.drive_service.files().create.assert_not_called()

  def test_create_spreadsheet_new(self) -> None:
    file_name = "test_spreadsheet"
    folder_id = "folder_id"
    spreadsheet_id = "spreadsheet_id"

    # Mock drive service response for no existing spreadsheet
    self.sheet.drive_service.files().list().execute.return_value = {'files': []}

    # Mock spreadsheet creation
    self.sheet.sheet_service.spreadsheets().create.return_value.execute.return_value = {
      'spreadsheetId': spreadsheet_id
    }

    # Mock file move
    self.sheet.drive_service.files().update.return_value.execute.return_value = {}

    result = self.sheet._create_spreadsheet(file_name, folder_id)

    self.assertEqual(result, spreadsheet_id)
    self.sheet.sheet_service.spreadsheets().create.assert_called_once()
    self.sheet.drive_service.files().update.assert_called_once()

  def test_append_success(self) -> None:
    spreadsheet_id = "spreadsheet_id"
    values = [["test", "data"]]
    cursor = 5

    self.redis_mock.get.return_value = cursor
    self.sheet.sheet_service.spreadsheets().values().update.return_value.execute.return_value = {}
    result = self.sheet.append(spreadsheet_id, values)
    self.assertTrue(result)
    self.redis_mock.set.assert_called_once_with( f"sheet_cursor:TestSheet:{self.user_id}", 6)

  def test_append_failure(self) -> None:
    spreadsheet_id = "spreadsheet_id"
    values = [["test", "data"]]

    self.redis_mock.get.return_value = 5
    self.sheet.sheet_service.spreadsheets().values().update.side_effect = HttpError(
      Mock(status=400), b"error"
    )

    result = self.sheet.append(spreadsheet_id, values)

    self.assertFalse(result)


class TestJournalEntrySheet(unittest.TestCase):
  @patch.dict(os.environ, {
    "GOOGLE_SERVICE_CLIENT_ID": "client_id",
    "GOOGLE_SERVICE_CLIENT_SECRET": "client_secret"
  })
  def setUp(self) -> None:
    self.redis_mock = Mock(spec=Redis)
    self.user_id = "test_user"
    self.journal_sheet = JournalEntrySheet(self.redis_mock, self.user_id)
    self.journal_sheet.sheet_service = Mock()
    self.journal_sheet.drive_service = Mock()
    self.journal_sheet.script_service = Mock()

  @patch('google_core.google_sheet.gemini_response')
  @patch('google_core.google_sheet.sanitize_gemini_response')
  def test_generate_success(self, mock_sanitize, mock_gemini) -> None:
    transaction = [
      "", "2023-01-01", "100.00", "", "", "", "Purchase", "Credit Card", "Store", "", "False"
    ]

    mock_gemini.return_value = "gemini_response"
    mock_sanitize.return_value = JournalEntry(
      date=datetime(2023, 1, 1),
      description="Purchase",
      debit=[JournalAccount(name="Expense", account_id="EXP001", amount="100.00")],
      credit=[JournalAccount(name="Credit Card", account_id="CC001", amount="100.00")]
    )

    result = self.journal_sheet.generate(transaction)

    expected = [
      ["2023-01-01", "Purchase", "Expense", "EXP001", "100.00", ""],
      ["", "", "Credit Card", "CC001", "", "100.00"]
    ]
    self.assertEqual(result, expected)

  @patch('google_core.google_sheet.gemini_response')
  def test_generate_gemini_failure(self, mock_gemini) -> None:
    transaction = [
      "", "2023-01-01", "100.00", "", "", "", "Purchase", "Credit Card", "Store", "", "False"
    ]

    mock_gemini.side_effect = Exception("Gemini error")

    result = self.journal_sheet.generate(transaction)

    self.assertIsNone(result)


if __name__ == '__main__':
  unittest.main()