package postgres

import (
	"time"

	"github.com/google/uuid"
)

type User struct {
	ID         string `gorm:"type:text;primaryKey" json:"id"`
	Email      string `gorm:"type:text;not null" json:"email"`
	Name       string `gorm:"type:text;not null" json:"name"`
	GivenName  string `gorm:"type:text;not null" json:"givenName"`
	FamilyName string `gorm:"type:text;not null" json:"familyName"`
	Picture    string `gorm:"type:text" json:"picture"`
	Locale     string `gorm:"type:text" json:"locale"`
}

type Account struct {
	Id            uuid.UUID `gorm:"type:uuid;primaryKey;default:gen_random_uuid()" json:"id"`
	AccountName   string    `gorm:"type:text;not null" json:"accountName"`
	AccountRef    string    `gorm:"type:text;not null" json:"accountRef"`
	AccountType   string    `gorm:"type:text;not null" json:"accountType"`
	NormalBalance string    `gorm:"type:text;not null" json:"normalBalance"`
}

type Credit struct {
	JournalId   uuid.UUID `gorm:"type:uuid;foreignKey" json:"journalId"` // Foreign key
	AccountId   uuid.UUID `gorm:"type:uuid;not null" json:"id"`
	AccountName string    `gorm:"type:text;not null" json:"accountName"`
	AccountRef  string    `gorm:"type:text;not null" json:"accountRef"`
	Amount      int       `gorm:"type:integer;not null" json:"amount"`
}

type Debit struct {
	JournalId   uuid.UUID `gorm:"type:uuid;foreignKey" json:"journalId"` // Foreign key
	AccountId   uuid.UUID `gorm:"type:uuid;not null" json:"id"`
	AccountName string    `gorm:"type:text;not null" json:"accountName"`
	AccountRef  string    `gorm:"type:text;not null" json:"accountRef"`
	Amount      int       `gorm:"type:integer;not null" json:"amount"`
}

type JournalEntry struct {
	Id          uuid.UUID `gorm:"type:uuid;primaryKey;default:gen_random_uuid()" json:"id"`
	Date        string    `gorm:"type:text;not null" json:"date"`
	Description string    `gorm:"type:text;not null" json:"description"`
	Credits     []Credit  `gorm:"foreignKey:JournalId" json:"credits"` // One to many relationship
	Debits      []Debit   `gorm:"foreignKey:JournalId" json:"debits"`  // One to many relationship
	CreatedAt   time.Time `json:"createdAt"`
	UpdatedAt   time.Time `json:"updatedAt"`
}
