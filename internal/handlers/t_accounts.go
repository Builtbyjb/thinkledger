package handlers

// import (
// 	"errors"
// 	"fmt"
// 	"server/internal/database/postgres"
// 	"server/internal/utils"

// 	"github.com/gofiber/fiber/v2"
// 	"gorm.io/gorm"
// )

// type accountEntry struct {
// 	Credit int `json:"credit"`
// 	Debit  int `json:"debit"`
// }

// type accountEntries struct {
// 	AccountRef  string         `json:"accountRef"`
// 	AccountName string         `json:"accountName"`
// 	Entries     []accountEntry `json:"entries"`
// 	TotalCredit int            `json:"totalCredit"`
// 	TotalDebit  int            `json:"totalDebit"`
// }

// type TAccountResponse struct {
// 	Message        string         `json:"message"`
// 	Names          []string       `json:"names"`
// 	AccountEntries accountEntries `json:"accountEntries"`
// }

// // Handle T-Account
// func (h *Handler) HandleTAccount(c *fiber.Ctx) error {
// 	db := h.DB

// 	name := c.Query("name")
// 	ref := c.Query("ref")

// 	// msg := fmt.Sprintf("Account Name = %s and Account Ref = %s", name, ref)
// 	// fmt.Println(msg)

// 	accountNames, err := getAccountNames(db)
// 	if err != nil {
// 		errResponse := TAccountResponse{
// 			Message:        "Unable to retrieve account names",
// 			Names:          nil,
// 			AccountEntries: accountEntries{},
// 		}

// 		return c.Status(fiber.StatusNoContent).JSON(errResponse)
// 	}

// 	accountEntries, err := getAccountEntries(db, name, ref)
// 	if err != nil {
// 		return c.Status(fiber.StatusNoContent).SendString("No content")
// 	}

// 	response := TAccountResponse{
// 		Message:        "T-Account details retrieved successfully",
// 		Names:          accountNames,
// 		AccountEntries: accountEntries,
// 	}

// 	return c.Status(fiber.StatusOK).JSON(response)

// }

// // Get account names
// func getAccountNames(db *gorm.DB) ([]string, error) {
// 	var accounts []postgres.Account
// 	result := db.Find(&accounts)
// 	if result.Error != nil {
// 		return nil, fmt.Errorf("database error: %w", result.Error)
// 	}

// 	if result.RowsAffected == 0 {
// 		return nil, errors.New("no accounts")
// 	}

// 	var accountNames []string

// 	for i := range accounts {
// 		accountNames = append(accountNames, accounts[i].AccountName)
// 	}

// 	return accountNames, nil
// }

// // Get account debit and credit entries
// func getAccountEntries(
// 	db *gorm.DB,
// 	name string,
// 	ref string,
// ) (accountEntries, error) {

// 	var creditAcc []postgres.Credit
// 	var debitAcc []postgres.Debit
// 	var accountName string
// 	var accountRef string

// 	if name != "" {

// 		cResult := db.Where("account_name = ?", name).Find(&creditAcc)
// 		if cResult.Error != nil {
// 			return accountEntries{}, fmt.Errorf("database error: %w", cResult.Error)
// 		}

// 		dResult := db.Where("account_name = ?", name).Find(&debitAcc)
// 		if dResult.Error != nil {
// 			return accountEntries{}, fmt.Errorf("database error: %w", dResult.Error)
// 		}

// 		if cResult.RowsAffected > 0 {
// 			accountRef = creditAcc[0].AccountRef
// 		}

// 		if dResult.RowsAffected > 0 {
// 			accountRef = debitAcc[0].AccountRef
// 		}

// 		accountName = name
// 	}

// 	if ref != "" {

// 		cResult := db.Where("account_ref = ?", ref).Find(&creditAcc)
// 		if cResult.Error != nil {
// 			return accountEntries{}, fmt.Errorf("database error: %w", cResult.Error)
// 		}

// 		dResult := db.Where("account_ref = ?", ref).Find(&debitAcc)
// 		if dResult.Error != nil {
// 			return accountEntries{}, fmt.Errorf("database error: %w", dResult.Error)
// 		}

// 		if cResult.RowsAffected > 0 {
// 			accountName = creditAcc[0].AccountName
// 		}

// 		if dResult.RowsAffected > 0 {
// 			accountName = debitAcc[0].AccountName
// 		}

// 		accountRef = ref
// 	}

// 	var creditList []int
// 	for i := range creditAcc {
// 		creditList = append(creditList, creditAcc[i].Amount)
// 	}

// 	var debitList []int
// 	for i := range debitAcc {
// 		debitList = append(debitList, debitAcc[i].Amount)
// 	}

// 	aEntryList := generateAccountEntry(creditList, debitList)

// 	totalCredit := utils.Sum(creditList)
// 	totalDebit := utils.Sum(debitList)

// 	accEntries := accountEntries{
// 		AccountRef:  accountRef,
// 		AccountName: accountName,
// 		Entries:     aEntryList,
// 		TotalCredit: totalCredit,
// 		TotalDebit:  totalDebit,
// 	}

// 	return accEntries, nil
// }

// // Generate a list of the accountEntry type [{Credit Amount, Debit Amount}]
// func generateAccountEntry(cList []int, dList []int) []accountEntry {
// 	var aEntryList []accountEntry

// 	i := 0
// 	j := 0

// 	for j < len(cList) || i < len(dList) {

// 		var c int
// 		var d int

// 		// Checks if the list is empty or the index is out of bound
// 		if i >= len(dList) {
// 			d = 0
// 		} else {
// 			d = dList[i]
// 		}

// 		if i >= len(cList) {
// 			c = 0
// 		} else {
// 			c = cList[i]
// 		}

// 		aEntry := accountEntry{
// 			Credit: c,
// 			Debit:  d,
// 		}

// 		aEntryList = append(aEntryList, aEntry)
// 		j++
// 		i++
// 	}
// 	// fmt.Println(aEntryList)

// 	return aEntryList
// }
