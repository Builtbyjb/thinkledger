package postgres

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
	UserID        string `gorm:"type:text;not null" json:"userID"`
	InstitutionID string `gorm:"type:text;not null" json:"institutionID"`
	AccountID     string `gorm:"type:text;not null" json:"accountID"`
	AccountName   string `gorm:"type:text;not null" json:"accountName"`
	SubType       string `gorm:"type:text;not null" json:"subType"`
	Type          string `gorm:"type:text;not null" json:"type"`
}

type Institution struct {
	ID     string `gorm:"type:text;not null" json:"id"`
	UserID string `gorm:"type:text;not null" json:"userID"`
	Name   string `gorm:"type:text;not null" json:"name"`
}
