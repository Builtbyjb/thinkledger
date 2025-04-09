package utils

import (
	"golang.org/x/oauth2"
)

// In memory token store
type TokenStore interface {
	GetToken(userID string) (*oauth2.Token, error)
	SaveToken(userID string, token *oauth2.Token) error
}

// Google active scopes
type ActiveScopes struct {
	GoogleSheet string
	GoogleDrive string
}

// Google user info
type UserInfo struct {
	Sub        string `json:"sub"`
	Email      string `json:"email"`
	Name       string `json:"name"`
	GivenName  string `json:"given_name"`
	FamilyName string `json:"family_name"`
	Picture    string `json:"picture"`
	Locale     string `json:"locale"`
}

// Plaid transaction response
type PlaidTransactionResponse struct {
	Added                    []PlaidTransaction        `json:"added"`
	HasMore                  bool                      `json:"has_more"`
	Modified                 []PlaidTransaction        `json:"modified"`
	NextCursor               string                    `json:"next_cursor"`
	Removed                  []RemovedPlaidTransaction `json:"removed"`
	RequestID                string                    `json:"request_id"`
	TransactionsUpdateStatus string                    `json:"transactions_update_status,omitempty"`
}

type RemovedPlaidTransaction struct {
	AccountID     string `json:"account_id"`
	TransactionID string `json:"transaction_id"`
}

type PlaidTransaction struct {
	AccountID               string                                  `json:"account_id"`
	AccountOwner            string                                  `json:"account_owner,omitempty"`
	Amount                  float32                                 `json:"amount"`
	AuthorizedDate          string                                  `json:"authorized_data"`
	AuthorizedDatetime      string                                  `json:"authorized_datatime,omitempty"`
	Category                []string                                `json:"category"`
	CategoryID              string                                  `json:"category_id"`
	CheckNumber             string                                  `json:"check_number,omitempty"`
	Date                    string                                  `json:"date"`
	Datetime                string                                  `json:"datetime,omitempty"`
	ISOCurrencyCode         string                                  `json:"iso_currency_code"`
	Location                PlaidTransactionLocation                `json:"location"`
	MerchantName            string                                  `json:"merchant_name,omitempty"`
	Name                    string                                  `json:"name"`
	PaymentChannel          string                                  `json:"payment_channel"`
	PaymentMeta             PlaidTransactionPaymentMeta             `json:"payment_meta"`
	Pending                 bool                                    `json:"pending"`
	PendingTransactionID    string                                  `json:"pending_transaction_id"`
	PersonalFinanceCategory PlaidTransactionPersonalFinanceCategory `json:"personal_finance_category"`
	TransactionCode         string                                  `json:"transaction_code,omitempty"`
	TransactionID           string                                  `json:"transaction_id"`
	UnofficialCurrencyCode  string                                  `json:"unofficial_currency_code,omitempty"`
}

type PlaidTransactionPersonalFinanceCategory struct {
	ConfidenceLevel string `json:"confidence_level"`
	Detailed        string `json:"detailed"`
	Primary         string `json:"primary"`
}

type PlaidTransactionPaymentMeta struct {
	ByOrderOf        string `json:"by_order_of,omitempty"`
	Payee            string `json:"payee,omitempty"`
	Payer            string `json:"payer,omitempty"`
	PaymentMethod    string `json:"payment_method,omitempty"`
	PaymentProcessor string `json:"payment_precessor,omitempty"`
	PPDID            string `json:"ppd_id,omitempty"`
	Reason           string `json:"reason,omitempty"`
	ReferenceNumber  string `json:"reference_number,omitempty"`
}

type PlaidTransactionLocation struct {
	Address     string `json:"address,omitempty"`
	City        string `json:"city,omitempty"`
	Country     string `json:"country"`
	Lat         string `json:"lax,omitempty"`
	Lon         string `json:"lon,omitempty"`
	PostalCode  string `json:"postal_code,omitempty"`
	Region      string `json:"region,omityempty"`
	StoreNumber string `json:"store_number,omityempty"`
}

// Google chat event
type ChatEvent struct {
	Type      string `json:"type"`
	EventTime string `json:"eventTime"`
	Space     struct {
		Name        string `json:"name"`
		Type        string `json:"type"`
		DisplayName string `json:"displayName"`
	} `json:"space"`
	Message struct {
		Name       string `json:"name"`
		CreateTime string `json:"createTime"`
		Sender     struct {
			Name        string `json:"name"`
			DisplayName string `json:"displayName"`
			Email       string `json:"email"` // May be empty for Chat apps
		} `json:"sender"`
		Text   string `json:"text"`
		Thread struct {
			Name string `json:"name"`
		} `json:"thread"`
	} `json:"message"` // message is present for MESSAGE events
}

// Plaid metadata
type Account struct {
	ClassType          string `json:"class_type"`
	ID                 string `json:"id"`
	Name               string `json:"name"`
	Type               string `json:"type"`
	SubType            string `json:"sub_type"`
	Mask               string `json:"mask"`
	VerificationStatus string `json:"verification_status"`
}

type Institution struct {
	InstitutionID string `json:"institution_id"`
	Name          string `json:"name"`
}

// Depss
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
