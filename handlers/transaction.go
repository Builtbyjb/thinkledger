package handlers

import (
	"errors"
	"fmt"
	"log"
	"strconv"

	"server/agents/gemini"
	"server/database"
	"server/utils"

	"github.com/gofiber/fiber/v2"
	"github.com/google/uuid"
	"gorm.io/gorm"
)

type Transaction struct {
	Transaction string `json:"transaction"`
}

func (h *Handler) HandleTransaction(c *fiber.Ctx) error {

	// Get transaction record from the client
	var t Transaction
	if err := c.BodyParser((&t)); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "Cannot parse JSON",
		})
	}

	prompt, err := generatePrompt(t.Transaction)
	if err != nil {
		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"error": "Invalid transaction",
		})
	}

	response, err := gemini.GeminiTransaction(prompt, h.ApiKey)
	if err != nil {
		log.Fatalf("AI response error: %v", err)
	}

	if response.ClarificationNeeded {
		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"error": "More information is needed to accurately record the transaction",
			"info":  response.Questions,
		})
	}

	// Add response to database
	db := h.DB

	journal := database.JournalEntry{
		Id:          uuid.New(),
		Date:        response.JournalEntry.Date,
		Description: response.JournalEntry.Description,
	}

	// create journal entry
	journalResult := db.Create(&journal)
	if journalResult.Error != nil {
		log.Fatalf("Error creating journal entry: %v", journalResult.Error)
	}

	// INFO: Can use channels to run the functions concurrently

	// Add credit accounts
	creditAccountErr := addAccounts(db, journal.Id, response.JournalEntry.Credits, "credit")
	if creditAccountErr != nil {
		log.Fatalf("Error creating credit accounts: %v", creditAccountErr)
	}

	// Add debit accounts
	debitAccountErr := addAccounts(db, journal.Id, response.JournalEntry.Debits, "debit")
	if debitAccountErr != nil {
		log.Fatalf("Error creating debit accounts: %v", debitAccountErr)
	}

	return c.Status(fiber.StatusOK).JSON(fiber.Map{
		"success": "Transaction recorded successfully",
	})
}

// Sanitize transaction prompt
func generatePrompt(transaction string) (string, error) {

	if len(transaction) == 0 {
		return "", errors.New("Transaction cannot be empty")
	}

	prompt := fmt.Sprintf(`Create a journal entry for this transaction "%s"`, transaction)

	return prompt, nil
}

// Add journal entry accounts to the database
func addAccounts(
	db *gorm.DB,
	journalId uuid.UUID,
	accounts []utils.AccountDetail,
	t string, // Debit or Credit
) error {

	var r *gorm.DB

	for i := range len(accounts) {

		var account database.Account

		// Check if an account with this account name exist
		accountResult := db.Where("account_name", accounts[i].AccountName).First(&account)

		if accountResult.Error != nil {
			// if there is an error, The account does not exist. Create a new account
			account = database.Account{
				Id:            uuid.New(),
				AccountName:   accounts[i].AccountName,
				AccountRef:    generateAccountRef(db),
				AccountType:   accounts[i].AccountType,
				NormalBalance: accounts[i].NormalBalance,
			}

			r = db.Create(&account)
			if r.Error != nil {
				return fmt.Errorf("could not add account to database: %w", r.Error)
			}
		}

		amount, err := strconv.Atoi(accounts[i].Amount)
		if err != nil {
			return fmt.Errorf("unable to convert credit amount string to int: %w", err)
		}

		if t == "credit" {
			credit := database.Credit{
				JournalId:   journalId,
				AccountId:   account.Id,
				AccountName: accounts[i].AccountName,
				AccountRef:  account.AccountRef,
				Amount:      amount,
			}

			r = db.Create(&credit)
			if r.Error != nil {
				return fmt.Errorf("count not add credit account to database: %w", r.Error)
			}
		} else {
			debit := database.Debit{
				JournalId:   journalId,
				AccountId:   account.Id,
				AccountRef:  account.AccountRef,
				AccountName: accounts[i].AccountName,
				Amount:      amount,
			}

			r = db.Create(&debit)
			if r.Error != nil {
				return fmt.Errorf("count not add credit account to database: %w", r.Error)
			}
		}
	}
	return nil
}

// Generate Account references
func generateAccountRef(db *gorm.DB) string {
	const base int = 100

	var a []database.Account
	result := db.Find(&a)

	if result.Error != nil {
		log.Fatalf("database error: %v", result.Error)
	}

	length := int(result.RowsAffected) + base

	accountRef := fmt.Sprintf("J%v", length)

	return accountRef
}
