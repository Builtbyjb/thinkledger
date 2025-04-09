package postgres

import (
	"fmt"
	"log"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func DB() *gorm.DB {

	POSTGRES_URL := os.Getenv("POSTGRES_URL")

	// Connect to database
	db, err := gorm.Open(postgres.Open(POSTGRES_URL), &gorm.Config{})
	if err != nil {
		log.Fatalf("Database connection error: %v", err)
	} else {
		fmt.Println("Connected to database...")
	}

	// Enable UUID extension
	db.Exec("CREATE EXTENSION IF NOT EXISTS pgcrypto")

	// Auto migrate models
	err = db.AutoMigrate(
		&User{},
		&Account{},
		&Institution{},
	)
	if err != nil {
		log.Fatalf("failed to migrate database: %v", err)
	}

	return db
}
