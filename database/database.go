package database

import (
	"fmt"
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func DB(
	POSTGRES_DB string,
	POSTGRES_USER string,
	POSTGRES_PASSWORD string,
	POSTGRES_HOST string,
	POSTGRES_PORT string,
) *gorm.DB {

	// Connect to database
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		POSTGRES_HOST,
		POSTGRES_PORT,
		POSTGRES_USER,
		POSTGRES_PASSWORD,
		POSTGRES_DB,
	)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Database connection error: %v", err)
	} else {
		fmt.Println("Connected to database...")
	}

	// Enable UUID extension
	db.Exec("CREATE EXTENSION IF NOT EXISTS pgcrypto")

	// Auto migrate models
	err = db.AutoMigrate(
		&JournalEntry{},
		&Account{},
		&Credit{},
		&Debit{},
	)

	if err != nil {
		log.Fatalf("failed to migrate database: %v", err)
	}

	return db
}
