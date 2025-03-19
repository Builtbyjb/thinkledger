package utils

type AccountDetail struct {
	AccountName   string `json:"accountName"`
	Amount        string `json:"amount"`
	AccountType   string `json:"accountType"`
	NormalBalance string `json:"normalBalance"`
}

type JournalEntry struct {
	Date        string          `json:"date"`
	Description string          `json:"description"`
	Credits     []AccountDetail `json:"credits"`
	Debits      []AccountDetail `json:"debits"`
}

// AI response struct to store unmarshaled AI response
type TransactionResponse struct {
	ClarificationNeeded bool         `json:"clarificationNeeded"`
	Questions           []string     `json:"questions"`
	JournalEntry        JournalEntry `json:"journalEntry"`
}

var TransactionResponseFormat = `
{
	"clarificationNeeded":"", // Can be either true or false, true if you need further clarification
	"questions":[], // A list of the questions you need answered in order to accurately record the transaction
	"journalEntry": {
		"date": "", // Transaction date
		"credits": [ // For all the accounts credited
			{
  		  		"accountName": "", // Account name
  		  		"amount": "", // Amount 
				"accountType": "" // Account type
				"normalBalance": ""// The accounts normal balance, debit or credit
  		  	},
		],
		"debits": [ // For all the accounts debited
			{
  		  		"accountName": "", // Account name
  		  		"amount": "", // Amount 
				"accountType": "" // Account type
				"normalBalance": ""// The accounts normal balance, debit or credit
  		  	},
		]
		"description": "", // Why the accounts were affected, and the actions taken
	}
}`

type TrialBalanceEntry struct {
	AccountName string `json:"accountName"`
	Debit       int    `json:"debit"`
	Credit      int    `json:"credit"`
}

var TrialBalanceResponseFormat = `
[
{"accountName": "", "debit": 0, "credit": 0},
]
`
