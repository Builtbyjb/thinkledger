package handlers

import (
	"errors"
	"fmt"
	"log"
	"server/internal/agents/gemini"
	"server/internal/database"
	"server/internal/utils"

	"github.com/gofiber/fiber/v2"
	"gorm.io/gorm"
)

type TrialBalanceResponse struct {
	Message string                    `json:"message"`
	Data    []utils.TrialBalanceEntry `json:"data"`
}

func (h *Handler) HandleTrialBalance(c *fiber.Ctx) error {
	db := h.DB

	unOrderedTrialBalance, err := generateTrialBalance(db)
	if err != nil {
		return c.Status(fiber.StatusOK).SendString("Trial Balance error")
	}

	prompt, err := generateTrialBalancePrompt(unOrderedTrialBalance)
	if err != nil {
		log.Fatalf("error generating prompt: %v", err)
	}

	OrderedTrialBalance, err := gemini.GeminiTrialBalance(prompt, h.ApiKey)
	if err != nil {
		log.Fatalf("error ordering trial balance: %v", err)
	}

	response := TrialBalanceResponse{
		Message: "Trial Balance retrieved successfully",
		Data:    OrderedTrialBalance,
	}

	return c.Status(fiber.StatusOK).JSON(response)
}

func generateTrialBalance(db *gorm.DB) ([]utils.TrialBalanceEntry, error) {
	var accounts []database.Account
	accountResult := db.Find(&accounts)
	if accountResult.Error != nil {
		return nil, fmt.Errorf("database error: %w", accountResult.Error)
	}

	if accountResult.RowsAffected == 0 {
		return nil, errors.New("no account found")
	}

	var trialBalance []utils.TrialBalanceEntry

	for i := range accounts {
		aName := accounts[i].AccountName

		var cAccounts []database.Credit
		var dAccounts []database.Debit

		cResult := db.Where("account_name = ?", aName).Find(&cAccounts)
		if cResult.Error != nil {
			return nil, fmt.Errorf("database error: %w", cResult.Error)
		}

		dResult := db.Where("account_name = ?", aName).Find(&dAccounts)
		if dResult.Error != nil {
			return nil, fmt.Errorf("database error: %w", dResult.Error)
		}

		var cList []int
		var dList []int

		for i := range cAccounts {
			cList = append(cList, cAccounts[i].Amount)
		}

		for i := range dAccounts {
			dList = append(dList, dAccounts[i].Amount)
		}

		tCredit := utils.Sum(cList)
		tDebit := utils.Sum(dList)

		var credit int
		var debit int

		bal, isDebitBal := balanceCheck(tCredit, tDebit)
		if isDebitBal {
			debit = bal
			credit = 0
		} else {
			credit = bal * -1
			debit = 0
		}

		trialBalance = append(trialBalance, utils.TrialBalanceEntry{
			AccountName: aName,
			Debit:       debit,
			Credit:      credit,
		})
	}

	return trialBalance, nil
}

func balanceCheck(c int, d int) (int, bool) {
	bal := d - c
	isDebitBal := bal >= 0

	return bal, isDebitBal
}

func generateTrialBalancePrompt(trialBalance []utils.TrialBalanceEntry) (string, error) {

	if len(trialBalance) <= 0 {
		return "", errors.New("trial balance cannot be empty")
	}

	prompt := fmt.Sprintf(`Rearrange this trial balance entries "%v" in order of
	liquidity, adhering by the following rules assets first, followed by liabilities,
	shareholder's equity, revenue, and expenses. You response should be in this format "%v".`,
		trialBalance, utils.TrialBalanceResponseFormat,
	)

	return prompt, nil
}
