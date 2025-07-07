# type: ignore
import unittest
from unittest.mock import Mock, patch
from redis import Redis
from sqlalchemy.orm import Session
from main import handle_high_priority_task
from google_core.google_sheet import GoogleSheet, TransactionSheet, JournalEntrySheet
from database.postgres.postgres_schema import Institution
from utils.tasks import TaskPriority, Tasks


class TestHandleHighPriorityTask(unittest.TestCase):
  def setUp(self) -> None:
    self.mock_redis = Mock(spec=Redis)
    self.mock_session = Mock(spec=Session)
    self.mock_session.exec = Mock()
    self.mock_google_sheet = Mock(spec=GoogleSheet)
    self.mock_transaction_sheet = Mock(spec=TransactionSheet)
    self.mock_journal_entry_sheet = Mock(spec=JournalEntrySheet)
    self.user_id = "test_user_123"

  def test_no_high_priority_tasks(self) -> None:
    self.mock_redis.llen.return_value = 0
    result = handle_high_priority_task(self.mock_session, self.mock_redis, self.user_id)
    self.assertIsNone(result)
    self.mock_redis.llen.assert_called_once_with(f"task:{TaskPriority.HIGH.value}:{self.user_id}")

  def test_redis_llen_error(self) -> None:
    self.mock_redis.llen.side_effect = Exception("Redis error")
    result = handle_high_priority_task(self.mock_session, self.mock_redis, self.user_id)
    self.assertIsNone(result)

  def test_redis_rpop_error(self) -> None:
    self.mock_redis.llen.return_value = 1
    self.mock_redis.rpop.side_effect = Exception("Pop error")
    result = handle_high_priority_task(self.mock_session, self.mock_redis, self.user_id)
    self.assertIsNone(result)

  def test_setup_spreadsheet_task_success(self) -> None:
    self.mock_redis.llen.return_value = 1
    self.mock_redis.rpop.return_value = "setup_spreadsheet"
    with patch('main.get_task', return_value=Tasks.setup_spreadsheet.value):
      with patch('main.GoogleSheet', return_value=self.mock_google_sheet):
        self.mock_google_sheet.__init__(
          redis=self.mock_redis, user_id=self.user_id, init=True)
        result = handle_high_priority_task(self.mock_session, self.mock_redis, self.user_id)
        self.assertIsNone(result)

  def test_setup_spreadsheet_task_failure(self) -> None:
    self.mock_redis.llen.return_value = 1
    self.mock_redis.rpop.return_value = "setup_spreadsheet"
    with patch('main.get_task', return_value=Tasks.setup_spreadsheet.value):
      with patch('main.GoogleSheet', side_effect=Exception("Sheet error")):
        result = handle_high_priority_task(self.mock_session, self.mock_redis, self.user_id)
        self.assertIsNone(result)

  def test_sync_transaction_task_success(self) -> None:
    self.mock_redis.llen.return_value = 1
    self.mock_redis.rpop.return_value = "sync_transaction:spreadsheet_123"
    self.mock_session.exec.return_value = [Mock(spec=Institution, access_token="access-token123")]
    self.mock_transaction_sheet.append.return_value = True
    self.mock_journal_entry_sheet.append.return_value = True
    self.mock_journal_entry_sheet.generate.return_value = ["journal_entry_data"]

    with patch('main.get_task', return_value=Tasks.sync_transaction.value):
      with patch('main.get_task_args', return_value=["spreadsheet_123"]):
        with patch('main.get_transactions', return_value=["trans1"]):
          with patch('main.parse_transactions', return_value=["parsed_trans"]):
            with patch( 'main.TransactionSheet', return_value=self.mock_transaction_sheet):
              with patch( 'main.JournalEntrySheet', return_value=self.mock_journal_entry_sheet):
                  result = handle_high_priority_task(
                    self.mock_session, self.mock_redis, self.user_id
                    )
                  self.assertIsNone(result)
                  self.mock_transaction_sheet.append.assert_called_once_with(
                    "spreadsheet_123", ["parsed_trans"]
                    )
                  self.mock_journal_entry_sheet.append.assert_called_once_with(
                    "spreadsheet_123", ["journal_entry_data"]
                    )

  def test_sync_transaction_db_error(self) -> None:
    self.mock_redis.llen.return_value = 1
    self.mock_redis.rpop.return_value = "sync_transaction:spreadsheet_123"
    self.mock_session.exec.side_effect = Exception("DB error")
    with patch('main.get_task', return_value=Tasks.sync_transaction.value):
      with patch('main.get_task_args', return_value=["spreadsheet_123"]):
        with self.assertRaises(Exception) as context:
          handle_high_priority_task(self.mock_session, self.mock_redis, self.user_id)
        self.assertEqual(str(context.exception), "Error getting institution: DB error")

  def test_invalid_task_value_type(self) -> None:
    self.mock_redis.llen.return_value = 1
    self.mock_redis.rpop.return_value = 123
    with self.assertRaises(ValueError) as context:
      handle_high_priority_task(self.mock_session, self.mock_redis, self.user_id)
    self.assertEqual(str(context.exception), "Value must be a string")

  def test_none_task_value(self) -> None:
    self.mock_redis.llen.return_value = 1
    self.mock_redis.rpop.return_value = None
    result = handle_high_priority_task(self.mock_session, self.mock_redis, self.user_id)
    self.assertIsNone(result)


if __name__ == '__main__':
  unittest.main()