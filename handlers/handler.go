package handlers

import (
	"gorm.io/gorm"
)

// To pass database engine between api endpoints
type Handler struct {
	DB     *gorm.DB
	ApiKey string
}
