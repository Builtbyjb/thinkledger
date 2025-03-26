package handlers

import (
	"errors"
	"fmt"
	"server/internal/database/postgres"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

type JournalResponse struct {
	Message string                  `json:"message"`
	Data    []postgres.JournalEntry `json:"data"`
}

func (h *Handler) HandleJournal(c *fiber.Ctx) error {
	db := h.DB

	journalEntries, err := getJournalEntries(db)
	if err != nil {
		errResponse := JournalResponse{
			Message: "Unable to retrieve journal entries",
			Data:    nil,
		}
		return c.Status(fiber.StatusNoContent).JSON(errResponse)
	}

	// jsondata, err := json.MarshalIndent(journalEntries, "", "  ")
	// if err != nil {
	// 	log.Fatalf("error: %v", err)
	// }
	// fmt.Println(string(jsondata))

	response := JournalResponse{
		Message: "Journal entries retrieved successfully",
		Data:    journalEntries,
	}

	return c.Status(fiber.StatusOK).JSON(response)
}

func getJournalEntries(db *gorm.DB) ([]postgres.JournalEntry, error) {

	// Raw journal entries from database
	var J []postgres.JournalEntry
	result := db.Find(&J)
	if result.Error != nil {
		return nil, fmt.Errorf("database error: %w", result.Error)
	}

	if result.RowsAffected == 0 {
		return nil, errors.New("no journal entries found")
	}

	// sanitized journal entries
	var JournalEntries []postgres.JournalEntry

	for i := range len(J) {

		// Get credit accounts
		var creditAccounts []postgres.Credit
		creditResult := db.Where("journal_id = ?", J[i].Id).Find(&creditAccounts)
		if creditResult.Error != nil {
			return nil, fmt.Errorf("database error: %w", creditResult.Error)
		}

		if creditResult.RowsAffected == 0 {
			return nil, errors.New("no credit accounts found")
		}

		// Get debit accounts
		var debitAccounts []postgres.Debit
		debitResult := db.Where("journal_id = ?", J[i].Id).Find(&debitAccounts)
		if debitResult.Error != nil {
			return nil, fmt.Errorf("database error: %w", debitResult.Error)
		}

		if debitResult.RowsAffected == 0 {
			return nil, errors.New("no debit accounts found")
		}

		JournalEntries = append(JournalEntries, postgres.JournalEntry{
			Id:          J[i].Id,
			Date:        J[i].Date,
			Debits:      debitAccounts,
			Credits:     creditAccounts,
			Description: J[i].Description,
		})
	}
	return JournalEntries, nil
}
